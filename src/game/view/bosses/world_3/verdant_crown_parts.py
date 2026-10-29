"""P09-R09, 3-5: the Verdant Crown's destroyable parts (thorn cannons, seed batteries, root
generators), each drawn around its centre `at`, each turret around its pivot. Ported from
`view/bosses/world-3/verdant-crown-parts.ts`. Model space: logical pixels, nose +Z, Y up."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_3.verdant_crown import VERDANT_SEEDS, VERDANT_THORN
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_3.jungle_flesh import F, table
from game.view.bosses.world_3.verdant_crown_garden import (
    DECK_TOP,
    EMERALD,
    JUNGLE,
    MAGENTA,
    strut,
)
from game.view.enemies.enemy_shapes import POD_SECTION, around, decal, radial
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# Height of the outriggers' top, where the thorn cannons turn.
OUTRIGGER_TOP = 3


def rect(w: float, d: float, centre: list[float] | None = None) -> list[OutlinePoint]:
    """A rectangle `w` wide and `d` long around (x, z) (the origin by default)."""
    x: float = 0
    z: float = 0
    if centre is not None:
        x = centre[0]
        z = centre[1]
    return [
        [x - w / 2, z - d / 2],
        [x + w / 2, z - d / 2],
        [x + w / 2, z + d / 2],
        [x - w / 2, z + d / 2],
    ]


# A thorn cannon's pod (loft stations around its pivot), mossy on its back.
THORN_POD = table(
    [
        [-13, 5.5, 0, 7],
        [-4, 7.5, -0.5, 9],
        [9, 6.5, 0, 8.5],
        [15, 4, 2, 7],
    ]
)
POD_BACK = 2
# The lens at the front of its barrel (lathe profile, along the barrel).
LENS = table([[0, 0], [3.2, 1], [2.2, 3], [0, 3.6]])
# The thorns along its barrel: how far along from the pod, and how they are turned (roll).
THORNS = table([[3, 0], [6, 1.1], [9, -1.1], [12, 0], [15, 1.1], [18, -1.1]])


def pod_paint(side: int, band: int) -> Any:
    """The thorn pod's paint: its back mossy."""
    if side == POD_BACK:
        return JUNGLE["moss"]
    return None


def thorn_cannon(p: EnemyParts, pos: Vec3) -> None:
    """A thorn cannon (P09-R09), turning on its outrigger's turntable (D-073): a mossy pod crowned
    with magenta spikes, a long barrel bristling with thorns, its lens glowing as the laser
    charges."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = pos[0]
    z = pos[2]
    at: Vec3 = [x, OUTRIGGER_TOP, z]
    hull.loft(
        POD_SECTION,
        THORN_POD,
        H.base,
        Placement(at),
        LoftOptions(False, pod_paint),
    )
    source = VERDANT_THORN if x < 0 else mirror(VERDANT_THORN)
    tip = boss_point(source[0][0], source[0][1], source[0][2]) if len(source) > 0 else at
    lens_at = tip[2] - LENS[3][1]
    start = z + 14
    hull.cylinder(
        2.4,
        lens_at - start,
        6,
        JUNGLE.bark,
        Placement([x, tip[1], start], 0, QUARTER),
        1.9,
    )
    for thorn in THORNS:
        dz = thorn[0]
        roll = thorn[1]
        sx = -math.sin(roll) * 2
        sy = math.cos(roll) * 2
        hull.lathe(
            [[0.9, 0], [0, 3]],
            3,
            H.panel,
            Placement([x + sx, tip[1] + sy, start + dz], 0, 0, roll),
        )
    charge.lathe(LENS, 6, WHITE, Placement([x, tip[1], lens_at], 0, QUARTER))
    muzzle(tip, "laser")
    for dx in [-3, 0, 3]:
        neon.lathe(
            [[1, 0], [0, 4 + (2 if dx == 0 else 0)]],
            4,
            MAGENTA,
            Placement([x + dx, OUTRIGGER_TOP + 8.6, z - 2]),
        )
    neon.box([0.6, 0.8, 18], EMERALD, Placement([x + 7, OUTRIGGER_TOP + 3, z]))
    neon.box([0.6, 0.8, 18], EMERALD, Placement([x - 7, OUTRIGGER_TOP + 3, z]))


def thorn_mount(p: EnemyParts, pos: Vec3) -> None:
    """The turntable a thorn cannon turns on: a low drum on the outrigger, ringed with magenta."""
    x = pos[0]
    z = pos[2]
    # P16-R06: a swollen knuckle of flesh at the limb's end, a metal turntable grafted on top.
    p.flesh.cylinder(10, OUTRIGGER_TOP - 1, 7, F.crimson, Placement([x, 0, z]), 8.4)
    p.hull.cylinder(8.8, 1, 8, H.dark, Placement([x, OUTRIGGER_TOP - 1, z]))
    p.neon.ring(10.3, 0.6, 8, MAGENTA, Placement([x, OUTRIGGER_TOP - 0.4, z]))


def seed_point(a: float) -> list[float]:
    """A point of a seed battery's pod outline (around its centre), at turn `a`."""
    r = radial(a, 1, 0)
    return [r[0] * 12, r[2] * 15.5]


