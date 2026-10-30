"""P10-R11, 4-5: the Caldera Throne, World 4's last boss. Model space: logical pixels, nose +Z (down
the screen), Y
up towards the camera; +X is the screen's left. A war fortress: an armoured hull carrying a stepped
keep over the core, a prow gun deck, side bastions out to the magma cannons, missile batteries and
smokestacks aft. P16-R06: a living tyrant of the caldera, its vast flesh back ribbed in bone and
veined with magma, a keep of flesh and armour rising over its heart, crowned in metal and gold.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.caldera_throne import (  # noqa: E402
    CALDERA_GUNS,
    CALDERA_HATCHES,
    CALDERA_LENS,
    CALDERA_THRONE,
)
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_greebles import grille, hazard, plate, rect  # noqa: E402
from game.view.bosses.final_boss_mechanism import glow_line  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H  # noqa: E402
from game.view.bosses.overlord_city import edge_lights, symmetric  # noqa: E402
from game.view.bosses.world_4.caldera_throne_keep import draw_keep  # noqa: E402
from game.view.bosses.world_4.caldera_throne_parts import (  # noqa: E402
    BASTION_TOP,
    CRIMSON,
    DECK_TOP,
    GOLD,
    HEAT,
    magma_cannon,
    magma_mount,
    missile_battery,
    shield_generator,
)
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import SIDES, decal, flip_x  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type OutlinePoint = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The hull (right half, front to tail), closed across the prow.
HULL = symmetric(
    [
        [14, 94],
        [30, 80],
        [46, 58],
        [58, 34],
        [64, 8],
        [66, -20],
        [62, -52],
        [52, -78],
        [36, -96],
        [16, -102],
    ],
    100,
)
# The right bastion (mirrored on the left), out to the magma cannon's turntable.
BASTION = [
    [58.0, 36.0],
    [90.0, 28.0],
    [104.0, 18.0],
    [104.0, -2.0],
    [90.0, -12.0],
    [60.0, -22.0],
]
# The engine block across the stern.
ENGINES = rect([0, -96], [72, 12])
# The prow's gun deck, and its top.
PROW = rect([0, 78], [30, 30])
PROW_TOP = 14
# The block the core's missile hatches open in, behind the keep.
HATCH_BLOCK = rect([0, -63], [28, 22])
LENS = [
    [0.0, 0.0],
    [3.8, 1.0],
    [2.6, 3.0],
    [0.0, 4.0],
]
# The molten seams across the deck (right half, `[x, z]` from and to).
SEAMS = [
    [
        [40.0, 30.0],
        [56.0, 6.0],
    ],
    [
        [42.0, -24.0],
        [58.0, -46.0],
    ],
    [
        [14.0, 52.0],
        [22.0, 40.0],
    ],
    [
        [30.0, -84.0],
        [46.0, -70.0],
    ],
]
# Armour plates on the deck (right half): centre, size, turn.
PLATES = [
    [48.0, 14.0, 12.0, 20.0, -0.25],
    [50.0, -30.0, 12.0, 22.0, 0.2],
    [20.0, -82.0, 14.0, 10.0, 0.0],
]


def _flipped(outline: Any) -> Any:
    """`flipX` of an outline (enemy_shapes types its points as tuples)."""
    mirrored: Any = flip_x(outline)
    return mirrored


def _along_z(x: float, y: float, z: float) -> Any:
    """A placement at `[x, y, z]`, lying along Z (`{ at, pitch: QUARTER }`)."""
    return Placement([x, y, z], 0, QUARTER)


def _all_edges(outline: list[Any]) -> list[int]:
    """The indices of every edge of an outline."""
    return [i for i in range(len(outline))]


def _draw_hull(p: Any) -> None:
    """The hull with its crimson rim, the engine block, the bastions out to the turntables."""
    hull = p.hull
    neon = p.neon
    p.flesh.bevel_slab(HULL, [-10, -2, DECK_TOP], [3, 3], SKIN.base, None, SKIN.dark)
    back_ribs(p, [-84, -72, 56, 66], RibSpec(44, 3, 6.5, 1.3))
    every = _all_edges(HULL)
    edge_lights(neon, HULL, every, [-2.8, -1.4], CRIMSON)
    edge_lights(neon, HULL, every, [-8.6, -7.8], HEAT["glow"], 0.2)
    hull.bevel_slab(ENGINES, [-8, -1, 6], [1, 1.5], H.dark, None, HEAT["soot"])
    for s in SIDES:
        bastion = BASTION if s > 0 else _flipped(BASTION)
        p.flesh.bevel_slab(bastion, [-5, -1, BASTION_TOP], [1, 2], SKIN.panel, None, SKIN.dark)
        magma_vein(
            p,
            [
                [s * 22, DECK_TOP + 0.3, -46],
                [s * 42, DECK_TOP + 0.3, -20],
                [s * 40, DECK_TOP + 0.3, 30],
            ],
            1.6,
        )
        glands(
            p,
            [
                [s * 50, DECK_TOP - 0.5, -6],
                [s * 36, DECK_TOP, 58],
            ],
            2.6,
            CRIMSON,
        )
        edge_lights(neon, bastion, [0, 1, 2, 3, 4], [-1.4, -0.4], GOLD)
        edge_lights(neon, bastion, [1, 2, 3], [-4.2, -3.6], CRIMSON)


def _draw_deck(p: Any) -> None:
    """The deck's dressing: molten seams, armour plates, vents and hazard bands."""
    hull = p.hull
    neon = p.neon
    for s in SIDES:
        for seam in SEAMS:
            a = seam[0]
            b = seam[1]
            glow_line(
                neon,
                [
                    [s * a[0], a[1]],
                    [s * b[0], b[1]],
                ],
                DECK_TOP - 0.3,
                HEAT["molten"],
            )
        for item in PLATES:
            plate(
                hull,
                rect([s * item[0], item[1]], [item[2], item[3]], s * item[4]),
                DECK_TOP,
                H.panel,
                0.8,
            )
        grille(hull, [s * 30, -40], [10, 12], [4, DECK_TOP + 0.05])
        grille(hull, [s * 44, 40], [8, 10], [3, DECK_TOP + 0.05], s * 0.4)
    hazard(hull, [0, 46], [24, 4], 6, DECK_TOP + 0.05)
    hazard(hull, [0, -80], [30, 4], 7, DECK_TOP + 0.05)


