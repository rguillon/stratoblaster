# Copyright (c) 2026 Renaud Guillon
"""FB-RIVER-LEVIATHAN-01 to FB-RIVER-LEVIATHAN-07, 3-1: the River Leviathan.

Logical pixels, nose +Z, Y up (towards the camera). A serpent-ship: an armoured, wedge-shaped head
(its core) with a dorsal crest, glaring teal eyes, fang guns and a laser lens on its snout; behind
it, its swaying body (`river-leviathan-body`). The plating of its head is the armour it sheds
(FB-RIVER-LEVIATHAN-13, FB-RIVER-LEVIATHAN-14, D-254): drawn apart from its skull, in two regions.
"""

import math

from game.config.bosses.world_3.river_leviathan import (
    LEVIATHAN_CREST,
    LEVIATHAN_FANGS,
    LEVIATHAN_LENS,
    RIVER_LEVIATHAN,
    SEGMENTS,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import F, gland, table
from game.view.bosses.world_3.mangrove_croc_jungle import barrel_to, moss, scutes, stone
from game.view.bosses.world_3.river_leviathan_body import (
    LEVIATHAN_TEAL,
    leviathan_body,
    missile_rack,
    ring_turret,
    turret_mount,
)
from game.view.enemies.enemy_shapes import SIDES, angry_eyes, decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


N = LEVIATHAN_TEAL

# The head (loft stations, neck to snout: z, half width, bottom, top).
HEAD = table([
    [-24, 13, -3, 10],
    [-12, 17, -4, 13],
    [2, 18, -4, 13.5],
    [14, 15, -3, 11],
    [23, 10, -1.5, 8],
    [29, 5.5, 0.5, 6],
])
# The skull (the core's head) is the head up to `SKULL_TOP`, its back flat; its plating (the armour
# it sheds, FB-RIVER-LEVIATHAN-13 and FB-RIVER-LEVIATHAN-14) is the rest, from `PLATING_BOTTOM`
# (sunk into the skull) up to the head's top, in two regions split at `PLATING_SPLIT`: the back
# plating behind it, the spine plating over the front of the head down to the snout.
SKULL_TOP = 5
PLATING_BOTTOM = 4.7
PLATING_SPLIT = 1
# The head's round section (`SUB_SECTION`) in two halves, counter-clockwise seen from the nose: the
# skull's, its belly and flanks up to a flat back; the plating's, its shoulders and back.
SKULL_SECTION = table([[0.4, 0], [0.92, 0.4], [1, 1], [-1, 1], [-0.92, 0.4], [-0.4, 0]])
PLATING_SECTION = table([[1, 0], [0.85, 0.6], [0.35, 1], [-0.35, 1], [-0.85, 0.6], [-1, 0]])
# The dorsal crest on the head, seen from the side (z, height), rolled upright: a membrane fin
# rooted in the skull, through the plating, so that it stands once the plating is shed (BOSS-52).
CREST = table([
    [-18, SKULL_TOP - 0.5],
    [-18, 12.5],
    [-12, 17.5],
    [4, 17.5],
    [10, 13],
    [10, SKULL_TOP - 0.5],
])
# The crest emitter's housing (a lathe profile from the crest's top).
EMITTER = table([[3.6, 0], [3.4, 0.8], [2.2, 1.3], [0, 1.5]])


def _station(z: float) -> Any:
    """Return the head's loft station at `z`, interpolated between `HEAD`'s stations."""
    for k in range(len(HEAD) - 1):
        a = HEAD[k]
        b = HEAD[k + 1]
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [
                z,
                a[1] + (b[1] - a[1]) * t,
                a[2] + (b[2] - a[2]) * t,
                a[3] + (b[3] - a[3]) * t,
            ]
    return HEAD[len(HEAD) - 1]


def skull_stations() -> Any:
    """Return the skull's loft stations: the head's, flattened to `SKULL_TOP`."""
    return [[st[0], st[1], st[2], SKULL_TOP] for st in HEAD]


def plating_stations(z0: float, z1: float) -> Any:
    """Return the plating's loft stations from `z0` to `z1`: the head's, from `PLATING_BOTTOM`."""
    stations: list[Any] = [_station(z0)]
    stations.extend([st for st in HEAD if z0 < st[0] and st[0] < z1])
    stations.append(_station(z1))
    return [[st[0], st[1], PLATING_BOTTOM, st[3]] for st in stations]


def draw_head(p: EnemyParts) -> None:
    """Draw the skull: the head's teal flesh up to its flat back, its jaw line round the snout.

    FB-RIVER-LEVIATHAN-02: a living serpent's head of teal flesh, its jaw line grafted armour. Its
    plating, with the scutes and the eyes, is drawn apart (`draw_back_plating`,
    `draw_spine_plating`).
    """
    p.flesh.loft(SKULL_SECTION, skull_stations(), F.teal)
    # The jaw line: a dark lip round the snout, under the eyes.
    for s in SIDES:
        p.hull.box([2, 2.4, 22], H.dark, Placement([s * 13.5, 1, 12], -s * 0.3))


def draw_back_plating(p: EnemyParts) -> None:
    """Draw the plating at the back of the head (FB-RIVER-LEVIATHAN-13): the armour shed first.

    The head's shoulders and back behind `PLATING_SPLIT`, from `PLATING_BOTTOM` up to the head's
    top, the worn edges along its shoulders, its scutes, moss and river stone on it.
    """
    hull = p.hull
    p.flesh.loft(PLATING_SECTION, plating_stations(HEAD[0][0], PLATING_SPLIT), F.teal)
    for s in SIDES:
        hull.box([1.4, 1.2, 16], SHADE["edge"], Placement([s * 15.4, 9.6, -6]))
    points: list[Vec3] = [[s * 8, 13, z] for z in [-16, -6] for s in SIDES]
    scutes(hull, points, 2)
    moss(
        hull,
        [[-11, -20], [-4, -18], [-5, -12], [-12, -14]],
        12.5,
    )
    stone(hull, [10, 12.6, -16], 2.4, 0.7)


def draw_spine_plating(p: EnemyParts) -> None:
    """Draw the plating over the front of the head (FB-RIVER-LEVIATHAN-14): the armour shed second.

    The head's shoulders and back from `PLATING_SPLIT` down to the snout, from `PLATING_BOTTOM` up
    to the head's top, the teal glands and the glaring eyes on it.
    """
    last = HEAD[len(HEAD) - 1]
    p.flesh.loft(PLATING_SECTION, plating_stations(PLATING_SPLIT, last[0]), F.teal)
    for s in SIDES:
        gland(p, [s * 9, 10.6, 10], 2.2, N)
    for eye in angry_eyes(table([0, 18]), 9, [6, 1.6], 0.35):
        decal(p.neon, eye, 11.4, N)


def draw_crest(p: EnemyParts) -> None:
    """Draw the crest on its back and the ring emitter at its top (the core's spirals).

    The teal light along the head's back runs along the crest's root.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(LEVIATHAN_CREST) == 0:
        return
    tip = LEVIATHAN_CREST[0]
    top = boss_point(tip[0], tip[1], tip[2])
    # FB-RIVER-LEVIATHAN-03: a membrane fin on its back, the emitter grafted at its top.
    flesh.slab(
        CREST,
        [-1.4, 1.4],
        F.membrane,
        Placement(None, -QUARTER, -QUARTER),
        F.bone,
    )
    neon.box([1.2, 0.5, 28], N, Placement([0, 13.55, -4]))
    base = offset(top, 0, -1.5, 0)
    hull.lathe(EMITTER, 8, H.dark, Placement(base))
    neon.ring(3.7, 0.5, 8, N, Placement(base))
    charge.cylinder(1.2, 0.2, 6, WHITE, Placement(offset(top, 0, -0.2, 0)))
    muzzle(top, "ring")


def draw_snout(p: EnemyParts) -> None:
    """Draw the snout: laser lens at its tip, fang guns at its cheeks, teeth under its lip."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(LEVIATHAN_LENS) > 0:
        lens = LEVIATHAN_LENS[0]
        at = boss_point(lens[0], lens[1], lens[2])
        hull.cylinder(
            3.6,
            5,
            8,
            H.panel,
            Placement(offset(at, 0, 0, -5), 0, QUARTER),
            3,
        )
        neon.ring(3.2, 0.6, 8, N, Placement(offset(at, 0, 0, -1.6), 0, QUARTER))
        charge.cylinder(
            2.4,
            0.6,
            8,
            WHITE,
            Placement(offset(at, 0, 0, -0.6), 0, QUARTER),
        )
        muzzle(at, "laser")
    for tip_def in LEVIATHAN_FANGS:
        barrel_to(p, tip_def, [1.3, 6])
        tip = boss_point(tip_def[0], tip_def[1], tip_def[2])
        x = tip[0]
        z = tip[2]
        hull.box([3.6, 3, 5], H.dark, Placement([x, 1.6, z - 9]), H.panel)
        p.flesh.cylinder(0.9, 2.6, 4, F.bone, Placement([x * 0.6, 2, z - 1], 0, math.pi), 0)


def river_leviathan_core(p: EnemyParts) -> None:
    """Add the core of the River Leviathan: its skull, crest and snout (its plating drawn apart)."""
    draw_head(p)
    draw_crest(p)
    draw_snout(p)


def build_river_leviathan(scene: Any) -> Any:
    """FB-RIVER-LEVIATHAN-01, FB-RIVER-LEVIATHAN-07: the River Leviathan.

    A segmented serpent-ship 6 L long, teal neon along its spine: an armoured head with a crest, its
    four segments with their ring turrets and its tail with a missile rack swaying one after the
    other behind it, moss and vines from the river. The plating of its head is the armour it sheds,
    in two regions (`back`, then `spine`).
    """
    parts: dict[str, Any] = {}
    turrets: dict[str, Any] = {}
    for k in SEGMENTS:
        key = "segment-" + str(k)
        parts[key] = turret_mount
        turrets[key] = ring_turret
    parts["tail-rack"] = missile_rack
    return build_boss_model(
        RIVER_LEVIATHAN,
        scene,
        N,
        {
            "core": river_leviathan_core,
            "parts": parts,
            "turrets": turrets,
            "limbs": leviathan_body(),
            "armour": {
                "back": {"whole": draw_back_plating},
                "spine": {"whole": draw_spine_plating},
            },
        },
    )
