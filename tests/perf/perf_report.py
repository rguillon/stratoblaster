# Copyright (c) 2026 Renaud Guillon
"""Write the tables of an `analyse_perf.py` run as Markdown.

uv run python tests/perf/perf_report.py /tmp/perf > tables.md
"""

import json
import sys
from pathlib import Path
from typing import Any

# What is not the main thread working.
NOT_WORK = {"(idle)", "(profiler start)"}
# Bytes per pixel of a texture, by Babylon's texture type (0: bytes, 1: floats, 2: half floats).
PIXEL_BYTES = {0: 4, 1: 16, 2: 8}
MB = 1024 * 1024


def _out(text: str = "") -> None:
    sys.stdout.write(text + "\n")


def table(head: list[str], rows: list[list[Any]]) -> None:
    """Write a Markdown table; numbers are right-aligned."""
    _out("| " + " | ".join(head) + " |")
    _out("|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|")
    for row in rows:
        _out("| " + " | ".join(str(cell) for cell in row) + " |")
    _out()


def num(value: float, digits: int = 2) -> str:
    """Return `value` with `digits` decimals; a dash for nothing."""
    if value == 0:
        return "-"
    return f"{value:.{digits}f}"


def matrix(
    columns: list[str], cells: dict[str, dict[str, float]], digits: int, first: str, least: float
) -> None:
    """Write rows (keys of `cells`) by `columns`, largest mean first; rows under `least` summed."""
    rows = []
    rest = dict.fromkeys(columns, 0.0)
    order = sorted(cells, key=lambda key: -sum(cells[key].get(c, 0.0) for c in columns))
    for key in order:
        values = [cells[key].get(c, 0.0) for c in columns]
        if max(values) < least:
            for c in columns:
                rest[c] += cells[key].get(c, 0.0)
            continue
        rows.append([key, *[num(v, digits) for v in values]])
    if any(rest.values()):
        rows.append(["(others)", *[num(rest[c], digits) for c in columns]])
    totals = [sum(cells[key].get(c, 0.0) for key in cells) for c in columns]
    rows.append(["**total**", *["**" + num(v, digits) + "**" for v in totals]])
    table([first, *columns], rows)


def play_overview(plays: dict[str, Any]) -> None:
    """Write the frames of each scenario."""
    _out("## Play: the frames of each scenario\n")
    rows = []
    for name, play in plays.items():
        plain = play["plain"]
        work = plain["work"]
        rows.append([
            name,
            num(work["mean"]),
            num(work["p95"], 1),
            num(work["max"], 1),
            num(plain["render"]["mean"]),
            num(work["mean"] - plain["render"]["mean"]),
            num(plain["gpu"]["mean"]),
            num(plain["gpu"]["p95"]),
            num(plain["draws"]["mean"], 0),
            num(plain["draws"]["max"], 0),
            num(plain["active"]["mean"], 0),
            num(plain["interval"]["p99"], 1),
            num(plain["allocated_per_s"] / MB, 1),
            num(play["page"]["JSHeapUsedSize"] / MB, 0),
            "yes" if play["over"] else "",
        ])
    table(
        [
            "scenario",
            "work ms",
            "p95",
            "max",
            "draw ms",
            "sim+view ms",
            "GPU ms",
            "GPU p95",
            "draw calls",
            "max",
            "active meshes",
            "interval p99",
            "alloc MB/s",
            "heap MB",
            "over",
        ],
        rows,
    )


def play_cpu(plays: dict[str, Any]) -> None:
    """Write the main thread's time by component, and the modules behind it."""
    _out("## Play: main thread, ms per frame, by component (CPU profile)\n")
    names = list(plays)
    cells: dict[str, dict[str, float]] = {}
    for name, play in plays.items():
        frames = play["profiled"]["frames"]
        for component, time_ms in play["cpu"]["component"]:
            if component not in NOT_WORK:
                cells.setdefault(component, {})[name] = time_ms / frames
    matrix(names, cells, 2, "component", 0.03)
    _out("### The game's modules that answer for the most time (ms per frame)\n")
    cells = {}
    for name, play in plays.items():
        frames = play["profiled"]["frames"]
        for module, time_ms in play["cpu"]["owner_module"]:
            if not module.startswith("(") and module != "babylon":
                cells.setdefault(module, {})[name] = time_ms / frames
    matrix(names, cells, 3, "module", 0.03)
    _out("### The functions with the most self time (ms per frame)\n")
    cells = {}
    for name, play in plays.items():
        frames = play["profiled"]["frames"]
        for function, time_ms in play["cpu"]["function"]:
            if not function.startswith("(idle)"):
                cells.setdefault("`" + function + "`", {})[name] = time_ms / frames
    matrix(names, cells, 3, "function", 0.12)


