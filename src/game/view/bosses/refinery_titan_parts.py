"""P07-R05, P16-R06: the Refinery Titan's destroyable parts (fuel bladders, rotary turrets, missile
brood), ported from `bosses/refinery-titan-parts.ts`, each drawn around its centre `at` (model
space: logical pixels, nose +Z, Y up).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.bosses.world_1_organic_kit import F, graft, polygon, vein_line  # noqa: E402
from game.view.enemies.enemy_shapes import POD_SECTION, decal  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2
# Orange: the boss's neon (GD-61).
TITAN_NEON = BOSS_LOOK.neon["refinery-titan"]

# Heights the parts stand on: the tank beam, the turret sponson, the hull's back.
TITAN_DECK = {"beam": 3, "sponson": 8, "back": 13}


def rect(w: float, d: float, at: Any = None) -> list[Any]:
    """A rectangle `w` wide and `d` long around (x, z)."""
    x = 0 if at == None else at[0]  # noqa: E711
    z = 0 if at == None else at[1]  # noqa: E711
    return [
        [x - w / 2, z - d / 2],
        [x + w / 2, z - d / 2],
        [x + w / 2, z + d / 2],
        [x - w / 2, z + d / 2],
    ]


# A fuel tank lying along Z (a lathe profile along its axis): a capsule of octagonal section, a
# flat on top, ringed with glowing bands.
TANK_PROFILE = [
    [0, -22],
    [8, -21],
    [12.5, -17],
    [14, -10],
    [14, 10],
    [12.5, 17],
    [8, 21],
    [0, 22],
]
TANK_RADIUS = 14
# Where the bands sit along the tank, and the lit windows between them.
TANK_BANDS = [-13.2, -1.2, 10.8]
TANK_WINDOWS = [-6, 6]


def draw_tank(parts: Any, at_point: Vec3) -> None:
    """P07-R05, P16-R06: a big fuel bladder held in the limbs, a swollen sac of flesh, orange bands
    of neon and glowing veins on it, grafted valves at its ends."""
    hull = parts.hull
    flesh = parts.flesh
    neon = parts.neon
    vein = parts.vein
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    axis = y + TITAN_DECK["beam"] + 9

    # Pitched, the lathe's axis runs along +Z; rolled by an eighth of a turn, a flat faces up.
    def along(dz: float) -> Any:
        return Placement([x, axis, z + dz], 0, QUARTER, math.pi / 8)

    flesh.lathe(TANK_PROFILE, 8, F.crimson, along(0))
    for dz in TANK_BANDS:
        neon.ring(TANK_RADIUS * 1.04, 2.4, 8, TITAN_NEON, along(dz))
    # The top flat of the octagon, a little above it: two lit windows and a valve.
    top = axis + TANK_RADIUS * math.cos(math.pi / 8)
    for dz in TANK_WINDOWS:
        decal(vein, rect(3.2, 7, [x, z + dz]), top + 0.05, TITAN_NEON)
    hull.cylinder(2.6, 3.2, 6, H.dark, Placement([x, top - 1.2, z + 15]), 1.8)
    hull.cylinder(2.6, 3.2, 6, H.dark, Placement([x, top - 1.2, z - 15]), 1.8)


# A rotary turret's base: a low faceted dome, its armoured barrel housing.
TURRET_BASE = [
    [12.5, 0],
    [13, 2.5],
    [10.5, 5.5],
    [6, 8],
    [0, 8.6],
]
TURRET_HOUSING = [
    [-5, 5, -3.2, 3.4],
    [4, 5.4, -3.6, 3.8],
    [11, 4.4, -3, 3.2],
]
# The barrels around the rotary axis (x, y), their length and radius.
BARRELS = [
    [0, 1.8],
    [-2.2, -1.2],
    [2.2, -1.2],
]
BARREL_LENGTH = 10
BARREL_RADIUS = 1.3


def draw_turret(p: Any, at_point: Vec3) -> None:
    """P07-R05, P16-R06: a rotary turret's base on the front apron, a swollen growth plated round
    its crown, under its turret (`draw_rotary`)."""
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + TITAN_DECK["sponson"]
    p.flesh.lathe(TURRET_BASE, 8, F.purple, Placement([x, base, z]))
    p.neon.ring(13.3, 0.9, 8, TITAN_NEON, Placement([x, base + 1, z]))
    graft(p, polygon(8, 9), [base + 5.6, base + 7], [x, 0, z], {"color": H.base})


def draw_rotary(p: Any, at_point: Vec3) -> None:
    """A rotary turret: its housing and three barrels with charge-lit muzzles, on its base."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    mark = p.muzzle
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    axis = y + TITAN_DECK["sponson"] + 9
    hull.loft(POD_SECTION, TURRET_HOUSING, H.panel, Placement([x, axis, z]))
    front = z + TURRET_HOUSING[2][0]
    # The barrel shroud, then the barrels; their muzzles light up as the spiral charges.
    hull.cylinder(4.6, 1.6, 6, H.dark, Placement([x, axis, front], 0, QUARTER))
    for b in BARRELS:
        bx = b[0]
        by = b[1]
        muzzle = Placement([x + bx, axis + by, front], 0, QUARTER)
        hull.cylinder(BARREL_RADIUS, BARREL_LENGTH, 6, H.dark, muzzle)
        tip = [x + bx, axis + by, front + BARREL_LENGTH]
        charge.cylinder(BARREL_RADIUS * 1.25, 1.6, 6, WHITE, Placement(tip, 0, QUARTER))
        mark([tip[0], tip[1], tip[2] + 1.6])
    # A neon sight slit along the housing's top.
    decal(neon, rect(1.4, 8, [x, z + 2]), axis + 3.9, TITAN_NEON)


# The missile battery's cells: 2 columns by 3 rows on its top.
CELLS = [[cx, cz] for cx in [-5.5, 5.5] for cz in [-7.5, 0, 7.5]]

# The block under the missile battery's cells.
BLOCK = [
    [-11, -13],
    [11, -13],
    [13.5, -9],
    [13.5, 10],
    [9, 13.5],
    [-9, 13.5],
    [-13.5, 10],
    [-13.5, -9],
]


def draw_missile_battery(p: Any, at_point: Vec3) -> None:
    """P07-R05, P16-R06: a missile brood on the body's back, a swollen mound under a grafted plate
    with six hatches lit as it loads."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + TITAN_DECK["back"]
    top = base + 8
    p.flesh.bevel_slab(
        BLOCK,
        [base - 2, base, top - 1],
        [0, 3],
        F.crimson,
        Placement([x, 0, z]),
        F.sinew,
    )
    hull.bevel_slab(
        BLOCK,
        [top - 1.2, top - 1.2, top],
        [0, 1],
        H.base,
        Placement([x, 0, z]),
        H.panel,
    )
    for cell in CELLS:
        cx = cell[0]
        cz = cell[1]
        decal(hull, rect(7.4, 5.6, [x + cx, z + cz]), top + 0.04, H.dark)
        decal(charge, rect(5.4, 3.6, [x + cx, z + cz]), top + 0.08, WHITE)
        muzzle([x + cx, top + 0.08, z + cz], "missile")
    # Neon strips down both flanks of the block.
    for s in [-1, 1]:
        neon.box([0.6, 1.4, 16], TITAN_NEON, Placement([x + s * 12.6, base + 3.2, z]))
        vein_line(
            p,
            [x + s * 13, base, z - 12],
            [x + s * 22, base - 4, z - 20],
            [0, 2, 0],
            1,
            TITAN_NEON,
        )
