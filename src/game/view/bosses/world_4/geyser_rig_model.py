"""P10-R11, 4-2: the Geyser Rig. Ported from `bosses/world-4/geyser-rig-model.ts`. Logical pixels,
nose
+Z, Y up (towards the camera). A flying drilling platform: a heavy deck, a lattice derrick in its
middle (the core), two drill arms reaching forward from its bow corners, two steam vents at its
stern,
a drone hangar jutting from its bow and a squat cooling tower aft. P16-R06: a living rock-tick, its
back a scorched flesh shell veined molten, a bone spire over its core, its drills, pipes and guns
metal grafts.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.geyser_rig import GEYSER_RIG, RIG_CORE_GUNS  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_shapes import mirrored, strip  # noqa: E402
from game.view.bosses.mini_boss_greebles import hazard, lamps, vent  # noqa: E402
from game.view.bosses.mini_boss_mechanism import conduit  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset  # noqa: E402
from game.view.bosses.world_3.toucan_jungle import segment  # noqa: E402
from game.view.bosses.world_4.ash_plains_soot import (  # noqa: E402
    EMBER,
    SCORCH,
    ash_drift,
    molten_seam,
    soot_streaks,
)
from game.view.bosses.world_4.geyser_rig_parts import (  # noqa: E402
    DECK_Y,
    RIG_YELLOW,
    arm_limbs,
    drill_head,
    hangar,
    steam_vent,
)
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type OutlinePoint = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The deck seen from above (right half, bow to stern), its stern corners cut.
DECK = mirrored(
    [
        [0, 38],
        [30, 38],
        [44, 26],
        [44, -54],
        [34, -70],
        [0, -70],
    ]
)

# The derrick's corner posts: their foot on the deck and their top, half spread (x = z).
DERRICK_FOOT = 9
DERRICK_TOP = 3
DERRICK_HEIGHT = 42
# The squat cooling tower aft (a lathe profile, from the deck up), around its centre.
COOLING_TOWER = [
    [10.0, 0.0],
    [8.2, 5.0],
    [7.2, 9.0],
    [7.6, 12.0],
    [8.4, 14.0],
]
TOWER_AT = [0.0, DECK_Y, -50.0]


def _pipe_rack(hull: Any, s: float) -> None:
    """The pipe rack along the `s` side of the deck: two pipes on trestles, a valve wheel."""
    for z in [16, -2, -18]:
        hull.box([7, 3, 1.6], H.dark, Placement([s * 35, DECK_Y, z]))
    for dx in [-1.8, 1.8]:
        conduit(hull, [s * (35 + dx), DECK_Y + 3.6, 20], [s * (35 + dx), DECK_Y + 3.6, -21], 1.1, 4)
    hull.cylinder(2.4, 0.6, 8, SHADE["edge"], Placement([s * 35, DECK_Y + 5, 4]))


# Deck plates, a little proud of the deck: worn, lighter metal.
PLATES = [
    [-20.0, 26.0, 14.0, 10.0],
    [22.0, 28.0, 12.0, 8.0],
    [-26.0, -14.0, 10.0, 14.0],
    [24.0, -44.0, 12.0, 10.0],
    [-8.0, -36.0, 10.0, 8.0],
]


def _deck_veins(p: Any, s: float) -> None:
    """P16-R05, P16-R06: its living flesh: veins, glands and ribs."""
    magma_vein(
        p,
        [
            [s * 8, DECK_Y + 0.2, 22],
            [s * 20, DECK_Y + 0.2, 4],
            [s * 16, DECK_Y + 0.2, -40],
        ],
        1.3,
    )
    glands(
        p,
        [
            [s * 28, DECK_Y, -44],
            [s * 6, DECK_Y, 30],
        ],
        2,
        RIG_YELLOW,
    )


def _draw_deck(p: Any) -> None:
    """The deck: dark bevelled plates, yellow neon along its sides, hazard paint, ash and soot."""
    hull = p.hull
    neon = p.neon
    p.flesh.bevel_slab(DECK, [0, 3, DECK_Y], [2, 1.5], SKIN.base, None, SKIN.dark)
    back_ribs(p, [-40, -28, 28], RibSpec(30, DECK_Y - 2, 3.5, 1))
    for s in SIDES:
        _deck_veins(p, s)
        strip(neon, [s * 41.6, 22], [s * 41.6, -52], 0.8, [DECK_Y, DECK_Y + 0.4], RIG_YELLOW)
        _pipe_rack(hull, s)
        hazard(hull, [s * 33, DECK_Y, 33], [14, 4], 5, s * 0.75)
        soot_streaks(
            hull,
            [
                [
                    [s * 26, -38],
                    [s * 30, -56],
                ],
                [
                    [s * 18, -20],
                    [s * 14, -42],
                ],
            ],
            DECK_Y,
            2,
        )
        molten_seam(p, [s * 12, 4], [s * 24, -14], DECK_Y)
        molten_seam(p, [s * 30, 12], [s * 38, -6], DECK_Y)
        vent(hull, [s * 22, DECK_Y, -2], [6, 9], 3)
        ash_drift(hull, [s * 36, DECK_Y, 10], 3.4, s * 1.1)
        ash_drift(hull, [s * 14, DECK_Y, -62], 3, s * 2.4)
        conduit(hull, [s * 27, DECK_Y + 2, -30], [s * 8, DECK_Y + 2, -12], 1.3, 3)
    reactor_sacs(
        p,
        [
            [18, 3.6, -68],
            [-18, 3.6, -68],
        ],
        3.2,
        EMBER,
    )
    reactor_sacs(p, [[0, 3.6, -70]], 3.6, EMBER)
    for plate in PLATES:
        hull.box(
            [plate[2], 0.3, plate[3]],
            SHADE["edge"],
            Placement([plate[0], DECK_Y, plate[1]]),
            H.panel,
        )


def _derrick_point(x: float, z: float, k: float) -> Vec3:
    """A corner post's point at height fraction `k`, its spread narrowing to the top."""
    spread = DERRICK_FOOT + (DERRICK_TOP - DERRICK_FOOT) * k
    return [x * spread, DECK_Y + 3 + DERRICK_HEIGHT * k, z * spread]


