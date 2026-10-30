"""P10-R11, 4-4: the Foundry Ark's destroyable parts (rail cannons, chimney row, missile battery,
crucibles), each drawn around its centre `at`, each turret around its pivot, and its forge colours.
Model space: logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_4.foundry_ark import ARK_CELLS, ARK_RAIL  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.final_boss_greebles import rod  # noqa: E402
from game.view.bosses.mini_boss_greebles import lamps, seam  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H  # noqa: E402
from game.view.bosses.overlord_city import box2d  # noqa: E402
from game.view.bosses.world_4.living_forge import SKIN  # noqa: E402
from game.view.enemies.enemy_shapes import SIDES, decal  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:  # noqa: E711
        return fallback
    return colour


# The Ark's orange neon, its molten metal (hotter, yellower), and its red warning lamps.
ARK_ORANGE = _neon_or("foundry-ark", [1, 0.55, 0.12])
MOLTEN = [1.0, 0.78, 0.25]
ARK_RED = [1.0, 0.12, 0.05]
# Soot-blackened iron, and rust on the old plates (World 4: heavy industry).
SOOT = SHADE["soot"]
RUST = [0.18, 0.08, 0.04]
# Height of the deck, and of the outriggers' top, where the rail cannons turn.
DECK_TOP = 4

# P16-R06: its parts are flesh growths with metal grafted on: a flesh drum under each rail cannon, a
# flesh mound under the chimneys, crucibles as swollen sacs brimming with slag.


def rail_mount(p: Any, centre: Vec3) -> None:
    """The turntable a rail cannon turns on: a low drum on its outrigger, ringed with orange."""
    x = centre[0]
    z = centre[2]
    p.flesh.cylinder(11, DECK_TOP + 1, 8, SKIN.base, Placement([x, 0, z], math.pi / 8))
    p.hull.ring(9, 0.6, 8, H.dark, Placement([x, DECK_TOP + 0.6, z], math.pi / 8))
    p.neon.ring(11.3, 0.6, 8, ARK_ORANGE, Placement([x, DECK_TOP - 0.2, z], math.pi / 8))


# The coils wound round the rails, where the charge builds before a shot (along the rails).
COILS = [22.0, 30.0, 38.0]


def rail_cannon(p: Any, centre: Vec3) -> None:
    """A rail cannon (P10-R11), turning on its outrigger's turntable (D-073): an armoured breech,
    two
    long rails out to the emitter between their tips, glowing coils along them, the emitter lit as
    the laser charges."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = centre[0]
    z = centre[2]
    source = ARK_RAIL if x < 0 else mirror(ARK_RAIL)
    if len(source) == 0:
        return
    m = source[0]
    tip = boss_point(m[0], m[1], m[2])
    y = tip[1]
    hull.box([15, 6.4, 17], H.base, Placement([x, DECK_TOP + 1, z]), H.panel)
    hull.box([9, 2.6, 6], SOOT, Placement([x, DECK_TOP + 7.4, z - 4]))
    for s in SIDES:
        rail = Placement([x + s * 3.6, y - 1.2, (z + tip[2]) / 2 + 2])
        hull.box([2, 2.4, tip[2] - z - 4], H.dark, rail, SHADE["edge"])
        neon.box([0.4, 0.5, tip[2] - z - 12], ARK_ORANGE, Placement([x + s * 4.7, y, z + 18]))
    for dz in COILS:
        charge.box([9.6, 1, 1.6], WHITE, Placement([x, y - 2, z + dz]))
    hull.cylinder(2, 2.4, 6, H.dark, Placement([x, y, tip[2] - 3.2], 0, QUARTER))
    charge.cylinder(1.6, 0.8, 6, WHITE, Placement([x, y, tip[2] - 0.8], 0, QUARTER), 1)
    muzzle(tip, "laser")


# The chimneys of the row, across the foredeck (x), and their height.
CHIMNEYS = [-15.0, -5.0, 5.0, 15.0]
CHIMNEY_TOP = 32


