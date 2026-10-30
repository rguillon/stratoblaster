"""P10-R11, 4-4: the Furnace Drake. Logical
pixels, nose +Z, Y up (towards the camera). A dragon-shaped gunship: a heavy armoured torso with a
furnace glowing through a grate in its back, molten seams between its soot-black plates, four clawed
legs tucked under it, a long spiked tail lashing behind, beating wings and a horned head on a
swaying neck. P16-R05: a living dragon, its flesh torso ribbed in bone, a furnace heart grafted in
its back, magma veins under its hide, bone spines and claws.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.furnace_drake import (  # noqa: E402
    DRAKE_HEART,
    DRAKE_WING,
    FURNACE_DRAKE,
)
from game.config.record import record  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_greebles import rod  # noqa: E402
from game.view.bosses.mini_boss_greebles import seam, vent  # noqa: E402
from game.view.bosses.mini_boss_shapes import WHITE, H  # noqa: E402
from game.view.bosses.world_4.furnace_drake_parts import (  # noqa: E402
    DRAKE_ORANGE,
    DRAKE_RED,
    SOOT,
    jaw,
    spike,
    wing,
)
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, POD_SECTION, SIDES  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The torso along the centre line (loft stations: z, half width, bottom, top).
TORSO = [
    [-22.0, 6.0, -1.0, 6.0],
    [-12.0, 11.0, -3.0, 10.0],
    [0.0, 13.0, -4.0, 12.0],
    [10.0, 11.0, -3.0, 10.5],
    [17.0, 7.0, -1.0, 8.0],
]
# The tail, hips to tip (on its joint at the hips): a tapering spiked whip.
TAIL = [
    [-20.0, 5.0, -0.5, 5.5],
    [-31.0, 3.8, 0.0, 4.6],
    [-43.0, 2.6, 0.5, 3.6],
    [-53.0, 1.4, 1.0, 2.6],
    [-57.0, 0.4, 1.6, 2.0],
]
# The legs, front then back (left side, +X): hip, knee and claw, folded under the torso.
LEGS = [
    [
        [8.0, -1.0, 9.0],
        [15.0, -3.0, 13.0],
        [14.0, -5.0, 19.0],
    ],
    [
        [8.0, -1.0, -12.0],
        [16.0, -3.0, -14.0],
        [15.0, -5.0, -7.0],
    ],
]
# The furnace heart's grate on its back (a lathe dome), glowing as its next spiral charges.
HEART = [
    [4.6, 0.0],
    [4.0, 1.6],
    [2.2, 2.6],
    [0.0, 2.9],
]


def _draw_legs(p: Any) -> None:
    """Four short legs folded under the torso, ending in claws."""
    hull = p.flesh
    for s in SIDES:
        for leg in LEGS:
            hip = leg[0]
            knee = leg[1]
            claw = leg[2]
            rod(
                hull, [s * hip[0], hip[1], hip[2]], [s * knee[0], knee[1], knee[2]], 1.6, SKIN.panel
            )
            rod(
                hull,
                [s * knee[0], knee[1], knee[2]],
                [s * claw[0], claw[1], claw[2]],
                1.1,
                SKIN.base,
            )
            spike(hull, [s * claw[0], claw[1], claw[2]], [0.8, 3], SKIN.bone, -1.2)


def _draw_torso(p: Any) -> None:
    """The torso: plates, molten seams between them, soot, spines down the back, legs and
    reactors."""
    hull = p.hull
    neon = p.neon
    p.flesh.loft(HULL_SECTION, TORSO, SKIN.base)
    back_ribs(p, [-14, -6, 2], RibSpec(11, 2, 8.6, 0.8))
    magma_vein(
        p,
        [
            [0, 10.8, -16],
            [3, 11, -4],
            [-2, 10.8, 6],
            [0, 10, 16],
        ],
        1,
        DRAKE_ORANGE,
    )
    glands(
        p,
        [
            [7, 8.6, 2],
            [-7, 8.6, 2],
        ],
        1.5,
        DRAKE_RED,
    )
    for s in SIDES:
        seam(neon, [s * 9, -14], [s * 10.5, 9], [9.3, 0.5, 0.3], DRAKE_ORANGE)
        seam(neon, [s * 11.8, -6], [s * 12.4, 4], [6.5, 0.4, 0.4], DRAKE_RED)
        seam(hull, [s * 5, -18], [s * 6, 14], [11.4, 2.2, 0.3], SOOT)
        vent(hull, [s * 6.5, 10.4, 10], [3.4, 4], 3)
        # The shoulder the wing turns in.
        rx = DRAKE_WING.root[0]
        ry = DRAKE_WING.root[1]
        hull.cylinder(4.2, 6, 8, H.dark, Placement(boss_point(s * rx, ry, 1)))
    reactor_sacs(
        p,
        [
            [4, 2, -22.4],
            [-4, 2, -22.4],
        ],
        2.2,
        DRAKE_ORANGE,
    )
    for z in [12, -12, -18]:
        spike(p.flesh, [0, 11, z], [1.6, 4], SKIN.bone, 0.7)
    _draw_legs(p)


def _draw_heart(p: Any) -> None:
    """The furnace heart on its back, where its spirals leave from."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(DRAKE_HEART) == 0:
        return
    m = DRAKE_HEART[0]
    top = boss_point(m[0], m[1], m[2])
    x = top[0]
    y = top[1]
    z = top[2]
    hull.cylinder(6, 4, 8, H.dark, Placement([x, y - 6.4, z]), 5)
    neon.ring(5.2, 0.5, 8, DRAKE_ORANGE, Placement([x, y - 2.6, z]))
    charge.lathe(HEART, 8, WHITE, Placement([x, y - 2.9, z]))
    for dx in [-2, 0, 2]:
        hull.box([0.5, 0.5, 8], SOOT, Placement([x + dx, y - 0.4, z]))
    muzzle(top, "ring")


def _draw_tail(p: Any) -> None:
    """The tail on its joint at the hips: spikes down its back, a glowing blade at its tip."""
    hull = p.flesh
    neon = p.neon
    hull.loft(POD_SECTION, TAIL, SKIN.panel)
    for pair in [[-26.0, 5.0], [-35.0, 4.2], [-44.0, 3.4]]:
        spike(hull, [0, pair[1], pair[0]], [1.3, 3], SKIN.bone, 0.7)
    seam(neon, [0, -22], [0, -52], [5.6, 0.4, 0.3], DRAKE_RED)
    for s in SIDES:
        hull.box([5, 0.8, 4], SKIN.bone, Placement([s * 2.4, 1.6, -54], s * 0.7))
        seam(neon, [s * 2, -48], [s * 3.6, -55], [2.4, 0.4, 0.4], DRAKE_ORANGE)


# The tail on its joint at the hips.
TAIL_LIMB = record({"draw": _draw_tail})


def build_furnace_drake(scene: Any) -> Any:
    """P10-R11: the Furnace Drake, a dragon-shaped gunship (3.5 L) of soot-black plates with red and
    orange neon: beating wings with a fan pod under each, a horned head breathing flame, a furnace
    glowing in its back and a spiked tail lashing behind."""

    def core(p: Any) -> None:
        _draw_torso(p)
        _draw_heart(p)
        p.hull.box([8, 1, 3], SOOT, Placement([0, 11, -12]))

    return build_boss_model(
        FURNACE_DRAKE,
        scene,
        DRAKE_RED,
        {
            "core": core,
            "parts": {"wing-left": wing, "wing-right": wing, "jaw": jaw},
            "limbs": {"tail": TAIL_LIMB},
        },
    )
