"""P09-R09, 3-5: the Jaguar's destroyable parts (its two claw guns and its tail cannon) and its
spotted armour. Ported from `view/bosses/world-3/jaguar-parts.ts`. Model space: logical pixels,
nose +Z, Y up; each part drawn around its centre `at`, each turret around its pivot."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_3.jaguar import JAGUAR_CLAW, JAGUAR_TAIL
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_3.jungle_flesh import F, sign_of, table, vein_to
from game.view.enemies.enemy_shapes import POD_SECTION, decal
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# Its amber neon (GD-61, `boss-look.ts`).
AMBER = BOSS_LOOK.neon["jaguar"]
# The spotted armour: a warm ochre metal, dark rosettes on it, worn steel talons.
COAT = [0.2, 0.135, 0.06]
ROSETTE = [0.03, 0.022, 0.015]
ROSETTE_HEART = [0.13, 0.08, 0.03]


def rosette(hull: SolidBuilder, at: list[float], r: float, y: float) -> None:
    """A jaguar's rosette painted at height `y` around `[x, z]`: five dark blotches in a ring,
    `r` from its centre, round a darker heart."""
    x = at[0]
    z = at[1]
    heart: list[OutlinePoint] = []
    for k in range(5):
        a = (2 * math.pi * k) / 5
        heart.append([x + math.sin(a) * r * 0.7, z + math.cos(a) * r * 0.7])
    decal(hull, table(heart), y - 0.02, ROSETTE_HEART)
    for k in range(5):
        a = (2 * math.pi * k) / 5 + x * 0.1
        cx = x + math.sin(a) * r
        cz = z + math.cos(a) * r
        u = math.cos(a) * r * 0.42
        v = -math.sin(a) * r * 0.42
        du = math.sin(a) * r * 0.22
        dv = math.cos(a) * r * 0.22
        corners: list[OutlinePoint] = [
            [cx - u - du, cz - v - dv],
            [cx + u - du, cz + v - dv],
            [cx + u * 0.7 + du, cz + v * 0.7 + dv],
            [cx - u * 0.7 + du, cz - v * 0.7 + dv],
        ]
        decal(hull, table(corners), y, ROSETTE)


# A claw's armoured pad around its centre, and the arm reaching back to the wing root.
PAD = table(
    [
        [0, 9],
        [7, 6],
        [8, -3],
        [5, -9],
        [-5, -9],
        [-8, -3],
        [-7, 6],
    ]
)
PAD_TOP = 2.5


def moved(outline: list[OutlinePoint], at: Vec3) -> list[OutlinePoint]:
    """`outline` moved to `[at[0], at[2]]`."""
    return [[px + at[0], pz + at[2]] for px, pz in outline]


def claw_mount(p: EnemyParts, at: Vec3) -> None:
    """A claw gun's mount (P09-R09): an armoured pad on an arm reaching forward from the wing root,
    spotted on top, amber lights along its flank (its gun turns on it, {@link clawTurret})."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    s = sign_of(at[0])
    if s == 0:
        s = 1
    # P16-R05: a muscled paw of spotted flesh, a metal ring grafted where its gun turns.
    flesh.bevel_slab(moved(PAD, at), [-2, 0, PAD_TOP], [1, 1.4], F.sinew, None, COAT)
    flesh.box([7, 3.5, 14], F.sinew, Placement([at[0] - s * 2, -1.5, at[2] - 14]), COAT)
    hull.cylinder(
        7.2,
        0.8,
        8,
        H.panel,
        Placement([at[0], PAD_TOP - 0.6, at[2]], math.pi / 8),
    )
    vein_to(
        p,
        [[at[0] - s * 2, 2.2, at[2] - 20], [at[0] - s * 1, PAD_TOP, at[2] - 6]],
        [0, 0.6, 0],
        AMBER,
    )
    rosette(hull, [at[0] + s * 4, at[2] - 14], 2, 2.05)
    neon.box([0.8, 0.6, 12], AMBER, Placement([at[0] + s * 8.2, 0.2, at[2] - 1], s * 0.12))
    neon.ring(7.6, 0.5, 8, AMBER, Placement([at[0], PAD_TOP - 0.3, at[2]], math.pi / 8))


