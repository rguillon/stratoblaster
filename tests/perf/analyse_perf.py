# Copyright (c) 2026 Renaud Guillon
"""Analyse which component of the game uses which resource (PERF-02), in Chromium on the GPU.

Builds an unminified copy of the production bundle (so a profile's frames name their Python
module), serves it, and measures, into JSON files under `--out`:

- `play`: for each scenario (a level at a time of its run, the ship firing), the frames (interval,
  the main thread's work, its drawing part, the GPU's time, draw calls), the main thread's CPU
  profile and its allocations by component (`perf_attribution.py`), what the scene holds
  (meshes, triangles, buffers, textures, by component), and the cost of drawing each component
  (on a frozen frame, one thing taken away at a time);
- `load`: each level's loading from a cold start, step by step, with the main thread's profile
  and the workers' jobs;
- `boot`: the page's start up to the title screen, and the cost of the title and level select;
- `size`: what the bundles are made of, by package, and the size of every file downloaded.

    uv run python tests/perf/analyse_perf.py --out /tmp/perf --only play --scenarios 4-1@30
"""

import argparse
import gzip
import itertools
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from measure_perf import LOAD_PROBE, LOAD_STEPS, _serve
from perf_attribution import Bundle, Shares, allocation_shares, cpu_shares
from perf_probes import (
    ABLATION,
    BOOT_TIMINGS,
    INIT,
    INVENTORY,
    PLAY_PROBE,
    TAKE_FRAMES,
)
from playwright.sync_api import CDPSession, Page, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
ESBUILD = ROOT / "node" / "node_modules" / ".bin" / "esbuild"
GPU_ARGS = {
    "vulkan": ["--use-angle=vulkan", "--enable-features=Vulkan"],
    "gl": ["--use-gl=angle", "--use-angle=gl-egl"],
    "metal": ["--use-angle=metal"],
}
COMMON_ARGS = ["--enable-gpu", "--ignore-gpu-blocklist", "--enable-precise-memory-info"]
# The scenarios measured by default: `level@seconds` or `level@boss`.
SCENARIOS = "1-1@30,2-1@30,3-1@30,4-1@30,2-5@120,3-3@120,4-5@200,1-3@final,4-5@final"
ALL_LEVELS = ",".join(f"{world}-{level}" for world in range(1, 5) for level in range(1, 6))
# The ship's lives in the unminified bundle (`HULL_RULES`, game/config/hull.py).
LIVES = re.compile(r'(HULL_RULES = record\(dict\(\{ "lives": )\d+')
# The columns of a frame timed by `PLAY_PROBE`.
FRAME_COLUMNS = [
    "interval",
    "work",
    "render",
    "gpu",
    "draws",
    "active",
    "evaluate",
    "targets",
    "heap",
]
METRICS = [
    "LayoutCount",
    "RecalcStyleCount",
    "LayoutDuration",
    "RecalcStyleDuration",
    "ScriptDuration",
    "TaskDuration",
    "JSHeapUsedSize",
    "Nodes",
]


def _out(text: str = "") -> None:
    """Write a line of progress on the standard output."""
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def build_profiled(out: Path, lives: int) -> Path:
    """Make `out/dist`: the production `dist/` with unminified bundles; return it.

    The ship gets `lives` lives there (the one change to the game: left alone and firing, it
    would lose its three within a scenario, and the game over would be measured instead of play).
    Also writes `out/size.json`: the bytes of each Python module in the minified bundles.
    """
    dist = out / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    shutil.copytree(ROOT / "dist", dist)
    sizes: dict[str, Any] = {"bundles": {}, "files": []}
    for entry, name in (("game/main.js", "game.js"), ("worker/worker_main.js", "ground_worker.js")):
        source = "./build/" + entry
        base = [str(ESBUILD), source, "--bundle", "--format=esm", "--log-level=warning"]
        subprocess.run([*base, "--outfile=" + str(dist / "js" / name)], cwd=ROOT, check=True)  # noqa: S603
        meta = out / (name + ".meta.json")
        minified = out / (name + ".min.js")
        subprocess.run(  # noqa: S603
            [*base, "--minify", "--metafile=" + str(meta), "--outfile=" + str(minified)],
            cwd=ROOT,
            check=True,
        )
        inputs = next(iter(json.loads(meta.read_text())["outputs"].values()))["inputs"]
        sizes["bundles"][name] = {
            path.rsplit("/", 1)[-1][:-3]: value["bytesInOutput"] for path, value in inputs.items()
        }
        meta.unlink()
        minified.unlink()
    game = dist / "js" / "game.js"
    text, count = LIVES.subn(lambda found: found.group(1) + str(lives), game.read_text())
    if count != 1:
        msg = "the ship's lives were not found in the bundle (game/config/hull.py)"
        raise RuntimeError(msg)
    game.write_text(text)
    for path in sorted((ROOT / "dist").rglob("*")):
        if path.is_file() and path.name != ".public":
            data = path.read_bytes()
            sizes["files"].append([
                str(path.relative_to(ROOT / "dist")),
                len(data),
                len(gzip.compress(data, 9)),
            ])
    (out / "size.json").write_text(json.dumps(sizes, indent=1))
    return dist


