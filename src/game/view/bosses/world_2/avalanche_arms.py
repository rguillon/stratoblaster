"""P08-R10, 2-4: the Avalanche's drill arms, moving on their joints (D-061), and its drills,
ported from `bosses/world-2/avalanche-arms.ts`. Logical pixels, nose +Z, Y up (towards the
camera); the left arm is drawn at +X."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from game.view.bosses.boss_limbs import LimbDrawing  # noqa: E402
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
type Flat = list[float]
__pragma__("noskip")

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_2.avalanche import AVALANCHE_DRILL_GUN  # noqa: E402
from game.config.record import record  # noqa: E402
from game.view.bosses.mini_boss_mechanism import glow_line  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    QUARTER,
    SHADE,
    H,
    offset,
)
from game.view.bosses.world_2.avalanche_frost import (  # noqa: E402
    barrel_to,
    icicles,
    snow_cap,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    glow_vein,
    sinew,
)
from render.geometry.organic import organ  # noqa: E402
from render.geometry.outline import hypot2  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# The Avalanche's yellow neon (P08-R10).
_AVALANCHE_NEON = BOSS_LOOK.neon["avalanche"]
AVALANCHE_YELLOW = [1.0, 0.85, 0.1] if _AVALANCHE_NEON == None else _AVALANCHE_NEON  # noqa: E711

# The drill bit along +Z from its root (a lathe profile: radius, distance along).
BIT = [
    [7.0, 0.0],
    [7.4, 2.0],
    [5.4, 8.0],
    [3.2, 14.0],
    [0.0, 21.0],
]
# The drill's housing: its radius and its length, and the height of its axis.
HOUSING = record({"radius": 8.5, "length": 14, "axis": 6})


def _sign(x: float) -> float:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def beam_outline(a: Flat, b: Flat, width: float) -> list[OutlinePoint]:
    """A beam's outline (seen from above) from `a` to `b`, `width` wide, its ends cut square."""
    length = hypot2(b[0] - a[0], b[1] - a[1]) or 1
    nx = ((a[1] - b[1]) / length) * (width / 2)
    nz = ((b[0] - a[0]) / length) * (width / 2)
    return [
        [a[0] + nx, a[1] + nz],
        [b[0] + nx, b[1] + nz],
        [b[0] - nx, b[1] - nz],
        [a[0] - nx, a[1] - nz],
    ]


def segment(parts: EnemyParts, s: float, ends: Sequence[Flat], width: float) -> None:
    """One arm segment from `a` to `b` (side `s` applied to X): a dark bed of machinery under a
    fat armour plate, frost on its top, a yellow light along it and a ram working it."""
    hull = parts.hull
    flesh = parts.flesh
    neon = parts.neon
    a = ends[0]
    b = ends[1]
    pa = [s * a[0], a[1]]
    pb = [s * b[0], b[1]]
    # P16-R05: a muscle of flesh along the bone, an armour plate grafted on top of it.
    flesh.bevel_slab(beam_outline(pa, pb, width), [0, 1.5, 4], [0.6, 1], ICE_FLESH.sinew)

    def inset(t: float) -> Flat:
        return [pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t]

    ia = inset(0.12)
    ib = inset(0.82)
    flesh.bevel_slab(
        beam_outline(ia, ib, width * 1.15),
        [3, 5, 7.5],
        [0.8, 1.8],
        ICE_FLESH.purple,
        None,
        ICE_FLESH.teal,
    )
    hull.bevel_slab(
        beam_outline(inset(0.3), inset(0.7), width * 0.8),
        [7.3, 8.2, 9],
        [0.4, 0.8],
        H.base,
        None,
        H.panel,
    )
    snow_cap(flesh, beam_outline(inset(0.2), inset(0.55), width * 0.7), 9, 0.8)
    light_end = inset(0.72)
    light_start = inset(0.6)
    glow_line(
        neon,
        [light_start[0], 9.2, light_start[1]],
        [light_end[0], 9.2, light_end[1]],
        1,
        AVALANCHE_YELLOW,
    )
    sinew(
        flesh,
        [pa[0] - s * 3, 2, pa[1] + 2],
        [ib[0] - s * 2, 2.5, ib[1]],
        1.4,
    )


