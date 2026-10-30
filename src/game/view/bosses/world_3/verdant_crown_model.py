"""P09-R09, 3-5: the Verdant Crown, World 3's last boss. Model space: logical pixels, nose +Z (down
the
screen), Y up towards the camera; +X is the screen's left. A city-ship: an overgrown deck carrying
a glass garden dome over the core, a gun deck on its bow, outriggers out to the thorn cannons."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_3.verdant_crown import (
    VERDANT_CROWN,
    VERDANT_GUNS,
    VERDANT_HATCHES,
    VERDANT_LENS,
)
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.overlord_city import (
    edge_lights,
    symmetric,
)
from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, table, vein_to
from game.view.bosses.world_3.verdant_crown_city import draw_city
from game.view.bosses.world_3.verdant_crown_garden import (
    DECK_TOP,
    EMERALD,
    JUNGLE,
    MAGENTA,
    draw_garden,
)
from game.view.bosses.world_3.verdant_crown_parts import (
    OUTRIGGER_TOP,
    rect,
    root_generator,
    seed_battery,
    thorn_cannon,
    thorn_mount,
)
from game.view.enemies.enemy_shapes import SIDES, decal, flip_x
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# The deck (right half, front to tail), closed across the bow.
DECK = symmetric(
    [
        [18, 88],
        [40, 72],
        [58, 44],
        [64, 0],
        [60, -40],
        [46, -70],
        [24, -88],
    ],
    92,
)
# The right outrigger (mirrored on the left), out to the thorn cannon's turntable.
OUTRIGGER = table(
    [
        [56, 30],
        [94, 20],
        [102, 12],
        [102, -2],
        [94, -10],
        [56, -18],
    ]
)
# The engine block across the stern.
ENGINES = rect(64, 12, [0, -88])
# The gun deck on the bow, and its top.
BOW = rect(26, 18, [0, 76])
BOW_TOP = 7
# The block the core's missile hatches open in, behind the dome.
HATCH_BLOCK = rect(26, 18, [0, -52])
LENS = table([[0, 0], [3.4, 1], [2.2, 3], [0, 3.6]])


def draw_hull(p: EnemyParts) -> None:
    """The deck with its lit rim, the engine block, the outriggers wrapped in vines."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a colossal living plant-beast: its back a broad body of moss-skinned flesh, the
    # city grafted on it, its outriggers fleshy limbs, veins pulsing out from under the dome.
    flesh.bevel_slab(DECK, [-8, -2, DECK_TOP], [3, 3], F.sinew, None, JUNGLE_FLESH)
    for a in [0.5, 1.6, 2.6, 3.7, 4.7, 5.8]:
        out: Vec3 = [math.sin(a) * 74, DECK_TOP + 0.3, math.cos(a) * 74]
        start: Vec3 = [math.sin(a) * 34, DECK_TOP + 0.3, math.cos(a) * 34]
        vein_to(p, [start, out], [0, 0, 6], EMERALD, 1.6)
    edge_lights(
        neon,
        DECK,
        [i for i in range(len(DECK))],
        [-2.6, -1.4],
        EMERALD,
    )
    hull.bevel_slab(ENGINES, [-7, -1, 5], [1, 1.5], H.dark, None, H.base)
    for s in SIDES:
        wing = OUTRIGGER if s > 0 else flip_x(OUTRIGGER)
        flesh.bevel_slab(wing, [-4, -1, OUTRIGGER_TOP], [1, 2], F.sinew, None, JUNGLE["moss"])
        edge_lights(neon, wing, [0, 1, 2, 3, 4], [-1.5, -0.5], MAGENTA)
        for dz in [-6, 0, 6]:
            hull.box(
                [0.9, 0.5, 26],
                JUNGLE["leaf"],
                Placement([s * 70, OUTRIGGER_TOP, 6 + dz], dz * 0.03),
            )


def draw_bow(p: EnemyParts) -> None:
    """The gun deck on the bow: twin cannons and a laser lens, charging before they fire."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    hull.bevel_slab(BOW, [DECK_TOP - 1, DECK_TOP, BOW_TOP], [0, 1], H.panel, None, JUNGLE["stone"])
    decal(neon, table(rect(18, 1.2, [0, 70])), BOW_TOP + 0.05, MAGENTA)
    front = 84
    for m in VERDANT_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        hull.cylinder(
            1.8,
            tip[2] - 2 - (front - 12),
            6,
            H.dark,
            Placement([tip[0], tip[1], front - 12], 0, QUARTER),
            1.5,
        )
        charge.cylinder(
            1.7,
            2,
            6,
            WHITE,
            Placement([tip[0], tip[1], tip[2] - 2], 0, QUARTER),
            1.2,
        )
        muzzle(tip)
    lens = boss_point(VERDANT_LENS[0], VERDANT_LENS[1], VERDANT_LENS[2])
    lens_at = lens[2] - LENS[3][1]
    hull.cylinder(
        4,
        lens_at - (front - 14),
        8,
        JUNGLE["stone"],
        Placement([0, lens[1], front - 14], 0, QUARTER),
    )
    charge.lathe(LENS, 6, WHITE, Placement([0, lens[1], lens_at], 0, QUARTER))
    muzzle(lens, "laser")


def draw_hatches(p: EnemyParts) -> None:
    """The missile hatches in their block behind the dome, lit as missiles load."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    height = VERDANT_HATCHES[0][2] if len(VERDANT_HATCHES) > 0 else 9
    hull.bevel_slab(
        HATCH_BLOCK,
        [DECK_TOP - 1, DECK_TOP, height - 0.08],
        [0, 1.5],
        H.base,
    )
    for m in VERDANT_HATCHES:
        hatch = boss_point(m[0], m[1], m[2])
        x = hatch[0]
        y = hatch[1]
        z = hatch[2]
        decal(hull, table(rect(7, 5.4, [x, z])), y - 0.06, H.dark)
        decal(charge, table(rect(5, 3.6, [x, z])), y, WHITE)
        muzzle([x, y, z], "missile")
    neon.box([20, 0.8, 0.6], EMERALD, Placement([0, DECK_TOP + 1, -42.8]))


def verdant_crown_core(p: EnemyParts) -> None:
    """The core of the Verdant Crown: its deck, garden, city, bow and hatches, and its roots."""
    draw_hull(p)
    draw_garden(p)
    draw_city(p)
    draw_bow(p)
    draw_hatches(p)
    for s in SIDES:
        reactor_sac(p, table([s * 12, -1, -94]), 5.5, EMERALD, F.sinew, 8)
        reactor_sac(p, table([s * 26, -1, -94]), 4.2, EMERALD, F.sinew, 8)


def build_verdant_crown(scene: Any) -> Any:
    """P09-R09: the Verdant Crown, a city-ship (6 L) under emerald and magenta neon: an overgrown
    city round a glass garden dome over its core, two thorn cannons on its outriggers, two seed
    batteries aft, two root generators ahead, and a bow carrying twin cannons and a laser."""
    parts: dict[str, Any] = {
        "thorn-left": thorn_mount,
        "thorn-right": thorn_mount,
        "seed-left": seed_battery,
        "seed-right": seed_battery,
        "root-left": root_generator,
        "root-right": root_generator,
    }
    turrets: dict[str, Any] = {"thorn-left": thorn_cannon, "thorn-right": thorn_cannon}
    return build_boss_model(
        VERDANT_CROWN,
        scene,
        EMERALD,
        {"core": verdant_crown_core, "parts": parts, "turrets": turrets},
    )
