# Copyright (c) 2026 Renaud Guillon
"""FB-AERIAL-ARK-05, FB-AERIAL-ARK-11: the Aerial Ark's view rig, its outer wing segments' morphs.

Logical pixels, nose +Z, Y up (towards the camera). Each outer segment of its wing is four tiles
side by side across its span (each on a node of its own), a telescoping rod in the strut at its
joint, and two cables from the centre section's corners to its root. Staged on the reveal
timeline (`BOSS_LOOK.reveal`):
- first transformation (the squadron breaks formation): as the joint's fairing bursts, each outer
  segment slides out and back from its joint, swinging its tip back a little, the rod telescoping
  out of the strut's sleeve under it and the cables paying out from the corners;
- second transformation (the halo): the cables reel in, then the segment breaks into its tiles,
  which lift and swing round one after the other, each turning to lie along a ring round the
  centre section, until the eight tiles close into a halo, their lit seams its two rims; the rod
  draws back in to the orb at the halo's side.
The rig is only looks: its outer engines (parts) leave the fight as the segments break away, and
the orbs, gatlings and lance stand on the centre section, which never moves.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.aerial_ark import (
    CHORD,
    HALO_R,
    HALO_Y,
    JOINT_X,
    LEAD_SLOPE,
    NACELLE_AXIS,
    NACELLE_R,
    OUTER_ENGINE,
    STRUT_TOP,
    STRUT_Y,
    TILE_Y,
    TILES,
    TIP_X,
    WING_Y,
    lead,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_reveal import ease, share
from game.view.bosses.mini_boss_greebles import lamps
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


N = BOSS_LOOK.neon["aerial-ark"]
QUARTER = math.pi / 2
DEG = math.pi / 180
LAYERS = ["hull", "bare", "flesh", "neon", "vein", "charge"]
SIDES = [1, -1]
# A tile's span across the outer segment.
TILE_W = (TIP_X - JOINT_X) / TILES
# The split (shares of the first transformation, from the burst): the segment swings `SPLIT_TURN`
# degrees about `SPLIT_PIVOT` (its tip back) and slides `SPLIT_OUT` px out and back.
SPLIT = [0.15, 0.62]
SPLIT_PIVOT = [JOINT_X, -6]  # type: list[float]
SPLIT_TURN = 10
SPLIT_OUT = [22, 8]
# The halo (shares of the second transformation): each tile flies round over `HALO_SPAN`, the
# next `HALO_STEP` later, lifting `HALO_LIFT` px on its way, to lie `HALO_H` px higher than drawn.
HALO_FIRST = [0.2, 0.6]
HALO_STEP = 0.07
HALO_LIFT = 14
HALO_H = 4
# The cables: paid out with the split, reeled in at the second transformation's start.
REEL = [0.12, 0.32]
# The rod in each joint's strut: its length, its half width, its top; where its outer end is, at
# rest, split and as the halo.
ROD_LENGTH = 22
ROD_HALF = 3
ROD_REACH = [JOINT_X, 68, 53]
ROD_DRAW = [0.15, 0.45]


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the playfield point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def tile_centre(i: int) -> list[float]:
    """Return the centre `[x, y]` of tile `i` (0: by the joint) of the right segment at rest."""
    x = JOINT_X + TILE_W * (i + 0.5)
    return [x, lead(x) + CHORD / 2]


def tile_corners(side: float) -> list[list[float]]:
    """Return a tile's corners round its centre (config, on `side`): a sheared parallelogram.

    Its leading edge, then its outer edge, its trailing edge and its inner edge.
    """
    w = TILE_W / 2
    shear = LEAD_SLOPE * w
    c = CHORD / 2
    return [
        [-side * w, -c - shear],
        [side * w, -c + shear],
        [side * w, c + shear],
        [-side * w, c - shear],
    ]


def _turned(q: list[float], about: list[float], degrees: float) -> list[float]:
    a = degrees * DEG
    x = q[0] - about[0]
    y = q[1] - about[1]
    return [
        about[0] + x * math.cos(a) - y * math.sin(a),
        about[1] + x * math.sin(a) + y * math.cos(a),
    ]


def split_pose(i: int, k: float) -> list[float]:
    """Return tile `i`'s pose `[x, y, h, turn]` (right side) `k` of the way through the split."""
    q = _turned(tile_centre(i), SPLIT_PIVOT, SPLIT_TURN * k)
    return [q[0] + SPLIT_OUT[0] * k, q[1] + SPLIT_OUT[1] * k, 0, SPLIT_TURN * k]