def play_allocations(plays: dict[str, Any]) -> None:
    """Write what each component allocates."""
    _out("## Play: allocations, KB per frame, by component (sampled, garbage included)\n")
    names = list(plays)
    cells: dict[str, dict[str, float]] = {}
    modules: dict[str, dict[str, float]] = {}
    for name, play in plays.items():
        allocations = play["allocations"]
        frames = max(1, allocations["frames"])
        for component, size in allocations["component"]:
            cells.setdefault(component, {})[name] = size / 1024 / frames
        for module, size in allocations["owner_module"]:
            modules.setdefault(module, {})[name] = size / 1024 / frames
    matrix(names, cells, 0, "component", 8)
    _out("### By module (KB per frame)\n")
    matrix(names, modules, 0, "module", 15)


def _delta(whole: dict[str, float], without: dict[str, float], key: str) -> float:
    return whole[key] - without[key]


def play_drawing(plays: dict[str, Any]) -> None:
    """Write the cost of drawing each component of a frozen frame."""
    _out("## Play: what drawing each component costs (one frozen frame per scenario)\n")
    for name, play in plays.items():
        ablation = play["ablation"]
        variants = ablation["variants"]
        whole = variants["whole frame"]
        main = ablation["mainPass"]["whole frame"]
        _out(f"### {name}\n")
        again = [variants[k]["cpu"] for k in variants if k.startswith("whole frame")]
        _out(
            f"Whole frame: {whole['cpu']:.2f} ms of main thread to draw it"
            f" (measured {len(again)} times: {min(again):.2f} to {max(again):.2f}),"
            f" {whole['gpu']:.2f} ms of GPU, {whole['draws']:.0f} draw calls."
            f" Main pass alone (no glow layers, no shadow map): {main['cpu']:.2f} ms,"
            f" {main['gpu']:.2f} ms of GPU, {main['draws']:.0f} draw calls.\n"
        )
        rows = []
        for component, count in ablation["counts"].items():
            if component not in variants or component not in ablation["mainPass"]:
                continue
            off = variants[component]
            main_off = ablation["mainPass"][component]
            rows.append([
                component,
                count,
                num(_delta(whole, off, "draws"), 0),
                num(_delta(main, main_off, "draws"), 0),
                f"{_delta(whole, off, 'cpu'):+.2f}",
                f"{_delta(main, main_off, 'cpu'):+.2f}",
                f"{_delta(whole, off, 'gpu'):+.2f}",
                f"{_delta(main, main_off, 'gpu'):+.2f}",
            ])
        rows.sort(key=lambda row: -float(row[4]))
        table(
            [
                "component hidden",
                "meshes shown",
                "draw calls",
                "of which main pass",
                "CPU ms",
                "main pass",
                "GPU ms",
                "main pass",
            ],
            rows,
        )
        rows = []
        for key, value in variants.items():
            if key in ablation["counts"] or key == "whole frame":
                continue
            rows.append([
                key,
                f"{_delta(whole, value, 'cpu'):+.2f}",
                f"{_delta(whole, value, 'gpu'):+.2f}",
                num(_delta(whole, value, "draws"), 0),
            ])
        table(["taken away", "CPU ms saved", "GPU ms saved", "draw calls saved"], rows)
        kinds = ablation.get("enemyKinds", {})
        enemies = play["inventory"]["enemies"]
        rows = []
        for kind, value in kinds.items():
            entry = enemies.get(kind, {})
            shown = entry.get("shown", 0)
            saved = _delta(whole, value, "cpu")
            rows.append([
                kind,
                shown,
                value["meshes"],
                num(entry.get("triangles", 0), 0),
                num(_delta(whole, value, "draws"), 0),
                f"{saved:+.2f}",
                f"{saved / shown:.2f}" if shown else "",
                f"{_delta(whole, value, 'gpu'):+.2f}",
            ])
        rows.sort(key=lambda row: -float(row[5]))
        if rows:
            table(
                [
                    "enemy kind",
                    "on screen",
                    "meshes",
                    "triangles",
                    "draw calls",
                    "CPU ms",
                    "per enemy",
                    "GPU ms",
                ],
                rows,
            )


