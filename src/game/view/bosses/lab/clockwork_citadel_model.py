# Copyright (c) 2026 Renaud Guillon
"""FB-CLOCKWORK-CITADEL-01, FB-CLOCKWORK-CITADEL-02: the Clockwork Citadel, the Lab's L-24 final.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying clock-tower fortress seen
from above: a square stone citadel on a stepped plinth (an inverted step beneath), crenellated
parapets, a round bell tower at each corner, a gatehouse at its front, sponsons for its casemates,
steel shelves on its flanks for its gear trains and the rails its great wheels slide out on, the
pendulum's bracket on its back wall. Its roof holds the clock: the movement in a round pit (gears,
the centre boss and the arbor the hands turn on) under the face's two halves. Its parts and armour
are in `clockwork_citadel_parts`, its hour hand and roof gears in `clockwork_citadel_rig`. Stone,
steel and brass with warm light lines (shown yellow), not a creature (the Lab's fifth round, user
request 2026-11-06).
"""

import math

from game.config.bosses.lab.clockwork_citadel import (
    ARBOR,
    BLOCK,
    BROADSIDE_AT,
    CASEMATE_AT,
    CASEMATE_TOP,
    CENTRE,
    CLOCKWORK_CITADEL,
    FACE_RADIUS,
    GATE,
    GEARS_AT,
    MOVEMENT,
    NOON_AT,
    PARAPET,
    PENDULUM_PIVOT,
    PLINTH,
    ROOF,
    SHELF_TOP,
    TOWER_AT,
    TOWER_RADIUS,
    TOWER_TOP,
    WHEEL_AT,
    WHEEL_SLIDE,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.clockwork_citadel_parts import (
    BRASS,
    COURSE,
    STONE,
    N,
    belfry,
    bob,
    citadel_armour,
    gear,
    gear_train,
    minute_hand,
    pendulum_limbs,
    pt,
)
from game.view.bosses.lab.clockwork_citadel_rig import build_citadel_rig, rig_triangles
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The movement's gears in the pit, `[x, y, radius, teeth]` (the right ones; mirrored).
PIT_GEARS = [[20, -10, 7, 14], [18, 15, 7.5, 14]]  # type: list[list[float]]
# The towers' drum profile `[radius, height]` (bottom to top), from under the plinth.
TOWER_PROFILE = [  # type: list[list[float]]
    [TOWER_RADIUS - 2, -8],
    [TOWER_RADIUS + 1, -3],
    [TOWER_RADIUS, 0],
    [TOWER_RADIUS, TOWER_TOP - 4],
    [TOWER_RADIUS + 1.2, TOWER_TOP - 2.4],
    [TOWER_RADIUS + 1.2, TOWER_TOP],
]
SIDES = [-1, 1]


def _square(half: float) -> list[list[float]]:
    return [pt(-half, -half), pt(half, -half), pt(half, half), pt(-half, half)]


def _draw_plinth(p: Any) -> None:
    """Draw the plinth and the inverted step beneath it (FB-CLOCKWORK-CITADEL-01)."""
    p.flesh.bevel_slab(
        _square(PLINTH[0]), [-2, PLINTH[1] - 1, PLINTH[1]], [2, 0.6], STONE, None, COURSE
    )
    p.flesh.bevel_slab(_square(PLINTH[0] - 9), [-12, -3, -2], [12, 0], COURSE)
    p.neon.box([2 * PLINTH[0] + 0.2, 0.4, 2 * PLINTH[0] + 0.2], N, Placement([0, 2.4, 0]))


def _quadrant(sx: float, sy: float) -> list[list[float]]:
    """Return the roof's quadrant (`sx`, `sy` its signs): from the face's rim out to the block's."""
    result: list[list[float]] = []
    steps = 6
    for k in range(steps + 1):
        a = k * math.pi / 2 / steps
        result.append(pt(sx * FACE_RADIUS * math.cos(a), sy * FACE_RADIUS * math.sin(a)))
    result.append(pt(0, sy * BLOCK))
    result.append(pt(sx * BLOCK, sy * BLOCK))
    result.append(pt(sx * BLOCK, 0))
    return result


def _draw_block(p: Any) -> None:
    """Draw the citadel's block (FB-CLOCKWORK-CITADEL-01): its walls and roof round the clock's pit.

    Lit slits along its walls, a darker course at their foot, the parapet with its merlons.
    """
    for sx in SIDES:
        for sy in SIDES:
            p.flesh.slab(_quadrant(sx, sy), [PLINTH[1], ROOF], STONE, None, COURSE)
    p.flesh.ring(
        BLOCK * math.sqrt(2) + 0.1, 0.1, 4, COURSE, Placement([0, PLINTH[1], 0], math.pi / 4)
    )
    span = BLOCK - TOWER_RADIUS
    for k in range(4):
        yaw = k * math.pi / 2
        c = math.sin(yaw)
        s = math.cos(yaw)
        mid = [c * (BLOCK - PARAPET[0] / 2), ROOF, s * (BLOCK - PARAPET[0] / 2)]
        p.flesh.box([2 * span, PARAPET[1] - ROOF, PARAPET[0]], STONE, Placement(mid, yaw), COURSE)
        for j in range(6):
            along = -span + 3 + j * (2 * span - 6) / 5
            q = [mid[0] + s * along, PARAPET[1], mid[2] - c * along]
            p.flesh.box([2.4, 2, PARAPET[0]], STONE, Placement(q, yaw))
        for j in range(5):
            along = -span + 7 + j * (2 * span - 14) / 4
            q = [c * (BLOCK + 0.05) + s * along, 11, s * (BLOCK + 0.05) - c * along]
            p.charge.box([1, 2.6, 0.3], N, Placement(q, yaw))
        p.neon.box(
            [2 * span, 0.35, 0.4],
            N,
            Placement([c * (BLOCK + 0.1), ROOF - 1.6, s * (BLOCK + 0.1)], yaw),
        )


def _draw_pit(p: Any) -> None:
    """Draw the clock's movement in its pit (FB-CLOCKWORK-CITADEL-02, seen once the face splits).

    A dark floor, a lit ring round its wall, brass wheels meshing, the centre boss and the arbor.
    """
    p.hull.cylinder(
        FACE_RADIUS + 0.5, MOVEMENT - PLINTH[1], 24, M.base, Placement([0, PLINTH[1], 0])
    )
    p.hull.ring(FACE_RADIUS + 0.2, ROOF - MOVEMENT, 24, COURSE, Placement([0, MOVEMENT, 0]))
    p.neon.ring(FACE_RADIUS + 0.1, 0.35, 24, N, Placement([0, MOVEMENT + 1.5, 0]))
    for g in PIT_GEARS:
        for s in SIDES:
            gear(
                p,
                boss_point(s * g[0], g[1], 0),
                g[2],
                math.floor(g[3]),
                [MOVEMENT, MOVEMENT + 1.2],
                BRASS,
            )
    gear(p, boss_point(0, 26, 0), 5, 10, [MOVEMENT, MOVEMENT + 1.2], BRASS)
    for s in SIDES:
        p.hull.box([1.4, 1, 30], M.panel, Placement(boss_point(s * 9, 6, MOVEMENT), s * 0.2))
    p.hull.lathe(
        [
            [CENTRE[0] + 1, MOVEMENT],
            [CENTRE[0], MOVEMENT + 1],
            [CENTRE[0], CENTRE[1] - 0.6],
            [CENTRE[0] - 1, CENTRE[1]],
            [0, CENTRE[1]],
        ],
        12,
        BRASS,
    )
    p.neon.ring(CENTRE[0] + 0.05, 0.4, 12, N, Placement([0, CENTRE[1] - 2, 0]))
    p.hull.cylinder(ARBOR[0], ARBOR[1] - CENTRE[1], 8, M.panel, Placement([0, CENTRE[1], 0]))


def _draw_towers(p: Any) -> None:
    """Draw the corner towers' drums (FB-CLOCKWORK-CITADEL-04): stone, corbelled, lit windows.

    The front pair's belfries and the back pair's roofs are their parts and hatches.
    """
    for sx in SIDES:
        for sy in SIDES:
            at = boss_point(sx * TOWER_AT[0], sy * TOWER_AT[1], 0)
            place = Placement([at[0], 0, at[2]])
            p.flesh.lathe(TOWER_PROFILE, 12, STONE, place)
            p.flesh.ring(TOWER_RADIUS + 0.05, 1.2, 12, COURSE, Placement([at[0], 12, at[2]]))
            p.neon.ring(
                TOWER_RADIUS + 1.25, 0.35, 12, N, Placement([at[0], TOWER_TOP - 1.4, at[2]])
            )
            p.hull.cylinder(TOWER_RADIUS, 0.3, 12, M.base, Placement([at[0], TOWER_TOP, at[2]]))
            for k in range(5):
                a = k * 2 * math.pi / 5 + 0.3
                q = [
                    at[0] + math.cos(a) * (TOWER_RADIUS + 0.05),
                    19,
                    at[2] + math.sin(a) * (TOWER_RADIUS + 0.05),
                ]
                p.charge.box([0.7, 2.6, 0.7], N, Placement(q, -a))


def _draw_gatehouse(p: Any) -> None:
    """Draw the gatehouse (FB-CLOCKWORK-CITADEL-05): its arch, lit, the noon gun's pit on top."""
    depth = -GATE[1] - BLOCK + 2
    mid = boss_point(0, GATE[1] + depth / 2, -2)
    p.flesh.bevel_slab(
        [
            pt(-GATE[0], GATE[1]),
            pt(GATE[0], GATE[1]),
            pt(GATE[0], -BLOCK + 2),
            pt(-GATE[0], -BLOCK + 2),
        ],
        [-2, GATE[2] - 0.8, GATE[2]],
        [1, 0.5],
        STONE,
        None,
        COURSE,
    )
    front = -GATE[1] + 0.05
    p.bare.box([8, 7, 0.2], M.dark, Placement([0, 1, front]))
    p.neon.box([9, 0.5, 0.4], N, Placement([0, 8, front]))
    for s in SIDES:
        p.neon.box([0.5, 7, 0.4], N, Placement([s * 4.4, 1, front]))
        p.flesh.box(
            [3, GATE[2] + 3, 3], STONE, Placement([s * (GATE[0] - 1), -2, front - 1.6]), COURSE
        )
        p.neon.box([0.8, 0.8, 0.8], N, Placement([s * (GATE[0] - 1), GATE[2] + 1, front - 1.6]))
    gun = boss_point(NOON_AT[0], NOON_AT[1], GATE[2])
    p.hull.cylinder(5, 0.4, 10, M.base, Placement(gun))
    p.neon.ring(5.05, 0.3, 10, N, Placement(gun))
    p.hull.box([2.2, 0.5, depth], M.panel, Placement([mid[0], GATE[2], mid[2]]))


def _draw_sponsons(p: Any) -> None:
    """Draw the casemates' and broadsides' sponsons: half drums off the walls, open on top."""
    spots = [
        CASEMATE_AT,
        [-CASEMATE_AT[0], CASEMATE_AT[1]],
        BROADSIDE_AT,
        [-BROADSIDE_AT[0], BROADSIDE_AT[1]],
    ]
    for spot in spots:
        at = boss_point(spot[0], spot[1], 0)
        p.flesh.bevel_slab(
            polygon(8, 4.6),
            [0, CASEMATE_TOP - 0.6, CASEMATE_TOP],
            [1.6, 0.4],
            STONE,
            Placement([at[0], 0, at[2]], math.pi / 8),
            COURSE,
        )
        p.neon.ring(4.55, 0.3, 8, N, Placement([at[0], CASEMATE_TOP - 0.5, at[2]], math.pi / 8))
        p.bare.cylinder(3.2, 0.15, 8, M.dark, Placement([at[0], CASEMATE_TOP, at[2]], math.pi / 8))


def _draw_flanks(p: Any) -> None:
    """Draw the flanks' steelwork (FB-CLOCKWORK-CITADEL-06, -10): shelves, rails, the bracket.

    A shelf on brackets under each gear train, the two rails each great wheel slides out on (with
    stops at their ends), the pendulum's bracket and axle on the back wall.
    """
    for s in SIDES:
        g = boss_point(s * GEARS_AT[0], GEARS_AT[1], 0)
        p.hull.bevel_slab(
            polygon(8, 12.5),
            [SHELF_TOP - 2.4, SHELF_TOP - 0.5, SHELF_TOP],
            [1.4, 0.3],
            M.base,
            Placement([g[0] - s * 1, 0, g[2]], math.pi / 8),
            M.dark,
        )
        for dy in [-6, 6]:
            q = boss_point(
                s * (WHEEL_AT[0] + WHEEL_SLIDE / 2 - 2), WHEEL_AT[1] + dy, SHELF_TOP - 2.4
            )
            p.hull.box([WHEEL_SLIDE + 26, 2.4, 1.6], M.base, Placement(q))
            end = boss_point(s * (WHEEL_AT[0] + WHEEL_SLIDE + 11), WHEEL_AT[1] + dy, SHELF_TOP)
            p.hull.box([1.2, 1.6, 2], M.panel, Placement(end))
            p.neon.box([0.6, 0.4, 0.6], N, Placement([end[0], SHELF_TOP + 1.6, end[2]]))
    pivot = boss_point(PENDULUM_PIVOT[0], PENDULUM_PIVOT[1], 0)
    p.hull.box([10, 7, 6], M.panel, Placement([pivot[0], 6, pivot[2] + 2]), M.base)
    p.hull.cylinder(2.6, 1.4, 8, BRASS, Placement([pivot[0], 13, pivot[2]]))


def build_clockwork_citadel(scene: Any) -> Any:
    """FB-CLOCKWORK-CITADEL-01, FB-CLOCKWORK-CITADEL-04: the Clockwork Citadel.

    A clock-tower fortress 5 L across, brass light lines (shown yellow).
    """

    def core(p: Any) -> None:
        _draw_plinth(p)
        _draw_block(p)
        _draw_pit(p)
        _draw_towers(p)
        _draw_gatehouse(p)
        _draw_sponsons(p)
        _draw_flanks(p)

    return build_boss_model(
        CLOCKWORK_CITADEL,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "gear-left": gear_train,
                "gear-right": gear_train,
                "pendulum": bob,
                "hand": minute_hand,
                "bell-left": belfry,
                "bell-right": belfry,
            },
            "limbs": pendulum_limbs(),
            "armour": citadel_armour(),
            "rig": {"build": build_citadel_rig, "triangles": rig_triangles},
        },
    )
