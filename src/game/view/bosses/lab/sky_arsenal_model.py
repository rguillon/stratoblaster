# Copyright (c) 2026 Renaud Guillon
"""FB-SKY-ARSENAL-01 to FB-SKY-ARSENAL-04: the Sky Arsenal, the Lab's L-14 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A tiered flying fortress stacked like a
wedding cake of gun decks: a broad lower tier (its four corner petals are moving pieces of their
own, `sky_arsenal_parts`), a middle tier, the turntable the top tier turns on, the lift engines'
ducted fans slung under the lower tier's flanks, an ammunition hoist and the slide rails the petals
run out on. A machine, not a creature: the Lab's third round builds flying fortresses (user
request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.sky_arsenal import (
    BOW_AT,
    CRANE_AT,
    CRANE_HEIGHT,
    ENGINE_RADIUS,
    ENGINE_X,
    LOW_HALF,
    LOW_TOP,
    MID_HALF,
    MID_TOP,
    PETAL_CUT,
    SKY_ARSENAL,
    TOP_HALF,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import grille, rod
from game.view.bosses.lab.sky_arsenal_parts import (
    PLATE,
    bastion,
    crane,
    deck_gun,
    petal_armour,
    xz,
)
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["sky-arsenal"]
# The middle tier's walls: darker than the lower tier's, so the tiers read apart.
WALL = [0.07, 0.072, 0.085]
# The ammunition hoist on the middle tier's back right corner (config `[x, y]`).
HOIST_AT = [27, 27]


def _low_outline() -> list[list[float]]:
    """Return the lower tier's outline without its petals: an octagon (model XZ)."""
    c = PETAL_CUT - LOW_HALF
    h = LOW_HALF
    return [
        xz(-c, -h),
        xz(c, -h),
        xz(h, -c),
        xz(h, c),
        xz(c, h),
        xz(-c, h),
        xz(-h, c),
        xz(-h, -c),
    ]


def _square(half: float) -> list[list[float]]:
    return [[-half, -half], [half, -half], [half, half], [-half, half]]


def _draw_lower_tier(p: Any) -> None:
    """Draw the lower tier (FB-SKY-ARSENAL-02): a broad plated octagon between the petals.

    Gun ports round its flanks, a lit band, deck plates, the bow turret's seat, and the slide rails
    each petal runs out on along its diagonal.
    """
    p.hull.bevel_slab(_low_outline(), [0, 4.5, LOW_TOP], [4.5, 0.8], M.base, None, M.panel)
    p.neon.box([LOW_HALF * 2 - 4, 0.5, 0.5], N, Placement([0, 5, LOW_HALF - 0.4]))
    p.neon.box([LOW_HALF * 2 - 4, 0.5, 0.5], N, Placement([0, 5, -LOW_HALF + 0.4]))
    for k in range(4):
        yaw = k * math.pi / 2
        c = math.cos(yaw)
        s = math.sin(yaw)
        for u in [-9, -3, 3, 9]:
            q = [-(LOW_HALF + 0.05) * c + u * s, 6, (LOW_HALF + 0.05) * s + u * c]
            p.bare.box([0.5, 1.6, 2.6], M.dark, Placement(q, yaw))
    # Deck plates on the flanks, between the middle tier's foot and the engines' pylons.
    for sx in [-1, 1]:
        at = boss_point(sx * 43, 0, 0)
        p.hull.bevel_slab(
            [[at[0] + q[0] * 0.25, at[2] + q[1]] for q in _square(14)],
            [LOW_TOP - 0.2, LOW_TOP - 0.2, LOW_TOP + 0.5],
            [0, 0.4],
            PLATE,
        )
    # Vent grilles either side of the bow turret.
    for sx in [-1, 1]:
        vent = boss_point(sx * 15.5, -43, 0)
        grille(p.hull, [vent[0], vent[2]], [7, 6], [4, LOW_TOP + 0.05])
    seat = boss_point(BOW_AT[0], BOW_AT[1], 0)
    p.hull.cylinder(6.6, 1, 10, M.panel, Placement([seat[0], LOW_TOP - 0.2, seat[2]]))
    p.neon.ring(6.65, 0.35, 10, N, Placement([seat[0], LOW_TOP + 0.5, seat[2]]))
    # The petals' slide rails: two girders out along each diagonal, under the petal.
    d = 1 / math.sqrt(2)
    edge = PETAL_CUT * d
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            for off in [-6, 6]:
                ox = -sy * off * d
                oy = sx * off * d
                a = boss_point(sx * (edge - 8) * d + ox, sy * (edge - 8) * d + oy, 2.2)
                b = boss_point(sx * (edge + 18) * d + ox, sy * (edge + 18) * d + oy, 2.2)
                rod(p.hull, a, b, 1.3, M.panel)