def play_inventory(plays: dict[str, Any]) -> None:
    """Write what each scene holds."""
    _out("## Play: what the scene holds, by component\n")
    for name, play in plays.items():
        inventory = play["inventory"]
        groups: dict[str, list[float]] = {}
        for component, shown, triangles, thin, size, instance_size, _kind, _shadow in inventory[
            "meshes"
        ]:
            entry = groups.setdefault(component, [0, 0, 0, 0, 0, 0])
            entry[0] += 1
            entry[1] += shown
            entry[2] += triangles * max(1, thin) if shown else 0
            entry[3] += thin if shown else 0
            entry[4] += size
            entry[5] += instance_size
        canvas = inventory["canvas"]
        _out(f"### {name}\n")
        _out(
            f"{inventory['total']} meshes, {inventory['nodes']} transform nodes,"
            f" {inventory['materials']} materials, {inventory['effects']} shader programs,"
            f" canvas {canvas['width']}x{canvas['height']} with {canvas['samples']}x MSAA,"
            f" JS heap {inventory['heap'] / MB:.0f} MB.\n"
        )
        rows = [
            [
                component,
                int(entry[0]),
                int(entry[1]),
                num(entry[2], 0),
                num(entry[3], 0),
                inventory["kinds"].get(component, 0),
                num(entry[4] / 1024, 0),
                num(entry[5] / 1024, 0),
            ]
            for component, entry in sorted(groups.items(), key=lambda item: -item[1][2])
        ]
        table(
            [
                "component",
                "meshes",
                "shown",
                "triangles drawn",
                "thin instances",
                "materials",
                "geometry KB",
                "instance buffers KB",
            ],
            rows,
        )
    _out("### Textures and render targets (estimated GPU memory)\n")
    for name, play in plays.items():
        rows = []
        total = 0.0
        for texture in play["inventory"]["textures"]:
            size = texture["width"] * texture["height"] * PIXEL_BYTES.get(texture["kind"], 4)
            size *= 6 if texture["cube"] else 1
            size *= 4 / 3 if texture["mipmaps"] else 1
            size *= max(1, texture["samples"]) if texture["target"] else 1
            total += size
            rows.append([
                texture["name"] or "(generated)",
                f"{texture['width']}x{texture['height']}",
                "target" if texture["target"] else ("cube" if texture["cube"] else "texture"),
                ", ".join(texture["users"]),
                num(size / MB, 1),
            ])
        canvas = play["inventory"]["canvas"]
        frame = canvas["width"] * canvas["height"] * (canvas["samples"] * 8 + 4)
        rows.append(["canvas (colour + depth, MSAA, resolve)", "", "", "", num(frame / MB, 1)])
        rows.append(["**total**", "", "", "", "**" + num((total + frame) / MB, 1) + "**"])
        _out(f"#### {name}\n")
        table(["texture", "size", "kind", "used by", "MB"], rows)


def play_parts(plays: dict[str, Any]) -> None:
    """Write the meshes shown, by name."""
    _out("## Play: the meshes shown, by name (numbers dropped)\n")
    for name, play in plays.items():
        parts = sorted(play["inventory"]["parts"].items(), key=lambda item: -item[1][0])
        _out(f"### {name}\n")
        rows = [[key, value[0], num(value[1], 0)] for key, value in parts[:25]]
        table(["component | mesh", "meshes shown", "triangles"], rows)


def _jobs(log: list[dict[str, Any]]) -> dict[str, float]:
    """Return the time of the workers' jobs by kind: from asked (or the worker free) to answered."""
    asked: dict[tuple[int, int], dict[str, Any]] = {}
    free: dict[int, float] = {}
    times: dict[str, float] = {}
    for event in log:
        key = (event["worker"], event["id"])
        if event["way"] == "ask":
            asked.setdefault(key, event)
            continue
        ask = asked.get(key)
        if ask is None:
            continue
        start = max(ask["at"], free.get(event["worker"], 0.0))
        free[event["worker"]] = event["at"]
        times[ask["kind"]] = times.get(ask["kind"], 0.0) + event["at"] - start
    return times


