"""P10-R11, 4-5: the Caldera Throne's colours and its destroyable parts (magma cannons, missile
batteries, heat shield generators), each drawn around its centre `at`, each turret around its
pivot. Ported from `bosses/world-4/caldera-throne-parts.ts`. Model space: logical pixels, nose +Z,
Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_4.caldera_throne import CALDERA_CELLS, CALDERA_MAGMA  # noqa: E402
from game.config.record import record  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.final_boss_greebles import rect  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H  # noqa: E402
from game.view.bosses.world_4.living_forge import SKIN  # noqa: E402
from game.view.enemies.enemy_shapes import POD_SECTION, around, decal  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
type OutlinePoint = list[float]
__pragma__("noskip")


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:  # noqa: E711
        return fallback
    return colour


# Crimson, its registered neon (GD-61), and gold, its second neon colour (P10-R11).
CRIMSON = _neon_or("caldera-throne", [1, 1, 1])
GOLD = [1.0, 0.72, 0.16]
# World 4 heat over the dark metal (P10-R11): molten seams and glow, soot, heat-blued plates.
HEAT = record(
    {
        "molten": [1, 0.36, 0.04],
        "glow": [0.75, 0.16, 0.03],
        "soot": SHADE["soot"],
        "blued": [0.09, 0.08, 0.12],
    }
)

# Height of the deck's top, which the keep and the parts stand on, and the bastions' top.
DECK_TOP = 8
BASTION_TOP = 5

# P16-R06: its parts are growths of its body: flesh drums under the magma cannons, shield
# generators as glowing glands in crowns of bone, batteries cased in metal.

# A magma cannon's housing (loft stations around its pivot), soot-black on its back.
HOUSING = [
    [-14.0, 7.0, 0.0, 8.0],
    [-4.0, 9.0, -0.5, 10.0],
    [10.0, 8.0, 0.0, 9.5],
    [17.0, 5.0, 2.0, 8.0],
]
HOUSING_BACK = 2
# The lens at the front of its barrel (lathe profile, along the barrel).
LENS = [
    [0.0, 0.0],
    [3.6, 1.0],
    [2.6, 3.0],
    [0.0, 3.8],
]
# How far along the barrel (from the housing) its glowing cooling coils stand.
COILS = [3.0, 7.0, 11.0, 15.0]


def _along_z(x: float, y: float, z: float) -> Any:
    """A barrel's placement at `[x, y, z]`, lying along Z (`{ at, pitch: QUARTER }`)."""
    return Placement([x, y, z], 0, QUARTER)


