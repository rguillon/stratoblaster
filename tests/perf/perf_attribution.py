# Copyright (c) 2026 Renaud Guillon
"""Say which component of the game a sample of a CPU or allocation profile belongs to.

The profiles are taken on an unminified bundle (`analyse_perf.py` makes one), where esbuild leaves
a `// build/game/<module>.js` comment before each Python module's code: a frame's line gives its
module. A sample goes to the component of the deepest frame of its stack whose module names one
(`COMPONENTS`); helpers shared by every component (the Transcrypt runtime, the Babylon wrappers)
name none, so their time goes to whoever called them, with Babylon's and the browser's own time
below them. A sample with no such frame is Babylon drawing the scene: it goes to the part of the
drawing it is in (`RENDER_PHASES`).
"""

import bisect
import re
from pathlib import Path
from typing import Any

# The components, by the modules that make them: the first pattern that matches wins.
COMPONENTS: list[tuple[str, str]] = [
    (r"^audio\.|^app\.(game_audio|page_audio)|^game\.view\.audio", "audio (music, sounds)"),
    (
        r"^core\.scenery\.(traffic|road_traffic)|^render\.scenery\.(traffic_layer|imposter)",
        "traffic",
    ),
    (r"^game\.view\.props\.car", "traffic"),
    (
        r"^render\.scenery\.(terrain|lava)|^core\.scenery\.(height_field|ground_fit|ice_sculpt)",
        "terrain",
    ),
    (r"^core\.scenery\.(cliff_blocks|ground_boxes)", "terrain"),
    (
        r"^render\.scenery\.(road|tile_road)|^core\.scenery\.(road_|street_|lanes|tile_streets)",
        "roads",
    ),
    (r"^render\.scenery\.(prop_field|window)|^game\.view\.props", "buildings & props"),
    (r"^core\.scenery\.(prop_placement|district|tile_packing|block_towers)", "buildings & props"),
    (r"^core\.scenery\.(away_placement|float_placement|draws|ordering)", "buildings & props"),
    (
        r"^render\.scenery\.(sky|cloud|weather|rain|lightning|aurora|plume|atmosphere)",
        "sky & weather",
    ),
    (r"^render\.scenery\.scenery_(lighting|look)|^render\.environment", "sky & weather"),
    (r"^core\.scenery\.(atmosphere|lightning|sky_look)", "sky & weather"),
    (r"^render\.scenery\.procedural_textures|^core\.math\.noise", "procedural textures & noise"),
    (r"^render\.scenery\.|^core\.scenery\.", "scenery stage (streaming, ground)"),
    (r"^game\.view\.reactor_flame", "reactor flames (ship & enemies)"),
    (
        r"^game\.view\.(ship_|player_ship)|^core\.systems\.(player_flight|player_hull|ship_journey)",
        "player ship",
    ),
    (r"^core\.entities\.player_ship", "player ship"),
    (r"^game\.view\.enemies\.(enemy_shot_renderer|enemy_lasers|missile_smoke)", "enemy shots"),
    (r"^core\.systems\.enemy_shots|^app\.enemy_viewer_shots", "enemy shots"),
    (
        r"^game\.view\.enemies\.blast|^app\.hit_blasts|^game\.view\.shots\.(impact|spark)",
        "effects & bonuses",
    ),
    (
        r"^game\.view\.(bombs|bonuses)|^core\.systems\.(bonus_world|player_bombs)",
        "effects & bonuses",
    ),
    (r"^game\.view\.shots|^game\.view\.shot_geometry", "player shots"),
    (
        r"^core\.systems\.(shot_world|projectile_motion|beam|run_arsenal|player_hits|gun_muzzles)",
        "player shots",
    ),
    (r"^core\.entities\.(weapon|muzzle|barrel|shot_target)", "player shots"),
    (r"^game\.view\.bosses|^core\.systems\.boss|^core\.entities\.boss", "bosses"),
    (
        r"^game\.view\.enemies|^render\.enemy_layer|^core\.entities\.(enemy|jointed_enemy)",
        "enemies",
    ),
    (r"^core\.systems\.(enemy_world|enemy_motion|wave_runner|level_models)", "enemies"),
    (r"^ui\.|^app\.(game_play_hud|menu|pause_menu|settings_menu)", "HUD & menus (DOM)"),
    (r"^input\.|^app\.listen_controls", "input"),
    (
        r"^app\.(graphics_quality|perf_monitor|rate_meter)|^core\.loop|^render\.quality",
        "frame pacing & quality",
    ),
    (
        r"^core\.systems\.level_run|^app\.game_play|^app\.level_scene|^render\.game_view",
        "level run (other)",
    ),
    (r"^app\.(game_session|level_prepare)|^assets\.", "level loading (steps)"),
    (r"^game\.(sim|config)|^core\.content", "game content & rules"),
    (r"^render\.geometry|^render\.(mesh_merge|edge_trim|outline)", "model geometry"),
    (r"^host\.", "host (storage, worker data)"),
]
_COMPILED = [(re.compile(pattern), name) for pattern, name in COMPONENTS]

# Where a sample of Babylon's drawing is, by the first of these functions on its stack.
RENDER_PHASES: list[tuple[str, str]] = [
    ("_renderForShadowMap", "Babylon: shadow map pass"),
    ("_shadowMap.customRenderFunction", "Babylon: shadow map pass"),
    ("_renderMainTexture", "Babylon: glow layers (scene drawn again)"),
    ("_renderToTarget", "Babylon: glow layers (scene drawn again)"),
    ("_evaluateActiveMeshes", "Babylon: active meshes (culling, world matrices)"),
    ("_prepareRenderingManager", "Babylon: main pass (draw list)"),
    ("_RenderSorted", "Babylon: main pass (draw submission)"),
    ("_renderForCamera", "Babylon: scene render (other)"),
    ("render", "Babylon: scene render (other)"),
]