def load_tables(loads: list[dict[str, Any]]) -> None:
    """Write each level's loading."""
    _out("## Loading: each level from a cold start (`?level=`), ms\n")
    plain = [load for load in loads if not load["profiled"]]
    steps = [step[0] for step in plain[0]["steps"]]
    rows = []
    for load in plain:
        jobs = _jobs(load["workers"])
        longest = max(step[3] for step in load["steps"])
        rows.append([
            load["level"],
            num(load["load_ms"], 0),
            *[num(step[1], 0) for step in load["steps"]],
            num(longest, 0),
            num(jobs.get("ground", 0), 0),
            num(jobs.get("texture", 0), 0),
            num(jobs.get("roads", 0), 0),
            num(load["heap"] / MB, 0),
        ])
    head = ["level", "total", *steps, "longest frame", "worker: ground", "textures", "roads"]
    table([*head, "heap MB"], rows)
    _out("### Main thread during the loading, ms, by component (CPU profile)\n")
    profiled = [load for load in loads if load["profiled"] and "cpu" in load]
    names = [load["level"] for load in profiled]
    cells: dict[str, dict[str, float]] = {}
    modules: dict[str, dict[str, float]] = {}
    for load in profiled:
        for component, time_ms in load["cpu"]["component"]:
            if component not in NOT_WORK:
                cells.setdefault(component, {})[load["level"]] = time_ms
        for module, time_ms in load["cpu"]["owner_module"]:
            if not module.startswith("("):
                modules.setdefault(module, {})[load["level"]] = time_ms
    matrix(names, cells, 0, "component", 25)
    _out("### The modules behind it (ms)\n")
    matrix(names, modules, 0, "module", 40)


def boot_tables(boot: dict[str, Any]) -> None:
    """Write the page's start and the menus."""
    _out("## Start-up: from the page's request to the title screen\n")
    timings = boot["timings"]
    _out(
        f"Title screen after {timings['now']:.0f} ms (local server, no network delay);"
        f" JS heap then {timings['heap'] / MB:.0f} MB,"
        f" {boot['heap_menus'] / MB:.0f} MB after the level select built a level ahead.\n"
    )
    cpu = boot.get("cpu")
    if cpu:
        rows = [[key, num(value, 0)] for key, value in cpu["component"] if value >= 4]
        table(["component", "ms"], rows)
        rows = [[key, num(value, 0)] for key, value in cpu["owner_module"][:22]]
        table(["module", "ms"], rows)
    _out("### The menus' frames\n")
    rows = []
    for key in ("title", "level_select_building", "level_select"):
        stats = boot[key]
        rows.append([
            key.replace("_", " "),
            num(stats["work"]["mean"]),
            num(stats["work"]["max"], 1),
            num(stats["render"]["mean"]),
            num(stats["gpu"]["mean"]),
            num(stats["draws"]["mean"], 0),
            num(stats["active"]["mean"], 0),
        ])
    table(["screen", "work ms", "max", "draw ms", "GPU ms", "draw calls", "active meshes"], rows)


def size_tables(size: dict[str, Any]) -> None:
    """Write the files downloaded and what the bundles are made of."""
    _out("## Download: the files of `dist/`\n")
    rows = []
    groups: dict[str, list[int]] = {}
    for path, raw, packed in size["files"]:
        key = (
            "sfx/*.ogg"
            if path.endswith(".ogg")
            else ("sfx/*.mp3" if path.endswith(".mp3") else path)
        )
        entry = groups.setdefault(key, [0, 0, 0])
        entry[0] += 1
        entry[1] += raw
        entry[2] += packed
    for key, entry in groups.items():
        rows.append([key, entry[0], num(entry[1] / 1024, 0), num(entry[2] / 1024, 0)])
    table(["file", "files", "KB", "KB gzip"], rows)
    for bundle, modules in size["bundles"].items():
        packages: dict[str, list[float]] = {}
        for module, count in modules.items():
            parts = module.split(".")
            depth = 3 if parts[0] == "game" and len(parts) > 3 else 2
            key = ".".join(parts[: min(depth, len(parts) - 1)]) or module
            entry = packages.setdefault(key, [0, 0])
            entry[0] += 1
            entry[1] += count
        total = sum(entry[1] for entry in packages.values())
        _out(f"### `{bundle}` (minified, {total / 1024:.0f} KB), by package\n")
        rows = [
            [key, int(entry[0]), num(entry[1] / 1024, 0), num(100 * entry[1] / total, 1)]
            for key, entry in sorted(packages.items(), key=lambda item: -item[1][1])
            if entry[1] / total >= 0.004
        ]
        table(["package", "modules", "KB", "%"], rows)


def main() -> None:
    """Write every table of the run in the directory given."""
    out = Path(sys.argv[1])
    plays = {}
    for path in sorted(out.glob("play-*.json")):
        play = json.loads(path.read_text())
        plays[play["scenario"]] = play
    if plays:
        play_overview(plays)
        play_cpu(plays)
        play_drawing(plays)
        play_allocations(plays)
        play_inventory(plays)
        play_parts(plays)
    if (out / "load.json").exists():
        load_tables(json.loads((out / "load.json").read_text()))
    if (out / "boot.json").exists():
        boot_tables(json.loads((out / "boot.json").read_text()))
    if (out / "size.json").exists():
        size_tables(json.loads((out / "size.json").read_text()))


if __name__ == "__main__":
    main()