def _bundles(dist: Path) -> dict[str, Bundle]:
    return {
        "game.js": Bundle(dist / "js" / "game.js", "build/game/"),
        "ground_worker.js": Bundle(dist / "js" / "ground_worker.js", "build/worker/"),
    }


def _column(frames: list[list[float]], name: str) -> list[float]:
    index = FRAME_COLUMNS.index(name) + 1
    return [frame[index] for frame in frames]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _percentile(values: list[float], share: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(share * len(ordered)))]


def frame_stats(frames: list[list[float]]) -> dict[str, Any]:
    """Return the means and percentiles of the frames of `PLAY_PROBE`, and a line per second."""
    frames = frames[1:]
    stats: dict[str, Any] = {"frames": len(frames)}
    for name in FRAME_COLUMNS:
        values = _column(frames, name)
        if name == "gpu":
            values = [value for value in values if value > 0]
        stats[name] = {
            "mean": _mean(values),
            "p50": _percentile(values, 0.5),
            "p95": _percentile(values, 0.95),
            "p99": _percentile(values, 0.99),
            "max": max(values) if values else 0.0,
        }
    heap = _column(frames, "heap")
    grown = sum(max(0.0, b - a) for a, b in itertools.pairwise(heap))
    span = (frames[-1][0] - frames[0][0]) / 1000 if len(frames) > 1 else 0.0
    stats["allocated_per_s"] = grown / span if span > 0 else 0.0
    stats["collections"] = sum(1 for a, b in itertools.pairwise(heap) if b < a)
    seconds: dict[int, list[list[float]]] = {}
    start = frames[0][0] if frames else 0.0
    for frame in frames:
        seconds.setdefault(int((frame[0] - start) / 1000), []).append(frame)
    stats["per_second"] = [
        [second, len(rows)] + [round(_mean(_column(rows, name)), 2) for name in FRAME_COLUMNS]
        for second, rows in sorted(seconds.items())
    ]
    return stats


def _metrics(cdp: CDPSession) -> dict[str, float]:
    values = {m["name"]: m["value"] for m in cdp.send("Performance.getMetrics")["metrics"]}
    return {name: values.get(name, 0.0) for name in METRICS}


def _shares_json(shares: Shares) -> dict[str, Any]:
    return shares.summary()


def _open_level(page: Page, base: str, scenario: str) -> None:
    level, _, at = scenario.partition("@")
    option = "&boss=" + at if at in {"mini", "final"} else "&t=" + (at or "0")
    page.goto(base + "?level=" + level + option)
    page.wait_for_selector(".game-hud", state="visible", timeout=300000)
    page.wait_for_selector(".loading-screen", state="detached", timeout=300000)
    page.wait_for_selector(".level-loading", state="detached", timeout=300000)


