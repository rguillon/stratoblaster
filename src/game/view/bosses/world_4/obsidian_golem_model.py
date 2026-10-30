"""P10-R11, 4-3: the Obsidian Golem. Logical
pixels, nose +Z, Y up (towards the camera). A massive flying fortress shaped like a hunched giant: a
broad armoured torso of black obsidian plates split by glowing magma seams, a small helmed head
low on
its chest, a furnace stack on its back, heavy pauldrons, two arms bending at the shoulder and elbow
down to huge fists (limbs on joints), the shoulder cannons behind the pauldrons, the armour plate
and
the chest emitter on its front. P16-R06: a living hunched giant, its flesh torso and hump ribbed in
bone and veined with magma, obsidian growths for pauldrons, knuckles and chest plate, a metal helm
and
guns grafted on.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.obsidian_golem import (  # noqa: E402
    GOLEM_BROW,
    GOLEM_STACK,
    OBSIDIAN_GOLEM,
)
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_shapes import mirrored  # noqa: E402
from game.view.bosses.mini_boss_greebles import vent  # noqa: E402
from game.view.bosses.mini_boss_shapes import SHADE, WHITE, H, offset, socket  # noqa: E402
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    flesh_shell,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.bosses.world_4.magma_salamander_parts import barrel  # noqa: E402
from game.view.bosses.world_4.obsidian_golem_parts import (  # noqa: E402
    GOLEM_NEON,
    MAGMA,
    OBSIDIAN,
    arm_limbs,
    cannon_mount,
    cannon_turret,
    crack,
    emitter,
    fist,
    plate,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type OutlinePoint = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The torso seen from above (right half, chest to back).
TORSO = mirrored(
    [
        [0, 30],
        [18, 28],
        [32, 18],
        [40, 4],
        [38, -16],
        [28, -32],
        [0, -36],
    ]
)
# The hunched upper torso on it, back to front (loft stations: z, half width, bottom, top).
HUMP = [
    [-32.0, 22.0, 16.0, 23.0],
    [-12.0, 30.0, 16.0, 28.0],
    [8.0, 28.0, 16.0, 26.0],
    [22.0, 18.0, 16.0, 21.0],
]
# The magma seams across its back, as paths of points (x, z) on the hump's top.
SEAMS = [
    [
        [-16.0, 12.0],
        [-6.0, 4.0],
        [4.0, 8.0],
        [16.0, 0.0],
    ],
    [
        [-18.0, -10.0],
        [-8.0, -6.0],
        [2.0, -14.0],
        [14.0, -10.0],
    ],
    [
        [0.0, -14.0],
        [-2.0, -26.0],
    ],
]
# The head: a small helm low on its chest, from its nape to its brow.
HELM = [
    [8.0, 9.0, 16.0, 28.0],
    [16.0, 10.0, 16.0, 29.0],
    [22.0, 8.0, 17.0, 26.0],
]


def _draw_torso(p: Any) -> None:
    """The torso: a slab of dark metal, the obsidian hump on it, magma seams across its back."""
    hull = p.hull
    neon = p.neon
    p.flesh.bevel_slab(TORSO, [-4, 2, 16], [4, 3], SKIN.base, None, SKIN.panel)
    flesh_shell(p.flesh, HULL_SECTION, HUMP, [SKIN.dark, SKIN.base])
    back_ribs(p, [-22, -10], RibSpec(26, 12, 15, 1.2))
    for s in SIDES:
        magma_vein(
            p,
            [
                [s * 30, 16.2, 16],
                [s * 34, 16.2, -2],
                [s * 28, 16.2, -24],
            ],
            1.4,
        )
        glands(p, [[s * 32, 15.8, -30]], 2.4, GOLEM_NEON)
    for path in SEAMS:
        crack(neon, path, 28.2)
    for s in SIDES:
        neon.box([0.7, 0.6, 50], GOLEM_NEON, Placement([s * 39.6, 10, -6], s * 0.05))
        vent(hull, [s * 20, 16.2, -26], [8, 6], 3, s * 0.2)
        hull.box([10, 0.5, 8], SHADE["soot"], Placement([s * 26, 16.1, 18 - s * 6]))
        socket(hull, [s * 46, 0, -20], 9, 2)


def _draw_head(p: Any) -> None:
    """The head: a helm with a glowing visor, the twin guns under its brow."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    hull.loft(HULL_SECTION, HELM, H.panel)
    neon.box([14, 1.2, 1], GOLEM_NEON, Placement([0, 25.6, 22.2]))
    charge.box([10, 0.6, 0.6], WHITE, Placement([0, 26, 22.5]))
    hull.box([3, 4, 10], SHADE["edge"], Placement([0, 28.6, 14]))
    for m in GOLEM_BROW:
        tip = boss_point(m[0], m[1], m[2])
        hull.box([3.6, 3, 4], H.dark, Placement(offset(tip, 0, -1.5, -6)))
        barrel(p, tip, [1.1, 5])


