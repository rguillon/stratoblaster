# Copyright (c) 2026 Renaud Guillon
"""FB-OBSIDIAN-GOLEM-01 to FB-OBSIDIAN-GOLEM-07, 4-3: the Obsidian Golem.

Logical pixels, nose +Z, Y up (towards the camera). A massive flying fortress shaped like a hunched
giant: a broad armoured torso of black obsidian plates split by glowing magma seams, a small helmed
head low on its chest, a furnace stack on its back, heavy pauldrons, two arms bending at the
shoulder and elbow down to huge fists (limbs on joints), the shoulder cannons behind the pauldrons,
the armour plate and the chest emitter on its front. The pauldrons ride the flank slabs and the
helm ends the spine ridge: its armour (D-254, `obsidian_golem_armour`). FB-OBSIDIAN-GOLEM-02: a
living hunched giant, its flesh torso and hump ribbed in bone and veined with magma, obsidian
growths for pauldrons, knuckles and chest plate, a metal helm and guns grafted on.
"""

import math

from game.config.bosses.world_4.obsidian_golem import (
    GOLEM_BROW,
    GOLEM_STACK,
    OBSIDIAN_GOLEM,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import mirrored
from game.view.bosses.mini_boss_shapes import SHADE, WHITE, H, offset, socket
from game.view.bosses.world_4.living_forge import (
    SKIN,
    back_ribs,
    flesh_shell,
    reactor_sacs,
)
from game.view.bosses.world_4.magma_salamander_parts import barrel
from game.view.bosses.world_4.obsidian_golem_armour import (
    OBSIDIAN_GOLEM_ARMOUR,
    PAULDRON_AT,
    TORSO_TOP,
)
from game.view.bosses.world_4.obsidian_golem_parts import (
    GOLEM_NEON,
    MAGMA,
    arm_limbs,
    cannon_mount,
    cannon_turret,
    emitter,
    fist,
    plate,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES
from render.geometry.organic import RibSpec
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The torso seen from above (right half, chest to back).
TORSO = mirrored([
    [0, 30],
    [18, 28],
    [32, 18],
    [40, 4],
    [38, -16],
    [28, -32],
    [0, -36],
])
# The hunched upper torso on it, back to front (loft stations: z, half width, bottom, top).
HUMP = [
    [-32.0, 22.0, 16.0, 23.0],
    [-12.0, 30.0, 16.0, 28.0],
    [8.0, 28.0, 16.0, 26.0],
    [22.0, 18.0, 16.0, 21.0],
]
# The shoulder drums under the pauldrons: their radius, within the pauldrons' domes.
SHOULDER = 12.5


def _draw_torso(p: Any) -> None:
    """Draw the torso: a slab of dark metal, the flesh hump on it, ribs over its back.

    The flank slabs with the pauldrons, the magma veins and glands, and the obsidian ridge with its
    magma seams along the hump's crest are its armour (`obsidian_golem_armour`).
    """
    hull = p.hull
    neon = p.neon
    p.flesh.bevel_slab(TORSO, [-4, 2, TORSO_TOP], [4, 3], SKIN.base, None, SKIN.panel)
    flesh_shell(p.flesh, HULL_SECTION, HUMP, [SKIN.dark, SKIN.base])
    back_ribs(p, [-22, -10], RibSpec(26, 12, 15, 1.2))
    for s in SIDES:
        neon.box([0.7, 0.6, 50], GOLEM_NEON, Placement([s * 39.6, 10, -6], s * 0.05))
        socket(hull, [s * 46, 0, -20], 9, 2)
        # The shoulder: a dark drum from the underside up to the torso's top, under the pauldron
        # and its hinge (the flank slab's foot once it has lifted, BOSS-52).
        hull.cylinder(
            SHOULDER,
            TORSO_TOP,
            8,
            H.dark,
            Placement([s * PAULDRON_AT[0], 0, PAULDRON_AT[1]], math.pi / 8),
        )


def _draw_brow_guns(p: Any) -> None:
    """Draw the twin guns under the helm's brow (the core's; the helm is its spine armour)."""
    for m in GOLEM_BROW:
        tip = boss_point(m[0], m[1], m[2])
        p.hull.box([3.6, 3, 4], H.dark, Placement(offset(tip, 0, -1.5, -6)))
        barrel(p, tip, [1.1, 5])


def _draw_stack(p: Any) -> None:
    """Draw the furnace stack on its back, its glowing top where the core's rings leave from."""
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
    """Build the Obsidian Golem (FB-OBSIDIAN-GOLEM-01, FB-OBSIDIAN-GOLEM-06).

    A massive armoured flying fortress of black obsidian with glowing magma seams and two huge fists
    on bending arms.
    """

    def core(p: Any) -> None:
        _draw_torso(p)
        _draw_brow_guns(p)
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
            "armour": OBSIDIAN_GOLEM_ARMOUR,
        },
    )
