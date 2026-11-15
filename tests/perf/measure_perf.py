# Copyright (c) 2026 Renaud Guillon
"""Measure the game's frame times in Chromium on the machine's GPU (DEV-PERF-06).

Serves a build (the production `dist/` by default), starts each level asked for at a time of its
run with the URL debug options (DEV-OPT-01), lets it play for a while untouched, and reports:
the frame intervals (FPS, percentiles, long frames), the main thread's time per frame (the
simulation and the drawing, from the engine's begin to its end of frame), the GPU's time per frame
(a timer query, where the browser has one), the draw calls and the active meshes.

`--load` times the levels' loading instead, step by step, from a cold start (PERF-08, PERF-09).

`--uncapped` lifts the 60 Hz cap (no vsync), so the FPS shows the headroom; `--cpu-slowdown N`
slows the page's CPU N times (Chrome's throttling), an older machine's processor; `--profile`
prints the functions the main thread spends the most time in.

    uv run python tests/perf/measure_perf.py --levels 1-1,4-1 --seconds 20 --uncapped
"""

import argparse
import contextlib
import functools
import http.server
import json
import socketserver
import sys
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

GPU_ARGS = ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"]
UNCAPPED_ARGS = ["--disable-gpu-vsync", "--disable-frame-rate-limit"]

# Installed once the level plays: counts every frame from the engine's begin to its end (the
# main thread's work), the frame intervals, the draw calls and active meshes of every scene, and
# the GPU's frame time when the browser has a timer query.
INSTALL = """() => {
  const B = window.BABYLON;
  const engine = B.EngineStore.Instances[0];
  const probe = { intervals: [], cpu: [], gpu: [], draws: [], meshes: [], last: 0, begin: 0 };
  const scenes = engine.scenes.map((scene) => {
    const inst = new B.SceneInstrumentation(scene);
    inst.captureFrameTime = true;
    return inst;
  });
  let gpu = null;
  try {
    gpu = new B.EngineInstrumentation(engine);
    gpu.captureGPUFrameTime = true;
  } catch (e) { gpu = null; }
  engine.onBeginFrameObservable.add(() => {
    const now = performance.now();
    if (probe.last) probe.intervals.push(now - probe.last);
    probe.last = now;
    probe.begin = now;
  });
  engine.onEndFrameObservable.add(() => {
    probe.cpu.push(performance.now() - probe.begin);
    let draws = 0;
    let meshes = 0;
    for (const scene of engine.scenes) {
      meshes += scene.getActiveMeshes().length;
    }
    for (const inst of scenes) draws += inst.drawCallsCounter.current;
    probe.draws.push(draws);
    probe.meshes.push(meshes);
    if (gpu && gpu.gpuFrameTimeCounter.current > 0) {
      probe.gpu.push(gpu.gpuFrameTimeCounter.current / 1e6);
    }
  });
  window.__perfProbe = probe;
}"""


# Installed before the page's own scripts (so its frame callback runs first in each frame): from
# the frame the level's loading screen is added to the one it is removed in, each frame's start
# and the loading bar's progress then, which tells the loading step the frame ran (PERF-09). The
# main thread's profile of that time is taken with `console.profile` (`--profile`).
LOAD_PROBE = """() => {
  const probe = { frames: [], start: 0, end: 0, profile: false };
  window.__loadProbe = probe;
  const percent = () => {
    const bar = document.querySelector('.level-loading .loading-bar');
    return bar ? Number(bar.getAttribute('aria-valuenow')) : -1;
  };
  const frame = (now) => {
    if (probe.start && !probe.end) probe.frames.push([performance.now(), percent()]);
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
  new MutationObserver((records) => {
    for (const record of records) {
      for (const node of record.addedNodes) {
        if (node.classList && node.classList.contains('level-loading') && !probe.start) {
          probe.start = performance.now();
          if (probe.profile) console.profile('load');
        }
      }
      for (const node of record.removedNodes) {
        if (node.classList && node.classList.contains('level-loading') && !probe.end) {
          probe.end = performance.now();
          if (probe.profile) console.profileEnd('load');
        }
      }
    }
  }).observe(document, { childList: true, subtree: true });
}"""