def halo_pose(i: int) -> list[float]:
    """Return tile `i`'s place in the halo `[x, y, h, turn]` (right side): along the ring."""
    turn = -67.5 + 45 * i
    a = turn * DEG
    return [HALO_R * math.cos(a), HALO_Y + HALO_R * math.sin(a), HALO_H, turn]


def tile_pose(i: int, boss: Any) -> list[float]:
    """Return tile `i`'s pose `[x, y, h, turn]` (right side) for `boss` (None: at rest)."""
    if boss == None:
        return split_pose(i, 0)
    if boss.form >= 2:
        return halo_pose(i)
    if boss.form < 1:
        k = 0.0
        if boss.transforming_into == 1:
            k = ease(share(boss.transform, SPLIT))
        return split_pose(i, k)
    a = split_pose(i, 1)
    if boss.transforming_into != 2:
        return a
    u = ease(share(boss.transform, [HALO_FIRST[0] + HALO_STEP * i, HALO_FIRST[1] + HALO_STEP * i]))
    b = halo_pose(i)
    pose = [a[k] + (b[k] - a[k]) * u for k in range(4)]
    pose[2] += HALO_LIFT * math.sin(math.pi * u)
    return pose


def corner_at(pose: list[float], corner: list[float]) -> list[float]:
    """Return where a tile's `corner` (round its centre, right side) is with the tile at `pose`."""
    q = _turned(corner, [0, 0], pose[3])
    return [pose[0] + q[0], pose[1] + q[1]]


def rod_reach(boss: Any) -> float:
    """Return how far out the strut's rod reaches (its outer end's X) for `boss`."""
    if boss == None or (boss.form < 1 and boss.transforming_into != 1):
        return ROD_REACH[0]
    if boss.form < 1:
        k = ease(share(boss.transform, SPLIT))
        return ROD_REACH[0] + (ROD_REACH[1] - ROD_REACH[0]) * k
    if boss.form >= 2:
        return ROD_REACH[2]
    if boss.transforming_into != 2:
        return ROD_REACH[1]
    k = ease(share(boss.transform, ROD_DRAW))
    return ROD_REACH[1] + (ROD_REACH[2] - ROD_REACH[1]) * k


def cable_reel(boss: Any) -> float:
    """How far the cables are reeled in (0: out to the segment, 1: in; -1: none to show)."""
    if boss == None or boss.form >= 2:
        return -1
    if boss.form < 1:
        if boss.transforming_into != 1 or share(boss.transform, SPLIT) <= 0.02:
            return -1
        return 0
    if boss.transforming_into != 2:
        return 0
    k = ease(share(boss.transform, REEL))
    return -1 if k >= 1 else k


def draw_tile(side: float, i: int) -> Any:
    """Return the drawing of tile `i` of the segment on `side`, round its centre (model space).

    A thick plate of dark plating, the outer segment's skin, its leading edge lit, a lit seam
    along each of its sides across the span (they become the halo's rims), panel lines; the tip
    tile carries a winglet and a light, the third tile the outer engine's nacelle.
    """
    corners = tile_corners(side)
    centre = tile_centre(i)

    def local(x: float, y: float, h: float) -> Vec3:
        return [-x, h, -y]

    def draw(p: Any) -> None:
        outline = [flat(q[0], q[1]) for q in corners]
        p.flesh.bevel_slab(outline, TILE_Y, [0.4, 0.8], F.graphite, None, F.slate)
        top = TILE_Y[2]
        for k in [0, 1, 2, 3]:
            a = corners[k]
            b = corners[(k + 1) % 4]
            inset = 0.5 if k != 0 else 0.7
            dx = b[0] - a[0]
            dy = b[1] - a[1]
            length = math.hypot(dx, dy)
            mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
            # Its edge's light, a little in from the edge (towards the centre).
            nx = -mid[0]
            ny = -mid[1]
            reach = math.hypot(nx, ny) or 1
            at = local(mid[0] + nx / reach * inset, mid[1] + ny / reach * inset, top - 0.2)
            yaw = math.atan2(-dx, -dy)
            width = 0.7 if k != 2 else 0.4
            p.neon.box([width, 0.45, length - 1.4], N, Placement(at, yaw))
        for v in [-0.2, 0.2]:
            p.bare.box([TILE_W - 3, 0.3, 0.5], M.dark, Placement(local(0, v * CHORD, top)))
        p.hull.box([TILE_W * 0.45, 0.8, 4], M.panel, Placement(local(side * 1, 3, top - 0.3)))
        if i == TILES - 1:
            fin = [
                flat(side * (TILE_W / 2 - 1.6), -4),
                flat(side * (TILE_W / 2), -6),
                flat(side * (TILE_W / 2), 9),
                flat(side * (TILE_W / 2 - 1.6), 9),
            ]
            p.hull.slab(fin, [top - 0.5, top + 5], M.panel, None, M.base)
            lamps(p.neon, [local(side * (TILE_W / 2 - 0.8), 7, top + 5)], 1.2, N)
        if i == 2:
            nacelle(
                p,
                side * (OUTER_ENGINE[0] - centre[0]),
                OUTER_ENGINE[1] - centre[1],
                OUTER_ENGINE[2] - centre[1],
            )

    return draw


