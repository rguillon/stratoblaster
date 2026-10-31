"""The homes made for the grid of tiles (Phase 15, P15-R09): houses with their gardens, terraces,
flats, workshops, farms and desert homes See `tile_kit.py`
for the plot."""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from game.config.window_look import DOOR_STYLES, WINDOW_STYLES
from game.view.props.tile_kit import (
    NEON,
    TileKit,
    any_of,
    door,
    front_lights,
    gable,
    js_round,
    plot,
    r,
    tree,
    windows,
)
from render.geometry.solids import Placement

WALLS = [C.white, C.farmWall, C.brick, C.concrete]
ROOFS = [C.roof, C.farmRoof, C.brick, C.metalDark]


def build_house(k: TileKit) -> None:
    """A house at the front of its plot, a garden with a tree or two behind it."""
    plot(k, C.leafDark)
    bw = min(k.w - 2, r(k, [6, 8]))
    bd = min(k.d * 0.6, r(k, [5, 7]))
    z = -k.d / 2 + bd / 2 + 1
    h = r(k, [3.5, 5])
    k.s.box([bw, h, bd], any_of(k, WALLS), Placement([0, 0, z], 0, 0, 0))
    gable(k, [bw, bd], h, r(k, [2, 3]), any_of(k, ROOFS), [0, z])
    windows(k, [bw, bd], [1, h - 0.5], L.window, [0, z])
    back = (k.d / 2 + (z + bd / 2)) / 2
    for _i in range(max(1, js_round(k.d / 10))):
        x = r(k, [-k.w / 3, k.w / 3])
        z2 = back + r(k, [-1, 1]) * (k.d / 6)
        tree(k, x, z2, r(k, [3, 4.5]))


def build_villa(k: TileKit) -> None:
    """A modern villa: two offset flat-roofed slabs, a pool, a lawn."""
    plot(k, C.leaf)
    w = k.w * 0.7
    d = k.d * 0.45
    k.s.box([w, 4, d], C.white, Placement([-k.w * 0.1, 0, -k.d * 0.2], 0, 0, 0), C.roof)
    k.s.box(
        [w * 0.6, 3.5, d * 0.8],
        C.concreteDark,
        Placement([k.w * 0.05, 4, -k.d * 0.15], 0, 0, 0),
        C.roof,
    )
    k.s.box(
        [k.w * 0.35, 0.3, k.d * 0.2], C.glassBlue, Placement([k.w * 0.2, 0, k.d * 0.28], 0, 0, 0)
    )
    k.lights.box([k.w * 0.35, 0.1, 0.2], L.cyan, Placement([k.w * 0.2, 0.32, k.d * 0.18], 0, 0, 0))
    windows(k, [w, d], [1, 3.5], L.window, [-k.w * 0.1, -k.d * 0.2])
    tree(k, -k.w * 0.25, k.d * 0.25, min(3.5, k.w * 0.3))


def build_cottage(k: TileKit) -> None:
    """A small cottage: a low house under a steep roof, a garden round it."""
    plot(k, C.leafDark)
    s = min(k.w, k.d) * 0.55
    k.s.box(
        [s, 3, s * 0.8],
        any_of(k, [C.farmWall, C.white, C.adobe]),
        Placement([0, 0, -k.d * 0.12], 0, 0, 0),
    )
    gable(k, [s, s * 0.8], 3, 3, any_of(k, [C.thatch, C.farmRoof, C.roof]), [0, -k.d * 0.12])
    # D-215: its windows and its door, quads from the windows' atlas.
    windows(k, [s, s * 0.8], [0.7, 2.7], L.window, [0, -k.d * 0.12], WINDOW_STYLES.punched)
    door(k, [-s * 0.2, 0, -k.d * 0.12 - s * 0.4], DOOR_STYLES.door, L.window)
    tree(k, k.w * 0.3, k.d * 0.3, 3)