def _draw_derrick(p: Any) -> None:
    """The derrick (the core): a lattice tower of four posts braced crosswise, its crown block lit
    yellow, the drill pipe glowing hot down its middle."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    hull.box([26, 3, 26], H.panel, Placement([0, DECK_Y, 0]), SCORCH)
    # P16-R06: a spire of bone, braced by sinews.
    corners = [
        [1, 1],
        [1, -1],
        [-1, -1],
        [-1, 1],
    ]
    for i in range(len(corners)):
        x = corners[i][0]
        z = corners[i][1]
        nxz = corners[(i + 1) % 4]
        nx = nxz[0]
        nz = nxz[1]
        segment(flesh, [_derrick_point(x, z, 0), _derrick_point(x, z, 1)], [1.4, 0.8], SKIN.bone, 4)
        segment(
            flesh,
            [_derrick_point(x, z, 0.08), _derrick_point(nx, nz, 0.45)],
            [0.5, 0.5],
            SKIN.panel,
            4,
        )
        segment(
            flesh,
            [_derrick_point(nx, nz, 0.08), _derrick_point(x, z, 0.45)],
            [0.5, 0.5],
            SKIN.panel,
            4,
        )
        segment(
            flesh,
            [_derrick_point(x, z, 0.45), _derrick_point(nx, nz, 0.8)],
            [0.4, 0.4],
            SKIN.panel,
            4,
        )
    hull.box([9, 4, 9], H.panel, Placement([0, DECK_Y + 3 + DERRICK_HEIGHT, 0]), H.base)
    neon.ring(5, 0.8, 8, RIG_YELLOW, Placement([0, DECK_Y + 4 + DERRICK_HEIGHT, 0], math.pi / 8))
    lamps(neon, [[0, DECK_Y + 7.4 + DERRICK_HEIGHT, 0]], 1.6, EMBER)
    neon.cylinder(1.1, DERRICK_HEIGHT, 6, EMBER, Placement([0, DECK_Y + 3, 0]))


def _draw_gun_house(p: Any) -> None:
    """The drill floor's house at the derrick's foot, its twin fan guns pointing forward."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    hull.box([28, 8, 13], H.base, Placement([0, DECK_Y, 14]), H.panel)
    strip(neon, [-12, 20.6], [12, 20.6], 0.7, [DECK_Y + 6.4, DECK_Y + 7.2], RIG_YELLOW)
    for m in RIG_CORE_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(2.6, 2, 6, H.dark, Placement([x, y, z - 5], 0, QUARTER))
        hull.cylinder(1.4, 3.4, 6, H.dark, Placement([x, y, z - 4], 0, QUARTER))
        charge.cylinder(1.45, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


def _draw_cooling_tower(p: Any) -> None:
    """The cooling tower aft: a squat flared stack, hot metal glowing in its mouth, ash on its
    rim."""
    hull = p.hull
    neon = p.neon
    p.flesh.lathe(COOLING_TOWER, 10, SKIN.panel, Placement(TOWER_AT), False)
    hull.cylinder(7.6, 0.4, 10, SHADE["soot"], Placement(offset(TOWER_AT, 0, 8, 0)))
    neon.ring(5.6, 1.2, 10, EMBER, Placement(offset(TOWER_AT, 0, 8.2, 0)))
    neon.ring(8.5, 0.6, 10, RIG_YELLOW, Placement(offset(TOWER_AT, 0, 12.6, 0)))
    ash_drift(hull, offset(TOWER_AT, 4, 14, 5), 2.2, 0.6)


def build_geyser_rig(scene: Any) -> Any:
    """P10-R11: the Geyser Rig, a flying drilling rig with two drill heads and steam vents, yellow
    neon, soot, ash and molten seams on its deck."""

    def core(p: Any) -> None:
        _draw_deck(p)
        _draw_derrick(p)
        _draw_gun_house(p)
        _draw_cooling_tower(p)

    return build_boss_model(
        GEYSER_RIG,
        scene,
        RIG_YELLOW,
        {
            "core": core,
            "parts": {
                "drill-left": drill_head,
                "drill-right": drill_head,
                "vent-left": steam_vent,
                "vent-right": steam_vent,
                "hangar": hangar,
            },
            "limbs": arm_limbs(),
        },
    )