def measure_play(
    page: Page, base: str, scenario: str, args: argparse.Namespace, bundles: dict[str, Bundle]
) -> dict[str, Any]:
    """Measure one scenario: frames, CPU profile, allocations, inventory and drawing costs."""
    _open_level(page, base, scenario)
    cdp = page.context.new_cdp_session(page)
    cdp.send("Performance.enable")
    cdp.send("Profiler.enable")
    page.keyboard.down("Space")
    page.wait_for_timeout(args.settle * 1000)
    page.evaluate(PLAY_PROBE)
    report: dict[str, Any] = {"scenario": scenario}
    # 1. The frames, with nothing else running.
    page.evaluate(TAKE_FRAMES)
    before = _metrics(cdp)
    page.wait_for_timeout(args.seconds * 1000)
    after = _metrics(cdp)
    report["plain"] = frame_stats(page.evaluate(TAKE_FRAMES))
    report["page"] = {name: after[name] - before[name] for name in METRICS}
    report["page"]["JSHeapUsedSize"] = after["JSHeapUsedSize"]
    report["page"]["Nodes"] = after["Nodes"]
    # 2. The main thread's CPU profile.
    cdp.send("Profiler.setSamplingInterval", {"interval": args.sampling})
    cdp.send("Profiler.start")
    page.evaluate(TAKE_FRAMES)
    page.wait_for_timeout(args.seconds * 1000)
    frames = page.evaluate(TAKE_FRAMES)
    profile = cdp.send("Profiler.stop")["profile"]
    report["profiled"] = frame_stats(frames)
    report["cpu"] = _shares_json(cpu_shares(profile, bundles))
    if args.save_profiles:
        name = scenario.replace("@", "-at-") + ".cpuprofile"
        (Path(args.out) / name).write_text(json.dumps(profile))
    # 3. What is allocated, garbage included.
    cdp.send("HeapProfiler.enable")
    cdp.send(
        "HeapProfiler.startSampling",
        {
            "samplingInterval": 8192,
            "includeObjectsCollectedByMajorGC": True,
            "includeObjectsCollectedByMinorGC": True,
        },
    )
    page.evaluate(TAKE_FRAMES)
    page.wait_for_timeout(args.alloc_seconds * 1000)
    frames = page.evaluate(TAKE_FRAMES)
    sampled = cdp.send("HeapProfiler.stopSampling")["profile"]
    report["allocations"] = _shares_json(allocation_shares(sampled, bundles))
    report["allocations"]["frames"] = len(frames) - 1
    report["allocations"]["seconds"] = args.alloc_seconds
    # 4. What the scene holds, then the cost of drawing each component of this frame.
    report["over"] = page.locator(".level-complete").count() > 0
    report["inventory"] = page.evaluate(INVENTORY)
    report["ablation"] = page.evaluate(ABLATION, args.ablation_frames)
    page.keyboard.up("Space")
    cdp.detach()
    return report


def measure_load(
    page: Page, base: str, level: str, bundles: dict[str, Bundle], profiled: bool
) -> dict[str, Any]:
    """Time `level`'s loading from a cold start: its steps, its profile, the workers' jobs."""
    result: dict[str, Any] = {}
    cdp = page.context.new_cdp_session(page)
    if profiled:
        cdp.send("Profiler.enable")
        cdp.send("Profiler.setSamplingInterval", {"interval": 500})
        cdp.on("Profiler.consoleProfileFinished", lambda event: result.update(event))
    page.goto(base + "?level=" + level)
    if profiled:
        page.evaluate("() => { window.__loadProbe.profile = true; }")
    page.wait_for_function(
        "() => window.__loadProbe && window.__loadProbe.end > 0", timeout=300000, polling=100
    )
    probe = page.evaluate("() => window.__loadProbe")
    marks = [[probe["start"], 0], *probe["frames"], [probe["end"], 100]]
    steps = [[name, 0.0, 0, 0.0] for name in LOAD_STEPS]
    for k in range(len(marks) - 1):
        time_ms = marks[k + 1][0] - marks[k][0]
        index = min(len(LOAD_STEPS) - 1, round(max(0, marks[k][1]) / 100 * len(LOAD_STEPS)))
        steps[index][1] += time_ms
        steps[index][2] += 1
        steps[index][3] = max(steps[index][3], time_ms)
    report: dict[str, Any] = {
        "level": level,
        "load_ms": probe["end"] - probe["start"],
        "start": probe["start"],
        "frames": len(marks) - 1,
        "steps": steps,
        "workers": page.evaluate("() => window.__workerLog"),
        "heap": page.evaluate("() => performance.memory.usedJSHeapSize"),
    }
    if profiled:
        page.wait_for_timeout(500)
        if "profile" in result:
            report["cpu"] = _shares_json(cpu_shares(result["profile"], bundles))
    cdp.detach()
    return report


def _menu_frames(page: Page, cdp: CDPSession, seconds: float) -> dict[str, Any]:
    page.evaluate(TAKE_FRAMES)
    before = _metrics(cdp)
    page.wait_for_timeout(seconds * 1000)
    after = _metrics(cdp)
    stats = frame_stats(page.evaluate(TAKE_FRAMES))
    stats["page"] = {name: after[name] - before[name] for name in METRICS}
    return stats