def _draw_prow(p: Any) -> None:
    """The prow's gun deck: twin cannons and a laser lens, charging before they fire."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    hull.bevel_slab(
        PROW, [DECK_TOP - 1, DECK_TOP, PROW_TOP], [0, 1.5], H.panel, None, HEAT["blued"]
    )
    edge_lights(neon, PROW, [0, 1, 2, 3], [PROW_TOP - 2.6, PROW_TOP - 1.8], CRIMSON)
    decal(neon, rect([0, 70], [20, 1.4]), PROW_TOP + 0.05, GOLD)
    front = 92
    for m in CALDERA_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        hull.cylinder(2.4, 6, 6, H.dark, _along_z(tip[0], tip[1], front - 14))
        hull.cylinder(
            1.9, tip[2] - 2 - (front - 8), 6, H.dark, _along_z(tip[0], tip[1], front - 8), 1.6
        )
        charge.cylinder(1.8, 2, 6, WHITE, _along_z(tip[0], tip[1], tip[2] - 2), 1.3)
        muzzle(tip)
    lens = boss_point(CALDERA_LENS[0], CALDERA_LENS[1], CALDERA_LENS[2])
    lens_at = lens[2] - LENS[3][1]
    hull.cylinder(4.6, lens_at - (front - 16), 8, H.base, _along_z(0, lens[1], front - 16), 4)
    neon.ring(4.5, 1.2, 8, HEAT["molten"], _along_z(0, lens[1], lens_at - 6))
    charge.lathe(LENS, 8, WHITE, _along_z(0, lens[1], lens_at))
    muzzle(lens, "laser")


def _draw_hatches(p: Any) -> None:
    """The missile hatches in their block behind the keep, lit as missiles load."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    height = CALDERA_HATCHES[0][2] if len(CALDERA_HATCHES) > 0 else DECK_TOP
    hull.bevel_slab(HATCH_BLOCK, [DECK_TOP - 1, DECK_TOP, height - 0.08], [0, 1], H.base)
    for m in CALDERA_HATCHES:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        decal(hull, rect([x, z], [7, 6]), y - 0.06, H.dark)
        decal(charge, rect([x, z], [5, 4]), y, WHITE)
        muzzle([x, y, z], "missile")
    neon.box([22, 0.8, 0.6], GOLD, Placement([0, DECK_TOP + 1, -51.6]))


def build_caldera_throne(scene: Any) -> Any:
    """P10-R11: the Caldera Throne, the enemy's war fortress rising from the magma lake (6.5 L),
    crimson and gold neon over its whole hull: a stepped keep and throne tower over its core, a prow
    carrying twin cannons and a laser, magma cannons on its bastions, missile batteries and
    smokestacks aft, heat shield generators ahead of the keep."""

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_deck(p)
        draw_keep(p)
        _draw_prow(p)
        _draw_hatches(p)
        for s in SIDES:
            reactor_sacs(p, [[s * 12, -1, -102]], 6, HEAT["molten"])
            reactor_sacs(p, [[s * 28, -1, -102]], 4.5, HEAT["molten"])

    return build_boss_model(
        CALDERA_THRONE,
        scene,
        CRIMSON,
        {
            "core": core,
            "parts": {
                "magma-left": magma_mount,
                "magma-right": magma_mount,
                "battery-left": missile_battery,
                "battery-right": missile_battery,
                "shield-left": shield_generator,
                "shield-right": shield_generator,
            },
            "turrets": {"magma-left": magma_cannon, "magma-right": magma_cannon},
        },
    )