def _draw_middle_tier(p: Any) -> None:
    """Draw the middle tier (FB-SKY-ARSENAL-02): a plated square, its walls lit and gun-ported.

    The turntable's track ring the top tier turns on, cross-braced corner buttresses, the hoist.
    """
    h = MID_HALF
    p.hull.bevel_slab(
        _square(h), [LOW_TOP - 0.5, LOW_TOP + 3, MID_TOP], [0, 1.2], WALL, None, PLATE
    )
    for k in range(4):
        yaw = k * math.pi / 2
        c = math.cos(yaw)
        s = math.sin(yaw)
        p.neon.box(
            [0.4, 0.6, h * 2 - 6], N, Placement([-(h + 0.05) * c, MID_TOP - 4, (h + 0.05) * s], yaw)
        )
        for u in [-24, -16, 16, 24]:
            q = [-(h + 0.05) * c + u * s, LOW_TOP + 3, (h + 0.05) * s + u * c]
            p.bare.box([0.6, 2, 3], M.dark, Placement(q, yaw))
    # The turntable: a drum under the top tier and a lit track ring on the deck round it.
    p.hull.cylinder(TOP_HALF - 1, 1.6, 16, M.panel, Placement([0, MID_TOP - 0.6, 0]))
    p.neon.ring(TOP_HALF * 1.24, 0.3, 24, N, Placement([0, MID_TOP + 0.05, 0]))
    p.hull.ring(TOP_HALF * 1.24 + 0.8, 0.5, 24, M.panel, Placement([0, MID_TOP - 0.1, 0]))
    # A balcony on each flank, its windows lit, buttresses down to the lower deck.
    for sx in [-1, 1]:
        at = boss_point(sx * (h + 2), 0, LOW_TOP)
        p.hull.box([4, MID_TOP - LOW_TOP - 3, 16], M.panel, Placement(at), PLATE)
        for k in range(4):
            q = [at[0] - sx * 2.05, MID_TOP - 6, at[2] - 5.4 + 3.6 * k]
            p.neon.box([0.3, 1.4, 1.6], N, Placement(q))
    # The crane's pedestal (what its laser leaves once destroyed stands on it).
    crane_at = boss_point(CRANE_AT[0], CRANE_AT[1], 0)
    p.hull.cylinder(
        5,
        CRANE_HEIGHT - MID_TOP + 0.4,
        8,
        M.panel,
        Placement([crane_at[0], MID_TOP - 0.2, crane_at[2]]),
    )
    # The ammunition hoist: a lattice tower with a shell drum and a stack of crates.
    at = boss_point(HOIST_AT[0], HOIST_AT[1], MID_TOP)
    for sx in [-1, 1]:
        for sz in [-1, 1]:
            rod(
                p.hull,
                [at[0] + sx * 3, MID_TOP, at[2] + sz * 3],
                [at[0] + sx * 2, MID_TOP + 10, at[2] + sz * 2],
                0.5,
                M.panel,
            )
    p.hull.box([5.4, 1.2, 5.4], M.panel, Placement([at[0], MID_TOP + 10, at[2]]), PLATE)
    p.hull.cylinder(
        1.8, 6, 8, M.base, Placement([at[0] - 3, MID_TOP + 6, at[2]], math.pi / 2, math.pi / 2)
    )
    p.neon.box([1, 1, 1], N, Placement([at[0], MID_TOP + 11.2, at[2]]))
    for k in range(3):
        p.hull.box(
            [3.6, 2.4, 3.6],
            M.base,
            Placement([at[0] - 6.5, MID_TOP + k * 2.4, at[2] + 4 - 3 * k], 0.3 * k),
            PLATE,
        )


def _draw_engines(p: Any) -> None:
    """Draw the lift engines (FB-SKY-ARSENAL-02): a ducted fan slung under each flank, spinning.

    A thick duct ring on pylons from the lower tier's side, its fan turning inside it, a lit lip.
    """
    r = ENGINE_RADIUS
    for s in [-1, 1]:
        at = boss_point(s * ENGINE_X, 0, 0)
        p.hull.lathe(
            [[r - 1, -1], [r + 1.4, 0], [r + 1.8, 3], [r + 0.8, 6], [r - 1.2, 5.5]],
            16,
            M.base,
            Placement(at),
            False,
        )
        p.neon.ring(r + 0.9, 0.4, 16, N, Placement([at[0], 5.6, at[2]]))
        p.hull.cylinder(2.6, 5, 8, M.panel, Placement([at[0], -0.5, at[2]]), 1.8)
        p.rotor([at[0], 2.5, at[2]], r - 1.2)
        # The stator arms holding the fan's hub in its duct.
        for k in range(3):
            a = math.pi / 2 + k * 2 * math.pi / 3
            rim = [at[0] + math.cos(a) * (r + 0.4), 0.6, at[2] + math.sin(a) * (r + 0.4)]
            rod(p.hull, [at[0], 0.6, at[2]], rim, 0.7, M.panel)
        for dz in [-6, 6]:
            rod(
                p.hull,
                [at[0], 1.5, at[2] + dz],
                [-s * (LOW_HALF - 4), 3.5, at[2] + dz],
                1.4,
                M.panel,
            )
            rod(
                p.hull,
                [at[0] - (-s) * 2, 4.5, at[2] + dz],
                [-s * (LOW_HALF - 4), 7, at[2] + dz],
                0.8,
                M.base,
            )


def build_sky_arsenal(scene: Any) -> Any:
    """FB-SKY-ARSENAL-01, FB-SKY-ARSENAL-04: the Sky Arsenal.

    A three-tiered flying fortress with blue light lines (shown green), lift engines on its flanks,
    5 L across.
    """

    def core(p: Any) -> None:
        _draw_lower_tier(p)
        _draw_middle_tier(p)
        _draw_engines(p)

    return build_boss_model(
        SKY_ARSENAL,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "deck-left": deck_gun,
                "deck-right": deck_gun,
                "bastion-left": bastion,
                "bastion-right": bastion,
                "crane": crane,
            },
            "armour": petal_armour(),
        },
    )
