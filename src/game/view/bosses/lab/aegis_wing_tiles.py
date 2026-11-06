# Copyright (c) 2026 Renaud Guillon
"""MB-AEGIS-WING-05, MB-AEGIS-WING-10: the Aegis Wing's skin panels and their view rig.

Logical pixels, nose +Z, Y up. On each outer wing, rows of smooth skin panels run along the chord
(`aegis_wing.row_x`, `row_span`), lying on the wing's top: at rest they are an armour region of
its own (`skin`, drawn whole here), its stealth skin. As it transforms the region hands over to
this rig, which flips the rows over about their axes, one row after another in a wave running in
from the wingtip and from the root, each turning up its weapon face (dark plates, a lit cell and a
vane on each). The three middle rows run through the orb's well: there the panels do not flip but
fold open like petals, the side ones about their outer edges, the middle ones fore and aft, and the
orb (a hidden weapon, drawn by the engine) rises out between them. Visual only: the sim knows
nothing of the panels.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.aegis_wing import (
    ORB_AT,
    ROW_COUNT,
    ROW_HALF,
    TILE,
    TILE_GAP,
    TILE_THICK,
    WELL,
    WING_TOP,
    in_well,
    row_span,
    row_x,
    tile_field,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.world_1_organic_kit import F, M
from game.view.enemies.enemy_mesh import build_enemy_model, collect_parts
from render.babylon import new_transform_node, set_enabled
from render.geometry.mesh_triangles import Vertex, triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["aegis-wing"]
LAYERS = ["hull", "flesh", "bare", "neon", "vein", "charge"]
# The skin's colours: its top (a smooth, dark stealth finish) and its edges.
SKIN = F.slate
SKIN_EDGE = F.graphite
# Shares of the transformation: the outermost rows start flipping as the skin bursts, each row
# `WAVE` later than the one outside it, each taking `FLIP`; the side petals and the middle petals
# fold open over `PETALS` and `MIDDLE`, as the orb begins to rise (`reveal.swing`).
START = 0.15
WAVE = 0.08
FLIP = 0.2
PETALS = [0.36, 0.56]
MIDDLE = [0.42, 0.62]
# How far the petals fold open (radians, from lying flat).
OPEN = 2.0
# The vanes on a panel's weapon face: their height.
VANE = 1.5
WELL_ROW = (ROW_COUNT - 1) // 2


def pieces_of(span: list[float]) -> list[list[float]]:
    """Return the panels `[y0, y1]` laid along `span`, `TILE` long, `TILE_GAP` apart."""
    length = span[1] - span[0]
    if length < 2.5:
        return []
    n = max(1, round(length / (TILE + TILE_GAP)))
    each = (length - (n - 1) * TILE_GAP) / n
    return [
        [span[0] + i * (each + TILE_GAP), span[0] + i * (each + TILE_GAP) + each] for i in range(n)
    ]


def row_tiles(k: int) -> list[list[float]]:
    """Return the panels of row `k` that flip (`[y0, y1]` each): all but those in the well."""
    span = row_span(k)
    if not in_well(k):
        return pieces_of(span)
    half = TILE_GAP / 2
    result = pieces_of([span[0], WELL[0] - half])
    result.extend(pieces_of([WELL[1] + half, span[1]]))
    return result


class Petal:
    """A panel over the orb's well that folds open.

    About its `hinge` (playfield `[x, y]`, on the wing's top), along the chord (`along`, its
    playfield X span `[x0, x1]`) or across it (its Y span `[y0, y1]`), `angle` radians as it opens
    (about the node's Z for one along the chord, X for one across it).
    """

    def __init__(self, hinge: list[float], along: bool, span: list[float], angle: float) -> None:
        self.hinge = hinge
        self.along = along
        self.span = span
        self.angle = angle


def petals(side: float) -> list[Petal]:
    """Return the petals of the well on `side` (1: the right wing, -1: the left).

    The side rows' panels hinge on their outer edges; the middle row's two on the well's fore and
    aft edges, meeting in its middle.
    """
    result: list[Petal] = []
    half = TILE_GAP / 2
    for k in [WELL_ROW - 1, WELL_ROW + 1]:
        out = -1 if k < WELL_ROW else 1
        edge = row_x(k) + out * ROW_HALF
        # Model X is the playfield's -X: the far edge's local X has the sign of -side * -out.
        far = side * out
        result.append(
            Petal([side * edge, WELL[0]], True, [WELL[0] + half, WELL[1] - half], far * OPEN)
        )
    mid = (WELL[0] + WELL[1]) / 2
    x = side * row_x(WELL_ROW)
    result.append(Petal([x, WELL[0]], False, [WELL[0] + half, mid - half], OPEN))
    result.append(Petal([x, WELL[1]], False, [mid + half, WELL[1] - half], -OPEN))
    return result


def _panel(p: Any, size: Vec3, at: Vec3) -> None:
    """Add a panel standing on `at` (local): skin on top, dark metal under and round it."""
    p.flesh.box(size, SKIN_EDGE, Placement(at), SKIN)


def _weapon_face(p: Any, size: Vec3, at: Vec3) -> None:
    """Add a panel's weapon face under it (local, `at` its underside's centre): a lit cell, vanes.

    A lit cell in its middle and a vane each side of it, hanging down (pointing up once flipped).
    """
    w = size[0]
    d = size[2]
    p.hull.box([w * 0.92, 0.25, d * 0.92], M.panel, Placement([at[0], at[1] - 0.25, at[2]]))
    p.neon.box([w * 0.5, 0.3, min(d * 0.6, 3.2)], N, Placement([at[0], at[1] - 0.55, at[2]]))
    for dx in [-1, 1]:
        p.bare.box(
            [0.5, VANE, d * 0.7],
            M.dark,
            Placement([at[0] + dx * w * 0.3, at[1] - VANE - 0.25, at[2]]),
        )


def draw_row(k: int) -> Any:
    """Return the drawing of row `k` in its node's frame (its axis along Z through the origin)."""

    def draw(p: Any) -> None:
        w = ROW_HALF * 2
        for tile in row_tiles(k):
            z = -(tile[0] + tile[1]) / 2
            size = [w, TILE_THICK, tile[1] - tile[0]]
            _panel(p, size, [0, -TILE_THICK / 2, z])
            _weapon_face(p, size, [0, -TILE_THICK / 2, z])

    return draw


