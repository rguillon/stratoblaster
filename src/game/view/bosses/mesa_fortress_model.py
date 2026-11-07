# Copyright (c) 2026 Renaud Guillon
"""FB-MESA-FORTRESS-01 to FB-MESA-FORTRESS-04: the Mesa Fortress.

The final boss of 1-3 Logical pixels, nose +Z, Y up (towards the camera). A colossal canyon
tortoise: a wide skirt of hide under a high, stepped shell like the mesas, plated with grafted
armour, a fan turret on its brow and a rotor on its back (the core's mounts, BOSS-58), a forelimb
on each side cradling a laser lance, two spore silos on its back, red veins along its shell. Its
skirt's flank plates and its keep's roof halves are drawn as pieces of their own
(`mesa_fortress_armour`, D-254).
"""

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.final_bosses import MESA_FORTRESS
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_mesa import BASE_TOP, draw_lance, draw_silo
from game.view.bosses.final_boss_shapes import edge_strips, sided
from game.view.bosses.mesa_fortress_armour import (
    KEEP_Y,
    draw_centre,
    draw_skirt,
    mesa_armour,
)
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    graft,
    hide,
    polygon,
    rib_cage,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes, reactor_sac

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["mesa-fortress"]

# The right forelimb: a broad paddle out from the body, the lance cradled on it, then a forearm
# forward to the claw.
ARM = [
    [40, 20],
    [72, 20],
    [74, 26],
    [78, 32],
    [85, 30],
    [86, -16],
    [80, -23],
    [40, -24],
]
# Grafted armour plates on the lower shell's brow (x, z, radius), mirrored; the keep's plates are
# on its roof halves.
BROW_PLATES = [
    [12, 24, 4.5],
]


def _draw_body(p: Any) -> None:
    """Draw the body (FB-MESA-FORTRESS-02): the skirt, the lower shell with its ribs and veins.

    Its keep (the upper shell) is drawn apart as its roof halves, and the skirt's flank plates as
    its armour. The lower shell's top is the flat step the keep stands on; the head is at its front.
    """
    draw_skirt(p)
    draw_centre(p)
    hide(
        p,
        {
            "tail": -50,
            "nose": 30,
            "width": 38,
            "bottom": BASE_TOP - 2,
            "top": KEEP_Y[0],
            "segments": 4,
            "shell": [F.slate, F.membrane],
            "belly": F.graphite,
        },
    )
    rib_cage(
        p,
        [-40, 22],
        {"halfWidth": 34, "y": BASE_TOP, "height": 9, "thickness": 1.4},
        F.bone,
    )
    for s in SIDES:
        brow_plates: list[Any] = BROW_PLATES
        for plate in brow_plates:
            graft(
                p,
                polygon(6, plate[2], [1, 1.3]),
                [13.2, 14.4],
                [s * plate[0], 0, plate[1]],
                {"color": M.base},
            )
        for z in [-30, -8]:
            vein_line(p, [s * 12, 16.5, z], [s * 30, 13.2, z - 6], [s * 2, 2, 0], 1.3, N)
        reactor_sac(p, [s * 10, 0.5, -53.4], 3.8, N)
        reactor_sac(p, [s * 24, 0.5, -51.8], 3.8, N)
    eyes(p, [0, BASE_TOP + 0.2, 40], {"count": 2, "size": 1.6, "spacing": 10}, N)
    barbs(p, [0, BASE_TOP, 46], {"count": 4, "spacing": 6, "size": 3, "dir": [0, -0.2, 1]})


def _draw_arms(p: Any) -> None:
    """Draw the forelimbs (FB-MESA-FORTRESS-02): a broad paddle out to each lance's cradle.

    A bone claw at its front; its scaly sinew lies on it (the flank armour, drawn apart).
    """
    for s in SIDES:
        p.flesh.bevel_slab(sided(ARM, s), [-4, 0, 5], [1, 2], F.sinew, None, F.slate)
        for dx in [-3, 3]:
            tentacle(
                p,
                [s * (81 + dx), 4, 26],
                [s * (80 + dx), 0, 36],
                [0, 2, 0],
                [1.6, 0.1],
                F.bone,
                3,
            )
        edge_strips(
            p.neon,
            sided(
                [
                    [79, 27],
                    [81, -15],
                ],
                s,
            ),
            1,
            [5.8, 6.4],
            N,
        )


def build_mesa_fortress(scene: Any) -> Any:
    """FB-MESA-FORTRESS-01, FB-MESA-FORTRESS-04: the Mesa Fortress, a colossal canyon tortoise.

    It is 5 L across with red veins; a laser lance in each forelimb, two spore silos on its back,
    and the core's fan turret on its armoured brow and rotor behind its keep (its gun mounts,
    drawn by `build_boss_model`, BOSS-58). Its skirt's flank plates and its roof halves are drawn
    apart (FB-MESA-FORTRESS-05).
    """

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_arms(p)

    return build_boss_model(
        MESA_FORTRESS,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "lance-left": draw_lance,
                "lance-right": draw_lance,
                "silo-left": draw_silo,
                "silo-right": draw_silo,
            },
            "armour": mesa_armour(),
        },
    )
