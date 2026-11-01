"""A boss's armour regions (docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md):
cut out of its core body, they burst off in chunks as it transforms and leave a dark metal frame
(BOSS-42, BOSS-43).

The cut is made on the core's drawing (`cut_armour`): its faces inside a region's outlines (and
heights) leave the core and make the region's armour. A region is then drawn three ways: whole
(at rest, flashing with the core), as chunks (shown only while they fly) and as its frame (hidden
until the burst). Which regions each boss sheds, and when, is its own boss file's (its shedding
and transformation requirements, specs/bosses/mini/*.md and specs/bosses/final/*.md).

Model space of a boss: logical pixels, +Y up (towards the camera), see `boss_limbs.boss_point`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.moving_regions import is_moving, motion_value
from game.config.record import concat
from game.view.bosses.boss_frame import UP, floor_height, floor_triangles, frame_drawings
from game.view.bosses.boss_reveal import HIDDEN, SHOWN, ease, reveal_phase
from game.view.bosses.boss_stems import surface_below
from game.view.bosses.region_motion import node_pose, posed, progress, relative_value
from game.view.enemies.enemy_mesh import EnemyParts, build_enemy_model
from render.babylon import new_transform_node, set_enabled
from render.edge_trim_mesh import clear_trim, set_trim_group
from render.geometry.islands import bounds_of, holding_surfaces, loose_triangles, pieces
from render.geometry.shatter import (
    Carve,
    Vertex,
    append_triangles,
    carve,
    centroid,
    chunk_cells,
    inside,
    straddles,
    subdivide,
    triangles,
    up_facing,
)
from render.geometry.solids import SolidBuilder

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

Vec3 = list[float]
__pragma__("noskip")

# The layers of a drawing that are cut (the solid and lit ones of `EnemyParts`).
LAYERS = ["hull", "flesh", "neon", "vein", "charge"]
# The layers the frame's top view is taken from.
SOLID = ["hull", "flesh"]


def model_outline(outline: list[Any]) -> list[list[float]]:
    """An outline in px from the boss's centre (X right, Y up) as XZ points in model space."""
    return [[-point[0], -point[1]] for point in outline]


def region_carve(region: Any) -> Carve:
    """Where `region` is cut, in model space."""
    return Carve([model_outline(o) for o in region.outlines], region.heights)


def _bounds_overlap(tri: list[Any], low: list[float], high: list[float]) -> bool:
    """Whether a triangle's XZ bounds overlap the box `low`..`high`."""
    xs = [tri[0].position[0], tri[1].position[0], tri[2].position[0]]
    zs = [tri[0].position[2], tri[1].position[2], tri[2].position[2]]
    return not (
        max(xs[0], xs[1], xs[2]) < low[0]
        or min(xs[0], xs[1], xs[2]) > high[0]
        or max(zs[0], zs[1], zs[2]) < low[1]
        or min(zs[0], zs[1], zs[2]) > high[1]
    )


def _region_box(carves: list[Carve]) -> list[list[float]]:
    low = [math.inf, math.inf]
    high = [-math.inf, -math.inf]
    for c in carves:
        for outline in c.outlines:
            for point in outline:
                low = [min(low[0], point[0]), min(low[1], point[1])]
                high = [max(high[0], point[0]), max(high[1], point[1])]
    return [low, high]


class Recorder:
    """A drawing's parts recorded: its layers' triangles and the calls that add nodes (wings,
    reactors, rotors and muzzles), to be played back on the core."""

    def __init__(self) -> None:
        self.builders: dict[str, Any] = {}
        for layer in LAYERS:
            self.builders[layer] = SolidBuilder()
        self.calls: list[list[Any]] = []

    def parts(self) -> EnemyParts:
        b = self.builders
        calls = self.calls

        def flap(pivot: Any, side: float, span: float, draw: Any) -> None:
            calls.append(["flap", pivot, side, span, draw])

        def reactor(at: Any, radius: float) -> None:
            calls.append(["reactor", at, radius])

        def rotor(at: Any, radius: float) -> None:
            calls.append(["rotor", at, radius])

        def muzzle(at: Any, kind: Any = None) -> None:
            calls.append(["muzzle", at, kind])

        return EnemyParts(
            b["hull"], b["flesh"], b["vein"], flap, b["neon"], b["charge"], reactor, rotor, muzzle
        )