# A seed battery's pod seen from above (around its centre): a long, rounded seed.
SEED_POD = [seed_point(a) for a in around(10)]
HATCH = [7, 5.6]


def seed_battery(p: EnemyParts, pos: Vec3) -> None:
    """A seed battery (P09-R09): a mossy armoured seed pod on the deck, six hatches lit as its
    missiles load, magenta strips down its sides, leaves sprouting at its ends."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = pos[0]
    z = pos[2]
    source = VERDANT_SEEDS if x < 0 else mirror(VERDANT_SEEDS)
    cells = [boss_point(m[0], m[1], m[2]) for m in source]
    height = cells[0][1] if len(cells) > 0 else 0
    top = height - 0.08
    pod: list[OutlinePoint] = [[x + pt[0], z + pt[1]] for pt in SEED_POD]
    # P16-R06: a living seed pod of purple flesh, its hatches grafted metal.
    flesh.bevel_slab(
        pod,
        [DECK_TOP - 1, DECK_TOP + 2, top],
        [0, 3],
        F.purple,
        None,
        JUNGLE["moss"],
    )
    for cell in cells:
        cx = cell[0]
        cz = cell[2]
        decal(hull, table(rect(HATCH[0], HATCH[1], [cx, cz])), top + 0.04, H.dark)
        decal(charge, table(rect(HATCH[0] - 2, HATCH[1] - 2, [cx, cz])), height, WHITE)
        muzzle([cx, height, cz], "missile")
    for s in [-1, 1]:
        neon.box([0.6, 1.2, 18], MAGENTA, Placement([x + s * 12.1, DECK_TOP + 1.6, z]))
        leaf = Placement([x, top - 1, z + s * 14], 0, s * 0.6)
        hull.box([5, 0.6, 7], JUNGLE["leaf"], leaf)


# The roots of a root generator: their turns around it (from the nose), and how far they reach.
ROOTS = [0.3, 1.5, 2.6, 3.7, 4.9]
ROOT_REACH = 12


def root_generator(p: EnemyParts, pos: Vec3) -> None:
    """A root generator (P09-R09; no weapon, it shields the core): a glowing magenta seed on a stone
    pedestal, gnarled roots arching from it into the deck, an emerald ring round its foot."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    x = pos[0]
    z = pos[2]
    hull.lathe(
        [[8, 0], [7, 3], [4.5, 5]],
        6,
        JUNGLE["stone"],
        Placement([x, DECK_TOP, z]),
    )
    neon.lathe(
        [[0, 0], [4.4, 2.4], [3.8, 6], [0, 8]],
        6,
        MAGENTA,
        Placement([x, DECK_TOP + 5, z]),
    )
    for i in range(len(ROOTS)):
        a = ROOTS[i]
        top: Vec3 = [x + math.sin(a) * 3, DECK_TOP + 8 + (i % 2), z + math.cos(a) * 3]
        knee: Vec3 = [x + math.sin(a) * 8, DECK_TOP + 6.5, z + math.cos(a) * 8]
        foot: Vec3 = [
            x + math.sin(a) * ROOT_REACH,
            DECK_TOP,
            z + math.cos(a) * ROOT_REACH,
        ]
        # P16-R06: roots of living sinew arching from the seed into the beast's flesh.
        strut(flesh, [top, knee], [1.7, 1.5], F.sinew, 5)
        strut(
            flesh,
            [knee, foot],
            [1.5, 1.1],
            JUNGLE["moss"] if i % 2 == 0 else F.crimson,
            5,
        )
    neon.ring(ROOT_REACH + 0.6, 0.6, 10, EMERALD, Placement([x, DECK_TOP + 0.1, z]))
