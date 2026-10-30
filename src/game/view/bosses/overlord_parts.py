"""P07-R05, P16-R06: the Overlord's destroyable parts: wing
laser cannons, missile batteries, shield generators, each drawn around its centre `at` (model
space: logical pixels, nose +Z, Y up).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.bosses.overlord_city import OVERLORD_DECK, OVERLORD_NEON, box2d  # noqa: E402
from game.view.bosses.world_1_organic_kit import F, graft, polygon, tentacle, vein_line  # noqa: E402
from game.view.enemies.enemy_shapes import around, decal, radial, side_stripe  # noqa: E402
from render.geometry.organic import ROUND_SECTION  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# Height of the wings' top, where the laser cannons sit.
WING_TOP = 2

# A laser cannon's pod (loft stations around its centre), its barrel and its lens.
LASER_POD = [
    [-15, 5, -2, 5],
    [-6, 8, -3, 8],
    [8, 7, -2.5, 7],
    [15, 4, -1, 4.5],
]
LASER_BARREL = {"from": 15, "length": 10, "radius": 2.4}
LASER_LENS = [
    [0, 0],
    [3.2, 1],
    [2.2, 3],
    [0, 3.6],
]


def draw_laser(p: Any, at_point: Vec3) -> None:
    """P07-R05, P16-R06: a wing laser cannon: a swollen gland on the wing, a grafted collar, a long
    barrel, coils and a lens charging."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    at = [x, y + WING_TOP - 1, z]
    p.flesh.loft(ROUND_SECTION, LASER_POD, F.crimson, Placement(at))
    graft(p, polygon(6, 4, [1.2, 1.4]), [at[1] + 6.6, at[1] + 7.6], [x, 0, z + 8])
    for side in [1, 3]:
        stripe = side_stripe(ROUND_SECTION, side, [0.25, 0.55])
        neon.loft(stripe, LASER_POD[0:3], OVERLORD_NEON, Placement(at), LoftOptions(True))
    axis = at[1] + 3

    def along(dz: float) -> Any:
        return Placement([x, axis, z + dz], 0, QUARTER)

    barrel_from = LASER_BARREL["from"]
    barrel_length = LASER_BARREL["length"]
    radius = LASER_BARREL["radius"]
    hull.cylinder(radius, barrel_length, 6, H.dark, along(barrel_from))
    # The coils and the lens brighten through the warning line, full while the beam fires.
    for dz in [barrel_from + 2.5, barrel_from + 6]:
        charge.ring(radius * 1.25, 1.3, 6, WHITE, along(dz))
    charge.lathe(LASER_LENS, 6, WHITE, along(barrel_from + barrel_length))
    muzzle([x, axis, z + barrel_from + barrel_length + 3.6], "laser")
    # Bone fins on the gland's back, a vein between them.
    for s in [-1, 1]:
        tentacle(
            p,
            [x + s * 3.2, at[1] + 7, z - 10],
            [x + s * 4, at[1] + 10, z - 2],
            [0, 1, 0],
            [1.2, 0.2],
            F.bone,
            3,
        )
    vein_line(p, [x, at[1] + 8, z - 12], [x, at[1] + 8, z + 2], [0, 0.6, 0], 1.2, OVERLORD_NEON)


# A missile battery's block, and its cells: 2 columns by 3 rows on its top.
BATTERY = [
    [-10, -13],
    [10, -13],
    [12.5, -9],
    [12.5, 10],
    [8.5, 13.5],
    [-8.5, 13.5],
    [-12.5, 10],
    [-12.5, -9],
]
CELLS = [[cx, cz] for cx in [-5, 5] for cz in [-7.5, 0, 7.5]]


def draw_battery(p: Any, at_point: Vec3) -> None:
    """P07-R05, P16-R06: a missile brood on the mantle: a swollen mound under a grafted plate, six
    hatches lit as it loads."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + OVERLORD_DECK["top"]
    top = base + 8
    p.flesh.bevel_slab(
        BATTERY,
        [base - 1, base, top - 1],
        [0, 3],
        F.crimson,
        Placement([x, 0, z]),
        F.sinew,
    )
    hull.bevel_slab(
        BATTERY,
        [top - 1.2, top - 1.2, top],
        [0, 1],
        H.base,
        Placement([x, 0, z]),
        H.panel,
    )
    vein_line(p, [x, base, z - 13], [x, base - 2, z - 22], [0, 1.5, 0], 1.1, OVERLORD_NEON)
    for cell in CELLS:
        cx = cell[0]
        cz = cell[1]
        decal(hull, box2d(7, 5.6, [x + cx, z + cz]), top + 0.04, H.dark)
        decal(charge, box2d(5, 3.6, [x + cx, z + cz]), top + 0.08, WHITE)
        muzzle([x + cx, top + 0.08, z + cz], "missile")
    for s in [-1, 1]:
        neon.box([0.6, 1.4, 16], OVERLORD_NEON, Placement([x + s * 11.7, base + 3.2, z]))


# A shield generator's pedestal and glowing dome (lathe profiles, bottom to top).
PEDESTAL = [
    [12, 0],
    [12.5, 2],
    [10.5, 4.5],
    [0, 4.5],
]
DOME = [
    [8.5, 0],
    [7.5, 3.5],
    [4.5, 6],
    [0, 7],
]


def draw_generator(p: Any, at_point: Vec3) -> None:
    """P07-R05, P16-R06: a shield generator: a glowing neon gland in a ring of grafted coil,
    swelling out of a flesh mound, three bone horns around it tipped with neon."""
    hull = p.hull
    neon = p.neon
    x = at_point[0]
    y = at_point[1]
    z = at_point[2]
    base = y + OVERLORD_DECK["top"]
    p.flesh.lathe(PEDESTAL, 8, F.purple, Placement([x, base, z], math.pi / 8))
    neon.ring(12.6, 0.8, 8, OVERLORD_NEON, Placement([x, base + 0.6, z], math.pi / 8))
    neon.lathe(DOME, 8, OVERLORD_NEON, Placement([x, base + 4, z]))
    hull.ring(9.2, 1.6, 8, H.dark, Placement([x, base + 5.2, z]))
    for a in around(3):
        r = radial(a + math.pi / 3, 10.5, 0)
        horn = [x + r[0] * 1.1, base + 15, z + r[2] * 1.1]
        tentacle(p, [x + r[0], base + 3, z + r[2]], horn, [0, 0, 0], [1.6, 0.4], F.bone, 4)
        neon.box([1, 1, 1], OVERLORD_NEON, Placement(horn))