# The loading steps of `GameSession._new_load`, in order (PERF-09).
LOAD_STEPS = [
    "ground",
    "ask roads",
    "textures",
    "build",
    "prepare",
    "enemies",
    "roads",
    "compile",
    "start",
]


def _serve(root: Path, port: int) -> socketserver.TCPServer:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_args: Any) -> None:
            return

    handler = functools.partial(Quiet, directory=str(root))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _out(text: str = "") -> None:
    """Write a line of the report on the standard output."""
    sys.stdout.write(text + "\n")


def _percentile(values: list[float], share: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(share * len(ordered)))]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


@contextlib.contextmanager
def _profiling(page: Page, enabled: bool) -> Iterator[dict[str, Any]]:
    result: dict[str, Any] = {}
    if not enabled:
        yield result
        return
    cdp = page.context.new_cdp_session(page)
    cdp.send("Profiler.enable")
    cdp.send("Profiler.setSamplingInterval", {"interval": 200})
    cdp.send("Profiler.start")
    yield result
    result["profile"] = cdp.send("Profiler.stop")["profile"]


def _inclusive(profile: dict[str, Any], count: int, names: Any) -> list[tuple[float, str]]:
    """Return the functions with the most inclusive time (with all they call), as shares."""
    nodes = {node["id"]: node for node in profile["nodes"]}
    parent: dict[int, int] = {}
    for node in profile["nodes"]:
        for child in node.get("children", []):
            parent[child] = node["id"]
    hits: dict[str, int] = {}
    total = 0
    for sample in profile.get("samples", []):
        total += 1
        seen: set[str] = set()
        node_id: int | None = sample
        while node_id is not None:
            frame = nodes[node_id]["callFrame"]
            key = names(frame)
            if key not in seen:
                seen.add(key)
                hits[key] = hits.get(key, 0) + 1
            node_id = parent.get(node_id)
    ranked = sorted(hits.items(), key=lambda item: -item[1])[:count]
    return [(100.0 * hits_ / max(1, total), key) for key, hits_ in ranked]


def _namer(build: Path) -> Any:
    """Return a namer of profile frames: their function, or the nearest one above them.

    For an anonymous function in the game's bundle, the nearest method (`get name()`) or function
    above its line.
    """
    lines: list[str] = []
    bundle = build / "js" / "game.js"
    if bundle.exists():
        lines = bundle.read_text().split("\n")

    def name(frame: dict[str, Any]) -> str:
        url = frame["url"].rsplit("/", 1)[-1].split("?")[0]
        label = frame["functionName"] or "(anonymous)"
        line = frame["lineNumber"]
        if url == "game.js" and lines and 0 <= line < len(lines):
            for k in range(line, max(0, line - 400), -1):
                text = lines[k].strip()
                if text.startswith("get ") and text.endswith("() {"):
                    owner = ""
                    for j in range(k, max(0, k - 3000), -1):
                        if "= __class__(" in lines[j]:
                            owner = lines[j].split("__class__(")[1].split(",")[0].strip('"') + "."
                            break
                    label = owner + text[4:-5] if label == "(anonymous)" else label
                    break
                if label != "(anonymous)":
                    break
        return label + " " + url + ":" + str(line)

    return name


def _top_functions(profile: dict[str, Any], count: int) -> list[tuple[float, str]]:
    """Return the functions with the most self time, as shares of the samples."""
    nodes = {node["id"]: node for node in profile["nodes"]}
    hits: dict[str, int] = {}
    total = 0
    for sample in profile.get("samples", []):
        node = nodes[sample]
        frame = node["callFrame"]
        name = frame["functionName"] or "(anonymous)"
        url = frame["url"].rsplit("/", 1)[-1]
        key = name + " " + url + ":" + str(frame["lineNumber"])
        hits[key] = hits.get(key, 0) + 1
        total += 1
    ranked = sorted(hits.items(), key=lambda item: -item[1])[:count]
    return [(100.0 * hits_ / max(1, total), key) for key, hits_ in ranked]