# The claw gun's housing (a lathe profile, bottom to top) and its talons (from above).
HOUSING = table([[6.5, 0], [7, 1.6], [5.4, 4.2], [2.4, 5.2], [0, 5.4]])
BLADE = table([[-1.5, 0], [1.5, 0], [0.9, 7], [-0.3, 10]])


def barrel(parts: EnemyParts, tip: Vec3, dims: list[float], kind: str = "gun") -> None:
    """A barrel along +Z from `dims[0]` to the muzzle `tip`, its charge light at the tip."""
    start = dims[0]
    bore = dims[1]
    hull = parts.hull
    hull.cylinder(
        bore,
        tip[2] - 2 - start,
        6,
        H.dark,
        Placement([tip[0], tip[1], start], 0, QUARTER),
        bore * 0.85,
    )
    parts.charge.cylinder(
        bore * 1.1,
        2,
        6,
        WHITE,
        Placement([tip[0], tip[1], tip[2] - 2], 0, QUARTER),
        bore * 0.7,
    )
    parts.muzzle(tip, kind)


def claw_turret(p: EnemyParts, at: Vec3) -> None:
    """A claw gun (P09-R09), turning on its pad: a low housing, twin barrels between three steel
    talons curving forward like a paw's claws."""
    hull = p.hull
    neon = p.neon
    source = JAGUAR_CLAW if at[0] < 0 else mirror(JAGUAR_CLAW)
    tips = [boss_point(m[0], m[1], m[2]) for m in source]
    hull.lathe(HOUSING, 8, H.panel, Placement([at[0], PAD_TOP, at[2]], math.pi / 8))
    hull.box([9, 2.6, 4], H.dark, Placement([at[0], 4.6, at[2] + 4]), COAT)
    for tip in tips:
        barrel(p, tip, [at[2] + 4, 1.2])
    for dx in [-5, 0, 5]:
        p.flesh.bevel_slab(
            BLADE,
            [3, 3.6, 4.6],
            [0.2, 0.5],
            F.bone,
            Placement([at[0] + dx, 0, at[2] + (7 if dx == 0 else 5)], dx * 0.05),
        )
    neon.box([4, 0.4, 0.8], AMBER, Placement([at[0], PAD_TOP + 5.1, at[2] - 2.5]))


# The tail cannon's mount: a pod at the tip of the tail, and the pylon its cannon turns on.
PYLON_TOP = 13


def tail_mount(p: EnemyParts, at: Vec3) -> None:
    """The tail cannon's mount (P09-R09): a spotted pod at the tail's tip, a pylon, a lit ring."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a swollen tail tip of spotted flesh, the cannon's metal pylon grafted into it.
    flesh.lathe(
        [[7, -2], [8, 1], [6, 3.5], [3.5, 4]],
        8,
        COAT,
        Placement(at, math.pi / 8),
    )
    hull.cylinder(2.6, PYLON_TOP - 3, 6, H.dark, Placement([at[0], 3, at[2]]), 2)
    neon.ring(8.1, 0.6, 8, AMBER, Placement([at[0], 0.4, at[2]], math.pi / 8))


# The tail cannon's body along Z around its pivot (loft stations: z, half width, bottom, top).
CANNON = table(
    [
        [-9, 2.5, -1.5, 2.5],
        [-4, 4.5, -2.5, 4],
        [4, 4.5, -2.5, 4],
        [8, 3, -1.5, 3],
    ]
)


def tail_turret(p: EnemyParts, at: Vec3) -> None:
    """The tail cannon (P09-R09), turning on its pylon high over the tail: a spotted pod, a long
    barrel reaching forward over the wing, its lens glowing as the laser charges."""
    if len(JAGUAR_TAIL) > 0:
        m = JAGUAR_TAIL[0]
        tip = boss_point(m[0], m[1], m[2])
    else:
        tip = at
    p.hull.loft(
        POD_SECTION,
        CANNON,
        COAT,
        Placement([at[0], PYLON_TOP + 2.5, at[2]]),
    )
    rosette(p.hull, [at[0], at[2] - 3], 1.4, PYLON_TOP + 6.55)
    barrel(p, tip, [at[2] + 8, 1.8], "laser")
    for dz in [at[2] + 12, at[2] + 17]:
        p.neon.ring(2.1, 0.8, 6, AMBER, Placement([tip[0], tip[1], dz], 0, QUARTER))