def _play(p: Any, call: list[Any]) -> None:
    """Plays a recorded call back on the parts `p`."""
    kind = call[0]
    if kind == "flap":
        p.flap(call[1], call[2], call[3], call[4])
    elif kind == "reactor":
        p.reactor(call[1], call[2])
    elif kind == "rotor":
        p.rotor(call[1], call[2])
    else:
        p.muzzle(call[1], call[2])


class ArmourCut:
    """The core's drawing with its armour cut out: what the core keeps (`kept`, triangles by
    layer, and the recorded `calls`), each region's armour (`regions`, triangles by layer) and
    the solid faces of it its frame is laid under (`frames`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        kept: dict[str, Any],
        calls: list[Any],
        regions: list[Any],
        frames: list[Any],
        floors: list[float],
        bridges: list[Any],
        framed: list[bool] | None = None,
        floating: dict[str, Any] | None = None,
    ) -> None:
        self.kept = kept
        self.calls = calls
        self.regions = regions
        self.frames = frames
        # The height of each frame's floor: just over its whole armour's lowest point.
        self.floors = floors
        # Beams holding patches of each frame to the boss (`_held_frames`).
        self.bridges = bridges
        # Whether each region leaves a frame (a moving one may not, D-230).
        self.framed = framed if framed is not None else [True for _ in regions]
        # What of the core is loose at rest (held by a stem or a part standing on it), by layer:
        # drawn with the core, but nothing is held by it.
        self.floating = floating if floating is not None else {}

    def core_drawing(self) -> Any:
        """The drawing of the core without its armour."""
        kept = self.kept
        calls = self.calls
        floating = self.floating

        def draw(p: Any) -> None:
            for layer in LAYERS:
                append_triangles(getattr(p, layer).geometry, kept[layer])
                if layer in floating:
                    append_triangles(getattr(p, layer).geometry, floating[layer])
            for call in calls:
                _play(p, call)

        return draw


def _straddler(carves: list[Carve]) -> Any:
    """Whether a triangle may cross the edge of any of `carves` (and so must be cut down)."""

    def needs(tri: list[Any]) -> bool:
        for c in carves:  # noqa: SIM110 (ENG-157: any() over a generator is slow)
            if straddles(tri, c):
                return True
        return False

    return needs


def cut_armour(draw_core: Any, regions: list[Any]) -> ArmourCut:
    """Cuts the `regions` (in order: a face goes to the first that holds it) out of the core's
    drawing `draw_core`. Faces near the regions are first cut down to `BOSS_LOOK.armour.cut`."""
    recorder = Recorder()
    draw_core(recorder.parts())
    carves = [region_carve(r) for r in regions]
    box = _region_box(carves)
    kept: dict[str, Any] = {}
    cut: list[dict[str, Any]] = [{} for _ in regions]
    for layer in LAYERS:
        near: list[Any] = []
        far: list[Any] = []
        for tri in triangles(recorder.builders[layer].geometry):
            if _bounds_overlap(tri, box[0], box[1]):
                near.append(tri)
            else:
                far.append(tri)
        rest = subdivide(near, BOSS_LOOK.armour.cut, _straddler(carves))
        for k in range(len(carves)):
            split = carve(rest, carves[k])
            rest = split[0]
            cut[k][layer] = split[1]
        far.extend(rest)
        kept[layer] = far
    _settle_moving(kept, cut, regions)
    floating = _free_cut_off(kept, cut, carves, regions)
    frames = [concat(c["hull"], c["flesh"]) for c in cut]
    floors = [floor_height(f) for f in frames]
    bridges = _held_frames(kept, cut, frames, floors, regions)
    framed = [r.frame != None for r in regions]  # noqa: E711
    return ArmourCut(kept, recorder.calls, cut, frames, floors, bridges, framed, floating)


def _framed_state(
    kept: dict[str, Any],
    cut: list[dict[str, Any]],
    frames: list[Any],
    floors: list[float],
    regions: list[Any],
    form: int,
) -> list[Any]:
    """The boss after transformation `form`, `[triangles, sources]`: the core, the armour still
    on, and its frames' floors (the up-facing faces of `frames`, flat at `floors`), the last
    `len(sources)` triangles, each `[region, face]` it comes from."""
    tris: list[Any] = []
    for layer in LAYERS:
        tris.extend(kept[layer])
    for k in range(len(regions)):
        if regions[k].form > form or is_moving(regions[k]):
            # On still, or moved into its new pose (D-230).
            tris.extend(posed(concat(cut[k]["hull"], cut[k]["flesh"]), regions[k], form))
    sources: list[list[int]] = []
    for k in range(len(regions)):
        if regions[k].form > form or regions[k].frame == None:  # noqa: E711
            continue
        for i in range(len(frames[k])):
            tri = frames[k][i]
            if up_facing(tri, UP):
                tris.append(
                    [Vertex([v.position[0], floors[k], v.position[2]], v.color) for v in tri]
                )
                sources.append([k, i])
    return [tris, sources]


def _held_frames(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    kept: dict[str, Any],
    cut: list[dict[str, Any]],
    frames: list[Any],
    floors: list[float],
    regions: list[Any],
) -> list[list[Any]]:
    """The bridges each frame needs to hold to the boss (D-227): a patch of frame that would hang
    once its region is shed (it was held only through what went) gets a beam out to the nearest
    point of the boss, `[from, to]`, by region."""
    bridges: list[list[Any]] = [[] for _ in regions]
    for form in sorted_forms(regions):
        state = _framed_state(kept, cut, frames, floors, regions, form)
        tris = state[0]
        sources = state[1]
        loose = loose_triangles(tris, BOSS_LOOK.armour.hold)
        start = len(tris) - len(sources)
        hanging = [n for n in range(len(sources)) if loose[start + n]]
        if len(hanging) == 0:
            continue
        held: list[Any] = []
        for i in range(len(tris)):
            if not loose[i]:
                held.extend([v.position for v in tris[i]])
        for patch in pieces([tris[start + n] for n in hanging]):
            members = [tris[start + hanging[k]] for k in patch]
            region = sources[hanging[patch[0]]][0]
            bridges[region].append(_bridge(members, held))
    return bridges


def _bridge(patch: list[Any], held: list[Any]) -> list[Any]:
    """A beam from a hanging `patch` of floor to the nearest of the `held` points: `[from, to]`."""
    b = bounds_of(patch)
    cx = (b[0] + b[3]) / 2
    cz = (b[2] + b[5]) / 2
    target = held[0]
    best = math.inf
    for p in held:
        d = (p[0] - cx) * (p[0] - cx) + (p[2] - cz) * (p[2] - cz)
        if d < best:
            best = d
            target = p
    start = patch[0][0].position
    best = math.inf
    for tri in patch:
        for v in tri:
            p = v.position
            d = (p[0] - target[0]) * (p[0] - target[0]) + (p[2] - target[2]) * (p[2] - target[2])
            if d < best:
                best = d
                start = p
    return [start, target]


def _tagged(layers: dict[str, Any]) -> list[list[Any]]:
    """The triangles of `layers` (by layer), each `[layer, triangle]`."""
    result: list[list[Any]] = []
    for layer in LAYERS:
        for tri in layers[layer]:
            result.append([layer, tri])
    return result


def _split(
    tagged: list[list[Any]], keep: list[bool], into: dict[str, Any], out: dict[str, Any]
) -> None:
    """Puts each of `tagged` (`[layer, triangle]`) in `into` (by layer) where `keep` says so, else
    in `out`; `into` is emptied first."""
    for layer in LAYERS:
        into[layer] = []
    for i in range(len(tagged)):
        layer = tagged[i][0]
        if keep[i]:
            into[layer].append(tagged[i][1])
        else:
            out[layer].append(tagged[i][1])


def _settle_moving(kept: dict[str, Any], cut: list[dict[str, Any]], regions: list[Any]) -> None:
    """A moving region's piece is one body (D-230): what the cut gave it apart from its biggest
    body holding together (a light hanging over it, held by a stem on the core) stays with the
    core."""
    for k in range(len(regions)):
        if not is_moving(regions[k]):
            continue
        tagged = _tagged(cut[k])
        tris = [t[1] for t in tagged]
        groups = pieces(tris)
        held = holding_surfaces(tris, groups, BOSS_LOOK.armour.hold)
        sizes = [0 for _ in groups]
        for g in range(len(groups)):
            sizes[held[g]] += len(groups[g])
        main = 0
        for h in range(len(sizes)):
            if sizes[h] > sizes[main]:
                main = h
        keep = [False for _ in tagged]
        for g in range(len(groups)):
            if held[g] == main:
                for i in groups[g]:
                    keep[i] = True
        _split(tagged, keep, cut[k], kept)


def _free_cut_off(
    kept: dict[str, Any], cut: list[dict[str, Any]], carves: list[Carve], regions: list[Any]
) -> dict[str, list[Any]]:
    """Pieces of the core the cut leaves hanging go with a region (D-227: a boss stays one object).
    After each transformation, what is still on (the core, the armour not yet shed) and the floors
    of the frames shed must hold together: a piece of the core that no longer does goes with the
    region it stands in, else with the region that held it up. A piece already loose at rest (held
    by a part standing on it, or by a stem) stays off `kept`: returned by layer, its stem holds it
    whatever is shed."""
    floating = _floating_at_rest(kept, cut, regions)
    for form in sorted_forms(regions):
        _free_after(kept, cut, carves, regions, form)
    return floating


def _floating_at_rest(
    kept: dict[str, Any], cut: list[dict[str, Any]], regions: list[Any]
) -> dict[str, list[Any]]:
    """Takes out of `kept` (by layer) the pieces of the core loose at rest, with all its armour on,
    and returns them."""
    tagged = _tagged(kept)
    tris = [t[1] for t in tagged]
    count = len(tris)
    for k in range(len(regions)):
        for layer in LAYERS:
            tris.extend(posed(cut[k][layer], regions[k], 0))
    loose = loose_triangles(tris, BOSS_LOOK.armour.hold)
    floating: dict[str, list[Any]] = {}
    for layer in LAYERS:
        floating[layer] = []
    _split(tagged, [not loose[i] for i in range(count)], kept, floating)
    return floating


def _free_after(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    kept: dict[str, Any],
    cut: list[dict[str, Any]],
    carves: list[Carve],
    regions: list[Any],
    form: int,
) -> None:
    """`_free_cut_off` after transformation `form`."""
    tagged = _tagged(kept)
    tris = [t[1] for t in tagged]
    count = len(tris)
    tris.extend(_regions_after(cut, regions, form))
    loose = loose_triangles(tris, BOSS_LOOK.armour.hold)
    hanging = [i for i in range(count) if loose[i]]
    if len(hanging) == 0:
        return
    moved = [False for _ in range(count)]
    for piece in pieces([tris[i] for i in hanging]):
        members = [hanging[k] for k in piece]
        k = _owner(tris, members, carves, regions, form)
        if k < 0:
            continue
        for i in members:
            cut[k][tagged[i][0]].append(tris[i])
            moved[i] = True
    for layer in LAYERS:
        kept[layer] = [tagged[i][1] for i in range(count) if tagged[i][0] == layer and not moved[i]]


def _regions_after(cut: list[dict[str, Any]], regions: list[Any], form: int) -> list[Any]:
    """What the regions make of the boss after transformation `form`: the armour still on and the
    pieces moved into their new pose (D-230), and the floors of the frames shed."""
    tris: list[Any] = []
    for k in range(len(regions)):
        if regions[k].form > form or is_moving(regions[k]):
            for layer in LAYERS:
                tris.extend(posed(cut[k][layer], regions[k], form))
        solid = concat(cut[k]["hull"], cut[k]["flesh"])
        if regions[k].form <= form and regions[k].frame != None and len(solid) > 0:  # noqa: E711
            tris.extend(floor_triangles(solid, floor_height(solid)))
    return tris


def sorted_forms(regions: list[Any]) -> list[int]:
    """The transformations that shed `regions`, in order, each once."""
    result: list[int] = []
    for region in regions:
        if region.form not in result:
            result.append(region.form)
    return sorted(result)


def _owner(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    tris: list[Any], members: list[int], carves: list[Carve], regions: list[Any], form: int
) -> int:
    """The region a hanging piece (`members` of `tris`) goes with: the one shed by `form` or
    before (or moved by `form`: a piece moved before cannot take it now) that it stands in, else
    the nearest one `form` sheds or moves (the one that held it up)."""
    b = bounds_of([tris[i] for i in members])
    x = (b[0] + b[3]) / 2
    z = (b[2] + b[5]) / 2
    for k in range(len(carves)):
        if regions[k].form > form or (is_moving(regions[k]) and regions[k].form < form):
            continue
        if any(inside(o, x, z) for o in carves[k].outlines):
            return k
    best = -1
    near = math.inf
    for k in range(len(regions)):
        if regions[k].form != form:
            continue
        for outline in carves[k].outlines:
            d = _distance_to(outline, x, z)
            if d < near:
                near = d
                best = k
    return best


def _distance_to(outline: list[list[float]], x: float, z: float) -> float:
    """How far `(x, z)` is from the edge of `outline` (XZ, model space)."""
    best = math.inf
    n = len(outline)
    for i in range(n):
        a = outline[i]
        b = outline[(i + 1) % n]
        dx = b[0] - a[0]
        dz = b[1] - a[1]
        length = dx * dx + dz * dz
        t = 0.0 if length == 0 else max(0, min(1, ((x - a[0]) * dx + (z - a[1]) * dz) / length))
        px = a[0] + t * dx - x
        pz = a[1] + t * dz - z
        best = min(best, math.hypot(px, pz))
    return best


class ArmourChunk:
    """A chunk of armour: its node (at its `centre` at rest), its index among its region's."""

    def __init__(self, node: Any, centre: Vec3, index: int) -> None:
        self.node = node
        self.centre = centre
        self.index = index


