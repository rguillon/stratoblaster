# Copyright (c) 2026 Renaud Guillon
"""FB-GEYSER-RIG-15, FB-GEYSER-RIG-17, 4-2: the Geyser Rig's armour (D-254).

Drawn as pieces of their own, lying on the deck as the boss rests (BOSS-42): the back plating with
the cooling tower on it (`back`), shed at its first transformation, and the two wing plates with
the pipe racks on them (`wings`), shed at its second. The deck under them is the core's, flat at
`DECK_Y`. Each bursts into plates cracked from its outline at the plating's own height (not at the
top of the tower or the pipes standing on it, where the default plates would lie). Logical pixels,
nose +Z, Y up; a config outline (x, y) is drawn at (-x, -y).
"""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_armour import plate_pieces
from game.view.bosses.mini_boss_greebles import hazard
from game.view.bosses.mini_boss_mechanism import conduit
from game.view.bosses.mini_boss_shapes import SHADE, H, offset
from game.view.bosses.world_4.ash_plains_soot import (
    EMBER,
    ash_drift,
    molten_seam,
    soot_streaks,
)
from game.view.bosses.world_4.geyser_rig_parts import DECK_Y, RIG_YELLOW
from game.view.bosses.world_4.living_forge import (
    SKIN,
    back_ribs,
    glands,
    magma_vein,
)
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.organic import RibSpec
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The plating lies on the deck, `PLATE` thick: its top is where its dressing stands.
PLATE = 1.5
TOP = DECK_Y + PLATE
# The back plating over the stern of the deck (its config outline is this one, Z reversed).
BACK: list[OutlinePoint] = [
    [-27, -26],
    [27, -26],
    [27, -70],
    [-27, -70],
]
# A wing plate (the +X one; the other is its mirror), inset from the deck's edge so the yellow
# strip along the deck's side stays in sight beside it.
WING: list[OutlinePoint] = [
    [14, -4],
    [41, -4],
    [41, 28],
    [29, 37],
    [14, 37],
]
# The squat cooling tower aft (a lathe profile, from the plating up), around its centre.
COOLING_TOWER = [
    [10.0, 0.0],
    [8.2, 5.0],
    [7.2, 9.0],
    [7.6, 12.0],
    [8.4, 14.0],
]
TOWER_AT = [0.0, TOP, -50.0]
# Deck plates on the plating, a little proud of it: worn, lighter metal (x, z, width, depth).
BACK_PLATES = [
    [24.0, -44.0, 12.0, 10.0],
    [-8.0, -36.0, 10.0, 8.0],
]
WING_PLATES = [
    [-20.0, 26.0, 14.0, 10.0],
    [22.0, 28.0, 12.0, 8.0],
]


def plating(p: Any, outline: list[OutlinePoint]) -> None:
    """Draw a plate of scorched hide over `outline`, lying on the deck, `PLATE` thick."""
    p.flesh.bevel_slab(outline, [DECK_Y, DECK_Y + 0.5, TOP], [0, 1], SKIN.dark, None, SKIN.panel)


def plating_pieces(outlines: list[list[OutlinePoint]]) -> list[Any]:
    """Return the pieces a plating over `outlines` bursts into: plates cracked at its own height."""
    most: int = BOSS_LOOK.armour.chunks
    return [piece[0] for piece in plate_pieces(outlines, [DECK_Y, TOP], SKIN.panel, most)]


def deck_plates(hull: Any, plates: list[Any], y: float) -> None:
    """Draw worn metal deck plates, each `[x, z, width, depth]`, lying at height `y`."""
    for plate in plates:
        hull.box(
            [plate[2], 0.3, plate[3]],
            SHADE["edge"],
            Placement([plate[0], y, plate[1]]),
            H.panel,
        )


def _cooling_tower(p: Any) -> None:
    """Draw the cooling tower aft: a squat flared stack, hot metal in its mouth, ash on its rim."""
    hull = p.hull
    neon = p.neon
    p.flesh.lathe(COOLING_TOWER, 10, SKIN.panel, Placement(TOWER_AT), False)
    hull.cylinder(7.6, 0.4, 10, SHADE["soot"], Placement(offset(TOWER_AT, 0, 8, 0)))
    neon.ring(5.6, 1.2, 10, EMBER, Placement(offset(TOWER_AT, 0, 8.2, 0)))
    neon.ring(8.5, 0.6, 10, RIG_YELLOW, Placement(offset(TOWER_AT, 0, 12.6, 0)))
    ash_drift(hull, offset(TOWER_AT, 4, 14, 5), 2.2, 0.6)


def draw_back(p: Any) -> None:
    """Draw the back plating (FB-GEYSER-RIG-15): the shell over the stern of the deck.

    Two bone ribs arch over it; the cooling tower, two glands, two deck plates, ash drifts, soot
    streaks and the molten veins' stern runs lie on it. The missile racks lie folded under it.
    """
    plating(p, BACK)
    back_ribs(p, [-40, -28], RibSpec(30, DECK_Y + 0.8, 2.5, 1))
    _cooling_tower(p)
    deck_plates(p.hull, BACK_PLATES, TOP)
    for s in SIDES:
        magma_vein(p, [[s * 17, TOP + 0.2, -27], [s * 16, TOP + 0.2, -40]], 1.3)
        glands(p, [[s * 22, TOP, -58]], 2, RIG_YELLOW)
        ash_drift(p.hull, [s * 14, TOP, -62], 3, s * 2.4)
        soot_streaks(
            p.hull,
            [
                [[s * 26, -38], [s * 30, -56]],
                [[s * 18, -28], [s * 14, -46]],
            ],
            TOP,
            2,
        )


def _pipe_rack(hull: Any, s: float) -> None:
    """Draw the pipe rack along the `s` side: two pipes on trestles, a valve wheel.

    Two trestles stand on the wing plate, the stern one on the deck behind it.
    """
    for z in [16, -2]:
        hull.box([7, 3, 1.6], H.dark, Placement([s * 35, TOP, z]))
    hull.box([7, 3, 1.6], H.dark, Placement([s * 35, DECK_Y, -18]))
    for dx in [-1.8, 1.8]:
        conduit(hull, [s * (35 + dx), TOP + 3.1, 20], [s * (35 + dx), TOP + 3.1, -21], 1.1, 4)
    hull.cylinder(2.4, 0.6, 8, SHADE["edge"], Placement([s * 35, TOP + 4.5, 4]))


def draw_wings(p: Any) -> None:
    """Draw the wing plates (FB-GEYSER-RIG-17), both sides: a plate on the deck under the pipe rack.

    The pipe rack, hazard paint, a molten seam, a deck plate and an ash drift lie on each. The ring
    emitters lie folded under them.
    """
    hull = p.hull
    deck_plates(hull, WING_PLATES, TOP)
    for s in SIDES:
        plating(p, WING if s > 0 else flip_x(WING))
        _pipe_rack(hull, s)
        hazard(hull, [s * 33, TOP, 33], [14, 4], 5, s * 0.75)
        molten_seam(p, [s * 30, 12], [s * 37, -3], TOP)
        ash_drift(hull, [s * 36, TOP, 10], 3.4, s * 1.1)


# The regions' drawings (`drawing.armour`): their whole plating, and the plates it bursts into.
GEYSER_RIG_ARMOUR = {
    "back": {"whole": draw_back, "pieces": plating_pieces([BACK])},
    "wings": {"whole": draw_wings, "pieces": plating_pieces([WING, flip_x(WING)])},
}
