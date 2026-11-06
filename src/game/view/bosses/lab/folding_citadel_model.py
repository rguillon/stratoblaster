# Copyright (c) 2026 Renaud Guillon
"""FB-FOLDING-CITADEL-01 to FB-FOLDING-CITADEL-04: the Folding Citadel, the Lab's L-9 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A flat, square fortress folded shut like an
origami box: a square base deck, a stepped keep in its middle, an octagonal tower at each corner,
hinge knuckles along its edges; its four wall panels (`folding_citadel_panels`) are moving pieces
leaning in over the courtyard, which swing open flat like a flower. A machine, not a creature: the
Lab's second round drops the animal look (user request, 2026-11-06).
"""

import math

from game.config.bosses.lab.folding_citadel import (
    BASE,
    CUPOLA_TOP,
    FOLDING_CITADEL,
    HINGE_H,
    KEEP_GUN_AT,
    KEEP_HALF,
    KEEP_TOP,
    ROTOR_AT,
    TOWER_AT,
    TOWER_RADIUS,
    TOWER_TOP,
    WALL_GUN_HEIGHT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.folding_citadel_panels import N, citadel_armour
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The keep's two steps: the lower block's top, the upper block's half width.
KEEP_STEP = 19
KEEP_UPPER = 13.5
# The hinge knuckles along each edge of the base (centres along the edge) and their length.
KNUCKLES = [-30, 0, 30]
KNUCKLE = 9


def _square(half: float) -> list[list[float]]:
    return [[-half, -half], [half, -half], [half, half], [-half, half]]


def _draw_deck(p: Any) -> None:
    """Draw the base deck (FB-FOLDING-CITADEL-02): a square slab, its edges the panels' hinges.

    Its courtyard (bared as the panels open) lit by strips from the keep out to each hinge, grated
    bays at its back corners; the hinge knuckles along its edges; a buttress out to each tower.
    """
    p.hull.bevel_slab(_square(BASE), [0, HINGE_H - 1.2, HINGE_H], [1.4, 0.6], M.base)
    for k in range(4):
        yaw = k * math.pi / 2
        c = math.cos(yaw)
        s = math.sin(yaw)
        # A lit strip from the keep's foot out to the hinge's middle, and its knuckles.
        a = KEEP_HALF + 1
        b = BASE - 3
        mid = [(a + b) / 2, 0]
        p.neon.box([b - a, 0.4, 0.8], N, Placement([mid[0] * c, HINGE_H, -mid[0] * s], yaw))
        for u in KNUCKLES:
            at = [-BASE * c + u * s, HINGE_H - 1.6, BASE * s + u * c]
            p.hull.cylinder(
                1.7,
                KNUCKLE,
                8,
                M.panel,
                Placement(
                    [at[0] - s * KNUCKLE / 2, at[1], at[2] - c * KNUCKLE / 2], yaw, math.pi / 2
                ),
            )
    for sx in [-1, 1]:
        bay = boss_point(sx * 30, 30, HINGE_H)
        p.bare.box([16, 0.5, 16], M.dark, Placement(bay))
        for k in range(4):
            p.bare.box([15, 0.9, 0.9], M.panel, Placement([bay[0], HINGE_H, bay[2] - 6 + 4 * k]))
        # The buttresses out to the towers.
        for sy in [-1, 1]:
            corner = boss_point(sx * (BASE - 4), sy * (BASE - 4), 0)
            tower = boss_point(sx * TOWER_AT, sy * TOWER_AT, 0)
            p.hull.slab(_buttress(corner, tower), [0, HINGE_H - 1], M.panel)
    for sx in [-1, 1]:
        for k in range(3):
            p.bare.box(
                [3.5, 1.4, 6],
                M.dark,
                Placement(boss_point(sx * (KEEP_HALF + 6), 6 - 10 * k, HINGE_H)),
            )


def _buttress(a: Vec3, b: Vec3) -> list[list[float]]:
    """Return the outline (model XZ) of a buttress 9 px wide from `a` to `b`."""
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    n = math.sqrt(dx * dx + dz * dz)
    ox = -dz / n * 4.5
    oz = dx / n * 4.5
    return [
        [a[0] + ox, a[2] + oz],
        [b[0] + ox, b[2] + oz],
        [b[0] - ox, b[2] - oz],
        [a[0] - ox, a[2] - oz],
    ]


def _draw_keep(p: Any) -> None:
    """Draw the keep (FB-FOLDING-CITADEL-02): two stepped square blocks in the middle.

    A lit band and window slits round its lower block, a parapet on its roof with a pinnacle at
    each corner, the seat of its fan turret on its front and the rotor's well under the hatch.
    """
    p.hull.bevel_slab(_square(KEEP_HALF), [HINGE_H, KEEP_STEP - 1.5, KEEP_STEP], [0, 1.2], M.panel)
    p.hull.bevel_slab(
        _square(KEEP_UPPER), [KEEP_STEP, KEEP_TOP - 1.5, KEEP_TOP], [0, 1], M.base, None, M.panel
    )
    p.neon.box([KEEP_HALF * 2 + 0.3, 0.6, KEEP_HALF * 2 + 0.3], N, Placement([0, 12, 0]))
    for k in range(4):
        yaw = k * math.pi / 2
        c = math.cos(yaw)
        s = math.sin(yaw)
        for u in [-9, -3, 3, 9]:
            q = [-(KEEP_HALF + 0.1) * c + u * s, 7.5, (KEEP_HALF + 0.1) * s + u * c]
            p.neon.box([0.5, 2.6, 1.2], N, Placement(q, yaw))
        q = [-(KEEP_UPPER + 0.1) * c, 24, (KEEP_UPPER + 0.1) * s]
        p.neon.box([0.5, 0.6, KEEP_UPPER * 1.6], N, Placement(q, yaw))
        # The parapet round its roof's edge, and a vent grille on each face of its upper block.
        q = [-(KEEP_UPPER - 0.9) * c, KEEP_TOP, (KEEP_UPPER - 0.9) * s]
        p.hull.box([1.2, 1.1, KEEP_UPPER * 2 - 1.6], M.panel, Placement(q, yaw), M.base)
        for v in [-1, 1]:
            q = [-(KEEP_UPPER + 0.05) * c + v * 6 * s, 20.6, (KEEP_UPPER + 0.05) * s + v * 6 * c]
            p.bare.box([0.6, 1.8, 6], M.dark, Placement(q, yaw))
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            q = boss_point(sx * (KEEP_UPPER - 2), sy * (KEEP_UPPER - 2), KEEP_TOP)
            p.hull.box([3.6, 3, 3.6], M.panel, Placement(q), M.base)
            p.neon.box([1, 0.6, 1], N, Placement([q[0], KEEP_TOP + 3, q[2]]))
    gun = boss_point(KEEP_GUN_AT[0], KEEP_GUN_AT[1], 0)
    p.hull.cylinder(6.4, 1.2, 10, M.panel, Placement([gun[0], KEEP_TOP - 0.6, gun[2]]))
    p.neon.ring(6.5, 0.35, 10, N, Placement([gun[0], KEEP_TOP + 0.2, gun[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(6.6, 0.6, 8, M.dark, Placement([well[0], KEEP_TOP - 0.5, well[2]]))


def _draw_towers(p: Any) -> None:
    """Draw the corner towers (FB-FOLDING-CITADEL-02): octagonal, tapering, a lit ring near the top.

    The front bastions' and the rear towers' cupolas are their parts.
    """
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            at = boss_point(sx * TOWER_AT, sy * TOWER_AT, 0)
            p.hull.lathe(
                [
                    [TOWER_RADIUS + 1, 0],
                    [TOWER_RADIUS + 1, 2],
                    [TOWER_RADIUS, 3],
                    [TOWER_RADIUS - 1.2, TOWER_TOP],
                ],
                8,
                M.panel,
                Placement(at, math.pi / 8),
            )
            p.neon.ring(
                TOWER_RADIUS - 0.75,
                0.6,
                8,
                N,
                Placement([at[0], TOWER_TOP - 4, at[2]], math.pi / 8),
            )
            for k in range(4):
                a = math.pi / 4 + k * math.pi / 2
                q = [
                    at[0] + math.cos(a) * (TOWER_RADIUS - 0.4),
                    8,
                    at[2] + math.sin(a) * (TOWER_RADIUS - 0.4),
                ]
                p.bare.box([1.2, 3.2, 1.2], M.dark, Placement(q, -a))


def _wall_gun(p: Any, at: Vec3) -> None:
    """Add a wall gun's cowl (FB-FOLDING-CITADEL-03): an armoured ring on its sponson, lit."""
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, 5.8),
        [WALL_GUN_HEIGHT - 2.8, WALL_GUN_HEIGHT - 1, WALL_GUN_HEIGHT],
        [0, 0.6],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(5.85, 0.4, 8, N, Placement([x, WALL_GUN_HEIGHT - 1.6, z], math.pi / 8))
    s = 1 if x < 0 else -1
    for dz in [-4.6, 4.6]:
        p.hull.box([2.4, 4, 1.4], M.base, Placement([x - s * 4.2, WALL_GUN_HEIGHT - 4, z + dz]))


def _cupola(p: Any, at: Vec3, fins: bool) -> None:
    """Add a tower's cupola (FB-FOLDING-CITADEL-03): an armoured octagonal cap, its gun's seat.

    A lit ring round it; the rear towers' have fins standing round their laser.
    """
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, TOWER_RADIUS - 0.6),
        [TOWER_TOP - 0.5, TOWER_TOP + 2.2, CUPOLA_TOP],
        [0.2, 1.6],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(TOWER_RADIUS - 0.5, 0.4, 8, N, Placement([x, TOWER_TOP + 1.2, z], math.pi / 8))
    if fins:
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            q = [
                x + math.cos(a) * (TOWER_RADIUS - 2),
                CUPOLA_TOP - 0.4,
                z + math.sin(a) * (TOWER_RADIUS - 2),
            ]
            p.hull.box([0.9, 3.4, 3], M.base, Placement(q, -a))
            p.neon.box([0.4, 0.4, 1.4], N, Placement([q[0], CUPOLA_TOP + 3, q[2]], -a))


def _bastion(p: Any, at: Vec3) -> None:
    _cupola(p, at, False)


def _tower(p: Any, at: Vec3) -> None:
    _cupola(p, at, True)


def build_folding_citadel(scene: Any) -> Any:
    """FB-FOLDING-CITADEL-01, FB-FOLDING-CITADEL-04: the Folding Citadel.

    A square fortress folded shut like an origami box, its four wall panels leaning in round its
    keep, a tower at each corner, orange light lines (shown yellow) along its creases; 4.5 L across
    once its panels have swung open flat.
    """

    def core(p: Any) -> None:
        _draw_deck(p)
        _draw_keep(p)
        _draw_towers(p)

    return build_boss_model(
        FOLDING_CITADEL,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "wall-left": _wall_gun,
                "wall-right": _wall_gun,
                "bastion-left": _bastion,
                "bastion-right": _bastion,
                "tower-left": _tower,
                "tower-right": _tower,
            },
            "armour": citadel_armour(),
        },
    )