def measure_boot(page: Page, base: str, bundles: dict[str, Bundle]) -> dict[str, Any]:
    """Time the page's start up to the title screen, then the title and the level select."""
    result: dict[str, Any] = {}
    cdp = page.context.new_cdp_session(page)
    cdp.send("Performance.enable")
    cdp.send("Profiler.enable")
    cdp.send("Profiler.setSamplingInterval", {"interval": 500})
    cdp.on("Profiler.consoleProfileFinished", lambda event: result.update(event))
    # A page of the same origin first, to ask for the profile of the next one's start.
    page.goto(base + "sfx/hit.ogg?blank")
    page.evaluate("() => sessionStorage.setItem('__bootProfile', '1')")
    page.goto(base)
    page.wait_for_selector(".loading-screen", state="detached", timeout=300000)
    page.evaluate("() => { console.profileEnd('boot'); sessionStorage.clear(); }")
    report: dict[str, Any] = {"timings": page.evaluate(BOOT_TIMINGS)}
    page.wait_for_timeout(500)
    if "profile" in result:
        report["cpu"] = _shares_json(cpu_shares(result["profile"], bundles))
    report["metrics"] = _metrics(cdp)
    page.wait_for_timeout(2000)
    page.evaluate(PLAY_PROBE)
    report["title"] = _menu_frames(page, cdp, 6)
    page.keyboard.press("Enter")
    page.wait_for_timeout(1500)
    # The highlighted level is built ahead, hidden (PERF-13): its steps, then the screen at rest.
    report["level_select_building"] = _menu_frames(page, cdp, 6)
    report["level_select"] = _menu_frames(page, cdp, 6)
    report["heap_menus"] = page.evaluate("() => performance.memory.usedJSHeapSize")
    cdp.detach()
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--out", required=True, help="directory of the results")
    parser.add_argument("--only", default="play,load,boot", help="play, load, boot")
    parser.add_argument("--scenarios", default=SCENARIOS)
    parser.add_argument("--levels", default=ALL_LEVELS, help="levels whose loading is timed")
    parser.add_argument("--settle", type=float, default=12.0, help="seconds before measuring")
    parser.add_argument("--seconds", type=float, default=15.0, help="seconds per measure")
    parser.add_argument("--alloc-seconds", type=float, default=8.0)
    parser.add_argument("--ablation-frames", type=int, default=90)
    parser.add_argument("--sampling", type=int, default=500, help="CPU profile interval (µs)")
    parser.add_argument("--port", type=int, default=8772)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--gpu", default="vulkan", choices=sorted(GPU_ARGS))
    parser.add_argument("--cpu-slowdown", type=float, default=1.0)
    parser.add_argument("--save-profiles", action="store_true")
    parser.add_argument("--lives", type=int, default=99, help="the ship's lives while measured")
    parser.add_argument("--no-build", action="store_true", help="reuse `--out`/dist")
    return parser


def main() -> None:
    """Run the measures asked for and write their JSON files."""
    args = _parser().parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dist = out / "dist" if args.no_build else build_profiled(out, args.lives)
    bundles = _bundles(dist)
    server = _serve(dist, args.port)
    base = "http://127.0.0.1:" + str(args.port) + "/"
    only = args.only.split(",")
    launch = [*GPU_ARGS[args.gpu], *COMMON_ARGS]
    try:
        with sync_playwright() as play:
            browser = play.chromium.launch(channel="chromium", args=launch)

            def new_page(load_probe: bool) -> Page:
                context = browser.new_context(viewport={"width": args.width, "height": args.height})
                page = context.new_page()
                page.add_init_script("(" + INIT + ")();")
                if load_probe:
                    page.add_init_script("(" + LOAD_PROBE + ")();")
                if args.cpu_slowdown > 1:
                    cdp = context.new_cdp_session(page)
                    cdp.send("Emulation.setCPUThrottlingRate", {"rate": args.cpu_slowdown})
                return page

            if "boot" in only:
                page = new_page(False)
                report = measure_boot(page, base, bundles)
                (out / "boot.json").write_text(json.dumps(report, indent=1))
                _out("boot: title after " + str(round(report["timings"]["now"])) + " ms")
                page.context.close()
            if "load" in only:
                loads = []
                for level in args.levels.split(","):
                    for profiled in (False, True):
                        page = new_page(True)
                        report = measure_load(page, base, level.strip(), bundles, profiled)
                        report["profiled"] = profiled
                        loads.append(report)
                        _out(f"load {level}: {report['load_ms']:.0f} ms (profiled: {profiled})")
                        page.context.close()
                    (out / "load.json").write_text(json.dumps(loads, indent=1))
            if "play" in only:
                for scenario in args.scenarios.split(","):
                    page = new_page(False)
                    report = measure_play(page, base, scenario.strip(), args, bundles)
                    name = "play-" + scenario.strip().replace("@", "-at-") + ".json"
                    (out / name).write_text(json.dumps(report, indent=1))
                    plain = report["plain"]
                    _out(
                        f"play {scenario}: work {plain['work']['mean']:.2f} ms,"
                        f" render {plain['render']['mean']:.2f} ms,"
                        f" gpu {plain['gpu']['mean']:.2f} ms,"
                        f" draws {plain['draws']['mean']:.0f}, over: {report['over']}"
                    )
                    page.context.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
