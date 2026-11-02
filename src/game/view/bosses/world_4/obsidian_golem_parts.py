# Copyright (c) 2026 Renaud Guillon
"""FB-OBSIDIAN-GOLEM-03 to FB-OBSIDIAN-GOLEM-05, 4-3: the Obsidian Golem's parts, arms and look.

The parts: its fists, shoulder cannons, chest emitter and armour plate. The arms:
FB-OBSIDIAN-GOLEM-07. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_4.obsidian_golem import (
    ARMS,
    GOLEM_ARM,
    GOLEM_CANNON_GUNS,
    GOLEM_KNUCKLES,
    GOLEM_LENS,
    side_of,
)
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_shapes import mirrored
from game.view.bosses.mini_boss_greebles import seam
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset
from game.view.bosses.world_3.toucan_jungle import segment
from game.view.bosses.world_4.living_forge import SKIN, glands
from game.view.bosses.world_4.magma_salamander_parts import barrel
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Rgb = list[float]
type Vec3 = list[float]
type OutlinePoint = list[float]
# __pragma__ ("noskip")


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:
        return fallback
    return colour


def _sign(v: float) -> float:
    """`Math.sign`."""
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


# The Golem's neon: the deep orange of its magma seams (FB-OBSIDIAN-GOLEM-06).
GOLEM_NEON = _neon_or("obsidian-golem", [1, 0.32, 0.04])
# Molten rock glowing in its seams and cracks, hotter than its neon.
MAGMA = [1.0, 0.55, 0.1]
# Black volcanic glass: its armour plates (matte, a touch of violet).
OBSIDIAN = [0.045, 0.04, 0.055]


def crack(neon: Any, path: list[OutlinePoint], y: float) -> None:
    """Add a crack of magma across a surface at height `y`.

    Glowing strips through the points `path`.
    """
    for i in range(1, len(path)):
        seam(neon, path[i - 1], path[i], [y, 0.7, 0.3], MAGMA)


def arm_points(arm: str) -> list[Vec3]:
    """Return the model-space points of `arm` at rest.

    Its shoulder, its elbow and its fist's centre.
    """
    s = side_of(arm)

    def at(point: list[float], h: float) -> Vec3:
        return boss_point(s * point[0], point[1], h)

    return [at(GOLEM_ARM.shoulder, 12), at(GOLEM_ARM.elbow, 10), at(GOLEM_ARM.fist, 8)]


def upper_arm(arm: str) -> Any:
    """Return `arm`'s upper arm, on its shoulder (FB-OBSIDIAN-GOLEM-02).

    A thick, plated strut down to the elbow's joint.
    """

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        flesh = p.flesh
        points = arm_points(arm)
        shoulder = points[0]
        elbow = points[1]
        segment(flesh, [shoulder, elbow], [7, 6], SKIN.base, 6)
        segment(
            hull,
            [offset(shoulder, 0, 4, 0), offset(elbow, 0, 3.6, 0)],
            [3.6, 3],
            OBSIDIAN,
            5,
        )
        segment(
            neon,
            [offset(shoulder, 0, 6.8, 0), offset(elbow, 0, 6.2, 0)],
            [0.5, 0.5],
            MAGMA,
            4,
        )
        hull.cylinder(7.4, 9, 7, H.dark, Placement(offset(elbow, 0, -4.5, 0)))
        neon.ring(7.5, 0.8, 7, GOLEM_NEON, Placement(offset(elbow, 0, 2, 0)))

    return draw


def forearm(arm: str) -> Any:
    """Return `arm`'s forearm, on its elbow (FB-OBSIDIAN-GOLEM-02).

    A massive tapering block of armour down to the wrist.
    """

    def draw(p: Any) -> None:
        neon = p.neon
        flesh = p.flesh
        points = arm_points(arm)
        elbow = points[1]
        fist = points[2]
        wrist = offset(fist, 0, 0, -10)
        segment(flesh, [elbow, wrist], [6.4, 7.6], SKIN.panel, 6)
        for t in [0.35, 0.7]:
            at = [
                elbow[0] + (wrist[0] - elbow[0]) * t,
                elbow[1] + (wrist[1] - elbow[1]) * t,
                elbow[2] + (wrist[2] - elbow[2]) * t,
            ]
            neon.box([1.2, 1, 1.2], MAGMA, Placement(offset(at, 0, 7.4, 0)))

    return draw


def arm_limbs() -> Any:
    """Return the limbs of the two arms (FB-OBSIDIAN-GOLEM-07).

    An upper arm on each shoulder and a forearm on each elbow.
    """
    limbs = {}
    for arm in ARMS:
        limbs["shoulder-" + arm] = record({"draw": upper_arm(arm)})
        limbs["elbow-" + arm] = record({"draw": forearm(arm)})
    return limbs


def fist(p: Any, at: Vec3) -> None:
    """Add a fist around its centre `at` (FB-OBSIDIAN-GOLEM-03), on its elbow.

    A huge block of obsidian, four knuckles with magma glowing between them, a thumb on the inside,
    and the magma vent in the middle of its knuckles that throws rings of slow, big globs.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    s = _sign(at[0])
    base = offset(at, 0, -1, -2)
    p.flesh.box([26, 15, 20], SKIN.base, Placement(base), SKIN.panel)
    glands(p, [offset(at, s * 8, 13.6, -6)], 2, GOLEM_NEON)
    hull.box([27, 4, 21], H.dark, Placement(offset(base, 0, 4, 0)))
    for k in range(4):
        x = (k - 1.5) * 6.2
        hull.box([5.6, 8, 5], H.panel, Placement(offset(at, x, 1, 9)), SHADE["edge"])
        if k > 0:
            neon.box([0.6, 6, 4], MAGMA, Placement(offset(at, x - 3.1, 1.6, 9.4)))
    p.flesh.box([6, 7, 12], SKIN.panel, Placement(offset(at, -s * 15, 0, 2), -s * 0.3))
    crack(
        neon,
        [
            [at[0] + 8, at[2] - 6],
            [at[0] + 2, at[2] - 2],
            [at[0] - 6, at[2] - 7],
        ],
        at[1] + 14.1,
    )
    guns = GOLEM_KNUCKLES if s > 0 else mirror(GOLEM_KNUCKLES)
    for m in guns:
        tip = boss_point(m[0], m[1], m[2])
        hull.cylinder(3.4, 2, 7, H.dark, Placement(offset(tip, 0, 0, -5.4), 0, QUARTER))
        charge.ring(2.6, 1.2, 7, WHITE, Placement(offset(tip, 0, 0, -3.6), 0, QUARTER))
        barrel(p, tip, [1.8, 2.4])


