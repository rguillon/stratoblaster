"""P10-R11, 4-1: the Cinder Crab. Logical pixels,
nose +Z, Y up (towards the camera). A wide, low crab-ship: a soot-black carapace cracked by molten
seams, orange neon along its rim and on its eye stalks, six short legs, arms reaching from under its
front rim to the two claws, the ring dome on its back and the mortar behind it. P16-R05: a living
crab, a scorched flesh shell banded in darker seams, bony legs, glowing eyes on fleshy stalks, metal
grafted on as its belly plate, dome, joints and guns.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.cinder_crab import CINDER_CRAB, CRAB_DOME  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import vent  # noqa: E402
from game.view.bosses.mini_boss_shapes import SHADE, WHITE, H, offset  # noqa: E402
from game.view.bosses.world_4.black_sands_kit import (  # noqa: E402
    FORGE,
    blot,
    bolts,
    molten_seam,
    soot,
    strut,
)
from game.view.bosses.world_4.cinder_crab_parts import (  # noqa: E402
    CRAB_LIMBS,
    CRAB_ORANGE,
    claw,
    mortar,
)
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    MAGMA,
    SKIN,
    back_ribs,
    flesh_shell,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES, side_stripe  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

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
# The legs either side: where along the carapace each hangs (z), and how it is bent.
LEGS = [9.0, -3.0, -15.0]
LEG_HIP = 3
LEG_KNEE = 9
LEG_OUT = 6
LEG_FOOT = 9
LEG_DROP = -3
# The eye stalks at the front: across, along, and how tall.
EYES_X = 6
EYES_Z = 20
EYES_HEIGHT = 13
# The ring dome on its back (a lathe profile around the dome's axis).
DOME = [
    [7.0, 0.0],
    [7.0, 1.4],
    [5.4, 3.2],
    [2.6, 4.2],
    [0.0, 4.4],
]


def _station_at(z: float, k: int) -> float:
    """Linear interpolation of station column `k` of the carapace at `z`."""
    for i in range(1, len(CARAPACE)):
        a = CARAPACE[i - 1]
        b = CARAPACE[i]
        if z > b[0]:
            continue
        return a[k] + ((b[k] - a[k]) * (z - a[0])) / (b[0] - a[0])
    return CARAPACE[len(CARAPACE) - 1][k]


def top_at(z: float) -> float:
    """The carapace's height at `z` (the top of its loft there), for things laid on it."""
    return _station_at(z, 3)


def _width_at(z: float) -> float:
    """The carapace's half width at `z`."""
    return _station_at(z, 1)


def _draw_carapace(p: Any) -> None:
    """The carapace, its orange neon flanks, the belly plate and the reactors."""
    hull = p.hull
    neon = p.neon
    flesh_shell(p.flesh, HULL_SECTION, CARAPACE, [SKIN.base, SKIN.dark])
    for side in [1, 3]:
        neon.loft(
            side_stripe(HULL_SECTION, side, [0.15, 0.4], 1.03),
            CARAPACE[1:6],
            CRAB_ORANGE,
            None,
            LoftOptions(True, None),
        )
    hull.box([44, 2.4, 40], H.dark, Placement([0, -3.4, -6]), H.panel)
    reactor_sacs(
        p,
        [
            [9, 2.5, -33],
            [-9, 2.5, -33],
        ],
        2.4,
        MAGMA,
    )


def _draw_legs(p: Any) -> None:
    """Its six short legs: each bends up at the knee and down to a pointed foot."""
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        for z in LEGS:
            w = _width_at(z)
            hip = [s * (w - 6), LEG_HIP, z]
            knee = [s * (w + LEG_OUT), LEG_KNEE, z - 3]
            foot = [s * (w + LEG_FOOT), LEG_DROP, z - 7]
            strut(flesh, [hip, knee], [2.2, 1.8], SKIN.panel, 5)
            strut(flesh, [knee, foot], [1.8, 0.4], SKIN.bone, 4)
            neon.box([1, 0.6, 1], CRAB_ORANGE, Placement(offset(knee, 0, 1.6, 0)))


