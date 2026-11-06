# Copyright (c) 2026 Renaud Guillon
"""FB-THRONE-OF-STORMS-01 to FB-THRONE-OF-STORMS-05: the Throne of Storms, the L-15 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A round sky castle on a floating disc of rock:
the rock's jagged rim and its spurs (a prow, a stern and a spur at each side), the rails its corner
towers slide out on, the keep in the middle with the throne on its roof under a tall lightning
spire, the generators' masts, and the barbican's and the loft's foundations. Its towers, ward and
curtain wall are pieces of their own (`throne_of_storms_parts`); the spire's lightning is its rig
(`throne_of_storms_storm`).
"""

import math

from game.config.bosses.lab.throne_of_storms import (
    BARBICAN_AT,
    BARBICAN_TOP,
    GENERATOR_AT,
    GENERATOR_TOP,
    KEEP_R,
    KEEP_TOP,
    LOFT_AT,
    LOFT_TOP,
    ROCK_R,
    ROCK_TOP,
    SLIDE_OUT,
    SPIRE_AT,
    SPIRE_TOP,
    THRONE_GUN_AT,
    THRONE_OF_STORMS,
    TOWER_AT,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, grille, rod
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.throne_of_storms_parts import (
    STONE,
    STONE_DARK,
    STONE_LIGHT,
    N,
    pt,
    throne_armour,
    tower_crown,
)
from game.view.bosses.lab.throne_of_storms_storm import build_storm_rig, storm_triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The rock: weathered, dark, greyed (BOSS-50), its underside darker still.
ROCK = [0.3, 0.29, 0.28]
ROCK_UNDER = [0.18, 0.17, 0.17]
# The rock's spurs (config outlines): the right one under its generator, the prow under the
# barbican, the stern under the loft.
SPUR_SIDE = [[50, -13], [70, -12], [83, -5], [85, 5], [76, 14], [56, 15], [48, 6]]
SPUR_PROW = [[-17, -50], [17, -50], [19, -61], [9, -72], [-9, -72], [-19, -61]]
SPUR_STERN = [[q[0], -q[1]] for q in SPUR_PROW]


def _model(outline: list[Any]) -> list[Any]:
    """Return a config outline (`[x, y]`, Y up the screen) in model space (`[-x, -y]`)."""
    return [[-q[0], -q[1]] for q in outline]


def _draw_rock(p: Any) -> None:
    """Draw the floating rock (FB-THRONE-OF-STORMS-02): a jagged disc tapering to a point below.

    Its spurs, boulders round its rim, and lit crystal seams in its flanks.
    """
    p.hull.lathe(
        [
            [0, -44],
            [14, -34],
            [30, -22],
            [46, -10],
            [ROCK_R - 2, -3],
            [ROCK_R + 1, 1],
            [ROCK_R, ROCK_TOP],
            [0, ROCK_TOP],
        ],
        14,
        ROCK,
        Placement([0, 0, 0], 0.2),
    )
    for spur in [SPUR_SIDE, [[-q[0], q[1]] for q in SPUR_SIDE], SPUR_PROW, SPUR_STERN]:
        p.hull.bevel_slab(_model(spur), [-12, ROCK_TOP - 1.5, ROCK_TOP], [5, 1.2], ROCK)
    # Boulders and crags round the rim.
    for k in range(11):
        a = k * math.pi * 2 / 11 + 0.15
        r = ROCK_R - 2 + (k % 3)
        at = [math.cos(a) * r, ROCK_TOP - 2.5, math.sin(a) * r]
        size = 4 + (k % 4)
        p.hull.box([size, 3 + k % 3, size * 0.8], ROCK, Placement(at, a + 0.4 * k), ROCK_UNDER)
    # Lit crystal seams on the rock's flanks, glowing with the storm.
    for k in range(6):
        a = k * math.pi / 3 + 0.5
        a0 = [math.cos(a) * (ROCK_R - 6), -6, math.sin(a) * (ROCK_R - 6)]
        a1 = [math.cos(a + 0.1) * (ROCK_R - 16), -18, math.sin(a + 0.1) * (ROCK_R - 16)]
        rod(p.neon, a0, a1, 0.5, N)


def _draw_rails(p: Any) -> None:
    """Draw the rails the towers slide out on (FB-THRONE-OF-STORMS-05).

    Two lit rails along each corner's diagonal, from under the tower out past the rock's rim on a
    girder, an end stop at their ends.
    """
    for c in [[1, 1], [-1, 1], [1, -1], [-1, -1]]:
        sx = c[0]
        sy = c[1]
        inner = TOWER_AT - 9
        outer = TOWER_AT + SLIDE_OUT + 9
        for k in [-1, 1]:
            ox = k * 3.4
            oy = -k * 3.4 * sx * sy
            a = pt(sx * inner + ox, sy * inner + oy, 0)
            b = pt(sx * outer + ox, sy * outer + oy, 0)
            edge_strips(
                p.hull, [[a[0], a[2]], [b[0], b[2]]], 1.6, [ROCK_TOP - 1, ROCK_TOP], STONE_DARK
            )
            edge_strips(p.neon, [[a[0], a[2]], [b[0], b[2]]], 0.5, [ROCK_TOP, ROCK_TOP + 0.2], N)
        # The girder under the rails' outer ends, from the rock out, and the end stop.
        g0 = pt(sx * (TOWER_AT + 4), sy * (TOWER_AT + 4), ROCK_TOP - 3.5)
        g1 = pt(sx * outer, sy * outer, ROCK_TOP - 3.5)
        rod(p.hull, g0, g1, 2.6, STONE_DARK)
        stop = pt(sx * (outer + 1), sy * (outer + 1), ROCK_TOP - 4)
        p.hull.box([4, 5, 4], SHADE["mid"], Placement(stop, math.pi / 4))
        p.neon.box([2, 0.5, 2], N, Placement([stop[0], ROCK_TOP + 1, stop[2]], math.pi / 4))


def _draw_keep(p: Any) -> None:
    """Draw the keep (FB-THRONE-OF-STORMS-02): a round stone drum, buttressed, lit bands round it.

    The throne on its roof: its dais, its armrests and its tall back, the spire rising from it.
    """
    p.hull.lathe(
        [[KEEP_R + 3, ROCK_TOP - 0.5], [KEEP_R, ROCK_TOP + 6], [KEEP_R, KEEP_TOP], [0, KEEP_TOP]],
        12,
        STONE,
        Placement([0, 0, 0], math.pi / 12),
    )
    p.neon.ring(KEEP_R + 0.15, 0.8, 12, N, Placement([0, KEEP_TOP - 5, 0], math.pi / 12))
    p.neon.ring(KEEP_R + 0.15, 0.4, 12, N, Placement([0, ROCK_TOP + 9, 0], math.pi / 12))
    p.hull.ring(KEEP_R + 0.6, 1.6, 12, STONE_LIGHT, Placement([0, KEEP_TOP - 1.6, 0], math.pi / 12))
    # The dais the throne gun stands on (its mount, BOSS-58).
    dais = pt(THRONE_GUN_AT[0], THRONE_GUN_AT[1], KEEP_TOP - 0.4)
    p.hull.cylinder(6.4, 1, 10, SHADE["dark"], Placement(dais, math.pi / 10))
    # The armrests either side of the seat, a lit line along their tops.
    for s in [-1, 1]:
        rest = [[s * 9, -15], [s * 13, -15], [s * 13, 10], [s * 9, 10]]
        p.hull.bevel_slab(_model(rest), [KEEP_TOP - 1, KEEP_TOP + 4, KEEP_TOP + 5], [0, 0.8], STONE)
        a = pt(s * 11, -14, 0)
        b = pt(s * 11, 9, 0)
        edge_strips(p.neon, [[a[0], a[2]], [b[0], b[2]]], 0.5, [KEEP_TOP + 5, KEEP_TOP + 5.15], N)
    # The throne's tall back behind the seat, stepped, and the spire rising from its crown.
    back = [
        [-12, SPIRE_AT[1] - 3.5],
        [12, SPIRE_AT[1] - 3.5],
        [9, SPIRE_AT[1] + 3.5],
        [-9, SPIRE_AT[1] + 3.5],
    ]
    p.hull.bevel_slab(_model(back), [KEEP_TOP - 1, KEEP_TOP + 12, KEEP_TOP + 13], [0, 1], STONE)
    high = [
        [-7, SPIRE_AT[1] - 3],
        [7, SPIRE_AT[1] - 3],
        [5, SPIRE_AT[1] + 3],
        [-5, SPIRE_AT[1] + 3],
    ]
    p.hull.bevel_slab(
        _model(high), [KEEP_TOP + 12, KEEP_TOP + 19, KEEP_TOP + 20], [0, 1], STONE_LIGHT
    )
    face = pt(0, SPIRE_AT[1] - 3.6, KEEP_TOP + 3)
    p.neon.box([8, 8, 0.4], N, Placement(face))
    p.hull.box([6, 7, 0.6], STONE_DARK, Placement([face[0], face[1] + 0.5, face[2] + 0.3]))
    _draw_spire(p, KEEP_TOP + 20)


def _draw_spire(p: Any, foot: float) -> None:
    """Draw the lightning spire from `foot` up to its tip: a tapering mast, coils and a lit orb."""
    at = pt(SPIRE_AT[0], SPIRE_AT[1], foot)
    p.hull.cylinder(2.6, SPIRE_TOP - foot, 6, SHADE["mid"], Placement(at), 0.6)
    for k in range(3):
        h = foot + 4 + k * 8
        r = 4.2 - k * 0.9
        p.neon.ring(r, 0.6, 8, N, Placement([at[0], h, at[2]]))
        p.hull.cylinder(r - 0.4, 0.5, 8, SHADE["dark"], Placement([at[0], h - 0.5, at[2]]))
    p.neon.cylinder(1.6, 2.6, 6, N, Placement([at[0], SPIRE_TOP - 1.3, at[2]]), 0.2)


def _draw_masts(p: Any) -> None:
    """Draw what stands under the parts' guns on the rock (their stumps stay on it, BOSS-18).

    The generators' bare masts on their platforms, the barbican's and the loft's foundations.
    """
    for s in [-1, 1]:
        at = pt(s * GENERATOR_AT[0], GENERATOR_AT[1], ROCK_TOP - 0.5)
        p.hull.cylinder(9, 1.8, 8, SHADE["mid"], Placement(at, math.pi / 8), 8)
        p.hull.cylinder(2.2, GENERATOR_TOP - ROCK_TOP, 6, SHADE["dark"], Placement(at), 1.8)
        grille(p.hull, [at[0] + s * 0, at[2] + 6.5], [6, 3], [3, ROCK_TOP + 1.4])
    found = [[-15, -51], [15, -51], [13, -66], [-13, -66]]
    p.hull.bevel_slab(
        _model(found), [ROCK_TOP - 1, ROCK_TOP + 1, ROCK_TOP + 2], [0, 0.6], STONE_DARK
    )
    gun = pt(BARBICAN_AT[0], BARBICAN_AT[1] - 4, ROCK_TOP)
    p.hull.box([6, BARBICAN_TOP - ROCK_TOP - 0.6, 5], SHADE["dark"], Placement(gun))
    p.hull.bevel_slab(
        _model([[q[0], -q[1]] for q in found]),
        [ROCK_TOP - 1, ROCK_TOP + 1, ROCK_TOP + 2],
        [0, 0.6],
        STONE_DARK,
    )
    loft = pt(LOFT_AT[0], LOFT_AT[1] + 2, ROCK_TOP)
    p.hull.box([12, LOFT_TOP - ROCK_TOP - 0.4, 9], SHADE["dark"], Placement(loft))


def _tower(p: Any, at: Vec3) -> None:
    tower_crown(p, at)


def _generator(p: Any, at: Vec3) -> None:
    """Add a storm generator (FB-THRONE-OF-STORMS-03): a coil tower round its mast.

    A stone plinth, three lit coils stacked up it and a crown its laser turret stands on.
    """
    p.hull.lathe(
        [
            [7.5, ROCK_TOP + 1],
            [6, ROCK_TOP + 6],
            [3.4, ROCK_TOP + 8],
            [3.4, GENERATOR_TOP - 3],
            [0, GENERATOR_TOP - 3],
        ],
        8,
        STONE,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    for k in range(3):
        h = ROCK_TOP + 10 + k * 5
        r = 7 - k * 1.2
        p.hull.cylinder(r, 2.2, 10, SHADE["base"], Placement([at[0], h, at[2]]), r - 0.6)
        p.neon.ring(r + 0.05, 0.6, 10, N, Placement([at[0], h + 0.8, at[2]]))
    p.hull.cylinder(
        6, 3, 8, SHADE["panel"], Placement([at[0], GENERATOR_TOP - 3, at[2]], math.pi / 8), 5.4
    )
    # Its insulators: four short lit studs round its crown.
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        q = [at[0] + math.cos(a) * 6.4, GENERATOR_TOP - 2.4, at[2] + math.sin(a) * 6.4]
        p.hull.cylinder(0.9, 2.6, 6, SHADE["light"], Placement(q))
        p.neon.box([1, 0.6, 1], N, Placement([q[0], GENERATOR_TOP + 0.2, q[2]]))


def _barbican(p: Any, _at: Vec3) -> None:
    """Add the barbican (FB-THRONE-OF-STORMS-03): a squat gatehouse on the rock's prow.

    Two round flanking turrets, a lit portcullis in its face, its wall gun on its front (BOSS-58).
    """
    body = [[-11, -66], [11, -66], [11, -50], [-11, -50]]
    p.hull.bevel_slab(
        _model(body), [ROCK_TOP, BARBICAN_TOP - 1.2, BARBICAN_TOP], [0, 1], STONE, None, STONE_LIGHT
    )
    for s in [-1, 1]:
        tur = pt(s * 11, -62, 0)
        p.hull.lathe(
            [
                [5, ROCK_TOP],
                [4.4, BARBICAN_TOP + 3],
                [5.2, BARBICAN_TOP + 3],
                [5.2, BARBICAN_TOP + 4.6],
                [0, BARBICAN_TOP + 4.6],
            ],
            8,
            STONE,
            Placement(tur, math.pi / 8),
        )
        p.neon.ring(5.3, 0.5, 8, N, Placement([tur[0], BARBICAN_TOP + 3.6, tur[2]], math.pi / 8))
    # The portcullis: lit bars in a dark doorway on its face.
    door = pt(0, -66.3, ROCK_TOP)
    p.hull.box([9, 7, 0.8], SHADE["dark"], Placement(door))
    for k in range(4):
        p.neon.box(
            [0.5, 6, 0.4], N, Placement([door[0] - 3.3 + k * 2.2, ROCK_TOP + 0.4, door[2] + 0.3])
        )


def _loft(p: Any, _at: Vec3) -> None:
    """Add the rocket loft (FB-THRONE-OF-STORMS-03): a long hall with a ribbed roof at its back.

    Its block of rocket ports stands on its roof (BOSS-58); lit slits along its sides.
    """
    hall = [[-12, 50], [12, 50], [12, 67], [-12, 67]]
    p.hull.bevel_slab(
        _model(hall), [ROCK_TOP, LOFT_TOP - 1.4, LOFT_TOP - 0.4], [0, 1.4], STONE, None, STONE_LIGHT
    )
    for k in range(4):
        y = 52 + k * 4.5
        if abs(y - LOFT_AT[1] - 2) < 5:
            continue
        rib = pt(0, y, LOFT_TOP - 0.6)
        p.hull.box([22, 0.8, 1.2], SHADE["mid"], Placement(rib))
    for s in [-1, 1]:
        a = pt(s * 12.2, 52, 0)
        b = pt(s * 12.2, 65, 0)
        edge_strips(p.neon, [[a[0], a[2]], [b[0], b[2]]], 0.5, [ROCK_TOP + 3, ROCK_TOP + 3.8], N)


def build_throne_of_storms(scene: Any) -> Any:
    """FB-THRONE-OF-STORMS-01, FB-THRONE-OF-STORMS-04: the Throne of Storms.

    A round sky castle on a floating rock, 5.5 L across with magenta lights: its front towers'
    turrets, its generators' lasers, the barbican's wall gun, the loft's rockets, the throne gun
    and the spire rotor (their mounts, drawn by `build_boss_model`, BOSS-58). Its towers slide out
    at its first transformation, its ward and wall burst off at its second (FB-THRONE-OF-STORMS-05);
    its spire crackles with lightning (its rig, FB-THRONE-OF-STORMS-12).
    """

    def core(p: Any) -> None:
        _draw_rock(p)
        _draw_rails(p)
        _draw_keep(p)
        _draw_masts(p)

    return build_boss_model(
        THRONE_OF_STORMS,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "tower-left": _tower,
                "tower-right": _tower,
                "generator-left": _generator,
                "generator-right": _generator,
                "barbican": _barbican,
                "loft": _loft,
            },
            "armour": throne_armour(),
            "rig": {"build": build_storm_rig, "triangles": storm_triangles},
        },
    )
