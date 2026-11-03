# Copyright (c) 2026 Renaud Guillon
"""MB-CINDER-CRAB-13, 4-1: the Cinder Crab's carapace and the flank plating it sheds (D-254).

Logical pixels, nose +Z, Y up (towards the camera). The carapace's body has a flat top and, outside
it, a low skirt out to the chine; the flank plating, the armour it sheds at its transformation, is
a wedge of shell either side from the chine up the carapace's old slope to the edge of its top,
resting on the skirt, with the orange neon stripe along its slope. It bursts into its bands.
"""

from game.view.bosses.world_4.cinder_crab_parts import CRAB_ORANGE
from game.view.bosses.world_4.living_forge import SKIN
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES, side_stripe
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The carapace (loft stations, tail to front: z, half width, bottom, top): wide and low.
CARAPACE = [
    [-32.0, 14.0, 1.0, 4.0],
    [-25.0, 32.0, -1.0, 8.0],
    [-12.0, 45.0, -2.0, 11.0],
    [2.0, 48.0, -2.0, 12.0],
    [14.0, 40.0, -1.0, 10.0],
    [20.0, 26.0, 0.0, 7.5],
    [24.0, 12.0, 1.0, 4.0],
]
# The body's section (counter-clockwise seen from the nose): the carapace's flat top (out to
# `TOP_U` of the half width) and, outside it, the skirt the plating rests on, out to the chine. The
# plating's section is the wedge from the chine up the old slope to the top's edge, sunk a little
# into the skirt; the config's `flanks` outline follows `TOP_U` and the half widths of `CARAPACE`.
TOP_U = 0.6
SKIRT_U = 0.7
SKIRT_V = 0.46
BODY_SECTION = [
    [0.55, 0],
    [1, 0.4],
    [SKIRT_U, SKIRT_V],
    [TOP_U, 1],
    [-TOP_U, 1],
    [-SKIRT_U, SKIRT_V],
    [-1, 0.4],
    [-0.55, 0],
]
PLATE_SECTION = [
    [1, 0.4],
    [TOP_U, 1],
    [SKIRT_U, SKIRT_V - 0.02],
]
# The bands of the carapace the orange flank stripe runs along (`CARAPACE[1:6]`).
STRIPE_BANDS = [1, 4]


def mirrored_section(section: list[Any]) -> list[Any]:
    """Return `section` mirrored across the centre line, keeping its winding."""
    n = len(section)
    return [[-section[n - 1 - k][0], section[n - 1 - k][1]] for k in range(n)]


def _plate_piece(s: float, k: int) -> Any:
    """Return the piece of the flank plating on side `s` over band `k` of the carapace.

    A wedge of shell (the bands alternate shades, as the body's), with its length of the orange
    neon stripe along its slope.
    """

    def draw(p: Any) -> None:
        stations = CARAPACE[k : k + 2]
        p.flesh.loft(
            PLATE_SECTION if s > 0 else mirrored_section(PLATE_SECTION),
            stations,
            SKIN.base if k % 2 == 0 else SKIN.dark,
        )
        if STRIPE_BANDS[0] <= k <= STRIPE_BANDS[1]:
            p.neon.loft(
                side_stripe(HULL_SECTION, 1 if s > 0 else 3, [0.15, 0.4], 1.03),
                stations,
                CRAB_ORANGE,
                None,
                LoftOptions(True, None),
            )

    return draw


# The pieces the flank plating bursts into: its bands, either side.
PLATE_PIECES = [_plate_piece(s, k) for s in SIDES for k in range(len(CARAPACE) - 1)]


def draw_plating(p: Any) -> None:
    """Draw the flank plating whole (MB-CINDER-CRAB-13): all its pieces, in place."""
    for piece in PLATE_PIECES:
        piece(p)