RUNTIME = "org.transcrypt.__runtime__"


class Bundle:
    """The module of each line of an unminified bundle."""

    def __init__(self, path: Path, prefix: str) -> None:
        marker = "// " + prefix
        self._lines: list[int] = []
        self._modules: list[str] = []
        for number, line in enumerate(path.read_text().split("\n")):
            if line.startswith(marker) and line.endswith(".js"):
                self._lines.append(number)
                self._modules.append(line[len(marker) : -3])

    def module(self, line: int) -> str:
        """Return the module of the bundle's `line` (from 0)."""
        index = bisect.bisect_right(self._lines, line) - 1
        return self._modules[index] if index >= 0 else "(bundle)"


def module_of(frame: dict[str, Any], bundles: dict[str, Bundle]) -> str:
    """Return the module of a profile's call frame: a Python module, `babylon`, or `(native)`."""
    url = frame["url"].rsplit("/", 1)[-1].split("?")[0]
    if url in bundles:
        return bundles[url].module(frame["lineNumber"])
    if url == "babylon.js":
        return "babylon"
    if not url:
        return "(" + (frame["functionName"] or "native").strip("()") + ")"
    return url


def component_of(module: str) -> str | None:
    """Return the component `module` belongs to, or None for a helper shared by all."""
    for pattern, name in _COMPILED:
        if pattern.search(module):
            return name
    return None


def _owner(stack: list[tuple[str, str]]) -> tuple[str, str]:
    """Return (component, module) for a stack of (module, function), root first."""
    for module, _function in reversed(stack):
        component = component_of(module)
        if component is not None:
            return component, module
    return _unowned(stack)


def _unowned(stack: list[tuple[str, str]]) -> tuple[str, str]:
    """Return (what, module) for a stack none of whose frames names a component."""
    leaf = stack[-1][0]
    what = "browser (native)"
    module = leaf
    drawing = {function for module, function in stack if module == "babylon"}
    phases = [phase for function, phase in RENDER_PHASES if function in drawing]
    game = [m for m, _function in stack if not m.startswith("(") and m not in {RUNTIME, "babylon"}]
    if leaf in {"(idle)", "(garbage collector)", "(program)"}:
        what = leaf
    elif leaf.startswith("(MutationObserver"):
        # `console.profile` called from the load probe's observer: the profiler starting.
        what = "(profiler start)"
    elif drawing:
        what = phases[0] if phases else "Babylon: engine (other)"
        module = "babylon"
    elif game:
        # Game code that names no component: the app's frame.
        what = "app frame & glue"
        module = game[-1]
    return what, module


class Shares:
    """Time (or bytes) by component, by module (self) and by module that answers for it."""

    def __init__(self) -> None:
        self.total = 0.0
        self.component: dict[str, float] = {}
        self.self_module: dict[str, float] = {}
        self.owner_module: dict[str, float] = {}
        self.function: dict[str, float] = {}

    def add(self, stack: list[tuple[str, str]], weight: float) -> None:
        """Count `weight` for the sample whose stack is `stack` (root first)."""
        if not stack or weight <= 0:
            return
        self.total += weight
        component, owner = _owner(stack)
        leaf_module, leaf_function = stack[-1]
        for table, key in (
            (self.component, component),
            (self.self_module, leaf_module),
            (self.owner_module, owner),
            (self.function, leaf_module + " " + leaf_function),
        ):
            table[key] = table.get(key, 0.0) + weight

    def summary(self, top: int = 40) -> dict[str, Any]:
        """Return the tables, largest first (the modules and functions cut to `top`)."""

        def ranked(table: dict[str, float], count: int) -> list[list[Any]]:
            items = sorted(table.items(), key=lambda item: -item[1])[:count]
            return [[key, value] for key, value in items]

        return {
            "total": self.total,
            "component": ranked(self.component, 100),
            "self_module": ranked(self.self_module, top),
            "owner_module": ranked(self.owner_module, top),
            "function": ranked(self.function, top),
        }


def cpu_shares(profile: dict[str, Any], bundles: dict[str, Bundle]) -> Shares:
    """Return the time of a CPU profile (`Profiler.stop`), in ms, by component and module."""
    nodes = {node["id"]: node for node in profile["nodes"]}
    parent: dict[int, int] = {}
    for node in profile["nodes"]:
        for child in node.get("children", []):
            parent[child] = node["id"]
    stacks: dict[int, list[tuple[str, str]]] = {}

    def stack_of(node_id: int) -> list[tuple[str, str]]:
        if node_id not in stacks:
            frame = nodes[node_id]["callFrame"]
            above = stack_of(parent[node_id]) if node_id in parent else []
            stacks[node_id] = [*above, (module_of(frame, bundles), frame["functionName"])]
        return stacks[node_id]

    shares = Shares()
    for sample, delta in zip(profile["samples"], profile["timeDeltas"], strict=False):
        # The root frame is not code: drop it.
        shares.add(stack_of(sample)[1:], delta / 1000)
    return shares


def allocation_shares(profile: dict[str, Any], bundles: dict[str, Bundle]) -> Shares:
    """Return the bytes of an allocation profile (`HeapProfiler.stopSampling`) the same way."""
    shares = Shares()

    def walk(node: dict[str, Any], above: list[tuple[str, str]]) -> None:
        frame = node["callFrame"]
        stack = [*above, (module_of(frame, bundles), frame["functionName"])]
        shares.add(stack[1:], node.get("selfSize", 0))
        for child in node.get("children", []):
            walk(child, stack)

    walk(profile["head"], [])
    return shares