def draw_petal(petal: Petal) -> Any:
    """Return the drawing of `petal` in its hinge's frame, lying flat (it stands on Y 0)."""

    def draw(p: Any) -> None:
        if petal.along:
            # Along the chord: it spans away from the hinge across X (the far edge's sign).
            sign = 1 if petal.angle > 0 else -1
            w = ROW_HALF * 2
            length = petal.span[1] - petal.span[0]
            z = -(petal.span[0] + petal.span[1]) / 2 + petal.hinge[1]
            size = [w, TILE_THICK, length]
            _panel(p, size, [sign * w / 2, 0, z])
            p.neon.box([0.6, 0.3, length * 0.8], N, Placement([sign * w * 0.7, -0.3, z]))
            return
        # Across the chord: it spans from the hinge along Z, towards the well's middle.
        length = petal.span[1] - petal.span[0]
        sign = -1 if petal.angle > 0 else 1
        size = [ROW_HALF * 2, TILE_THICK, length]
        _panel(p, size, [0, 0, sign * length / 2])
        p.neon.box([ROW_HALF, 0.3, 0.6], N, Placement([0, -0.3, sign * length * 0.7]))

    return draw


def row_point(k: int, side: float) -> Vec3:
    """Return row `k`'s node (model space): on its axis, at its panels' mid-thickness."""
    return boss_point(side * row_x(k), 0, WING_TOP + TILE_THICK / 2)


def petal_point(petal: Petal) -> Vec3:
    """Return a petal's hinge node (model space), on the wing's top."""
    return boss_point(petal.hinge[0], petal.hinge[1], WING_TOP)


def draw_skin(p: Any) -> None:
    """Draw the skin at rest (the `skin` region's whole armour): every panel lying flat."""
    for side in [-1, 1]:
        for k in range(ROW_COUNT):
            at = row_point(k, side)
            w = ROW_HALF * 2
            for tile in row_tiles(k):
                z = -(tile[0] + tile[1]) / 2
                _panel(p, [w, TILE_THICK, tile[1] - tile[0]], [at[0], WING_TOP, z])
        for petal in petals(side):
            draw_petal(petal)(_Shifted(p, petal_point(petal)))


class _Layer:
    """A layer of a drawing whose solids are moved by `offset` (for drawing a piece in place)."""

    def __init__(self, layer: Any, offset: Vec3) -> None:
        self.layer = layer
        self.offset = offset

    def box(self, size: Vec3, color: Any, place: Any, top: Any = None) -> None:
        a = place.at
        o = self.offset
        moved = Placement(
            [a[0] + o[0], a[1] + o[1], a[2] + o[2]], place.yaw, place.pitch, place.roll
        )
        self.layer.box(size, color, moved, top)


class _Shifted:
    """A drawing's layers, moved by `offset`: draws a hinged piece where it lies at rest."""

    def __init__(self, p: Any, offset: Vec3) -> None:
        self.flesh = _Layer(p.flesh, offset)
        self.bare = _Layer(p.bare, offset)
        self.neon = _Layer(p.neon, offset)


