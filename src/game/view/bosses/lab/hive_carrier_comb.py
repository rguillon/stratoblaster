# Copyright (c) 2026 Renaud Guillon
"""FB-HIVE-CARRIER-02, FB-HIVE-CARRIER-05: the Hive Carrier's honeycomb and its armour.

The deck of the hive is covered with hexagonal wax cells on a grid. The cells over its armour
regions (its side combs, its front combs and its rear comb) are that armour, drawn apart; the
others are the core's, kept clear of its queen chamber, its bays, its ram and its metal ribs.
Logical pixels, nose +Z, Y up (towards the camera); outlines and spots are taken from the design
(px, X right, Y up) and turned into model space here.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.hive_carrier import (
    BAY_X,
    BAY_Y,
    DECK_TOP,
    FRONT_COMB,
    REAR_COMB,
    SIDE_COMB,
)
from game.view.bosses.world_1_organic_kit import F, gland, vein_line
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["hive-carrier"]

# The hull's hexagon (px, X right, Y up): its side corners at (±66, 0), the others at (±36, ±54).
HEX = [[66, 0], [36, 54], [-36, 54], [-66, 0], [-36, -54], [36, -54]]
# The grid of cells: `GRID` px from a cell's centre to the next's corner (a flat-topped hexagon
# grid along X), each cell `CELL` px round, `CELL_HEIGHT` px high on the deck.
GRID = 6
CELL = 5.2
CELL_HEIGHT = 3.5
# The queen chamber's radius on the deck, and the bays' collars'.
CHAMBER_R = 20
BAY_R = 13
# Where the radial ribs stop: at a bay's collar, or short of the side combs.
RIB_BAY = math.hypot(BAY_X, BAY_Y) - BAY_R
RIB_SIDE = 37


def model(x: float, y: float, h: float) -> list[Any]:
    """Return a design point (px, X right, Y up) at height `h`, in model space."""
    return [-x, h, -y]


def inside(outline: list[Any], x: float, y: float) -> bool:
    """Whether the point (x, y) lies inside `outline` (even-odd rule)."""
    result = False
    n = len(outline)
    for i in range(n):
        a = outline[i]
        b = outline[(i + 1) % n]
        if (a[1] > y) != (b[1] > y):
            cross = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < cross:
                result = not result
    return result


def _in_hull(x: float, y: float, margin: float) -> bool:
    """Whether (x, y) lies at least `margin` px inside the hull's hexagon."""
    ax = abs(x)
    ay = abs(y)
    slant = 0.874 * (ax - 66) + 0.486 * ay
    return ay <= 54 - margin and slant <= -margin


def mirrored_outlines(outline: list[Any], mirror: bool) -> list[Any]:
    """Return a region's outline and, if `mirror`, its mirror image across the centre line."""
    result = [outline]
    if mirror:
        result.append([[-q[0], q[1]] for q in outline])
    return result


# The armour regions' ids and outlines (as the design's, mirrored where it mirrors them).
REGIONS = [
    ["side-combs", mirrored_outlines(SIDE_COMB, True)],
    ["front-combs", mirrored_outlines(FRONT_COMB, True)],
    ["rear-comb", mirrored_outlines(REAR_COMB, False)],
]


def _region_of(x: float, y: float) -> Any:
    """Return the id of the armour region whose outline holds (x, y), or None."""
    for entry in REGIONS:
        for outline in entry[1]:
            if inside(outline, x, y):
                return entry[0]
    return None


def rib_ends() -> list[list[Any]]:
    """Return the radial ribs (design px), from the queen chamber's foot out to each corner.

    Each `[[x0, y0], [x1, y1]]`: to the four bays' collars and short of the two side combs.
    """
    result: list[list[Any]] = []
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            d = math.hypot(BAY_X, BAY_Y)
            ux = sx * BAY_X / d
            uy = sy * BAY_Y / d
            result.append([[ux * CHAMBER_R, uy * CHAMBER_R], [ux * RIB_BAY, uy * RIB_BAY]])
        result.append([[sx * CHAMBER_R, 0], [sx * RIB_SIDE, 0]])
    return result