def chunk_pose(centre: Vec3, index: int, u: float) -> list[Any]:
    """Where a chunk resting at `centre` is `u` of the way through its flight: `[position, turn
    about X, turn about Z, scale]`. Thrown out from the boss's centre (each chunk a little off to
    one side), up and falling back, tumbling and shrinking away."""
    look = BOSS_LOOK.reveal
    jitter = ((index * 0.618) % 1) - 0.5
    horizontal = math.hypot(centre[0], centre[2])
    a = math.atan2(centre[0], centre[2]) if horizontal > 0 else index * 2.4
    a += jitter * 0.9
    out = u * look.throw * (1 + jitter * 0.5)
    up = 4 * u * (1 - u) * look.lift - u * u * look.fall
    turn = u * look.spin * (1 + jitter)
    position = [centre[0] + math.sin(a) * out, centre[1] + up, centre[2] + math.cos(a) * out]
    return [position, turn, -turn * 0.7, max(0, 1 - u * u)]


def _layers_drawing(layers: dict[str, Any], tris_of: Any, shift: Vec3 | None) -> Any:
    """A drawing that adds `tris_of(layers[layer])` to each layer, moved by `shift`."""

    def draw(p: Any) -> None:
        for layer in LAYERS:
            append_triangles(getattr(p, layer).geometry, tris_of(layers[layer]), shift)

    return draw