def nacelle(p: Any, x: float, y0: float, y1: float) -> None:
    """Draw an engine nacelle along Y at `x` (config, round a tile's centre) on its pylon.

    A plated tube with an intake lip at its front, its nozzle burning at its back (the engine of
    its part, whose gun stands on its back).
    """
    axis = NACELLE_AXIS
    r = NACELLE_R
    p.hull.box(
        [3, axis - TILE_Y[2] + 0.5, y1 - y0 - 8],
        M.base,
        Placement([-x, TILE_Y[2] - 0.3, -(y0 + y1) / 2]),
    )
    p.hull.cylinder(r, y1 - y0 - 4, 10, M.panel, Placement([-x, axis, -(y1 - 4)], 0, QUARTER))
    p.hull.lathe(
        [[r - 0.6, 0], [r + 0.4, 1.4], [r + 0.2, 4]],
        10,
        M.base,
        Placement([-x, axis, -y0], 0, -QUARTER),
        False,
    )
    p.neon.ring(r + 0.45, 0.4, 10, N, Placement([-x, axis, -(y0 + 1.6)], 0, QUARTER))
    p.hull.lathe(
        [[r, 0], [r - 0.6, 2], [r - 1.4, 4]],
        10,
        M.dark,
        Placement([-x, axis, -(y1 - 4)], 0, -QUARTER),
        False,
    )
    p.reactor([-x, axis, -(y1 - 0.5)], r - 1.6)


def draw_rod(side: float) -> Any:
    """Return the drawing of a strut's rod, from its outer end inwards (model space).

    A square bar, its lit end cap where it grips the segment.
    """

    def draw(p: Any) -> None:
        h0 = WING_Y[1] - 1.1
        p.hull.box(
            [ROD_LENGTH, STRUT_TOP - 1.2 - h0, ROD_HALF * 2],
            M.panel,
            Placement([side * ROD_LENGTH / 2, h0, 0]),
            M.base,
        )
        p.neon.box([1, 0.5, ROD_HALF * 2 + 0.4], N, Placement([side * 1.2, STRUT_TOP - 1.3, 0]))

    return draw


def draw_cable(p: Any) -> None:
    """Draw a cable one px long along +Z from its node (it is stretched to its length)."""
    p.bare.box([0.6, 0.6, 1], M.dark, Placement([0, -0.3, 0.5]))
    p.neon.box([0.25, 0.25, 1], N, Placement([0, 0.3, 0.5]))


def cable_ends(side: float, back: bool, pose: list[float], reel: float) -> list[Vec3]:
    """Return a cable's two ends (model space): from the centre section's corner to the segment's.

    `pose` is the tile by the joint's (right side), `reel` how far it is reeled in.
    """
    corners = tile_corners(1)
    corner = corners[3] if back else corners[0]
    end = corner_at(pose, corner)
    start = [JOINT_X - 1, (lead(JOINT_X) + CHORD - 1.5) if back else (lead(JOINT_X) + 1.5)]
    x = end[0] + (start[0] - end[0]) * reel
    y = end[1] + (start[1] - end[1]) * reel
    h = WING_Y[2] - 0.6
    return [pt(side * start[0], start[1], h), pt(side * x, y, h + pose[2])]


def _place_cable(node: Any, ends: list[Vec3]) -> None:
    a = ends[0]
    b = ends[1]
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    node.position.set(a[0], a[1], a[2])
    node.rotation.y = math.atan2(dx, dz)
    node.scaling.z = max(0.01, math.hypot(dx, dz))