def _draw_front(p: Any) -> None:
    """The front: two eye stalks with orange neon tips, a brow plate, the arms' shoulder sockets."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    flesh = p.flesh
    for s in SIDES:
        base = [s * EYES_X, top_at(EYES_Z) - 0.5, EYES_Z]
        flesh.cylinder(1.4, EYES_HEIGHT - base[1], 5, SKIN.panel, Placement(base), 1)
        glands(p, [[s * EYES_X, EYES_HEIGHT + 0.6, EYES_Z + 0.6]], 1.4, CRAB_ORANGE)
        neon.box([2.6, 1.6, 2.6], CRAB_ORANGE, Placement([s * EYES_X, EYES_HEIGHT, EYES_Z]))
        hull.cylinder(4.5, 4, 7, H.dark, Placement([s * 16, -1, 14]), 3.6)
    hull.box([18, 1.4, 3], SHADE["edge"], Placement([0, top_at(16), 16]))
    charge.box([8, 0.4, 1.6], WHITE, Placement([0, top_at(13) + 0.1, 13]))


def _back_flesh(p: Any) -> None:
    """P16-R05, P16-R06: its living flesh: veins, glands and ribs."""
    back_ribs(p, [-20, 1], RibSpec(30, 4, 6.5, 0.9))
    magma_vein(
        p,
        [
            [-24, 7, -16],
            [-10, top_at(-6), -6],
            [10, top_at(-6), -6],
            [24, 7, -16],
        ],
        1.1,
    )
    glands(
        p,
        [
            [-26, 7.5, 3],
            [26, 7.5, 3],
        ],
        1.8,
        MAGMA,
    )


def _draw_back(p: Any) -> None:
    """Its back: molten seams between the plates, soot, bolts, a hot vent and the ring dome."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    _back_flesh(p)
    for z in [-11, 9]:
        y = top_at(z) + 0.05
        half = _width_at(z) * 0.55
        molten_seam(
            neon,
            [
                [-half, z],
                [-half * 0.5, z + 1.5],
                [0, z - 1],
                [half * 0.5, z + 1.2],
                [half, z - 0.5],
            ],
            y,
        )
    soot(hull, blot([14, -4], 5, 0.8, 1), top_at(-4))
    soot(hull, blot([-17, 3], 4, 1.1, 3), top_at(3))
    soot(hull, blot([5, -19], 4.5, 0.7, 5), top_at(-19))
    bolts(hull, [[-20, 4], [-12, 4], [12, 4], [20, 4]], top_at(4), 1.2)
    vent(hull, [-14, top_at(-17) + 0.05, -17], [8, 5], 3)
    charge.box([6, 0.3, 3.4], WHITE, Placement([-14, top_at(-17), -17]))
    neon.box([6.4, 0.25, 0.5], FORGE["ember"], Placement([-14, top_at(-17) + 0.1, -14.7]))
    if len(CRAB_DOME) == 0:
        return
    emitter = CRAB_DOME[0]
    top = boss_point(emitter[0], emitter[1], emitter[2])
    base = [top[0], top_at(top[2]) - 0.4, top[2]]
    k = (top[1] - base[1] - 0.6) / DOME[len(DOME) - 1][1]
    hull.lathe([[r[0], r[1] * k] for r in DOME], 8, H.panel, Placement(base))
    neon.ring(7.2, 0.7, 8, CRAB_ORANGE, Placement(offset(base, 0, 0.5, 0)))
    charge.cylinder(1.6, 0.6, 6, WHITE, Placement(offset(top, 0, -0.6, 0)), 0.8)
    p.muzzle(top, "ring")


def _mortar_part(p: Any, at: Vec3) -> None:
    """The mortar on the carapace, standing where the carapace is at its z."""
    mortar(p, at, top_at(at[2]) - 0.4)


def build_cinder_crab(scene: Any) -> Any:
    """P10-R11: the Cinder Crab, a wide, low crab-ship 3 L across, orange neon: a soot-black
    carapace cracked by molten seams on six short legs, eye stalks, two claws on swinging arms whose
    outer fingers snap open and shut, the ring dome on its back and a mortar behind it."""

    def core(p: Any) -> None:
        _draw_carapace(p)
        _draw_legs(p)
        _draw_front(p)
        _draw_back(p)

    return build_boss_model(
        CINDER_CRAB,
        scene,
        CRAB_ORANGE,
        {
            "core": core,
            "parts": {"claw-left": claw, "claw-right": claw, "mortar": _mortar_part},
            "limbs": CRAB_LIMBS,
        },
    )