def _all(tris: list[Any]) -> list[Any]:
    return tris


def chunk_layers(layers: dict[str, Any], most: int) -> list[Any]:
    """The region's armour (`layers`, triangles by layer) broken into at most `most` chunks on an
    XZ grid a third of its size: a list of `[layers, centre]`."""
    tagged: list[list[Any]] = []
    for layer in LAYERS:
        for tri in layers[layer]:
            tagged.append([layer, tri, centroid(tri)])
    if len(tagged) == 0:
        return []
    low = [math.inf, math.inf]
    high = [-math.inf, -math.inf]
    for t in tagged:
        c = t[2]
        low = [min(low[0], c[0]), min(low[1], c[2])]
        high = [max(high[0], c[0]), max(high[1], c[2])]
    cell = max(4, max(high[0] - low[0], high[1] - low[1]) / 3)
    ids = chunk_cells([t[2] for t in tagged], cell, most)
    count = 0
    for i in ids:
        count = max(count, i + 1)
    result: list[Any] = []
    for _ in range(count):
        empty: dict[str, Any] = {}
        for layer in LAYERS:
            empty[layer] = []
        result.append([empty, [0.0, 0.0, 0.0], 0])
    for k in range(len(tagged)):
        entry = result[ids[k]]
        entry[0][tagged[k][0]].append(tagged[k][1])
        c = tagged[k][2]
        entry[1] = [entry[1][0] + c[0], entry[1][1] + c[1], entry[1][2] + c[2]]
        entry[2] += 1
    return [[e[0], [e[1][0] / e[2], e[1][1] / e[2], e[1][2] / e[2]]] for e in result]


