"""The Boreal Citadel's polar city: its colours, the towers and heated domes on its deck, the
icicles under its edges, ported from `bosses/world-2/boreal-citadel-city.ts` (P08-R10, 2-5).
Model space: logical pixels, nose +Z (down the screen), Y up towards the camera; +X is the
screen's left.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.world_2.w2_organic import ICE_FLESH
from game.view.enemies.enemy_shapes import SIDES
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

_AURORA_NEON = BOSS_LOOK.neon["boreal-citadel"]
# Aurora green: the boss's registered neon (GD-61).
AURORA = [1, 1, 1] if _AURORA_NEON == None else _AURORA_NEON  # noqa: E711
# Violet: the boss's second neon colour.
VIOLET = [0.62, 0.28, 1]

# World 2 frost (P08-R10): snow on top faces, pale ice, and frosted (snow-dusted) panels.
FROST = record(
    {
        "snow": [0.75, 0.82, 0.9],
        "ice": [0.56, 0.7, 0.92],
        "frosted": [0.36, 0.4, 0.47],
    }
)

# Heights of the deck's top and of the raised avenue down its middle.
CITADEL_DECK = record({"top": 6, "avenue": 12})


def rect(w: float, d: float, centre: list[float] | None = None) -> list[OutlinePoint]:
    """A rectangle `w` wide and `d` long around `centre` (x, z), the origin by default."""
    if centre == None:  # noqa: E711
        centre = [0, 0]
    x = centre[0]
    z = centre[1]
    return [
        [x - w / 2, z - d / 2],
        [x + w / 2, z - d / 2],
        [x + w / 2, z + d / 2],
        [x - w / 2, z + d / 2],
    ]


class Tower:
    """A tower of the city (an interface in the TypeScript): its footprint `w` by `d` at `x`, `z`
    on the deck, its height `h`, a setback `tier` `[w, d, h]` on top (or None), and the colour
    `lit` of its windows."""

    def __init__(
        self,
        x: float,
        z: float,
        size: list[float],
        h: float,
        tier: list[float] | None,
        lit: Rgb,
    ) -> None:
        self.x = x
        self.z = z
        self.w = size[0]
        self.d = size[1]
        self.h = h
        self.tier = tier
        self.lit = lit


# A spire taller than this is grown of purple flesh, a shorter one of sinew.
TALL_SPIRE = 12

# The towers of the right half of the deck (+X), mirrored on the left (some swapped in colour).
TOWERS = [
    Tower(12, 66, [9, 8], 11, None, VIOLET),
    Tower(26, 60, [7, 7], 16, [4.5, 4.5, 5], AURORA),
    Tower(50, 12, [8, 10], 13, [5, 6, 4], AURORA),
    Tower(52, -6, [7, 8], 9, None, VIOLET),
    Tower(24, -24, [8, 9], 19, [5, 6, 6], VIOLET),
    Tower(26, -62, [10, 8], 12, None, AURORA),
    Tower(42, -60, [7, 7], 8, None, VIOLET),
    Tower(40, 20, [6, 6], 10, None, VIOLET),
    Tower(36, 2, [6, 7], 15, [4, 4, 4], AURORA),
    Tower(36, -12, [6, 6], 7, None, VIOLET),
    Tower(10, -72, [6, 6], 9, None, AURORA),
]


def windows(neon: SolidBuilder, at: Vec3, size: list[float], lit: Rgb) -> None:
    """Lit window bands on a block's front (+Z) face: `at` is its left foot and front, `size`
    is `[w, h]`."""
    x = at[0]
    y0 = at[1]
    front = at[2]
    w = size[0]
    h = size[1]
    rows = math.floor((h - 1.5) / 3)
    for r in range(rows):
        y = y0 + 1.6 + r * 3
        a = x - w / 2 + 1
        b = x + w / 2 - 1
        neon.face(
            [
                [a, y, front],
                [b, y, front],
                [b, y + 1.1, front],
                [a, y + 1.1, front],
            ],
            lit,
        )


def _draw_tower(p: EnemyParts, t: Tower, s: float) -> None:
    """A tower on the deck: a dark block, its snowed roof, lit windows, a setback tier."""
    flesh = p.flesh
    neon = p.neon
    base = CITADEL_DECK.top
    x = s * t.x
    # P16-R06: a spire of flesh grown from the back, tapering, its pores lit like windows.
    flesh.bevel_slab(
        rect(t.w, t.d, [x, t.z]),
        [base, base, base + t.h],
        [0, t.w * 0.3],
        ICE_FLESH.purple if t.h > TALL_SPIRE else ICE_FLESH.sinew,
        None,
        ICE_FLESH.rime,
    )
    # The left half's towers have the other colour, so the city is not a mirror image.
    lit = t.lit if s > 0 else (VIOLET if t.lit is AURORA else AURORA)
    windows(neon, [x, base, t.z + t.d / 2 + 0.1], [t.w, t.h], lit)
    if t.tier == None:  # noqa: E711
        return
    w = t.tier[0]
    d = t.tier[1]
    h = t.tier[2]
    top = base + t.h
    # A crystal grown out of the spire's tip.
    flesh.cylinder(
        min(w, d) * 0.4,
        h * 1.4,
        4,
        ICE_FLESH.crystal,
        Placement([x, top, t.z - 0.5]),
        0,
    )
    windows(neon, [x, top - 1, t.z - 0.5 + d / 2 + 0.1], [w, h + 1], lit)


# A small heated dome of the city (lathe profile): glass glowing warm through the frost.
CITY_DOME = [
    [5, 0],
    [4.4, 2.4],
    [2.6, 4.2],
    [0, 5],
]


def draw_city(p: EnemyParts) -> None:
    """The city on the deck: its towers, two small heated domes, a few roof masts."""
    for s in SIDES:
        for t in TOWERS:
            _draw_tower(p, t, s)
        at: Vec3 = [s * 15, CITADEL_DECK.top, 77]
        p.flesh.cylinder(5.6, 1.2, 7, ICE_FLESH.purple, Placement(at))
        p.neon.lathe(
            CITY_DOME,
            8,
            AURORA if s > 0 else VIOLET,
            Placement([at[0], at[1] + 1.2, at[2]]),
        )
        p.hull.ring(5.2, 0.6, 8, H.panel, Placement([at[0], at[1] + 1.2, at[2]]))
        p.flesh.cylinder(
            0.4,
            9,
            4,
            ICE_FLESH.sinew,
            Placement([s * 26, CITADEL_DECK.top + 21, 60]),
            0.2,
        )
        p.neon.box([0.8, 0.8, 0.8], VIOLET, Placement([s * 26, CITADEL_DECK.top + 30, 60]))


def icicles(hull: SolidBuilder, pair: list[OutlinePoint], y: float, count: int) -> None:
    """Icicles hanging under the deck's edge between the two points of `pair` (seen from above,
    at height `y`), `count` of them, a little longer and shorter by turns."""
    a = pair[0]
    b = pair[1]
    for i in range(count):
        t = (i + 0.5) / count
        at: Vec3 = [a[0] + (b[0] - a[0]) * t, y, a[1] + (b[1] - a[1]) * t]
        hull.cylinder(0.9, 3 + (i % 3) * 1.6, 4, ICE_FLESH.crystal, Placement(at, 0, math.pi), 0)