def cannon_mount(p: Any, at: Vec3) -> None:
    """Add a shoulder cannon's mount around its centre `at` (FB-OBSIDIAN-GOLEM-04).

    A low armoured ring on the back of its shoulder, its turret turning on it.
    """
    hull = p.hull
    neon = p.neon
    p.flesh.cylinder(11, 11, 8, SKIN.base, Placement(offset(at, 0, 0, 0), math.pi / 8), 9.6)
    hull.ring(10, 1.2, 8, H.dark, Placement(offset(at, 0, 9.4, 0), math.pi / 8))
    neon.ring(9.8, 0.7, 8, GOLEM_NEON, Placement(offset(at, 0, 10.6, 0), math.pi / 8))


# The cannon turret's dome (a lathe profile around its pivot).
DOME = [
    [8.4, 0.0],
    [8.6, 2.2],
    [6.6, 5.0],
    [3.0, 6.4],
    [0.0, 6.6],
]


def cannon_turret(p: Any, at: Vec3) -> None:
    """Add a shoulder cannon's turret around its pivot `at` (FB-OBSIDIAN-GOLEM-04, D-060).

    A faceted dome on its mount and two heavy barrels, turning the way their aimed spreads fire.
    """
    hull = p.hull
    hull.lathe(DOME, 8, OBSIDIAN, Placement(offset(at, 0, 11, 0), math.pi / 8))
    hull.box([9, 4, 6], H.dark, Placement(offset(at, 0, 13, 7)), H.panel)
    # The left cannon (screen left) is on the model's +X side.
    guns = GOLEM_CANNON_GUNS if at[0] > 0 else mirror(GOLEM_CANNON_GUNS)
    for m in guns:
        barrel(p, boss_point(m[0], m[1], m[2]), [1.2, 7])


# The armour plate seen from above: a chevron of obsidian over the chest (right half).
PLATE = mirrored([
    [0, 14],
    [12, 10],
    [19, 2],
    [16, -10],
    [0, -6],
])


def plate(p: Any, at: Vec3) -> None:
    """Add the armour plate around its centre `at` (FB-OBSIDIAN-GOLEM-05, no weapon).

    A thick chevron of obsidian on its chest, cracked with magma, bolted on with dark studs.
    """
    hull = p.hull
    neon = p.neon
    x = at[0]
    z = at[2]
    hull.bevel_slab(PLATE, [2, 10, 17], [1, 2], H.base, Placement([x, 0, z]), OBSIDIAN)
    crack(
        neon,
        [
            [x - 10, z + 6],
            [x - 2, z + 2],
            [x + 3, z + 7],
            [x + 11, z + 3],
        ],
        17.1,
    )
    crack(
        neon,
        [
            [x - 2, z + 2],
            [x, z - 5],
        ],
        17.1,
    )
    for s in SIDES:
        hull.cylinder(1.4, 1, 6, SHADE["edge"], Placement([x + s * 13, 16.6, z + 3]))
        neon.box([0.6, 6, 0.6], GOLEM_NEON, Placement([x + s * 18.4, 8, z + 1]))


# The emitter's housing on its prow (a lathe profile along its axis, from its back).
HOUSING = [
    [5.0, 0.0],
    [8.0, 3.0],
    [8.6, 9.0],
    [6.8, 14.0],
    [5.0, 16.0],
]


def emitter(p: Any, at: Vec3) -> None:
    """Add the chest emitter around its centre `at` (FB-OBSIDIAN-GOLEM-05).

    A heavy housing on the prow under the plate, ringed in orange, its lens glowing as the laser
    charges; the beam fires straight down.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(GOLEM_LENS) == 0:
        return
    m = GOLEM_LENS[0]
    lens = boss_point(m[0], m[1], m[2])
    back = [lens[0], lens[1], lens[2] - 17.4]
    hull.lathe(HOUSING, 8, H.panel, Placement(back, math.pi / 8, QUARTER))
    neon.ring(8.8, 1, 8, GOLEM_NEON, Placement(offset(back, 0, 0, 8), 0, QUARTER))
    p.flesh.box([12, 4, 14], SKIN.panel, Placement(offset(at, 0, -2, -4)))
    charge.cylinder(4.4, 1.4, 8, WHITE, Placement(offset(lens, 0, 0, -1.4), 0, QUARTER))
    muzzle(lens, "laser")