class ArmourView:
    """One armour region of a boss model: `whole` (a model, with its flash group `flash`), its
    `chunks` and its `frame` (a model)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self, region: Any, whole: Any, flash: Any, chunks: list[ArmourChunk], frame: Any
    ) -> None:
        self.region = region
        self.whole = whole
        self.flash = flash
        self.chunks = chunks
        self.frame = frame

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Shows the region for `boss` (None: at rest) as its transformation goes."""
        if boss == None:  # noqa: E711
            self._rest(lit, dt, 1000)
            return
        phase = reveal_phase(self.region.form, boss.form, boss.transforming_into)
        if phase == HIDDEN:
            self._rest(lit, dt, boss.core.since_hit)
            return
        if phase == SHOWN:
            self._shed(lit, dt, 1)
            return
        look = BOSS_LOOK.reveal
        t = boss.transform
        if t < look.burst:
            # It strains: shudders and strobes.
            self._rest(lit, dt, 0 if math.floor(t * look.strobeHz * 4) % 2 == 0 else 1000)
            k = t / look.burst
            jolt = math.sin(t * 90) * look.shudder * k
            self.whole.root.position.set(jolt, 0, -jolt * 0.6)
            return
        self._shed(lit, dt, (t - look.burst) / (look.burstEnd - look.burst))

    def _rest(self, lit: Any, dt: float, since_hit: float) -> None:
        set_enabled(self.whole.root, True)
        self.whole.root.position.set(0, 0, 0)
        set_enabled(self.frame.root, False)
        for chunk in self.chunks:
            set_enabled(chunk.node, False)
        self.whole.sync(lit, dt)
        self.flash.show(since_hit)

    def _shed(self, lit: Any, dt: float, u: float) -> None:
        set_enabled(self.whole.root, False)
        set_enabled(self.frame.root, True)
        self.frame.sync(lit, dt)
        flying = u < 1
        for chunk in self.chunks:
            set_enabled(chunk.node, flying)
            if not flying:
                continue
            pose = chunk_pose(chunk.centre, chunk.index, ease(u) * 0.3 + u * 0.7)
            node = chunk.node
            node.position.set(pose[0][0], pose[0][1], pose[0][2])
            node.rotation.x = pose[1]
            node.rotation.z = pose[2]
            node.scaling.set(pose[3], pose[3], pose[3])


