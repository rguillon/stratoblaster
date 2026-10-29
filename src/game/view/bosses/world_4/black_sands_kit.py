"""P10-R11, 4-1: the heavy industry on the Black sands' bosses (the Cinder Crab and the Steam
Dreadnought): soot, molten seams glowing between the plates, steam, struts and barrels (GD-61,
World 4: dark metal with neon, plus soot, heat glow and molten seams). Ported from
`bosses/world-4/black-sands-kit.ts`. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record  # noqa: E402
from game.view.bosses.final_boss_shapes import edge_strips  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H  # noqa: E402
from game.view.enemies.enemy_shapes import decal  # noqa: E402
from render.geometry.outline import hypot2, hypot3  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
type OutlinePoint = list[float]
__pragma__("noskip")

from game.view.bosses.boss_limbs import boss_point  # noqa: E402

# Volcanic shades: molten metal in the seams, soot, ash dust, steam lit by the furnaces.
FORGE = record(
    {
        "molten": [1, 0.3, 0.02],
        "ember": [0.75, 0.12, 0.01],
        "soot": SHADE["soot"],
        "ash": [0.2, 0.19, 0.18],
        "steam": [0.2, 0.19, 0.19],
    }
)


def strut(builder: Any, ends: list[Vec3], radii: list[float], color: Rgb, sides: int = 6) -> None:
    """A cylinder from `a` to `b` (radius `r` at `a`, `rb` at `b`, `sides` facets): a strut, a leg,
    a barrel. Pitched off +Y, then yawed, so that its axis runs along `b - a`."""
    a = ends[0]
    b = ends[1]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = hypot3(dx, dy, dz)
    pitch = math.atan2(hypot2(dx, dz), dy)
    builder.cylinder(
        radii[0], length, sides, color, Placement(a, math.atan2(dx, dz), pitch), radii[1]
    )


def barrel_to(parts: Any, tip: list[float], dims: list[float], kind: str = "gun") -> None:
    """A barrel along +Z ending at the muzzle `tip` (playfield, `boss_point`), `[radius, length]`:
    its dark tube, a charge light at its mouth, and the muzzle's mark (of `kind`)."""
    p = boss_point(tip[0], tip[1], tip[2])
    x = p[0]
    y = p[1]
    z = p[2]
    radius = dims[0]
    length = dims[1]
    light = radius * 1.2
    parts.hull.cylinder(
        radius, length, 6, H.dark, Placement([x, y, z - light - length], 0, QUARTER)
    )
    parts.hull.ring(
        radius * 1.25,
        length * 0.18,
        6,
        H.panel,
        Placement([x, y, z - light - length * 0.35], 0, QUARTER),
    )
    parts.charge.cylinder(radius * 0.92, light, 6, WHITE, Placement([x, y, z - light], 0, QUARTER))
    parts.muzzle([x, y, z], kind)


def molten_seam(neon: Any, points: list[OutlinePoint], y: float, width: float = 0.7) -> None:
    """A molten seam along `points` (seen from above) at height `y`: a thin glowing line."""
    edge_strips(neon, points, width, [y - 0.15, y + 0.12], FORGE.molten)


def soot(hull: Any, outline: Any, y: float) -> None:
    """A soot stain over `outline` lying on a hull at height `y`."""
    decal(hull, outline, y + 0.04, FORGE.soot)


def blot(centre: OutlinePoint, radius: float, stretch: float = 1, seed: float = 0) -> list[Any]:
    """A rough, roundish outline `radius` wide around `[x, z]`, stretched `stretch` times along
    Z."""
    x = centre[0]
    z = centre[1]
    out: list[OutlinePoint] = []
    for k in range(6):
        a = (k * math.pi) / 3 + seed
        r = radius * (0.75 + 0.25 * math.sin(seed * 2.7 + k * 1.9))
        out.append([x + math.cos(a) * r, z + math.sin(a) * r * stretch])
    return out


def steam(neon: Any, origin: Vec3, count: int, size: float) -> None:
    """Puffs of steam trailing back (towards -Z) and rising from `from`: low-poly lumps growing as
    they go, faintly lit by the furnaces below (drawn as lights, so the hull's tint leaves them)."""
    for i in range(count):
        r = size * (1 + 0.45 * i)
        at = [
            origin[0] + (0.8 if i % 2 else -0.6),
            origin[1] + 1.6 * i,
            origin[2] - 4.5 * i,
        ]
        neon.lathe(
            [
                [r * 0.55, 0],
                [r, r * 0.45],
                [r * 0.7, r * 0.95],
                [0, r * 1.1],
            ],
            5,
            FORGE.steam,
            Placement(at, i * 0.7),
        )


def bolts(hull: Any, points: list[OutlinePoint], y: float, size: float) -> None:
    """Rivets or bolt heads along a row of `points` at height `y`, `size` wide."""
    for p in points:
        hull.box([size, size * 0.5, size], SHADE["edge"], Placement([p[0], y, p[1]]))