def _draw_pauldrons(p: Any) -> None:
    """The pauldrons over its shoulders: domes of obsidian ringed in orange."""
    hull = p.hull
    neon = p.neon
    for s in SIDES:
        at: Vec3 = [s * 38, 14, 2]
        hull.lathe(
            [
                [13, 0],
                [13.6, 4],
                [10, 9],
                [4, 11],
                [0, 11.4],
            ],
            8,
            OBSIDIAN,
            Placement(at, math.pi / 8),
        )
        neon.ring(13.7, 0.8, 8, GOLEM_NEON, Placement(offset(at, 0, 1.4, 0), math.pi / 8))
        crack(
            neon,
            [
                [s * 32, 6],
                [s * 38, 0],
                [s * 44, 3],
            ],
            at[1] + 9.8,
        )


def _draw_stack(p: Any) -> None:
    """The furnace stack on its back, its glowing top where the core's rings leave from."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(GOLEM_STACK) == 0:
        return
    m = GOLEM_STACK[0]
    top = boss_point(m[0], m[1], m[2])
    foot = offset(top, 0, -(top[1] - 18), 0)
    hull.cylinder(7, top[1] - 19, 8, H.base, Placement(foot), 5.4)
    hull.ring(7.2, 1.6, 8, SHADE["soot"], Placement(offset(foot, 0, 4, 0)))
    neon.ring(5.6, 1, 8, MAGMA, Placement(offset(top, 0, -2.2, 0)))
    charge.cylinder(4.6, 1, 8, WHITE, Placement(offset(top, 0, -1, 0)))
    muzzle(top, "ring")


def _draw_underside(p: Any) -> None:
    """Its reactors under the back, and the sockets where the plate and the emitter are bolted."""
    reactor_sacs(
        p,
        [
            [16, 4, -36],
            [-16, 4, -36],
        ],
        4.4,
        MAGMA,
    )
    reactor_sacs(p, [[0, 4, -36]], 3.6, MAGMA)
    socket(p.hull, [0, 0, 34], 10, 3)
    p.neon.box([30, 0.6, 0.8], MAGMA, Placement([0, 2.4, 29.6]))


def build_obsidian_golem(scene: Any) -> Any:
    """P10-R11: the Obsidian Golem, a massive armoured flying fortress of black obsidian with
    glowing
    magma seams and two huge fists on bending arms."""

    def core(p: Any) -> None:
        _draw_torso(p)
        _draw_head(p)
        _draw_pauldrons(p)
        _draw_stack(p)
        _draw_underside(p)

    return build_boss_model(
        OBSIDIAN_GOLEM,
        scene,
        GOLEM_NEON,
        {
            "core": core,
            "parts": {
                "fist-left": fist,
                "fist-right": fist,
                "cannon-left": cannon_mount,
                "cannon-right": cannon_mount,
                "emitter": emitter,
                "plate": plate,
            },
            "turrets": {"cannon-left": cannon_turret, "cannon-right": cannon_turret},
            "limbs": arm_limbs(),
        },
    )