def build_terrace(k: TileKit) -> None:
    """A row of terraced houses along the plot's long side, small back yards."""
    plot(k, C.leafDark)
    along_z = k.d > k.w
    length = k.d if along_z else k.w
    depth = k.w if along_z else k.d
    n = max(2, js_round(length / 4.5))
    each = length / n
    h = r(k, [5, 7])
    wall = any_of(k, [C.brick, C.farmWall, C.concrete])
    for i in range(n):
        a = -length / 2 + each * (i + 0.5)
        hh = h + (i % 2) * 0.4
        x = -depth * 0.15 if along_z else a
        z = a if along_z else -depth * 0.15
        bw = depth * 0.65 if along_z else each - 0.3
        bd = each - 0.3 if along_z else depth * 0.65
        k.s.box([bw, hh, bd], wall, Placement([x, 0, z], 0, 0, 0))
        gable(k, [bw, bd], hh, 2, C.roof, [x, z], along_z)
        windows(k, [bw, bd], [1, hh - 0.6], L.window, [x, z])


def build_flats(k: TileKit) -> None:
    """A block of flats: 3 to 6 floors, a flat roof with its plant, lit windows."""
    plot(k, C.concreteDark)
    w = k.w - 1.5
    d = k.d - 1.5
    h = r(k, [10, 18])
    k.s.box([w, h, d], any_of(k, [C.brick, C.concrete, C.farmWall]), Placement(), C.roof)
    k.s.box([w * 0.3, 2, d * 0.3], C.metalDark, Placement([w * 0.2, h, 0], 0, 0, 0))
    windows(k, [w, d], [1.5, h - 1], any_of(k, [L.window, L.windowDim]), [0, 0])
    front_lights(k, w, -d / 2, 1.8, any_of(k, NEON))


def build_workshop(k: TileKit) -> None:
    """A workshop: a saw-tooth roofed shed, a yard with crates at the front."""
    plot(k, C.concreteDark)
    w = k.w - 1
    d = k.d * 0.7
    z = (k.d - d) / 2 - 0.5
    h = r(k, [5, 7])
    k.s.box([w, h, d], any_of(k, [C.brick, C.corrugated, C.metal]), Placement([0, 0, z], 0, 0, 0))
    teeth = max(1, js_round(d / 5))
    for i in range(teeth):
        tz = z - d / 2 + (d / teeth) * (i + 0.5)
        gable(k, [w, d / teeth], h, 1.6, C.roof, [0, tz])
    for _i in range(3):
        size = [1.4, 1.2, 1.4]
        color = any_of(k, [C.wood, C.containerBlue, C.rust])
        at = [r(k, [-k.w / 3, k.w / 3]), 0, -k.d / 2 + 1.5]
        k.s.box(size, color, Placement(at, 0, 0, 0))
    front_lights(k, w, z - d / 2, h - 1, L.yellowDim)


def build_farmhouse(k: TileKit) -> None:
    """A farmhouse with a barn beside it, a vegetable plot."""
    plot(k, C.leaf)
    k.s.box(
        [k.w * 0.4, 4, k.d * 0.35], C.farmWall, Placement([-k.w * 0.22, 0, -k.d * 0.2], 0, 0, 0)
    )
    gable(k, [k.w * 0.4, k.d * 0.35], 4, 2.5, C.farmRoof, [-k.w * 0.22, -k.d * 0.2])
    # D-215: its windows and its door, quads from the windows' atlas.
    windows(
        k,
        [k.w * 0.4, k.d * 0.35],
        [1, 3.8],
        L.window,
        [-k.w * 0.22, -k.d * 0.2],
        WINDOW_STYLES.punched,
    )
    door(k, [-k.w * 0.3, 0, -k.d * 0.375], DOOR_STYLES.door, L.window)
    build_shed(k, [k.w * 0.25, k.d * 0.15], [k.w * 0.4, k.d * 0.5])
    for i in range(4):
        k.s.box(
            [k.w * 0.4, 0.5, 0.8],
            C.leafLight,
            Placement([-k.w * 0.22, 0.2, k.d * 0.15 + i * 1.6], 0, 0, 0),
        )


def build_shed(k: TileKit, at: list[float], size: list[float]) -> None:
    """A red shed of `w` × `d` at (x, z), gabled along Z."""
    x = at[0]
    z = at[1]
    w = size[0]
    d = size[1]
    k.s.box([w, 5, d], C.containerRed, Placement([x, 0, z], 0, 0, 0))
    gable(k, [w, d], 5, 3, C.metalDark, [x, z], True)