def place(node: Any, pose: list[Any]) -> None:
    """Puts `node` at `pose`, `[position, rotation]` (see `region_motion.node_pose`)."""
    p = pose[0]
    r = pose[1]
    node.position.set(p[0], p[1], p[2])
    node.rotation.set(r[0], r[1], r[2])


class MovingView:
    """A moving region of a boss model (BOSS-45, D-230): its piece, `whole` (a model on its `mover`
    node, with its flash group `flash`), moved by its motion as the boss transforms; the `carrier`
    node the weapons riding it hang from (drawn where they end up); and its `frame` (a model), if it
    leaves one where it was drawn."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self, region: Any, whole: Any, flash: Any, mover: Any, carrier: Any, frame: Any
    ) -> None:
        self.region = region
        self.whole = whole
        self.flash = flash
        self.mover = mover
        self.carrier = carrier
        self.frame = frame

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Poses the piece for `boss` (None: at rest) as its transformation goes: it strains as
        armour does, then moves into its new pose."""
        motion = self.region.motion
        k = progress(self.region, boss)
        value = motion_value(motion, k)
        place(self.mover, node_pose(motion, value))
        place(self.carrier, node_pose(motion, relative_value(motion, value)))
        since_hit = 1000 if boss == None else boss.core.since_hit  # noqa: E711
        look = BOSS_LOOK.reveal
        straining = (
            boss != None  # noqa: E711
            and boss.transforming_into == self.region.form
            and boss.transform < look.burst
        )
        if straining:
            t = boss.transform
            since_hit = 0 if math.floor(t * look.strobeHz * 4) % 2 == 0 else 1000
            jolt = math.sin(t * 90) * look.shudder * (t / look.burst)
            self.whole.root.position.set(jolt, 0, -jolt * 0.6)
        else:
            self.whole.root.position.set(0, 0, 0)
        self.whole.sync(lit, dt)
        self.flash.show(since_hit)
        if self.frame != None:  # noqa: E711
            out = boss != None and (k > 0 or boss.form >= self.region.form)  # noqa: E711
            set_enabled(self.frame.root, out)
            if out:
                self.frame.sync(lit, dt)