def _near_rib(x: float, y: float, gap: float) -> bool:
    """Whether (x, y) lies within `gap` px of a radial rib."""
    for rib in rib_ends():
        a = rib[0]
        b = rib[1]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
        if math.hypot(x - a[0] - t * dx, y - a[1] - t * dy) < gap:
            return True
    return False


def _clear_of_core(x: float, y: float) -> bool:
    """Whether a core cell at (x, y) is clear of the chamber, the bays, the ram and the ribs."""
    if math.hypot(x, y) < CHAMBER_R + 4:
        return False
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            if math.hypot(x - sx * BAY_X, y - sy * BAY_Y) < BAY_R + 4:
                return False
    if y < -44 and abs(x) < 18:
        return False
    return not _near_rib(x, y, 4.2)


def cells_of(region: Any) -> list[list[float]]:
    """Return the centres (design px) of the cells of `region` (an armour id; None: the core's)."""
    result: list[list[float]] = []
    step = math.sqrt(3) * GRID
    for i in range(-12, 13):
        x = i * 1.5 * GRID
        shift = step / 2 if i % 2 != 0 else 0
        for j in range(-10, 11):
            y = j * step + shift
            if not _in_hull(x, y, 4.5):
                continue
            where = _region_of(x, y)
            if where != region:
                continue
            if region == None and not _clear_of_core(x, y):
                continue
            result.append([x, y])
    return result


def _cell_hash(x: float, y: float) -> int:
    """Return a small number drawn from a cell's place, the same each time (its variety)."""
    return int(abs(math.floor(x * 7 + y * 13))) % 7


def draw_cells(p: Any, spots: list[Any]) -> None:
    """Draw wax cells at `spots` (design px): hexagonal prisms on the deck, a few lit larvae."""
    for spot in spots:
        k = _cell_hash(spot[0], spot[1])
        h = CELL_HEIGHT + (k % 3) * 0.4
        color = F.bone if k % 2 == 0 else F.sinew
        at = model(spot[0], spot[1], DECK_TOP)
        p.flesh.cylinder(CELL, h, 6, color, Placement(at), CELL * 0.88)
        if k == 3:
            organ(p.vein, CELL * 0.4, 6, N, Placement(model(spot[0], spot[1], DECK_TOP + h)), 0.4)


def draw_core_cells(p: Any) -> None:
    """Draw the core's own cells (FB-HIVE-CARRIER-02), off the armour regions."""
    draw_cells(p, cells_of(None))


def _draw_side_combs(p: Any) -> None:
    """Draw the side combs (FB-HIVE-CARRIER-05): the cells over the hull's side corners.

    A vein across each to a gland; the mortars lie folded under them.
    """
    draw_cells(p, cells_of("side-combs"))
    top = DECK_TOP + CELL_HEIGHT + 1
    for s in [-1, 1]:
        vein_line(p, model(s * 40, -12, top), model(s * 58, 8, top), [0, 1, 0], 0.9, N)
        gland(p, model(s * 52, -8, top - 0.4), 1.3, N)


def _draw_front_combs(p: Any) -> None:
    """Draw the front combs (FB-HIVE-CARRIER-05): the cells either side of the chamber's front.

    The sweepers lie folded under them.
    """
    draw_cells(p, cells_of("front-combs"))
    top = DECK_TOP + CELL_HEIGHT + 1
    for s in [-1, 1]:
        vein_line(p, model(s * 7, -24, top), model(s * 18, -40, top), [0, 1, 0], 0.8, N)


def _draw_rear_comb(p: Any) -> None:
    """Draw the rear comb (FB-HIVE-CARRIER-05): the cells behind the chamber, over the hangar."""
    draw_cells(p, cells_of("rear-comb"))
    top = DECK_TOP + CELL_HEIGHT + 1
    vein_line(p, model(-9, 22, top), model(9, 40, top), [0, 1, 0], 0.9, N)
    gland(p, model(0, 31, top - 0.4), 1.5, N)


def hive_armour() -> dict[str, Any]:
    """Return the Hive Carrier's comb armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "side-combs": {"whole": _draw_side_combs},
        "front-combs": {"whole": _draw_front_combs},
        "rear-comb": {"whole": _draw_rear_comb},
    }
