"""P08-R10, 2-2: the Harbour Kraken's crane arms: a boom on each shoulder, a jib on each elbow
(moving limbs, D-061), and the grab cannons hanging from the jibs' tips, ported from
`bosses/world-2/harbour-kraken-cranes.ts`. Logical pixels, nose +Z, Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from game.view.bosses.boss_limbs import LimbDrawing  # noqa: E402
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.world_2.harbour_kraken import CRANE_REST, CRANES  # noqa: E402
from game.config.record import record  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.final_boss_shapes import barrels  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_2.fjord_lynx_frost import (  # noqa: E402
    icicles,
    spread,
)
from game.view.bosses.world_2.w2_organic import ICE_FLESH  # noqa: E402
from render.geometry.organic import curve, organ, tendril  # noqa: E402
from render.geometry.outline import hypot2  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# The Kraken's orange neon.
_ORANGE = BOSS_LOOK.neon["harbour-kraken"]
ORANGE_NEON = [1.0, 0.5, 0.08] if _ORANGE == None else _ORANGE  # noqa: E711
# Height of the booms over the deck's level, and of the deck.
BOOM_Y = 12
DECK_Y = 4
# Where a grab cannon's barrel starts, from the grab's centre, and its radius and length.
GRAB_GUN = [0.0, 4.0, 5.0]
GRAB_BORE = [1.3, 9.0]


def beam(
    builder: SolidBuilder,
    a: Vec3,
    b: Vec3,
    size: Sequence[float],
    colors: Sequence[Rgb],
) -> None:
    """A beam from `a` to `b` (on the same level), `size` wide and high, its top `colors[1]`."""
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    builder.box(
        [size[0], size[1], hypot2(dx, dz)],
        colors[0],
        Placement(
            [(a[0] + b[0]) / 2, a[1], (a[2] + b[2]) / 2],
            math.atan2(dx, dz),
        ),
        colors[1],
    )


def crane_points(crane: str, y: float) -> list[Vec3]:
    """The model-space points of a crane at rest: its shoulder, elbow and grab, at `y`."""
    parts = crane.split("-")
    end = parts[0]
    side = parts[1]
    s = 1 if side == "left" else -1
    return [offset(boss_point(s * q[0], q[1]), 0, y, 0) for q in CRANE_REST[end]]


def boom(crane: str) -> Callable[[EnemyParts], None]:
    """A crane's boom, on its shoulder: a lattice-dark beam, rimed on top, a neon line along it."""

    def draw(p: EnemyParts) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        points = crane_points(crane, BOOM_Y)
        shoulder = points[0]
        elbow = points[1]
        # P16-R06: a tentacle's thick upper length, metal bands grafted round it.
        tendril(flesh, curve(shoulder, elbow, [0, 2, 0], 3), [3.4, 2.6], 6, ICE_FLESH.crimson)
        for t in [0.35, 0.7]:
            at = offset(
                shoulder,
                (elbow[0] - shoulder[0]) * t,
                1.2,
                (elbow[2] - shoulder[2]) * t,
            )
            hull.ring(
                3.3,
                1.2,
                6,
                H.panel,
                Placement(
                    at,
                    math.atan2(elbow[0] - shoulder[0], elbow[2] - shoulder[2]),
                    QUARTER,
                ),
            )
        beam(
            neon,
            offset(shoulder, 0, 3, 0),
            offset(elbow, 0, 3, 0),
            [0.8, 0.3],
            [ORANGE_NEON, ORANGE_NEON],
        )
        organ(flesh, 3.4, 6, ICE_FLESH.purple, Placement(offset(elbow, 0, -2.6, 0)), 0.7)
        for q in spread(shoulder, elbow, 3):
            organ(flesh, 1.2, 5, ICE_FLESH.bone, Placement(offset(q, 0, -3, 0)), 0.5)
        icicles(flesh, spread(shoulder, elbow, 4), 3)

    return draw


def jib(crane: str) -> Callable[[EnemyParts], None]:
    """A crane's jib, on its elbow: a lighter beam out to the winch its grab hangs from."""

    def draw(p: EnemyParts) -> None:
        points = crane_points(crane, BOOM_Y + 0.4)
        elbow = points[1]
        tip = points[2]
        tendril(p.flesh, curve(elbow, tip, [0, 1.5, 0], 3), [2.6, 1.6], 5, ICE_FLESH.crimson)
        beam(
            p.neon,
            offset(elbow, 0, 2.4, 0),
            offset(tip, 0, 2.4, 0),
            [0.7, 0.3],
            [ORANGE_NEON, ORANGE_NEON],
        )
        p.hull.cylinder(
            2.2, 4.4, 6, H.panel, Placement(offset(tip, 2.2, 0.6, 0), 0, 0, math.pi / 2)
        )
        icicles(p.flesh, spread(elbow, tip, 3), 2.5)

    return draw


def crane_limbs() -> dict[str, LimbDrawing]:
    """The limbs of the four cranes: a boom on each shoulder and a jib on each elbow."""
    limbs: dict[str, LimbDrawing] = {}
    for crane in CRANES:
        limbs["shoulder-" + crane] = record({"draw": boom(crane)})
        limbs["elbow-" + crane] = record({"draw": jib(crane)})
    return limbs


def pedestal(p: EnemyParts, at: Vec3) -> None:
    """A crane's pedestal on the deck at `at` (its shoulder): a drum, a neon ring, a slewing
    cog."""
    # P16-R06: the root of a tentacle, a swollen ring of muscle with a metal collar.
    p.flesh.cylinder(
        6.5,
        BOOM_Y - 2 - at[1],
        7,
        ICE_FLESH.purple,
        Placement(at, math.pi / 8),
        5,
    )
    p.neon.ring(6.3, 0.8, 8, ORANGE_NEON, Placement(offset(at, 0, 2, 0), math.pi / 8))
    p.hull.cylinder(
        5,
        2,
        8,
        SHADE.edge,
        Placement(offset(at, 0, BOOM_Y - 2 - at[1], 0)),
        4.5,
    )


def grab(p: EnemyParts, at: Vec3) -> None:
    """A grab cannon (P08-R10): a clamshell grab hanging from its jib on a cable, its four tines
    frosted, a cannon between them firing bursts at the player."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    # P16-R06: a tentacle's clubbed tip, four bone hooks round a grafted cannon.
    flesh.cylinder(1.4, BOOM_Y - 8, 4, ICE_FLESH.crimson, Placement(offset(at, 0, 8, 0)), 2)
    flesh.lathe(
        [[6.5, 0], [7.0, 2.0], [5.5, 5.0], [2.5, 6.5]],
        7,
        ICE_FLESH.crimson,
        Placement(offset(at, 0, 2, 0), math.pi / 8),
    )
    hull.cylinder(2.6, 0.6, 8, H.panel, Placement(offset(at, 0, 8.5, 0)))
    for k in range(4):
        yaw = math.pi / 4 + (k * math.pi) / 2
        out = offset(at, math.sin(yaw) * 6.5, 1, math.cos(yaw) * 6.5)
        flesh.cylinder(1.2, 5, 4, ICE_FLESH.bone, Placement(out, yaw, 0.5), 0)
    neon.ring(7.1, 0.7, 8, ORANGE_NEON, Placement(offset(at, 0, 3.2, 0), math.pi / 8))
    barrels(
        p,
        offset(at, GRAB_GUN[0], GRAB_GUN[1], GRAB_GUN[2]),
        [1, 0],
        GRAB_BORE,
    )
    charge.box([1.6, 1, 1.6], WHITE, Placement(offset(at, 0, 9.1, 0)))
