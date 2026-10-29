"""P09-R09, 3-1: the River Leviathan's body: its four segments and its tail, each drawn on its
hinge (D-061) so that they sway one after the other, the segments' ring turrets on their sponsons
and the tail's missile rack. Ported from `view/bosses/world-3/river-leviathan-body.ts`. Logical
pixels, nose +Z, Y up: the playfield's +Y (the tail) is the model's -Z, and its -X (the screen's
left) the model's +X."""

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.world_3.river_leviathan import (
    LEVIATHAN_BODY,
    LEVIATHAN_JOINTS,
    LEVIATHAN_RACK,
    SEGMENTS,
    TURRET_EMITTER_HEIGHT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_mechanism import GEAR
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import F, gland, sign_of, table, vein_to
from game.view.bosses.world_3.mangrove_croc_jungle import SWAMP, moss, scutes, vine
from game.view.enemies.enemy_shapes import SIDES, around, radial
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION, RibSpec, ribs
from render.geometry.outline import reversed_copy
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The River Leviathan's teal neon (P09-R09).
LEVIATHAN_TEAL = BOSS_LOOK.neon["river-leviathan"]
N = LEVIATHAN_TEAL

# The segments' half widths and their heights (bottom, top), head to tail.
SEGMENT_WIDTH = [15, 14, 13, 12]
SEGMENT_Y = [-3, 10]
# The tail (loft stations from its hinge, along -Z: z, half width, bottom, top).
TAIL = table(
    [
        [2, 11, -2.5, 8.5],
        [-14, 10, -2, 8],
        [-26, 7, -1, 6.5],
        [-36, 2.5, 1, 4],
    ]
)
# A tail fluke (the left one at +X), seen from above, from the tail's tip.
FLUKE = table([[1, 2], [12, -4], [14, -9], [9, -7], [1, -4]])
# The ring turret's dome (a lathe profile above its mount).
DOME = table([[8, 0], [8.2, 1.2], [6.6, 4.2], [3.2, 6], [0, 6.4]])
# Height of the turret's mount (where its dome stands) and of the sponson's deck.
MOUNT = 7.5


def hinge_z(i: int) -> float:
    """The model z of the hinge `i` (0 = the neck)."""
    return -(LEVIATHAN_BODY.hinges[i] or 0)


def collar(p: EnemyParts, i: int, radius: float) -> None:
    """A ball joint at hinge `i`: a round collar standing on the pivot, so that the bend between
    two segments never opens a gap whichever way they turn."""
    hull = p.hull
    neon = p.neon
    at: Vec3 = [0, SEGMENT_Y[0] + 0.5, hinge_z(i)]
    hull.cylinder(
        radius,
        SEGMENT_Y[1] - SEGMENT_Y[0] - 1.5,
        8,
        GEAR,
        Placement(at),
        radius * 0.9,
    )
    neon.ring(
        radius * 0.92,
        0.6,
        8,
        N,
        Placement(offset(at, 0, SEGMENT_Y[1] - SEGMENT_Y[0] - 2.4, 0)),
    )


def turret_spot(k: int) -> Vec3:
    """Where segment `k`'s turret stands, in model space (on its mount)."""
    i = k - 1
    side = LEVIATHAN_BODY.sides[i] or 1
    middle = LEVIATHAN_BODY.middles[i] or 0
    return boss_point(side * LEVIATHAN_BODY.turretOut, middle)


def sponson(p: EnemyParts, k: int) -> None:
    """The sponson carrying segment `k`'s turret: an armoured arm from the spine out to its
    mount."""
    hull = p.hull
    neon = p.neon
    spot = turret_spot(k)
    x = spot[0]
    z = spot[2]
    s = sign_of(x)
    hull.box(
        [abs(x) - 6, 3, 9],
        H.dark,
        Placement([x / 2 + s * 2, MOUNT - 4, z]),
        H.panel,
    )
    hull.box([abs(x) - 10, 1, 4], GEAR, Placement([x / 2 + s * 2, MOUNT - 1, z]))
    neon.box([abs(x) - 14, 0.4, 0.8], N, Placement([x / 2 + s * 3, MOUNT - 0.95, z + 2.6]))


def draw_segment(k: int) -> Any:
    """Segment `k`, on its hinge: its collar, an armoured hull plate along the spine with scutes
    and a teal light down its back, its turret's sponson out to one side, moss and a hanging
    vine."""
    i = k - 1
    w = SEGMENT_WIDTH[i] or 12
    front = hinge_z(i) - 2
    back = hinge_z(i + 1) + 1

    def draw(p: EnemyParts) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        collar(p, i, w * 0.85)
        b = SEGMENT_Y[0]
        t = SEGMENT_Y[1]
        # P16-R06: a living serpent's segment: swollen teal flesh, bone ribs over it, a vein along
        # its spine; the scutes and the sponson its grafted armour.
        stations = [
            [back, w * 0.8, b + 1, t - 1.5],
            [back + 6, w, b, t],
            [front - 6, w, b, t],
            [front, w * 0.85, b + 1, t - 1],
        ]
        flesh.loft(ROUND_SECTION, stations, F.teal)
        ribs(
            flesh,
            [back + 9, front - 9],
            RibSpec(w * 0.95, b + 2, t - b - 1.4, 0.7),
            F.bone,
        )
        neon.box(
            [1.2, 0.5, front - back - 8],
            N,
            Placement([0, t + 0.05, (front + back) / 2]),
        )
        mid = (front + back) / 2
        ridge: list[Vec3] = [[0, t - 0.4, front - 8], [0, t - 0.4, mid], [0, t - 0.4, back + 8]]
        scutes(hull, ridge[0:1], 2.2)
        scutes(hull, ridge[2:], 2.2)
        for s in SIDES:
            hull.box(
                [2.4, 1.2, front - back - 10],
                SHADE["edge"],
                Placement([s * w * 0.62, t - 0.4, (front + back) / 2]),
            )
        sponson(p, k)
        side = -(LEVIATHAN_BODY.sides[i] or 1)
        moss(
            hull,
            [
                [-side * 3, back + 6],
                [-side * 9, back + 7],
                [-side * 8, back + 13],
                [-side * 3, back + 12],
            ],
            t - 0.2,
        )
        vine(
            hull,
            [-side * w * 0.9, t - 3, front - 5],
            [-side * w * 0.9, t - 3, back + 6],
            5,
        )

    return draw


def draw_tail(p: EnemyParts) -> None:
    """The tail, on its hinge: its collar, a tapering hull, two flukes with reactors, moss."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    z0 = hinge_z(4)
    collar(p, 4, 9.5)
    # P16-R06: a tapering flesh tail, membrane flukes on bone, its reactors in flesh sacs.
    tail_stations = [[z0 + row[0], row[1], row[2], row[3]] for row in reversed_copy(TAIL)]
    flesh.loft(ROUND_SECTION, tail_stations, F.teal)
    tip = z0 + TAIL[len(TAIL) - 1][0]
    for s in SIDES:
        fluke: list[OutlinePoint] = [[s * f[0], tip + 4 + f[1]] for f in FLUKE]
        flesh.bevel_slab(fluke, [1.5, 2.5, 3.5], [0.4, 0.8], F.membrane, None, F.teal)
        neon.box([0.8, 0.5, 8], N, Placement([s * 8, 3.6, tip - 2], s * 0.9))
        reactor_sac(p, table([s * 4.5, 3, tip + 2]), 1.8, N, F.teal, None)
    neon.box([1, 0.5, 20], N, Placement([0, 8.55, z0 - 4]))
    moss(
        hull,
        [[-2, z0 - 28], [4, z0 - 26], [3, z0 - 20], [-3, z0 - 22]],
        6.8,
    )


def leviathan_body() -> dict[str, Any]:
    """The body (D-061): each segment, and the tail, drawn on its hinge; they go with the core."""
    limbs: dict[str, Any] = {}
    for k in SEGMENTS:
        joint = LEVIATHAN_JOINTS[k - 1] or "neck"
        limbs[joint] = {"draw": draw_segment(k)}
    limbs["tail"] = {"draw": draw_tail}
    return limbs


def turret_mount(p: EnemyParts, at: Vec3) -> None:
    """A segment's turret mount (the part, P09-R09): a round armoured base with a teal ring."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a swollen gland on the serpent's flank, the turret's metal ring grafted on top.
    flesh.cylinder(
        10,
        MOUNT,
        7,
        F.crimson,
        Placement(offset(at, 0, 0, 0), QUARTER / 4),
        9,
    )
    hull.cylinder(8.6, 0.6, 8, GEAR, Placement(offset(at, 0, MOUNT, 0), QUARTER / 4))
    neon.ring(10.1, 0.8, 8, N, Placement(offset(at, 0, MOUNT - 2.2, 0), QUARTER / 4))
    vein_to(
        p,
        [offset(at, 0, MOUNT * 0.4, -10), offset(at, 0, MOUNT * 0.4, 10)],
        [-sign_of(at[0]) * 3, 0, 0],
        N,
    )


def ring_turret(p: EnemyParts, at: Vec3) -> None:
    """A segment's ring turret (P09-R09), turning with its rings (D-060): a dome ringed with four
    stubby vanes, the ring emitter glowing on its axis at the top, where its rings leave from."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    base = offset(at, 0, MOUNT + 0.6, 0)
    top = TURRET_EMITTER_HEIGHT - 1.4 - base[1]
    hull.lathe(
        [[r, (y * top) / 6.4] for r, y in DOME],
        8,
        H.base,
        Placement(base, QUARTER / 4),
    )
    for a in around(4):
        foot = radial(a + QUARTER / 2, 6.4, 0)
        hull.box(
            [2.6, 2.6, 6],
            H.dark,
            Placement(offset(base, foot[0], 0.6, foot[2]), a + QUARTER / 2),
            H.panel,
        )
        lamp = radial(a + QUARTER / 2, 9.2, 0)
        charge.box(
            [1.8, 1.2, 0.8],
            WHITE,
            Placement(offset(base, lamp[0], 1.3, lamp[2]), a + QUARTER / 2),
        )
    neon.ring(5.2, 0.6, 8, N, Placement(offset(base, 0, top * 0.62, 0), QUARTER / 4))
    hull.cylinder(
        1.8,
        1.4,
        6,
        H.dark,
        Placement(offset(at, 0, TURRET_EMITTER_HEIGHT - 1.4, 0)),
    )
    charge.cylinder(
        1.3,
        0.3,
        6,
        WHITE,
        Placement(offset(at, 0, TURRET_EMITTER_HEIGHT - 0.3, 0)),
    )
    muzzle(offset(at, 0, TURRET_EMITTER_HEIGHT, 0))


def missile_rack(p: EnemyParts, at: Vec3) -> None:
    """The tail's missile rack (P09-R09): an armoured box on the tail's back, four cells open at
    its top, each with a charge light round its mouth, a teal band round it."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    height = LEVIATHAN_RACK[0][2] if len(LEVIATHAN_RACK) > 0 else 10
    # P16-R06: an egg sac swelling on the tail, a grafted rack of missile cells capping it.
    p.flesh.box(
        [16, height - 4, 18],
        F.crimson,
        Placement(offset(at, 0, 4, 0)),
        F.sinew,
    )
    gland(p, offset(at, 0, height - 2, -10), 2, N)
    hull.box([17, 1.4, 19], H.dark, Placement(offset(at, 0, 4.5, 0)))
    neon.box([16.4, 0.6, 18.4], N, Placement(offset(at, 0, 6.5, 0)))
    for cell in LEVIATHAN_RACK:
        mouth = boss_point(cell[0], cell[1], cell[2])
        hull.cylinder(2.6, 0.5, 6, H.dark, Placement(offset(mouth, 0, -0.45, 0)))
        charge.ring(2.8, 0.4, 6, WHITE, Placement(offset(mouth, 0, -0.35, 0)))
        muzzle(mouth, "missile")
    hull.box([3, 1.2, 18], SWAMP.stone, Placement(offset(at, 0, height - 0.2, 0)))
