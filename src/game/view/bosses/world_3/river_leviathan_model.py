"""P09-R09, 3-1: the River Leviathan. Ported from `view/bosses/world-3/river-leviathan-model.ts`.
Logical pixels, nose +Z, Y up (towards the camera). A serpent-ship: an armoured, wedge-shaped head
(its core) with a dorsal crest, glaring teal eyes, fang guns and a laser lens on its snout; behind
it, its swaying body (`river-leviathan-body`)."""

import math

from org.transcrypt.stubs.browser import __pragma__

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
from game.view.bosses.world_2.narwhal_parts import SUB_SECTION
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

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

N = LEVIATHAN_TEAL

# The head (loft stations, neck to snout: z, half width, bottom, top).
HEAD = table(
    [
        [-24, 13, -3, 10],
        [-12, 17, -4, 13],
        [2, 18, -4, 13.5],
        [14, 15, -3, 11],
        [23, 10, -1.5, 8],
        [29, 5.5, 0.5, 6],
    ]
)
# The dorsal crest on the head, seen from the side (z, height), rolled upright.
CREST = table([[-18, 12.5], [-12, 17.5], [4, 17.5], [10, 13]])
# The crest emitter's housing (a lathe profile from the crest's top).
EMITTER = table([[3.6, 0], [3.4, 0.8], [2.2, 1.3], [0, 1.5]])


def draw_head(p: EnemyParts) -> None:
    """The head's hull, its jaw line, the teal light along its back and its glaring eyes."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a living serpent's head of teal flesh, its scutes and jaw line grafted armour.
    flesh.loft(SUB_SECTION, HEAD, F.teal)
    for s in SIDES:
        gland(p, [s * 9, 10.6, 10], 2.2, N)
    # The jaw line: a dark lip round the snout, under the eyes.
    for s in SIDES:
        hull.box([2, 2.4, 22], H.dark, Placement([s * 13.5, 1, 12], -s * 0.3))
        hull.box([1.4, 1.2, 16], SHADE["edge"], Placement([s * 15.4, 9.6, -6]))
    neon.box([1.2, 0.5, 30], N, Placement([0, 13.55, -6]))
    for eye in angry_eyes(table([0, 18]), 9, [6, 1.6], 0.35):
        decal(neon, eye, 11.4, N)
    points: list[Vec3] = []
    for z in [-16, -6]:
        for s in SIDES:
            points.append([s * 8, 13, z])
    scutes(hull, points, 2)
    moss(
        hull,
        [[-11, -20], [-4, -18], [-5, -12], [-12, -14]],
        12.5,
    )
    stone(hull, [10, 12.6, -16], 2.4, 0.7)


def draw_crest(p: EnemyParts) -> None:
    """The crest on its back and the ring emitter at its top (the core's spirals)."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(LEVIATHAN_CREST) == 0:
        return
    tip = LEVIATHAN_CREST[0]
    top = boss_point(tip[0], tip[1], tip[2])
    # P16-R06: a membrane fin on its back, the emitter grafted at its top.
    flesh.slab(
        CREST,
        [-1.4, 1.4],
        F.membrane,
        Placement(None, -QUARTER, -QUARTER),
        F.bone,
    )
    base = offset(top, 0, -1.5, 0)
    hull.lathe(EMITTER, 8, H.dark, Placement(base))
    neon.ring(3.7, 0.5, 8, N, Placement(base))
    charge.cylinder(1.2, 0.2, 6, WHITE, Placement(offset(top, 0, -0.2, 0)))
    muzzle(top, "ring")


def draw_snout(p: EnemyParts) -> None:
    """The snout: the laser lens at its tip, the fang guns at its cheeks, teeth under its lip."""
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
    """The core of the River Leviathan: its head, crest and snout."""
    draw_head(p)
    draw_crest(p)
    draw_snout(p)


def build_river_leviathan(scene: Any) -> Any:
    """P09-R09: the River Leviathan, a segmented serpent-ship 6 L long, teal neon along its spine:
    an armoured head with a crest, its four segments with their ring turrets and its tail with a
    missile rack swaying one after the other behind it, moss and vines from the river."""
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
        },
    )
