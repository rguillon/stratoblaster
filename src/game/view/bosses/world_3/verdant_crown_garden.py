"""P09-R09, 3-5: the Verdant Crown's colours and its glass garden dome over the core: a lattice of
ribs and glowing mullions, trees inside, the tallest one rising through the oculus at the top. Model
space: logical pixels, nose +Z
(down the screen), Y up towards the camera."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.world_3.verdant_crown import VERDANT_BLOOM
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_3.jungle_flesh import F, table
from game.view.enemies.enemy_shapes import around, radial
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]

# Emerald, its registered neon (GD-61), and magenta, its second neon colour (P09-R09).
EMERALD = BOSS_LOOK.neon["verdant-crown"]
MAGENTA = [1, 0.15, 0.75]
# The World 3 jungle over the dark metal: moss, bark, leaves, old stone.
JUNGLE = record(
    {
        "moss": [0.1, 0.19, 0.07],
        "bark": [0.13, 0.085, 0.05],
        "leaf": [0.07, 0.24, 0.09],
        "stone": [0.2, 0.2, 0.17],
    }
)

# Height of the deck's top, which the dome, the city and the parts stand on.
DECK_TOP = 6
# The dome: its radius, its ribs, the elevations of its mullions and of its oculus's rim.
DOME = record(
    {
        "radius": 31,
        "ribs": 8,
        "mullions": [0.42, 0.85],
        "oculus": 1.2,
        "steps": 4,
    }
)


def strut(
    builder: SolidBuilder,
    ends: list[Vec3],
    radii: list[float],
    color: Rgb,
    sides: int = 4,
) -> None:
    """A cylinder from `ends[0]` to `ends[1]` (radius `radii[0]` at the start, `radii[1]` at the
    end), `sides` facets."""
    a = ends[0]
    b = ends[1]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = math.hypot(dx, dy, dz)
    place = Placement(a, math.atan2(dx, dz), math.acos(dy / length))
    builder.cylinder(radii[0], length, sides, color, place, radii[1])


def on_dome(a: float, e: float) -> Vec3:
    """The point of the dome at the turn `a` (from the nose) and the elevation `e` (radians)."""
    r = DOME.radius * math.cos(e)
    return [math.sin(a) * r, DECK_TOP + DOME.radius * math.sin(e), math.cos(a) * r]


def draw_lattice(p: EnemyParts) -> None:
    """The dome's lattice: dark ribs up to the oculus, glowing mullions round it, a lit rim."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    radius = DOME.radius
    ribs = DOME.ribs
    steps = DOME.steps
    oculus = DOME.oculus
    for a in around(ribs):
        turn = a + math.pi / ribs
        for k in range(steps):
            e0 = (oculus * k) / steps
            e1 = (oculus * (k + 1)) / steps
            # P16-R06: the dome's ribs are bone, a ribcage over the garden.
            strut(flesh, [on_dome(turn, e0), on_dome(turn, e1)], [1, 1], F.bone)
    for e in DOME.mullions:
        y = on_dome(0, e)[1]
        neon.ring(radius * math.cos(e), 0.4, ribs * 2, EMERALD, Placement([0, y, 0]))
    top = on_dome(0, oculus)[1]
    rim = radius * math.cos(oculus)
    hull.cylinder(
        rim + 1.5,
        1.6,
        ribs * 2,
        H.base,
        Placement([0, top - 0.8, 0]),
        rim + 1,
    )
    neon.ring(rim + 1.6, 0.6, ribs * 2, MAGENTA, Placement([0, top - 0.4, 0]))
    hull.cylinder(radius + 2, 3, ribs * 2, H.panel, Placement([0, DECK_TOP - 1, 0]), radius + 1)
    neon.ring(radius + 2.1, 0.8, ribs * 2, EMERALD, Placement([0, DECK_TOP + 0.6, 0]))


# A tree of the garden: where (model x, z), how tall, how wide its crown.
TREES = table(
    [
        [14, 10, 18, 7],
        [-15, 8, 16, 6.5],
        [10, -15, 15, 7],
        [-12, -14, 19, 6],
        [0, 18, 13, 5.5],
        [21, -4, 12, 5],
        [-21, -2, 13, 5],
    ]
)
# A crown of leaves (a lathe profile in units of its radius): a squat, faceted ball.
CROWN = table([[0.4, 0], [1, 0.35], [0.85, 0.8], [0, 1.1]])


def tree(p: EnemyParts, t: list[float], i: int) -> None:
    """A tree: a trunk and a faceted crown of leaves, a magenta flower or two in it."""
    hull = p.hull
    neon = p.neon
    tx = t[0]
    tz = t[1]
    th = t[2]
    tr = t[3]
    hull.cylinder(
        1.2,
        th - tr * 0.4,
        5,
        JUNGLE.bark,
        Placement([tx, DECK_TOP, tz]),
        0.7,
    )
    crown = [[u * tr, v * tr] for u, v in CROWN]
    hull.lathe(crown, 6, JUNGLE.leaf, Placement([tx, DECK_TOP + th - tr * 0.6, tz], i))
    flower = radial(i * 2.1, tr * 0.8, 0)
    neon.box(
        [1.2, 1.2, 1.2],
        MAGENTA,
        Placement([tx + flower[0], DECK_TOP + th - tr * 0.2, tz + flower[2]]),
    )


def great_tree(p: EnemyParts) -> None:
    """The tallest tree, rising through the oculus, its bloom the core's ring emitter."""
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    bloom = boss_point(VERDANT_BLOOM[0], VERDANT_BLOOM[1], VERDANT_BLOOM[2])
    hull.cylinder(
        2.6,
        bloom[1] - DECK_TOP - 9,
        6,
        JUNGLE.bark,
        Placement([0, DECK_TOP, 0]),
        1.4,
    )
    crown = [[u * 10, v * 6] for u, v in CROWN]
    hull.lathe(crown, 7, JUNGLE.leaf, Placement([0, bloom[1] - 8.6, 0]))
    hull.lathe(
        [[3.6, 0], [2.2, 1.6]],
        6,
        JUNGLE.moss,
        Placement([0, bloom[1] - 2.6, 0]),
    )
    charge.lathe(
        [[2.4, 0], [1.2, 0.8], [0, 1]],
        6,
        WHITE,
        Placement([0, bloom[1] - 1, 0]),
    )
    muzzle(bloom, "ring")


def draw_garden(p: EnemyParts) -> None:
    """The glass garden dome over the core (P09-R09): its lattice, its garden, its great tree."""
    p.hull.cylinder(DOME.radius, 0.4, 16, JUNGLE.moss, Placement([0, DECK_TOP, 0]))
    draw_lattice(p)
    for i in range(len(TREES)):
        tree(p, TREES[i], i)
    great_tree(p)
