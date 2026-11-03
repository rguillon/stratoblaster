# Copyright (c) 2026 Renaud Guillon
"""MB-EMBER-HERALD-11, 4-5: the Ember Herald's back plating, the armour it sheds (D-254).

Logical pixels, nose +Z, Y up (towards the camera). A dome over the tail half of the fuselage, which
is flattened to a deck under it (`ember_herald_model.DECK`), soot-black on its back from the
reactors' heat, with the dorsal spikes, the vents and the ridge seams on it.
"""

from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.mini_boss_shapes import H
from game.view.bosses.world_4.ember_herald_parts import spike
from game.view.bosses.world_4.living_forge import SKIN
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The dome (loft stations: z, half width, bottom, top): closed to a point at the tail, as wide as
# the fuselage was (a little wider over the orbs, which lie under it), its front end against the
# fuselage where it rises to its full height again. The config's `back` outline follows it.
DOME_FOOT = 2.3
DOME = [
    [-56.0, 0.0, DOME_FOOT, DOME_FOOT],
    [-52.0, 6.5, DOME_FOOT, 6.4],
    [-40.0, 10.5, DOME_FOOT, 9.5],
    [-26.0, 12.0, DOME_FOOT, 10.6],
    [-14.0, 12.0, DOME_FOOT, 11.0],
    [-9.0, 11.0, DOME_FOOT, 10.9],
    [-6.0, 10.6, DOME_FOOT, 10.8],
]
# The dome's section (counter-clockwise seen from the nose): a faceted shell flaring to its foot,
# flat underneath.
DOME_SECTION = [
    [1, 0],
    [0.92, 0.25],
    [0.62, 0.7],
    [0.3, 0.93],
    [0, 1],
    [-0.3, 0.93],
    [-0.62, 0.7],
    [-0.92, 0.25],
    [-1, 0],
]
# The dome's back (its sides between the shoulders) and the bands of `DOME` sooted over it.
BACK_SIDES = [2, 3, 4, 5]
SOOT_BANDS = [1, 2, 3]
# The dorsal spikes down its back, leaning aft: z and size.
SPIKES = [
    [-22.0, 3.0],
    [-30.0, 3.6],
    [-38.0, 3.0],
]


def _soot_paint(side: int, band: int) -> Any:
    """Paint the soot over the dome's back behind the canopy, from the reactors' heat."""
    if side in BACK_SIDES and band in SOOT_BANDS:
        return SKIN.dark
    return None


def draw_plating(p: Any) -> None:
    """Draw the back plating (MB-EMBER-HERALD-11): the armour it sheds at its transformation.

    A dome over the flattened tail of the fuselage, sooted on its back, the dorsal spikes leaning
    aft down it, a vent either side and the dark seams along its ridge.
    """
    hull = p.hull
    p.flesh.loft(DOME_SECTION, DOME, SKIN.base, None, LoftOptions(False, _soot_paint))
    for i in range(len(SPIKES)):
        z = SPIKES[i][0]
        size = SPIKES[i][1]
        spike(p, [0, 9.8 - i * 0.6, z], [-0.7, 0, 0], [size * 0.5, size * 2.6])
    for s in SIDES:
        vent(hull, [s * 5.5, 8.7, -32], [4, 8], 3, 0)
    seam(hull, [0, -40], [0, -16], [10.6, 0.8, 0.4], H.dark)
    seam(hull, [0, -48], [0, -40], [8.6, 0.8, 0.4], H.dark)