class ArkRig:
    """The tiles of its outer segments, the rods in its struts and its cables, on their nodes."""

    def __init__(
        self, tiles: list[Any], rods: list[Any], cables: list[Any], models: list[Any]
    ) -> None:
        self.tiles = tiles
        self.rods = rods
        self.cables = cables
        self.models = models

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Pose its pieces for the boss's transformations, and sync their models."""
        self.pose(boss)
        for model in self.models:
            model.sync(lit, dt)

    def pose(self, boss: Any) -> None:
        """Pose its pieces for `boss` (None: at rest)."""
        reach = rod_reach(boss)
        reel = cable_reel(boss)
        for j in range(2):
            side = SIDES[j]
            for i in range(TILES):
                pose = tile_pose(i, boss)
                node = self.tiles[j * TILES + i]
                at = pt(side * pose[0], pose[1], pose[2])
                node.position.set(at[0], at[1], at[2])
                node.rotation.y = -side * pose[3] * DEG
            rod = pt(side * reach, STRUT_Y, 0)
            self.rods[j].position.set(rod[0], 0, rod[2])
            first = tile_pose(0, boss)
            for b in range(2):
                cable = self.cables[j * 2 + b]
                set_enabled(cable, reel >= 0)
                if reel >= 0:
                    _place_cable(cable, cable_ends(side, b == 1, first, reel))


def _hang(name: str, root: Any, draw: Any, neon: Any, breath: Any) -> list[Any]:
    """Return `[node, model]`: a node on `root` carrying the model `draw` draws."""
    node = new_transform_node(name, root.getScene())
    node.parent = root
    model = build_enemy_model(name, root.getScene(), neon, draw, breath)
    model.root.parent = node
    return [node, model]


def build_ark_rig(root: Any, neon: Any, breath: Any) -> ArkRig:
    """Return the tiles, rods and cables on `root` (the boss model's), posed at rest."""
    models: list[Any] = []
    tiles: list[Any] = []
    rods: list[Any] = []
    cables: list[Any] = []
    for side in SIDES:
        name = "aerial-ark-" + ("right" if side > 0 else "left")
        for i in range(TILES):
            tile = _hang(name + "-tile-" + str(i), root, draw_tile(side, i), neon, breath)
            tiles.append(tile[0])
            models.append(tile[1])
        rod = _hang(name + "-rod", root, draw_rod(side), neon, breath)
        rods.append(rod[0])
        models.append(rod[1])
        for b in ["front", "back"]:
            cable = _hang(name + "-cable-" + b, root, draw_cable, neon, breath)
            set_enabled(cable[0], False)
            cables.append(cable[0])
            models.append(cable[1])
    rig = ArkRig(tiles, rods, cables, models)
    rig.pose(None)
    return rig


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


def _moved(tris: list[Any], at: Vec3, yaw: float, stretch: float) -> list[Any]:
    """`tris` stretched `stretch` along Z, turned `yaw` about Y (as Babylon's), moved to `at`."""
    c = math.cos(yaw)
    s = math.sin(yaw)
    result: list[Any] = []
    for tri in tris:
        placed: list[Any] = []
        for v in tri:
            x = v.position[0]
            y = v.position[1]
            z = v.position[2] * stretch
            placed.append(
                Vertex([x * c + z * s + at[0], y + at[1], -x * s + z * c + at[2]], v.color)
            )
        result.append(placed)
    return result


def ark_triangles(unfold: float) -> list[Any]:
    """Return the rig's triangles (model space): the wing whole, or split (`unfold` 1)."""
    k = 1 if unfold >= 1 else 0
    result: list[Any] = []
    cable = _drawn(draw_cable)
    for side in SIDES:
        for i in range(TILES):
            pose = split_pose(i, k)
            at = pt(side * pose[0], pose[1], pose[2])
            result.extend(_moved(_drawn(draw_tile(side, i)), at, -side * pose[3] * DEG, 1))
        rod = pt(side * ROD_REACH[k], STRUT_Y, 0)
        result.extend(_moved(_drawn(draw_rod(side)), [rod[0], 0, rod[2]], 0, 1))
        if k == 1:
            for back in [False, True]:
                ends = cable_ends(side, back, split_pose(0, 1), 0)
                a = ends[0]
                b = ends[1]
                yaw = math.atan2(b[0] - a[0], b[2] - a[2])
                result.extend(_moved(cable, a, yaw, math.hypot(b[0] - a[0], b[2] - a[2])))
    return result