def draw_skin_frame(p: Any) -> None:
    """Draw what the skin leaves under its panels (BOSS-44): a dark floor, the wells lit.

    The floor in the tile field's outline just over the wing's top, showing between the flipped
    panels; round each well a lit seam, and a lit socket under the orb's pod.
    """
    right = [[-q[0], -q[1]] for q in tile_field()]
    left = [[q[0], -q[1]] for q in tile_field()]
    for outline in [right, left]:
        p.bare.slab(outline, [WING_TOP, WING_TOP + 0.12], M.dark)
    for side in [-1, 1]:
        x0 = row_x(WELL_ROW - 1) - ROW_HALF
        x1 = row_x(WELL_ROW + 1) + ROW_HALF
        mid = (x0 + x1) / 2
        for y in [WELL[0], WELL[1]]:
            p.neon.box([x1 - x0, 0.25, 0.5], N, Placement(boss_point(side * mid, y, WING_TOP)))
        for x in [x0, x1]:
            p.neon.box(
                [0.5, 0.25, WELL[1] - WELL[0]],
                N,
                Placement(boss_point(side * x, (WELL[0] + WELL[1]) / 2, WING_TOP)),
            )
        at = boss_point(side * ORB_AT[0], ORB_AT[1], WING_TOP)
        p.hull.cylinder(5.2, 0.5, 8, M.panel, Placement(at, math.pi / 8))


def flip_of(boss: Any, k: int) -> float:
    """How far row `k` has flipped for `boss` (None: at rest), 0 to 1."""
    t = transform_of(boss)
    if t <= 0:
        return 0
    order = WELL_ROW - abs(k - WELL_ROW)
    start = START + order * WAVE
    return ease(share(t, [start, start + FLIP]))


def transform_of(boss: Any) -> float:
    """How far its transformation has gone for `boss`: 0 before (or None), 1 once done."""
    if boss == None:
        return 0
    if boss.form >= 1:
        return 1
    if boss.transforming_into != 1:
        return 0
    return float(boss.transform)


def shown(boss: Any) -> bool:
    """Whether the rig shows (the skin region has burst), for `boss`."""
    return transform_of(boss) >= START


class TileRig:
    """The rows (a node each on its axis) and the petals (a node each on its hinge)."""

    def __init__(self, rows: list[Any], wells: list[Any], models: list[Any]) -> None:
        # Each row: `[node, k, side]`; each petal: `[node, petal]`.
        self.rows = rows
        self.wells = wells
        self.models = models

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Flip the rows and open the petals for the boss, and sync their models."""
        on = shown(boss)
        t = transform_of(boss)
        for row in self.rows:
            set_enabled(row[0], on)
            row[0].rotation.z = -row[2] * math.pi * flip_of(boss, row[1])
        for well in self.wells:
            set_enabled(well[0], on)
            span = PETALS if well[1].along else MIDDLE
            turn = well[1].angle * ease(share(t, span))
            if well[1].along:
                well[0].rotation.z = turn
            else:
                well[0].rotation.x = turn
        if not on or lit == None:
            return
        for model in self.models:
            model.sync(lit, dt)


def _node(name: str, root: Any, at: Vec3) -> Any:
    node = new_transform_node(name, root.getScene())
    node.parent = root
    node.position.set(at[0], at[1], at[2])
    return node


def build_tile_rig(root: Any, neon: Any, breath: Any) -> TileRig:
    """Return the rows and petals on `root` (the boss model's), hidden until the skin bursts."""
    scene = root.getScene()
    rows: list[Any] = []
    wells: list[Any] = []
    models: list[Any] = []
    for side in [-1, 1]:
        tag = "r" if side > 0 else "l"
        for k in range(ROW_COUNT):
            name = "aegis-wing-row-" + tag + str(k)
            node = _node(name, root, row_point(k, side))
            model = build_enemy_model(name, scene, neon, draw_row(k), breath)
            model.root.parent = node
            rows.append([node, k, side])
            models.append(model)
        found = petals(side)
        for i in range(len(found)):
            name = "aegis-wing-petal-" + tag + str(i)
            node = _node(name, root, petal_point(found[i]))
            model = build_enemy_model(name, scene, neon, draw_petal(found[i]), breath)
            model.root.parent = node
            wells.append([node, found[i]])
            models.append(model)
    rig = TileRig(rows, wells, models)
    rig.show(None, None, 0)
    return rig


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _turned(tris: list[Any], at: Vec3, about: str, turn: float) -> list[Any]:
    """`tris` turned `turn` about Z or X (as Babylon's `rotation.z` / `.x`), then moved to `at`."""
    c = math.cos(turn)
    s = math.sin(turn)
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for v in tri:
            x = v.position[0]
            y = v.position[1]
            z = v.position[2]
            if about == "z":
                q = [x * c - y * s, x * s + y * c, z]
            else:
                q = [x, y * c - z * s, y * s + z * c]
            placed.append(Vertex([q[0] + at[0], q[1] + at[1], q[2] + at[2]], v.color))
        result.append(placed)
    return result


def tile_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): none at rest, flipped and open once unfolded."""
    if unfold <= 0:
        return []
    result: list[Any] = []
    for side in [-1, 1]:
        for k in range(ROW_COUNT):
            result.extend(_turned(_drawn(draw_row(k)), row_point(k, side), "z", -side * math.pi))
        for petal in petals(side):
            about = "z" if petal.along else "x"
            result.extend(
                _turned(_drawn(draw_petal(petal)), petal_point(petal), about, petal.angle)
            )
    return result
