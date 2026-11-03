# Copyright (c) 2026 Renaud Guillon
"""The Harbour Kraken's armour (FB-HARBOUR-KRAKEN-07, 2-2): the plating it sheds, drawn apart.

Its ridged shell (`SHELL`, a segmented body over the mantle) is lofted in three sections (D-254):
the stub under the head stays with the core, the section ahead of the head is the `back` region's
armour with the forecastle, the section behind it the `wings` region's. Logical pixels, nose +Z,
Y up (towards the camera).
"""

from game.view.bosses.mini_boss_greebles import plate, rect
from game.view.bosses.mini_boss_shapes import H
from game.view.bosses.world_2.fjord_lynx_frost import RIME, snow_cap
from game.view.bosses.world_2.harbour_kraken_cranes import DECK_Y, ORANGE_NEON
from game.view.bosses.world_2.loft_spans import shifted_paint, span_of
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals, gland, glow_vein
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import SHELL_SECTION, SegmentedBody, segment_stations
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


# The shell over the mantle: a swollen segmented body of graphite plates, its bottom just under the
# deck's level (the frame a shed section leaves lies 0.6 over the armour's lowest point, and must
# clear the mantle's top at `DECK_Y`).
SHELL_BOTTOM = DECK_Y - 0.2
SHELL = SegmentedBody(-64, 46, 6, 22, SHELL_BOTTOM, 11, 0.12)
SHELL_STATIONS = segment_stations(SHELL)
# Where the head stands on the shell: the section the core keeps. The armour's sections overlap
# it by `OVERLAP` so no seam shows at rest.
HEAD_SPAN = [-14, 17]
OVERLAP = 0.2
# The forecastle, raised over the bow (right half), and its top.
FORECASTLE = [  # type: list[list[float]]
    [0, 72],
    [9, 68],
    [19, 54],
    [22, 48],
    [0, 48],
    [-22, 48],
    [-19, 54],
    [-9, 68],
]
FORECASTLE_TOP = 8
# Hatch covers past this z (the bow cover) are nudged over by 2 instead of 3.
FRONT_COVER_Z = 20
# The glowing veins from the head to the stern: their ends, where the three sections meet.
VEIN = [  # type: list[list[float]]
    [8, 11, 30],
    [10.9, 9.9, HEAD_SPAN[1]],
    [17.9, 7.15, HEAD_SPAN[0]],
    [26, DECK_Y + 1, -50],
]


def _shell_paint(_side: int, band: int) -> Any:
    """Return the shell's dark seam on every other plate (as `carapace` paints it)."""
    return ICE_FLESH.seam if band % 2 == 1 else None


def shell_section(p: EnemyParts, z0: float, z1: float) -> None:
    """Draw the shell's plates from `z0` to `z1` (FB-HARBOUR-KRAKEN-02), a section of `SHELL`."""
    span = span_of(SHELL_STATIONS, z0, z1)
    paint = shifted_paint(_shell_paint, span[1])
    p.flesh.loft(SHELL_SECTION, span[0], ICE_FLESH.graphite, None, LoftOptions(False, paint))


def vein(p: EnemyParts, k: int) -> None:
    """Draw the `k`-th length of the glowing veins (both sides), between two of `VEIN`'s points."""
    a = VEIN[k]
    b = VEIN[k + 1]
    for s in SIDES:
        glow_vein(p, [s * a[0], a[1], a[2]], [s * b[0], b[1], b[2]], 1.2, ORANGE_NEON)


def hatch_cover(p: EnemyParts, z: float) -> None:
    """Add a hatch cover on the deck at `z` (FB-HARBOUR-KRAKEN-02): a frosted, rimed lid."""
    # Armour plates grafted on the shell.
    p.hull.bevel_slab(
        rect(26, 12),
        [DECK_Y - 0.2, DECK_Y, DECK_Y + 2],
        [0, 1],
        H.panel,
        Placement([0, 0, z]),
        RIME,
    )
    snow_cap(p.flesh, rect(18, 7), DECK_Y + 2, Placement([2 if z > FRONT_COVER_Z else -3, 0, z]))


def back_armour(p: EnemyParts) -> None:
    """Draw the fore plating (FB-HARBOUR-KRAKEN-07, region `back`): the shell ahead of the head.

    Its plates from the head's front to its nose, the forecastle of sinew over the bow with its
    metal plate and snow cap, the bow hatch cover with its gland, and the veins' first length. The
    gatlings lie folded under it.
    """
    shell_section(p, HEAD_SPAN[1] - OVERLAP, SHELL.nose)
    p.flesh.bevel_slab(
        FORECASTLE,
        [SHELL_BOTTOM, DECK_Y, FORECASTLE_TOP],
        [0, 1],
        ICE_FLESH.sinew,
        None,
        ICE_FLESH.rime,
    )
    plate(p.hull, rect(14, 8), [FORECASTLE_TOP, 0.6], H.panel, Placement([0, 0, 56]))
    snow_cap(
        p.flesh,
        [
            [-12, 62],
            [12, 62],
            [17, 52],
            [-17, 52],
        ],
        FORECASTLE_TOP,
    )
    hatch_cover(p, 40)
    gland(p, [-10, DECK_Y + 2.4, 40], 1.4, ORANGE_NEON)
    vein(p, 0)


def wings_armour(p: EnemyParts) -> None:
    """Draw the aft plating (FB-HARBOUR-KRAKEN-07, region `wings`): the shell behind the head.

    Its plates from the head's rear to its tail, the aft hatch cover, crystals on the shell and the
    veins' last length. The batteries lie folded under its flanks.
    """
    shell_section(p, SHELL.tail, HEAD_SPAN[0] + OVERLAP)
    hatch_cover(p, -20)
    for s in SIDES:
        crystals(p.flesh, [s * 16, 10, -40], 4)
    vein(p, 2)
