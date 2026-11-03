# Copyright (c) 2026 Renaud Guillon
"""A boss's armour regions (BOSS-42, BOSS-43, D-254): drawn as pieces of their own.

Each region of a boss's design has a drawing in its model (`drawing.armour[region.id]`): its
`whole` armour as it rests on the core, and, if the boss draws them, the `pieces` it bursts into
and the `frame` it leaves. Left out, the pieces are plates cracked from the region's outline
(`render/geometry/plates.py`) in the armour's own colour, and the frame is drawn from the outline
(`boss_frame.py`). A region is then shown three ways: whole (at rest, flashing with the core), as
its pieces (only while they fly) and as its frame (from the burst on). A moving region's piece
(BOSS-45) stays on, posed by its motion. Nothing is cut out of the core: the boss draws its core
without the armour.

Model space of a boss: logical pixels, +Y up (towards the camera), see `boss_limbs.boss_point`.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.moving_regions import is_moving, motion_value
from game.config.record import field
from game.view.bosses.boss_frame import frame_drawings
from game.view.bosses.boss_reveal import HIDDEN, SHOWN, ease, reveal_phase
from game.view.bosses.region_motion import node_pose, progress, relative_value
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node, set_enabled
from render.edge_trim_mesh import clear_trim, set_trim_group
from render.geometry.mesh_triangles import bounds_of, mean_color, triangles
from render.geometry.plates import crack
from render.geometry.solids import shaded

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

Vec3 = list[float]
# __pragma__ ("noskip")


# The layers of a drawing that make its body (the solid and lit ones of `EnemyParts`).
LAYERS = ["hull", "flesh", "neon", "vein", "charge"]
# The colour of a piece whose armour has no colour of its own.
GREY = [0.3, 0.3, 0.33]
# The share of an armour's surface under the height its plates are drawn at (`armour_top`).
TOP_SHARE = 0.9


def model_outline(outline: list[Any]) -> list[list[float]]:
    """Return an outline as XZ points in model space.

    The outline is in px from the boss's centre (X right, Y up).
    """
    return [[-point[0], -point[1]] for point in outline]


def model_outlines(region: Any) -> list[list[list[float]]]:
    """Return the outlines of `region` in model space."""
    return [model_outline(o) for o in region.outlines]


def drawn_layers(draw: Any) -> dict[str, Any]:
    """Return the triangles the drawing `draw` makes, by layer (`LAYERS`)."""
    parts = collect_parts(draw)["parts"]
    result: dict[str, Any] = {}
    for layer in LAYERS:
        result[layer] = triangles(getattr(parts, layer).geometry)
    return result


def all_triangles(layers: dict[str, Any]) -> list[Any]:
    """Return the triangles of every layer of `layers`, in one list."""
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(layers[layer])
    return result


def _centre(tris: list[Any]) -> Vec3:
    """Return the middle of the bounds of `tris` (the origin when there are none)."""
    b = bounds_of(tris)
    if b[0] == math.inf:
        return [0, 0, 0]
    return [(b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2]


def _body_color(layers: dict[str, Any]) -> list[float]:
    """Return the colour of the armour drawn as `layers`: its hull's, else its flesh's.

    Else its lights'.
    """
    for layer in ["hull", "flesh"]:
        if len(layers[layer]) > 0:
            return mean_color(layers[layer], GREY)
    return mean_color(all_triangles(layers), GREY)


class RegionDrawing:
    """How a region is drawn: its `whole` armour, its `pieces` (each `[draw, centre]`), its frame.

    The frame is a list of drawings (the first one trimmed), or None when it leaves none.
    """

    def __init__(self, whole: Any, pieces: list[Any], frame: Any) -> None:
        self.whole = whole
        self.pieces = pieces
        self.frame = frame


def _plate_drawing(plate: list[Any], heights: list[float], color: list[float]) -> Any:
    def draw(p: Any) -> None:
        p.hull.slab(plate, heights, shaded(color, 0.75), None, color)

    return draw


def plate_pieces(
    outlines: list[Any], heights: list[float], color: list[float], most: int
) -> list[Any]:
    """Return at most `most` plates cracked from `outlines` (XZ, model space).

    Each is `[draw, centre]`: a slab between `heights` in `color`, its underside darker; the plates
    of an outline are about a third of it across.
    """
    result: list[Any] = []
    per = max(1, math.floor(most / len(outlines)))
    y = (heights[0] + heights[1]) / 2
    for outline in outlines:
        low = [math.inf, math.inf]
        high = [-math.inf, -math.inf]
        for point in outline:
            low = [min(low[0], point[0]), min(low[1], point[1])]
            high = [max(high[0], point[0]), max(high[1], point[1])]
        cell = max(4, max(high[0] - low[0], high[1] - low[1]) / 3)
        for plate in crack(outline, cell, per):
            cx = 0.0
            cz = 0.0
            for point in plate:
                cx += point[0]
                cz += point[1]
            n = len(plate)
            result.append([_plate_drawing(plate, heights, color), [cx / n, y, cz / n]])
    return result


def _area(tri: list[Any]) -> float:
    a = tri[0].position
    b = tri[1].position
    c = tri[2].position
    u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
    v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    return math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]) / 2


def armour_top(tris: list[Any]) -> float:
    """Return the height of the top of armour drawn as `tris`.

    The height `TOP_SHARE` of its surface lies under, so a mast or a light standing on it does not
    count: each triangle counts at the height of its highest corner.
    """
    area_at: dict[str, float] = {}
    heights: list[float] = []
    total = 0.0
    for tri in tris:
        y = max(tri[0].position[1], tri[1].position[1], tri[2].position[1])
        k = str(round(y * 100))
        if k not in area_at:
            area_at[k] = 0
            heights.append(y)
        area = _area(tri)
        area_at[k] += area
        total += area
    heights.sort()
    reached = 0.0
    for i in range(len(heights) - 1):
        y = heights[i]
        reached += area_at[str(round(y * 100))]
        if reached >= TOP_SHARE * total:
            return y
    return heights[len(heights) - 1]


def default_pieces(region: Any, layers: dict[str, Any], most: int) -> list[Any]:
    """Return the pieces a region bursts into when its boss draws none (BOSS-43).

    Plates cracked from its outlines, `armour.plate` thick at the top of its armour, in the armour's
    colour; none when the armour draws nothing.
    """
    tris = all_triangles(layers)
    b = bounds_of(tris)
    if b[0] == math.inf:
        return []
    top = armour_top(tris)
    bottom = max(b[1], top - BOSS_LOOK.armour.plate)
    return plate_pieces(model_outlines(region), [bottom, top], _body_color(layers), most)


def default_frame(region: Any, layers: dict[str, Any], neon: Any) -> Any:
    """Return the frame drawings a region leaves when its boss draws none (BOSS-44).

    Drawn from its outlines just over its armour's lowest point; None when it leaves no frame.
    """
    if region.frame == None:
        return None
    b = bounds_of(all_triangles(layers))
    low = b[1] if b[1] < math.inf else 0
    return frame_drawings(model_outlines(region), region.frame, neon, low + BOSS_LOOK.frame.lift)


def region_drawing(armour: Any, region: Any, neon: Any, most: int) -> Any:
    """Return how `region` is drawn (a `RegionDrawing`), from the model's `armour` drawings.

    None when the model draws no armour for it. A region drawn without its `whole` is an error.
    `most` caps the plates a region cracks into.
    """
    entry = field(armour, region.id, None) if armour != None else None
    if entry == None:
        return None
    whole = field(entry, "whole", None)
    if whole == None:
        raise ValueError('The armour region "' + region.id + '" has no whole drawing')
    layers = drawn_layers(whole)
    given = field(entry, "pieces", None)
    if given != None:
        pieces = [[draw, _centre(all_triangles(drawn_layers(draw)))] for draw in given]
    else:
        pieces = default_pieces(region, layers, most)
    frame = field(entry, "frame", None)
    return RegionDrawing(
        whole, pieces, [frame] if frame != None else default_frame(region, layers, neon)
    )


def most_pieces(regions: list[Any]) -> int:
    """How many plates a region may crack into: `armour.chunks`, within `armour.bossChunks`."""
    most: int = min(BOSS_LOOK.armour.chunks, math.floor(BOSS_LOOK.armour.bossChunks / len(regions)))
    return most


class ArmourChunk:
    """A piece of armour: its node (at its `centre` at rest), its index among its region's."""

    def __init__(self, node: Any, centre: Vec3, index: int) -> None:
        self.node = node
        self.centre = centre
        self.index = index