def chimney_row(p: Any, centre: Vec3) -> None:
    """The chimney row (P10-R11; no weapon, it shields the core): four tall stacks on a brick-dark
    plinth, sooty at the top with a heat glow under their lips, a red lamp on each."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    x = centre[0]
    z = centre[2]
    flesh.bevel_slab(
        box2d(46, 15, [x, z]),
        [DECK_TOP - 1, DECK_TOP, 10],
        [0, 1.2],
        SKIN.base,
        None,
        SKIN.dark,
    )
    for i in range(len(CHIMNEYS)):
        dx = CHIMNEYS[i]
        top = CHIMNEY_TOP - (i % 2) * 3
        at = [x + dx, 10, z]
        hull.cylinder(4, top - 10, 6, H.panel, Placement(at), 3.2)
        hull.ring(3.5, 2.4, 6, SOOT, Placement([x + dx, top - 0.4, z]))
        neon.ring(3.45, 0.7, 6, ARK_ORANGE, Placement([x + dx, top - 3.6, z]))
        hull.ring(4.1, 0.8, 6, H.dark, Placement([x + dx, 14 + i, z]))
        lamps(neon, [[x + dx + 3.6, top - 6, z]], 0.9, ARK_RED)
    seam(hull, [x - 22, z + 6.6], [x + 22, z + 6.6], [10, 1.6, 0.8], H.dark)


# The missile hatches' size on the battery's top.
HATCH = [8.0, 7.0]


def battery(p: Any, centre: Vec3) -> None:
    """The missile battery on the bow (P10-R11): an armoured block, four hatches lit as missiles
    load, hazard-orange strips down its sides."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = centre[0]
    z = centre[2]
    cells = [boss_point(c[0], c[1], c[2]) for c in ARK_CELLS]
    height = cells[0][1] if len(cells) > 0 else 9
    top = height - 0.08
    hull.bevel_slab(
        box2d(24, 24, [x, z]),
        [DECK_TOP - 1, DECK_TOP, top],
        [0, 2],
        H.base,
        None,
        H.panel,
    )
    for cell in cells:
        cx = cell[0]
        cz = cell[2]
        decal(hull, box2d(HATCH[0], HATCH[1], [cx, cz]), top + 0.04, H.dark)
        decal(charge, box2d(HATCH[0] - 2.4, HATCH[1] - 2.4, [cx, cz]), height, WHITE)
        muzzle([cx, height, cz], "missile")
    for s in SIDES:
        neon.box([0.6, 1.2, 18], ARK_ORANGE, Placement([x + s * 12.2, 5, z]))
    hull.box([18, 1, 2], SOOT, Placement([x, top - 0.4, z - 11]))


# A crucible's bucket (a lathe profile around its axis, up).
BUCKET = [
    [7.5, 0.0],
    [10.5, 3.0],
    [12.0, 11.0],
    [12.6, 13.0],
]
BUCKET_FOOT = DECK_TOP + 2


def crucible(p: Any, centre: Vec3) -> None:
    """A crucible (P10-R11): a heavy bucket brimming with glowing molten metal, hung from a gantry
    on
    chains, a pouring lip on its inboard side, a hot band round its belly. Destroyed, it spills
    into a
    ring of bullets."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    x = centre[0]
    z = centre[2]
    sign = 0
    if x > 0:
        sign = 1
    elif x < 0:
        sign = -1
    inboard = -sign
    flesh.lathe(BUCKET, 8, SKIN.dark, Placement([x, BUCKET_FOOT, z]), False)
    neon.ring(11.7, 0.8, 8, ARK_ORANGE, Placement([x, BUCKET_FOOT + 7, z]))
    neon.cylinder(11.9, 0.3, 8, MOLTEN, Placement([x, BUCKET_FOOT + 11.4, z]))
    hull.box([5, 1.2, 5], H.dark, Placement([x + inboard * 12.5, BUCKET_FOOT + 11.6, z]))
    neon.box([3, 0.4, 3], MOLTEN, Placement([x + inboard * 13, BUCKET_FOOT + 12.8, z]))
    # The gantry: two legs either side of the bucket (along Z), a beam over it, chains to the rim.
    for s in SIDES:
        hull.box([2.4, 26, 2.4], H.panel, Placement([x, DECK_TOP, z + s * 15]), SHADE["edge"])
        rod(
            hull,
            [x + 4, DECK_TOP + 28, z + s * 4],
            [x + 9, BUCKET_FOOT + 13, z + s * 7],
            0.4,
        )
        rod(
            hull,
            [x - 4, DECK_TOP + 28, z + s * 4],
            [x - 9, BUCKET_FOOT + 13, z + s * 7],
            0.4,
        )
    hull.box([3, 2.4, 33], H.base, Placement([x, DECK_TOP + 26, z]), H.panel)
    hull.box([9, 2, 4], H.dark, Placement([x, DECK_TOP + 27, z]))
    lamps(neon, [[x, DECK_TOP + 28.6, z + 15]], 0.9, ARK_RED)
