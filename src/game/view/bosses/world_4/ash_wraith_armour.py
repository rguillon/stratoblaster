# Copyright (c) 2026 Renaud Guillon
"""MB-ASH-WRAITH-12, 4-2: the Ash Wraith's back plating, the armour it sheds (D-254).

Logical pixels, nose +Z, Y up (towards the camera). A faceted dome over the fuselage, flattened to
a deck under it (`ash_wraith_model.DECK`), with the dark canopy painted on its back, the glands and
the ridge light on it, the vents and the scorched flank strips on its sides.
"""

from game.view.bosses.final_boss_shapes import strip
from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.world_4.ash_wraith_parts import WRAITH_CYAN
from game.view.bosses.world_4.living_forge import SKIN, glands
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The dome (loft stations: z, half width, bottom, top): its foot sunk into the wing's top (3 px),
# closed to a point at both ends, as wide as the fuselage was (the lances lie under it). The
# config's `back` outline follows its stations.
DOME_FOOT = 2.8
DOME = [
    [-30.0, 0.0, DOME_FOOT, DOME_FOOT],
    [-26.0, 5.5, DOME_FOOT, 5.6],
    [-14.0, 10.5, DOME_FOOT, 8.4],
    [-2.0, 13.5, DOME_FOOT, 10.0],
    [8.0, 13.5, DOME_FOOT, 9.2],
    [16.0, 10.0, DOME_FOOT, 7.4],
    [22.0, 5.0, DOME_FOOT, 4.8],
    [25.0, 0.0, DOME_FOOT, DOME_FOOT],
]
# The dome's section (counter-clockwise seen from the nose): a faceted shell with a flat underside.
DOME_SECTION = [
    [1, 0],
    [0.86, 0.3],
    [0.55, 0.7],
    [0, 1],
    [-0.55, 0.7],
    [-0.86, 0.3],
    [-1, 0],
]
# The dark glass of its canopy: on the dome's back (its sides between the shoulders), over the
# bands `CANOPY_BANDS` of `DOME`.
CANOPY_GLASS = [0.03, 0.05, 0.06]
CANOPY_SIDES = [1, 2, 3, 4]
CANOPY_BANDS = [3, 4, 5]


def _canopy_paint(side: int, band: int) -> Any:
    """Paint the canopy's dark glass on the back of the dome's middle bands."""
    if side in CANOPY_SIDES and band in CANOPY_BANDS:
        return CANOPY_GLASS
    return None


def draw_plating(p: Any) -> None:
    """Draw the back plating (MB-ASH-WRAITH-12): the armour it sheds at its transformation.

    A faceted dome over the flattened fuselage, its dark canopy painted on it, the glands and the
    ridge light on its back, the vents and the scorched flank strips on its sides.
    """
    hull = p.hull
    neon = p.neon
    p.flesh.loft(DOME_SECTION, DOME, SKIN.base, None, LoftOptions(False, _canopy_paint))
    glands(
        p,
        [
            [0, 9.6, -4],
            [0, 9.0, 6],
        ],
        1.2,
        WRAITH_CYAN,
    )
    strip(neon, [0, 8], [0, -4], 0.6, [9.4, 9.8], WRAITH_CYAN)
    for s in SIDES:
        vent(hull, [s * 4.5, 7.4, -12], [3, 6], 3, s * 0.15)
        strip(neon, [s * 10.6, 2], [s * 9.2, -10], 0.6, [5.4, 6.0], WRAITH_CYAN)
