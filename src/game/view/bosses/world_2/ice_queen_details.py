"""The Ice Queen's details (P08-R10, 2-5): its crystal canopy, its engine nacelles, the crystal
fins at its tail, frosted plates and lights on its wings, ported from
`bosses/world-2/ice-queen-details.ts`. Logical pixels, nose +Z, Y up.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.mini_boss_greebles import lamps, plate
from game.view.bosses.mini_boss_shapes import QUARTER, H
from game.view.bosses.world_2.ice_queen_shards import FROST, PALE_BLUE, VIOLET, crystal, icicles
from game.view.bosses.world_2.w2_organic import ICE_FLESH, gland, glow_vein
from game.view.enemies.enemy_shapes import CANOPY_SECTION, POD_SECTION, SIDES, flip_x
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The crystal canopy on the fuselage's back (loft stations), closing to a point at the front.
CANOPY = [  # type: list[list[float]]
    [14, 3.6, 6.5, 11.4],
    [27, 3.4, 5, 10.8],
    [37, 2.2, 4.3, 8.4],
    [44, 0, 5.8, 5.8],
]
# An engine nacelle on a wing root (loft stations), its back snowed over.
NACELLE = [  # type: list[list[float]]
    [-53, 2.4, 0.4, 5],
    [-44, 3.2, 0, 5.6],
    [-26, 2.8, 0.4, 5],
    [-14, 0, 2.6, 2.6],
]
NACELLE_X = 12.5
NACELLE_BACK = 2

# The frosted armour plates on the right wing (+X), and its underwing crystal pod.
WING_PLATES = [  # type: list[list[list[float]]]
    [
        [10, 8],
        [22, -6],
        [22, -16],
        [10, -10],
    ],
    [
        [26, -10],
        [38, -22],
        [38, -28],
        [26, -22],
    ],
]
POD = [  # type: list[list[float]]
    [0, -7],
    [1.6, -3],
    [1.8, 3],
    [0, 8],
]


# The sides of the canopy that are pale (its shoulders).
CANOPY_SHOULDERS = [1, 2]


def _canopy_paint(side: int, band: int) -> Rgb | None:
    """The canopy's paint: pale on its two shoulders."""
    if side in CANOPY_SHOULDERS:
        pale: Rgb = FROST.pale
        return pale
    return None


def _nacelle_paint(side: int, band: int) -> Rgb | None:
    """The nacelle's paint: frosted on its back."""
    if side == NACELLE_BACK:
        rime: Rgb = ICE_FLESH.rime
        return rime
    return None


def _draw_canopy(p: EnemyParts) -> None:
    """The crystal canopy and the nose's sensor crystal."""
    hull = p.hull
    neon = p.neon
    hull.loft(
        CANOPY_SECTION,
        CANOPY,
        FROST.ice,
        None,
        LoftOptions(False, _canopy_paint),
    )
    neon.box([0.4, 0.4, 20], VIOLET, Placement([0, 11.3, 22], 0, -0.03))
    crystal(hull, [0, 2.6, 56], [QUARTER, 0, 0], [1.1, 6])


def _draw_nacelles(p: EnemyParts) -> None:
    """The engine nacelles on the wing roots: snowed backs, pale blue strips along their sides."""
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        at: Vec3 = [s * NACELLE_X, 0, 0]
        # P16-R05: swollen engine sacs of flesh on the wing roots.
        flesh.loft(
            POD_SECTION,
            NACELLE,
            ICE_FLESH.teal,
            Placement(at),
            LoftOptions(False, _nacelle_paint),
        )
        neon.box([0.4, 0.6, 20], PALE_BLUE, Placement([s * (NACELLE_X + 3.3), 2.4, -36]))
        glow_vein(p, [s * NACELLE_X, 5.6, -46], [s * NACELLE_X, 5.4, -22], 0.7, VIOLET)


def _draw_crystals(p: EnemyParts) -> None:
    """The crystal fins leaning back at the tail, and low crystals along the spine (under the
    crown ring and its spokes as they turn)."""
    hull = p.flesh
    for s in SIDES:
        crystal(hull, [s * 4.5, 7, -44], [-0.8, -0.35 * s, 0], [2.2, 13])
        crystal(hull, [s * 3, 8.4, -26], [-0.5, -0.6 * s, 0], [1.3, 3.5])
        crystal(hull, [s * 6.5, 8.6, -6], [-0.3, -0.9 * s, 0], [1.2, 3.2])
    crystal(hull, [0, 6.2, -50], [-0.6, 0, 0], [1.6, 8])


def _draw_wing_detail(p: EnemyParts) -> None:
    """Frosted plates, seams and a vent on the wings, lights at their tips, crystal pods under
    them."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        for outline in WING_PLATES:
            plate(hull, outline if s > 0 else flip_x(outline), [2.4, 0.5], FROST.frosted)
        gland(p, [s * 18, 2.6, -22], 1, PALE_BLUE)
        lamps(neon, [[s * 47, 2.6, -32]], 1.4, VIOLET)
        lamps(neon, [[s * 14.5, 3.6, 24]], 1, PALE_BLUE)
        flesh.lathe(POD, 6, ICE_FLESH.membrane, Placement([s * 30, -0.6, -14], 0, QUARTER))
        hull.box([1.2, 1.4, 6], H.dark, Placement([s * 30, -0.2, -14]))
        icicles(flesh, s, [[6, 24], [10, 23]])


def draw_details(p: EnemyParts) -> None:
    """The Ice Queen's details (P08-R10), on its core body."""
    _draw_canopy(p)
    _draw_nacelles(p)
    _draw_crystals(p)
    _draw_wing_detail(p)