class FrameView:
    """A region's frame: its `root` node, its floor and ribs models."""

    def __init__(self, root: Any, models: list[Any]) -> None:
        self.root = root
        self.models = models

    def sync(self, lit: Any, dt: float) -> None:
        for model in self.models:
            model.sync(lit, dt)


def _build_frame(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    name: str, scene: Any, neon: Any, breath: Any, drawings: list[Any]
) -> FrameView:
    """The frame of a region from its `[floor, ribs]` drawings: built under the armour, the floor
    is trimmed along its own outline (GFX-TRIM-09); the ribs are not, so it reads as dark metal."""
    root = new_transform_node(name + "-frame", scene)
    floor = build_enemy_model(name + "-frame-floor", scene, neon, drawings[0], breath)
    floor.root.parent = root
    set_trim_group(floor.root)
    ribs = build_enemy_model(name + "-frame-ribs", scene, neon, drawings[1], breath)
    ribs.root.parent = root
    clear_trim(ribs.root)
    return FrameView(root, [floor, ribs])


def lasting_surfaces(cut: ArmourCut) -> list[Any]:
    """What a boss keeps through all its transformations: its core and its frames' floors."""
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(cut.kept[layer])
    for k in range(len(cut.frames)):
        if not cut.framed[k]:
            continue
        for tri in cut.frames[k]:
            if up_facing(tri, UP):
                y = cut.floors[k]
                result.append([Vertex([v.position[0], y, v.position[2]], v.color) for v in tri])
    return result


def rooted(supports: list[Any], lasting: list[Any]) -> list[Any]:
    """`supports` with the height each stands on: the highest lasting surface under it."""
    result: list[Any] = []
    for s in supports:
        base = surface_below(lasting, s[0], s[1], s[2])
        result.append(s if base == None else [s[0], s[1], s[2], s[3], base])  # noqa: E711
    return result


def supports_in(region: Any, supports: list[Any]) -> list[Any]:
    """The `supports` (`[x, z, bottom, width]`, model space) standing over `region`, even in part:
    their centre, or a point most of their width out from it, is in it."""
    outlines = region_carve(region).outlines
    result: list[Any] = []
    for s in supports:
        r = s[3] * 0.7
        points = [[0, 0], [r, 0], [-r, 0], [0, r], [0, -r]]
        if any(inside(o, s[0] + d[0], s[1] + d[1]) for o in outlines for d in points):
            result.append(s)
    return result