def measure_level(page: Page, base: str, level: str, args: argparse.Namespace) -> dict[str, Any]:
    """Start `level` at `args.at` seconds, let it settle, then measure it for `args.seconds`."""
    page.goto(base + "?level=" + level + "&t=" + str(args.at))
    # The level loads in steps, then plays (its HUD shows, its loading screen goes): measured from
    # `settle` seconds after, whatever the machine's speed, so runs see the same part of the level.
    page.wait_for_selector(".game-hud", state="visible", timeout=300000)
    page.wait_for_selector(".loading-screen", state="detached", timeout=300000)
    page.wait_for_timeout(args.settle * 1000)
    page.evaluate(INSTALL)
    with _profiling(page, args.profile) as prof:
        page.wait_for_timeout(args.seconds * 1000)
    probe = page.evaluate(
        "() => { const p = window.__perfProbe;"
        " return {intervals: p.intervals, cpu: p.cpu, gpu: p.gpu, draws: p.draws,"
        " meshes: p.meshes}; }"
    )
    intervals = probe["intervals"]
    report = {
        "level": level,
        "frames": len(intervals),
        "fps": 1000.0 / _mean(intervals) if intervals else 0.0,
        "frame_p50": _percentile(intervals, 0.5),
        "frame_p95": _percentile(intervals, 0.95),
        "frame_p99": _percentile(intervals, 0.99),
        "frame_max": max(intervals) if intervals else 0.0,
        "over_16_7": sum(1 for v in intervals if v > 1000 / 60 * 1.2),
        "cpu_mean": _mean(probe["cpu"]),
        "cpu_p95": _percentile(probe["cpu"], 0.95),
        "gpu_mean": _mean(probe["gpu"]),
        "gpu_p95": _percentile(probe["gpu"], 0.95),
        "draws_mean": _mean(probe["draws"]),
        "draws_max": max(probe["draws"]) if probe["draws"] else 0,
        "meshes_mean": _mean(probe["meshes"]),
    }
    if "profile" in prof:
        report["top"] = _top_functions(prof["profile"], args.top)
        report["inclusive"] = _inclusive(prof["profile"], args.top, _namer(Path(args.build)))
    return report


def measure_load(page: Page, base: str, level: str, args: argparse.Namespace) -> dict[str, Any]:
    """Start `level` cold (`?level=`), and time its loading, step by step (PERF-08, PERF-09)."""
    result: dict[str, Any] = {}
    cdp = None
    if args.profile:
        cdp = page.context.new_cdp_session(page)
        cdp.send("Profiler.enable")
        cdp.send("Profiler.setSamplingInterval", {"interval": 200})
        cdp.on("Profiler.consoleProfileFinished", lambda event: result.update(event))
    # A build whose worker logs its jobs (`[worker] <kind> <t> ms, ends at <epoch ms>`).
    worker_jobs: list[str] = []

    def on_console(message: Any) -> None:
        if message.text.startswith("[worker]"):
            worker_jobs.append(message.text)

    page.on("console", on_console)
    # From the level's start, as when it is confirmed.
    page.goto(base + "?level=" + level)
    if args.profile:
        page.evaluate("() => { window.__loadProbe.profile = true; }")
    page.wait_for_function(
        "() => window.__loadProbe && window.__loadProbe.end > 0", timeout=300000, polling=100
    )
    probe = page.evaluate("() => window.__loadProbe")
    steps = [0.0 for _ in LOAD_STEPS]
    step_frames = [0 for _ in LOAD_STEPS]
    longest = [0.0 for _ in LOAD_STEPS]
    frames = probe["frames"]
    marks = [[probe["start"], 0]]
    marks.extend(frames)
    marks.append([probe["end"], 100])
    for k in range(len(marks) - 1):
        time_ms = marks[k + 1][0] - marks[k][0]
        done = max(0, marks[k][1])
        index = min(len(LOAD_STEPS) - 1, round(done / 100 * len(LOAD_STEPS)))
        steps[index] += time_ms
        step_frames[index] += 1
        longest[index] = max(longest[index], time_ms)
    report: dict[str, Any] = {
        "level": level,
        "load_ms": probe["end"] - probe["start"],
        "frames": len(marks) - 1,
        "steps": [
            [LOAD_STEPS[i], steps[i], step_frames[i], longest[i]] for i in range(len(LOAD_STEPS))
        ],
    }
    origin = page.evaluate("() => performance.timeOrigin")
    report["worker"] = []
    for text in worker_jobs:
        words = text.split(" ")
        ends = float(words[-1]) - origin - probe["start"]
        report["worker"].append([words[1], float(words[2]), ends])
    page.remove_listener("console", on_console)
    if cdp is not None:
        page.wait_for_timeout(500)
        if "profile" in result:
            if args.save_profile:
                Path(args.save_profile).write_text(json.dumps(result["profile"]))
            report["top"] = _top_functions(result["profile"], args.top)
            report["inclusive"] = _inclusive(result["profile"], args.top, _namer(Path(args.build)))
    return report


