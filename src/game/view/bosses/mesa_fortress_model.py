"""P07-R05, P16-R06: the Mesa Fortress, the final boss of 1-3 Logical pixels, nose +Z, Y up (towards
the camera). A colossal
canyon tortoise: a wide skirt of hide under a high, stepped shell like the mesas, plated with
grafted armour, a fan cannon on its brow, a forelimb on each side cradling a laser lance, two spore
silos on its back, red veins along its shell.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.final_bosses import MESA_FORTRESS  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_mesa import BASE_TOP, draw_lance, draw_silo  # noqa: E402
from game.view.bosses.final_boss_shapes import edge_strips, mirrored, shift, sided  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    gland,
    graft,
    hide,
    mantle,
    polygon,
    rib_cage,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

N = BOSS_LOOK.neon["mesa-fortress"]
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# The skirt of hide (right half, front to back): the silos stand on its rear.
BASE = mirrored(
    [
        [0, 48],
        [22, 46],
        [40, 30],
        [44, 10],
        [44, -36],
        [34, -50],
        [0, -54],
    ]
)
# The right forelimb: an upper limb out from the body, then a forearm forward.
ARM = [
    [40, -6],
    [72, -6],
    [74, 26],
    [78, 32],
    [85, 30],
    [86, -16],
    [80, -23],
    [40, -24],
]
# The fan cannon's housing, on the brow.
FAN_HOUSING = [
    [-12, -8],
    [12, -8],
    [14, 4],
    [7, 12],
    [-7, 12],
    [-14, 4],
]
FAN_AT = [0, 15, 26]
# Grafted armour plates on the shell (x, z, radius), mirrored.
SHELL_PLATES = [
    [14, -26, 6],
    [20, 2, 5],
    [10, 14, 4.5],
]


def _draw_body(p: Any) -> None:
    """The skirt, the stepped shell with its ribs, veins and grafted plates, the head at its
    front."""
    mantle(p, BASE, [-6, BASE_TOP], F.sinew, N)
    hide(
        p,
        {
            "tail": -50,
            "nose": 30,
            "width": 38,
            "bottom": BASE_TOP - 2,
            "top": 22,
            "segments": 4,
            "shell": [F.crimson, F.membrane],
            "belly": F.purple,
        },
    )
    hide(
        p,
        {
            "tail": -36,
            "nose": 18,
            "width": 22,
            "bottom": 14,
            "top": 30,
            "segments": 3,
            "shell": [F.sinew, F.crimson],
            "belly": F.crimson,
        },
    )
    rib_cage(
        p,
        [-40, 22],
        {"halfWidth": 34, "y": BASE_TOP, "height": 13, "thickness": 1.4},
        F.bone,
    )
    spine(p, [0, 30.5, -32], [0, 30.5, 14], {"color": N, "width": 1.6})
    rim = [
        [-34, 28.5],
        [-19, 41.5],
        [19, 41.5],
        [34, 28.5],
    ]
    edge_strips(p.neon, rim, 1.2, [BASE_TOP - 0.2, BASE_TOP + 0.5], N)
    for s in SIDES:
        shell_plates: list[Any] = SHELL_PLATES
        for plate in shell_plates:
            graft(
                p,
                polygon(6, plate[2], [1, 1.3]),
                [17, 18.4],
                [s * plate[0], 0, plate[1]],
                {"color": M.base},
            )
        for z in [-30, -8]:
            vein_line(p, [s * 18, 27, z], [s * 38, 12, z - 6], [s * 3, 4, 0], 1.3, N)
        gland(p, [s * 12, 29, 0], 2.2, N)
        reactor_sac(p, [s * 10, 0.5, -53.4], 3.8, N)
        reactor_sac(p, [s * 24, 0.5, -51.8], 3.8, N)
    eyes(p, [0, 12, 40], {"count": 2, "size": 1.6, "spacing": 10}, N)
    barbs(p, [0, 7, 46], {"count": 4, "spacing": 6, "size": 3, "dir": [0, -0.2, 1]})


def _draw_arms(p: Any) -> None:
    """The forelimbs: a scaly limb out to each lance's cradle, a bone claw at its front."""
    for s in SIDES:
        p.flesh.bevel_slab(sided(ARM, s), [-4, 0, 5], [1, 2], F.sinew, None, F.crimson)
        tentacle(p, [s * 36, 6, -15], [s * 76, 7, -14], [0, 3, 0], [6, 4], F.crimson, 5)
        graft(p, polygon(4, 5, [2, 0.9]), [8.5, 9.6], [s * 56, 0, -16])
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


def _fan_point(yaw: float, r: float) -> Vec3:
    """A point of a fan barrel, `r` out along its yaw from the fan's pivot."""
    return shift(FAN_AT, [math.sin(yaw) * r, 2.6, 4 + math.cos(yaw) * r])


def _draw_fan_cannon(p: Any, at: Any = None) -> None:
    """The fan cannon on the brow (the core's gun): a grafted housing and five barrels fanned out
    forward, turning around the hub of its barrels (its pivot)."""
    p.hull.bevel_slab(FAN_HOUSING, [0, 0, 5], [0, 1.5], M.dark, Placement(FAN_AT), M.panel)  # type: ignore[arg-type]
    for k in range(5):
        yaw = (k - 2) * 0.28
        p.hull.cylinder(
            1.6,
            9,
            6,
            M.dark,
            Placement(_fan_point(yaw, 4), yaw, QUARTER),
            1.3,
        )
        p.charge.cylinder(
            1.5,
            2,
            6,
            WHITE,
            Placement(_fan_point(yaw, 13), yaw, QUARTER),
        )
        p.muzzle(_fan_point(yaw, 15), None)


def build_mesa_fortress(scene: Any) -> Any:
    """P07-R05, P16-R06: the Mesa Fortress, a colossal canyon tortoise 5 L across with red veins; a
    laser lance in each forelimb, two spore silos on its back, and a fan cannon on its armoured brow
    (the core)."""

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
            "turrets": {"core": _draw_fan_cannon},
        },
    )