def upper_arm(s: float) -> Callable[[EnemyParts], None]:
    """The upper arm (side `s`, +1 left at +X), on its shoulder: its segment and the elbow's
    cog."""

    def draw(p: EnemyParts) -> None:
        segment(p, s, [[18, 10], [36, 26]], 9)
        organ(p.flesh, 4, 6, ICE_FLESH.bone, Placement([s * 34, 0, 24]), 0.6)

    return draw


def forearm(s: float) -> Callable[[EnemyParts], None]:
    """The forearm (side `s`), on its elbow: its segment, out to the drill's housing."""

    def draw(p: EnemyParts) -> None:
        segment(p, s, [[32, 22], [42, 32]], 8)
        icicles(
            p.flesh,
            [[s * 37, 3, 25], [s * 39.5, 3, 28], [s * 34.5, 3, 22.5]],
            3.5,
        )

    return draw


def arm_limbs(side: str) -> dict[str, LimbDrawing]:
    """The limbs of the arm on `side` (D-061): the upper arm on the shoulder, the forearm on the
    elbow."""
    s = 1 if side == "left" else -1
    limbs: dict[str, LimbDrawing] = {}
    limbs["shoulder-" + side] = record({"draw": upper_arm(s)})
    limbs["elbow-" + side] = record({"draw": forearm(s)})
    return limbs


def flutes(hull: SolidBuilder, root: Vec3, color: Rgb) -> None:
    """Ridges spiralling round the drill bit from `root` (its axis along +Z), `color`."""
    for k in range(6):
        along = 3 + k * 2.6
        r = 7 - along * 0.32
        a = k * 1.9
        hull.box(
            [1.2, 1.4, 3.2],
            color,
            Placement(
                offset(root, math.cos(a) * r, math.sin(a) * r - 0.7, along),
                0.5,
                0,
                a,
            ),
        )


def drill(p: EnemyParts, at: Vec3) -> None:
    """A drill (P08-R10), on its arm's elbow joint: a housing with a yellow neon collar, a
    fluted bit pointing down the screen, its gun along the outer side, frost on top and icicles
    under it."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    s = _sign(at[0])
    axis = offset(at, 0, HOUSING.axis, 0)
    back = offset(axis, 0, 0, -HOUSING.length / 2)
    # P16-R05: a swollen fist of flesh, the bit a metal graft driven into it.
    organ(flesh, HOUSING.radius, 7, ICE_FLESH.purple, Placement(back, 0, QUARTER), 0.8)
    flesh.cylinder(
        HOUSING.radius * 0.7,
        3,
        6,
        ICE_FLESH.sinew,
        Placement(offset(back, 0, 0, -3), 0, QUARTER),
    )
    front = offset(axis, 0, 0, HOUSING.length / 2)
    neon.ring(
        HOUSING.radius * 1.03,
        1.2,
        8,
        AVALANCHE_YELLOW,
        Placement(offset(front, 0, 0, -2.5), 0, QUARTER),
    )
    hull.lathe(BIT, 6, SHADE.edge, Placement(front, 0, QUARTER))
    flutes(hull, front, H.panel)
    # The gun on the outer side, on a bracket; the right one is the mirror image.
    guns = AVALANCHE_DRILL_GUN if s > 0 else mirror(AVALANCHE_DRILL_GUN)
    if len(guns) > 0:
        barrel_to(p, guns[0], [1.7, 9])
    hull.box([5, 3, 8], H.dark, Placement(offset(at, s * 6.5, 5, 7)), H.base)
    glow_vein(
        p,
        offset(axis, 0, HOUSING.radius - 1, -6),
        offset(axis, s * 3, HOUSING.radius - 2, 4),
        0.8,
        AVALANCHE_YELLOW,
    )
    cap = [[-4.0, -6.0], [3.0, -7.0], [4.5, 0.0], [-2.0, 2.0]]
    snow_cap(
        flesh,
        [[at[0] + q[0], at[2] + q[1]] for q in cap],
        HOUSING.axis + HOUSING.radius - 0.3,
        0.9,
    )
    under = HOUSING.axis - HOUSING.radius + 0.6
    icicles(
        flesh,
        [offset(at, -4, under, 4), offset(at, 3, under, 0), offset(at, 0, under, -4)],
        4,
    )
