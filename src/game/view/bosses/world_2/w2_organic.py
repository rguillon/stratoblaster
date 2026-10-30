"""The Cyber-Organic pieces of the World 2 bosses (ice world), ported from
`bosses/world-2/w2-organic.ts`: pale, cold flesh with crystals of frost grown through it, bone,
and metal grafts. Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from render.geometry.organic import carapace, curve, organ, plate, tendril, vein
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.organic import SegmentedBody  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

F = ENEMY_LOOK.flesh
M = ENEMY_LOOK.hull

# The World 2 flesh shades: cold teal and purple, bone, and the ice grown through them.
ICE_FLESH = record(
    {
        "teal": F.teal,
        "purple": F.purple,
        "crimson": F.crimson,
        "sinew": F.sinew,
        "bone": F.bone,
        "membrane": F.membrane,
        # Rimed flesh: a frosted, pale teal (top faces).
        "rime": [0.13, 0.17, 0.19],
        # Crystals of ice grown through the flesh.
        "crystal": [0.15, 0.19, 0.24],
        # The seams between shell plates.
        "seam": [0.02, 0.04, 0.05],
    }
)

# Metal shades for the grafts.
GRAFT = record({"base": M.base, "panel": M.panel, "dark": M.dark})


def shell(b: SolidBuilder, body: SegmentedBody, color: Rgb = ICE_FLESH.teal) -> None:
    """A shell over a swollen body (P16-R01): teal plates with dark seams."""
    carapace(b, body, [color, ICE_FLESH.seam])


def crystals(b: SolidBuilder, at: Vec3, size: float, n: int = 3) -> None:
    """A cluster of ice crystals grown from the flesh at `at`: `n` thin four-sided spikes, `size`
    long, fanning out upwards, uneven."""
    for k in range(n):
        a = (2 * math.pi * k) / n + size
        length = size * (0.7 + 0.3 * ((k * 7) % 3))
        b.cylinder(
            length * 0.2,
            length,
            4,
            ICE_FLESH.crystal,
            Placement(at, 0, 0.5 * math.cos(a), 0.5 * math.sin(a)),
            0,
        )


def spine_row(b: SolidBuilder, from_: Vec3, to: Vec3, n: int, size: float) -> None:
    """A row of spikes of ice along a back, from `from_` to `to`, `size` tall."""
    for i in range(n):
        t = 0.5 if n == 1 else i / (n - 1)
        at: Vec3 = [
            from_[0] + (to[0] - from_[0]) * t,
            from_[1] + (to[1] - from_[1]) * t,
            from_[2] + (to[2] - from_[2]) * t,
        ]
        b.cylinder(
            size * 0.25,
            size * (0.8 + 0.4 * (i % 2)),
            4,
            ICE_FLESH.crystal,
            Placement(at, 0, -0.4),
            0,
        )


def sinew(
    b: SolidBuilder,
    from_: Vec3,
    to: Vec3,
    r: float,
    color: Rgb = ICE_FLESH.sinew,
    bow: Vec3 | None = None,
) -> None:
    """A sinew from `from_` to `to`, bowed by `bow`, thinning from `r` to half of it."""
    if bow == None:  # noqa: E711
        bow = [0, r, 0]
    tendril(b, curve(from_, to, bow, 3), [r, r * 0.5], 4, color)


def glow_vein(p: EnemyParts, from_: Vec3, to: Vec3, width: float, glow: Rgb) -> None:
    """A glowing vein from `from_` to `to`, bowed upwards."""
    vein(p.vein, curve(from_, to, [0, width, 0], 3), width, glow)


def gland(p: EnemyParts, at: Vec3, radius: float, glow: Rgb, rim: Rgb = ICE_FLESH.purple) -> None:
    """A gland: a lit bulb of `radius` on `at`, in a ring of flesh."""
    p.flesh.ring(radius * 1.3, radius * 0.6, 6, rim, Placement(at))
    organ(p.vein, radius, 5, glow, Placement(at), 0.6)


def armoured_organ(
    p: EnemyParts,
    at: Vec3,
    radius: float,
    glow: Rgb,
    color: Rgb = ICE_FLESH.purple,
    height: float = 0.5,
) -> None:
    """A destroyable growth (P16-R05): a swollen organ of `radius` on `at`, a metal armour plate on
    its top, crystals on its flank and a gland lit `glow`. Its outline stays clear: one bulb."""
    x = at[0]
    y = at[1]
    z = at[2]
    organ(p.flesh, radius, 6, color, Placement([x, y - radius * 0.2, z]), height)
    r = radius * 0.55
    top = y - radius * 0.2 + radius * 2 * height * 0.8
    hexagon: list[list[float]] = []
    for k in range(6):
        a = (2 * math.pi * (k + 0.5)) / 6
        hexagon.append([math.sin(a) * r, math.cos(a) * r])
    plate(p.hull, hexagon, [0, radius * 0.18], [GRAFT.base, GRAFT.panel], Placement([x, top, z]))
    crystals(p.flesh, [x + radius * 0.6, y + radius * 0.4, z - radius * 0.3], radius * 0.5, 2)
    gland(p, [x - radius * 0.55, y + radius * 0.5, z + radius * 0.35], radius * 0.18, glow)


def fringe(
    b: SolidBuilder,
    at: Vec3,
    direction: list[float],
    n: int,
    length: float,
    color: Rgb = ICE_FLESH.sinew,
) -> None:
    """Flesh tendrils hanging off `at` outwards along `direction` (x, z), `n` of them, `length`
    long."""
    dx = direction[0]
    dz = direction[1]
    for i in range(n):
        s = (i - (n - 1) / 2) * 0.5
        tip: Vec3 = [
            at[0] + (dx - dz * s) * length,
            at[1] - 1,
            at[2] + (dz + dx * s) * length,
        ]
        tendril(b, curve(at, tip, [0, 1.5, 0], 2), [length * 0.12, 0], 3, color)


def ice_teeth(b: SolidBuilder, outline: list[OutlinePoint], y: float, every: int) -> None:
    """Icicles of `ICE_FLESH.crystal` under every `every`-th corner of `outline`, at height `y`."""
    for i in range(len(outline)):
        if i % every != 0:
            continue
        x = outline[i][0]
        z = outline[i][1]
        length = 2.5 + (i % 3)
        b.cylinder(
            length * 0.22,
            length,
            4,
            ICE_FLESH.crystal,
            Placement([x * 0.97, y, z * 0.97], 0, math.pi),
            0,
        )