def _moving_view(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    region: Any,
    cut: ArmourCut,
    k: int,
    whole: Any,
    flash_of: Any,
    standing: list[Any],
    carriers: Any,
    look: list[Any],
) -> MovingView:
    """The view of the moving region `region` (the `k`-th cut by `cut`), its piece `whole`: on its
    own mover node, with its carrier (from `carriers`, else a new one) and its frame if it leaves
    one. `look` is `[neon, breath, name]`."""
    neon = look[0]
    breath = look[1]
    name = look[2]
    root = whole.root.parent
    scene = root.getScene()
    mover = new_transform_node(name + "-mover", scene)
    mover.parent = root
    whole.root.parent = mover
    carrier = carriers[region.id] if carriers != None and region.id in carriers else None  # noqa: E711
    if carrier == None:  # noqa: E711
        carrier = new_transform_node(name + "-carrier", scene)
        carrier.parent = root
    frame = None
    if region.frame != None:  # noqa: E711
        held = supports_in(region, standing)
        drawings = frame_drawings(
            cut.frames[k], region.frame, neon, held, cut.floors[k], cut.bridges[k]
        )
        frame = _build_frame(name, scene, neon, breath, drawings)
        frame.root.parent = root
        set_enabled(frame.root, False)
    return MovingView(region, whole, flash_of(whole), mover, carrier, frame)


def build_armour(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    design: Any,
    cut: ArmourCut,
    root: Any,
    neon: Any,
    breath: Any,
    flash_of: Any,
    supports: list[Any] | None = None,
    carriers: Any = None,
) -> list[Any]:
    """The views of `design`'s armour regions, cut by `cut`, on `root`. `flash_of(model)` makes
    the flash group of a model; `supports` are the pieces standing on the boss (see
    `draw_pylon`), held up by the frame of the region under them; `carriers` the nodes (by region
    id) the weapons riding a moving region hang from (see `MovingView`)."""
    standing = rooted(supports if supports is not None else [], lasting_surfaces(cut))
    regions = design.armour
    scene = root.getScene()
    most = min(BOSS_LOOK.armour.chunks, math.floor(BOSS_LOOK.armour.bossChunks / len(regions)))
    result: list[Any] = []
    for k in range(len(regions)):
        region = regions[k]
        layers = cut.regions[k]
        name = design.id + "-armour-" + region.id
        whole = build_enemy_model(name, scene, neon, _layers_drawing(layers, _all, None), breath)
        whole.root.parent = root
        if is_moving(region):
            look = [neon, breath, name]
            result.append(_moving_view(region, cut, k, whole, flash_of, standing, carriers, look))
            continue
        chunks: list[ArmourChunk] = []
        pieces = chunk_layers(layers, most)
        for i in range(len(pieces)):
            centre = pieces[i][1]
            node = new_transform_node(name + "-chunk-" + str(i), scene)
            node.position.set(centre[0], centre[1], centre[2])
            node.parent = root
            shift = [-centre[0], -centre[1], -centre[2]]
            model = build_enemy_model(
                name + "-chunk-" + str(i),
                scene,
                neon,
                _layers_drawing(pieces[i][0], _all, shift),
                breath,
            )
            model.root.parent = node
            # Flying off, it must not trim the frame's edges (GFX-TRIM-09).
            clear_trim(model.root)
            set_enabled(node, False)
            chunks.append(ArmourChunk(node, centre, i))
        held = supports_in(region, standing)
        drawings = frame_drawings(
            cut.frames[k], region.frame, neon, held, cut.floors[k], cut.bridges[k]
        )
        frame = _build_frame(name, scene, neon, breath, drawings)
        frame.root.parent = root
        set_enabled(frame.root, False)
        result.append(ArmourView(region, whole, flash_of(whole), chunks, frame))
    return result