def _print_load(report: dict[str, Any]) -> None:
    _out(f"{report['level']}: loaded in {report['load_ms']:.0f} ms over {report['frames']} frames")
    for name, time_ms, frames, longest in report["steps"]:
        _out(f"    {name:9s} {time_ms:7.0f} ms  {frames:4d} frames  longest {longest:6.0f} ms")
    for kind, time_ms, ends in report.get("worker", []):
        _out(f"    worker {kind:8s} {time_ms:7.1f} ms, ends {ends:7.0f} ms into the load")
    for share, key in report.get("top", []):
        _out(f"    {share:5.1f}%  {key}")
    if report.get("inclusive"):
        _out("  inclusive:")
    for share, key in report.get("inclusive", []):
        _out(f"    {share:5.1f}%  {key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--levels", default="1-1,2-1,3-1,4-1")
    parser.add_argument("--at", type=float, default=30.0, help="start time in the level (s)")
    parser.add_argument("--settle", type=float, default=3.0, help="seconds after the load")
    parser.add_argument("--seconds", type=float, default=15.0)
    parser.add_argument("--build", default="dist")
    parser.add_argument("--port", type=int, default=8771)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--uncapped", action="store_true")
    parser.add_argument("--cpu-slowdown", type=float, default=1.0)
    parser.add_argument("--software", action="store_true", help="SwiftShader, no GPU")
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--load", action="store_true", help="time the levels' loading instead")
    parser.add_argument("--save-profile", help="write the (last) load's CPU profile there")
    parser.add_argument("--repeat", type=int, default=1, help="loads of each level (--load)")
    args = parser.parse_args()
    server = _serve(Path(args.build), args.port)
    launch = [] if args.software else list(GPU_ARGS)
    if args.uncapped:
        launch.extend(UNCAPPED_ARGS)
    reports = []
    try:
        with sync_playwright() as play:
            browser = play.chromium.launch(args=launch)
            page = browser.new_page(viewport={"width": args.width, "height": args.height})
            if args.cpu_slowdown > 1:
                cdp = page.context.new_cdp_session(page)
                cdp.send("Emulation.setCPUThrottlingRate", {"rate": args.cpu_slowdown})
            base = "http://127.0.0.1:" + str(args.port) + "/"
            if args.load:
                page.add_init_script("(" + LOAD_PROBE + ")();")
                for level in args.levels.split(","):
                    for _ in range(args.repeat):
                        report = measure_load(page, base, level.strip(), args)
                        reports.append(report)
                        if not args.json:
                            _print_load(report)
            for level in [] if args.load else args.levels.split(","):
                report = measure_level(page, base, level.strip(), args)
                reports.append(report)
                if not args.json:
                    __out(report)
            browser.close()
    finally:
        server.shutdown()
    if args.json:
        _out(json.dumps(reports, indent=1))


def __out(report: dict[str, Any]) -> None:
    _out(
        f"{report['level']}: {report['fps']:.1f} fps over {report['frames']} frames;"
        f" frame p50 {report['frame_p50']:.1f} p95 {report['frame_p95']:.1f}"
        f" p99 {report['frame_p99']:.1f} max {report['frame_max']:.1f} ms,"
        f" {report['over_16_7']} over 20 ms;"
        f" CPU {report['cpu_mean']:.2f} (p95 {report['cpu_p95']:.2f}) ms;"
        f" GPU {report['gpu_mean']:.2f} (p95 {report['gpu_p95']:.2f}) ms;"
        f" draws {report['draws_mean']:.0f} (max {report['draws_max']}),"
        f" active meshes {report['meshes_mean']:.0f}"
    )
    for share, key in report.get("top", []):
        _out(f"    {share:5.1f}%  {key}")
    if report.get("inclusive"):
        _out("  inclusive:")
    for share, key in report.get("inclusive", []):
        _out(f"    {share:5.1f}%  {key}")


if __name__ == "__main__":
    main()