def magma_cannon(p: Any, centre: Vec3) -> None:
    """A magma cannon (P10-R11), turning on its bastion's turntable (D-073): a heavy housing with
    gold neon flanks, a long barrel ringed with molten coils, its lens glowing as the laser
    charges."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = centre[0]
    z = centre[2]
    at = [x, BASTION_TOP, z]

    def paint(side: int, _band: int) -> Any:
        if side == HOUSING_BACK:
            return HEAT.soot
        return None

    hull.loft(POD_SECTION, HOUSING, H.base, Placement(at), LoftOptions(False, paint))
    m = CALDERA_MAGMA[0] if x < 0 else mirror(CALDERA_MAGMA)[0]
    tip = boss_point(m[0], m[1], m[2])
    lens_at = tip[2] - LENS[3][1]
    start = z + 16
    hull.cylinder(3, lens_at - start, 8, H.dark, _along_z(x, tip[1], start), 2.4)
    for dz in COILS:
        neon.ring(3.2 - dz * 0.03, 1.2, 8, HEAT["molten"], _along_z(x, tip[1], start + dz))
    hull.cylinder(4.2, 3, 8, SHADE["edge"], _along_z(x, tip[1], lens_at - 3))
    charge.lathe(LENS, 8, WHITE, _along_z(x, tip[1], lens_at))
    muzzle(tip, "laser")
    for s in [-1, 1]:
        neon.box([0.6, 1, 20], GOLD, Placement([x + s * 9.6, BASTION_TOP + 3, z]))
        hull.box([3, 3, 9], H.panel, Placement([x + s * 5, BASTION_TOP + 9, z - 6]), HEAT["soot"])
    neon.box([5, 0.6, 0.6], CRIMSON, Placement([x, BASTION_TOP + 10.2, z + 9]))


def magma_mount(p: Any, centre: Vec3) -> None:
    """The turntable a magma cannon turns on: a low drum on the bastion, ringed with crimson."""
    x = centre[0]
    z = centre[2]
    p.flesh.cylinder(12, BASTION_TOP, 8, SKIN.base, Placement([x, 0, z]))
    p.hull.ring(10, 0.6, 8, H.dark, Placement([x, BASTION_TOP - 0.3, z]))
    p.neon.ring(12.3, 0.7, 8, CRIMSON, Placement([x, BASTION_TOP - 0.5, z]))
    p.neon.ring(12.3, 0.5, 8, HEAT["glow"], Placement([x, 0.6, z]))


# A battery's armoured box seen from above (around its centre), its corners cut.
BATTERY = [
    [-10.0, -15.0],
    [10.0, -15.0],
    [13.0, -11.0],
    [13.0, 11.0],
    [10.0, 15.0],
    [-10.0, 15.0],
    [-13.0, 11.0],
    [-13.0, -11.0],
]
HATCH = [7.6, 6.4]


def missile_battery(p: Any, centre: Vec3) -> None:
    """A missile battery (P10-R11): an armoured box on the aft deck, six hatches lit as its missiles
    load, crimson strips down its sides, a heat-blued blast shield at its front."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = centre[0]
    z = centre[2]
    source = CALDERA_CELLS if x < 0 else mirror(CALDERA_CELLS)
    cells = [boss_point(c[0], c[1], c[2]) for c in source]
    height = cells[0][1] if len(cells) > 0 else 0
    top = height - 0.08
    box = [[x + q[0], z + q[1]] for q in BATTERY]
    hull.bevel_slab(box, [DECK_TOP - 1, DECK_TOP + 2, top], [0, 2], H.base, None, HEAT["blued"])
    for cell in cells:
        cx = cell[0]
        cz = cell[2]
        decal(hull, rect([cx, cz], HATCH), top + 0.04, H.dark)
        decal(charge, rect([cx, cz], [HATCH[0] - 2.4, HATCH[1] - 2.4]), height, WHITE)
        muzzle([cx, height, cz], "missile")
    for s in [-1, 1]:
        neon.box([0.6, 1.4, 20], CRIMSON, Placement([x + s * 13.3, DECK_TOP + 2.4, z]))
    hull.box([22, 5, 2], H.panel, Placement([x, top - 1, z + 16], 0, -0.3), HEAT["blued"])
    neon.box([16, 0.6, 0.6], GOLD, Placement([x, top + 2.4, z + 16.6]))


# A generator's heat sinks: how many fins round it, and their size.
FINS = record({"count": 8, "reach": 12, "height": 11, "thick": 1.2})
# The glowing core of a generator (lathe profile), and its dome.
CORE = [
    [0.0, 0.0],
    [4.4, 2.0],
    [4.8, 6.0],
    [3.4, 10.0],
    [0.0, 12.0],
]


def shield_generator(p: Any, centre: Vec3) -> None:
    """A heat shield generator (P10-R11; no weapon, it shields the core): a molten core glowing in a
    crown of heat-sink fins edged with gold, on an armoured drum ringed with crimson."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    x = centre[0]
    z = centre[2]
    base = DECK_TOP
    flesh.cylinder(13, 4, 8, SKIN.base, Placement([x, base - 1, z], math.pi / 8), 12)
    hull.ring(12.6, 0.6, 8, H.dark, Placement([x, base + 2.2, z], math.pi / 8))
    neon.ring(12.4, 0.7, 8, CRIMSON, Placement([x, base + 2.8, z], math.pi / 8))
    neon.lathe(CORE, 6, HEAT["molten"], Placement([x, base + 3, z]))
    for a in around(FINS.count):
        c = math.cos(a)
        s = math.sin(a)
        mid = [x + s * FINS.reach * 0.62, base + 3, z + c * FINS.reach * 0.62]
        flesh.box([FINS.thick, FINS.height, FINS.reach * 0.7], SKIN.bone, Placement(mid, a))
        edge = [x + s * FINS.reach * 0.96, base + 3, z + c * FINS.reach * 0.96]
        neon.box([FINS.thick * 1.1, FINS.height * 0.8, 0.5], GOLD, Placement(edge, a))
    neon.ring(7.4, 0.6, 8, GOLD, Placement([x, base + 3 + FINS.height, z]))