def build_barn(k: TileKit) -> None:
    """A long barn and a pair of silos."""
    plot(k, C.dryLeaf)
    build_shed(k, [-k.w * 0.12, 0], [k.w * 0.6, k.d - 2])
    # D-215: its door, a bay from the windows' atlas.
    door(k, [-k.w * 0.12, 0, -(k.d - 2) / 2], DOOR_STYLES.bay, L.yellowDim)
    for z in [-k.d * 0.2, k.d * 0.15]:
        k.s.cylinder(1.8, 9, 8, C.silver, Placement([k.w * 0.32, 0, z], 0, 0, 0))
        k.s.cylinder(1.8, 1.2, 8, C.metal, Placement([k.w * 0.32, 9, z], 0, 0, 0), 0.3)


def build_greenhouse(k: TileKit) -> None:
    """Glass greenhouses in rows, lit inside."""
    plot(k, C.leafDark)
    rows = max(1, js_round(k.w / 5))
    each = k.w / rows
    for i in range(rows):
        x = -k.w / 2 + each * (i + 0.5)
        k.s.box([each - 1, 2.5, k.d - 1.5], C.glassGreen, Placement([x, 0, 0], 0, 0, 0))
        gable(k, [each - 1, k.d - 1.5], 2.5, 1.5, C.glassGreen, [x, 0], True)
        k.lights.box([0.2, 0.2, k.d - 2], L.toxicDim, Placement([x, 2.4, 0], 0, 0, 0))


def build_adobe(k: TileKit) -> None:
    """Adobe homes: flat roofs, parapets, a windcatcher on some, a palm in the yard."""
    plot(k, C.sand)
    n = max(1, js_round((k.w * k.d) / 70))
    for i in range(n):
        w = k.w / min(n, 2) - 1.5
        d = k.d / math.ceil(n / 2) - 1.5
        x = ((-1 if i % 2 == 0 else 1) * (k.w / 4)) if n > 1 else 0
        z = ((-1 if i < 2 else 1) * (k.d / 4)) if n > 2 else 0  # noqa: PLR2004, PLR2004 (a geometry constant)
        h = r(k, [3.5, 6])
        k.s.box(
            [w, h, d], any_of(k, [C.adobe, C.adobeDark]), Placement([x, 0, z], 0, 0, 0), C.adobeRoof
        )
        k.s.box([w, 0.6, 0.4], C.adobeDark, Placement([x, h, z - d / 2 + 0.2], 0, 0, 0))
        if k.random() < 0.5:  # noqa: PLR2004 (a geometry constant)
            k.s.box([1.4, 3, 1.4], C.adobeDark, Placement([x + w / 4, h, z], 0, 0, 0))
        # D-215: its windows and its door, quads from the windows' atlas.
        windows(k, [w, d], [1.2, h - 0.6], L.window, [x, z], WINDOW_STYLES.punched)
        door(k, [x, 0, z - d / 2], DOOR_STYLES.door, L.window)


def build_courtyard(k: TileKit) -> None:
    """A courtyard house: four wings round a yard with a fountain and palms."""
    plot(k, C.paving)
    w = k.w - 1
    d = k.d - 1
    t = 4
    for x, z, bw, bd in [
        [0, -d / 2 + t / 2, w, t],
        [0, d / 2 - t / 2, w, t],
        [-w / 2 + t / 2, 0, t, d - 2 * t],
        [w / 2 - t / 2, 0, t, d - 2 * t],
    ]:
        k.s.box([bw, 5, bd], C.adobe, Placement([x, 0, z], 0, 0, 0), C.adobeRoof)
    k.s.cylinder(1.5, 0.8, 8, C.adobeDark, Placement([0, 0, 0], 0, 0, 0))
    k.lights.ring(1.2, 0.3, 8, L.cyan, Placement([0, 0.8, 0], 0, 0, 0))
    # D-215: its gate, a bay from the windows' atlas.
    door(k, [0, 0, -d / 2], DOOR_STYLES.bay, L.window)