def chunk_pose(centre: Vec3, index: int, u: float) -> list[Any]:
    """Where a piece resting at `centre` is `u` of the way through its flight.

    `[position, turn about X, turn about Z, scale]`. Thrown out from the boss's centre (each piece a
    little off to one side), up and falling back, tumbling and shrinking away.
    """
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


class ArmourView:
    """One armour region of a boss model that bursts off.

    `whole` (a model, with its flash group `flash`), its `chunks` (its pieces) and its `frame` (a
    `FrameView`).
    """

    def __init__(
        self, region: Any, whole: Any, flash: Any, chunks: list[ArmourChunk], frame: Any
    ) -> None:
        self.region = region
        self.whole = whole
        self.flash = flash
        self.chunks = chunks
        self.frame = frame

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Show the region for `boss` (None: at rest) as its transformation goes."""
        if boss == None:
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
    """Put `node` at `pose`, `[position, rotation]` (see `region_motion.node_pose`)."""
    p = pose[0]
    r = pose[1]
    node.position.set(p[0], p[1], p[2])
    node.rotation.set(r[0], r[1], r[2])


class MovingView:
    """A moving region of a boss model (BOSS-45, D-230): its piece.

    `whole` (a model on its `mover` node, with its flash group `flash`), moved by its motion as the
    boss transforms; the `carrier` node the weapons riding it hang from (drawn where they end up);
    and its `frame` (a `FrameView`), if it leaves one where it was drawn.
    """

    def __init__(
        self, region: Any, whole: Any, flash: Any, mover: Any, carrier: Any, frame: Any
    ) -> None:
        self.region = region
        self.whole = whole
        self.flash = flash
        self.mover = mover
        self.carrier = carrier
        self.frame = frame

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Poses the piece for `boss` (None: at rest) as its transformation goes.

        It strains as armour does, then moves into its new pose.
        """
        motion = self.region.motion
        k = progress(self.region, boss)
        value = motion_value(motion, k)
        place(self.mover, node_pose(motion, value))
        place(self.carrier, node_pose(motion, relative_value(motion, value)))
        since_hit = 1000 if boss == None else boss.core.since_hit
        look = BOSS_LOOK.reveal
        straining = (
            boss != None
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
        if self.frame != None:
            out = boss != None and (k > 0 or boss.form >= self.region.form)
            set_enabled(self.frame.root, out)
            if out:
                self.frame.sync(lit, dt)


class FrameView:
    """A region's frame: its `root` node, and its models (its floor and ribs)."""

    def __init__(self, root: Any, models: list[Any]) -> None:
        self.root = root
        self.models = models

    def sync(self, lit: Any, dt: float) -> None:
        """Sync every model with `lit` and `dt`."""
        for model in self.models:
            model.sync(lit, dt)


def _build_frame(name: str, scene: Any, look: list[Any], drawings: list[Any]) -> FrameView:
    """Return the frame of a region from its `drawings`, built hidden on a root of its own.

    `look` is `[neon, breath]`. The first drawing (the floor) is trimmed along its own outline
    (GFX-TRIM-09); the others (the ribs) are not, so the frame reads as dark metal.
    """
    root = new_transform_node(name + "-frame", scene)
    models: list[Any] = []
    for i in range(len(drawings)):
        part = "floor" if i == 0 else "ribs"
        model = build_enemy_model(name + "-frame-" + part, scene, look[0], drawings[i], look[1])
        model.root.parent = root
        if i == 0:
            set_trim_group(model.root)
        else:
            clear_trim(model.root)
        models.append(model)
    set_enabled(root, False)
    return FrameView(root, models)


def _build_pieces(name: str, root: Any, look: list[Any], pieces: list[Any]) -> list[ArmourChunk]:
    """Return the chunks of a region from its `pieces` (`[draw, centre]` each), hidden on `root`.

    Each piece's node sits at its centre, so it flies out from there; its drawing, in model space,
    is drawn back round the node. `look` is `[neon, breath]`.
    """
    scene = root.getScene()
    result: list[ArmourChunk] = []
    for i in range(len(pieces)):
        centre = pieces[i][1]
        node = new_transform_node(name + "-chunk-" + str(i), scene)
        node.position.set(centre[0], centre[1], centre[2])
        node.parent = root
        model = build_enemy_model(name + "-chunk-" + str(i), scene, look[0], pieces[i][0], look[1])
        model.root.parent = node
        model.root.position.set(-centre[0], -centre[1], -centre[2])
        # Flying off, it must not trim the frame's edges (GFX-TRIM-09).
        clear_trim(model.root)
        set_enabled(node, False)
        result.append(ArmourChunk(node, centre, i))
    return result


def _moving_view(
    region: Any, whole: Any, flash_of: Any, carriers: Any, frame: Any, name: str
) -> MovingView:
    """Return the view of the moving region `region`, its piece `whole`.

    On its own mover node, with its carrier (from `carriers`, else a new one) and its `frame`.
    """
    root = whole.root.parent
    scene = root.getScene()
    mover = new_transform_node(name + "-mover", scene)
    mover.parent = root
    whole.root.parent = mover
    carrier = carriers[region.id] if carriers != None and region.id in carriers else None
    if carrier == None:
        carrier = new_transform_node(name + "-carrier", scene)
        carrier.parent = root
    return MovingView(region, whole, flash_of(whole), mover, carrier, frame)


def build_armour(
    design: Any,
    drawing: Any,
    root: Any,
    neon: Any,
    breath: Any,
    flash_of: Any,
    carriers: Any = None,
) -> list[Any]:
    """Return the views of `design`'s armour regions drawn by `drawing.armour`, on `root`.

    A region the model draws no armour for has no view. `flash_of(model)` makes the flash group of
    a model; `carriers` are the nodes (by region id) the weapons riding a moving region hang from
    (see `MovingView`).
    """
    regions = design.armour
    armour = field(drawing, "armour", None)
    scene = root.getScene()
    most = most_pieces(regions)
    look = [neon, breath]
    result: list[Any] = []
    for region in regions:
        drawn = region_drawing(armour, region, neon, most)
        if drawn == None:
            continue
        name = design.id + "-armour-" + region.id
        whole = build_enemy_model(name, scene, neon, drawn.whole, breath)
        whole.root.parent = root
        frame = None
        if drawn.frame != None:
            frame = _build_frame(name, scene, look, drawn.frame)
            frame.root.parent = root
        if is_moving(region):
            result.append(_moving_view(region, whole, flash_of, carriers, frame, name))
            continue
        chunks = _build_pieces(name, root, look, drawn.pieces)
        result.append(ArmourView(region, whole, flash_of(whole), chunks, frame))
    return result
