"""P07-R05: shapes shared by the World 1 final bosses (Storm Petrel, Gull Mothership, Mesa
Fortress) Logical pixels, nose +Z, Y up (towards the
camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_shapes import flip_x  # noqa: E402
from render.geometry.outline import hypot2, reversed_copy  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2


def shift(at: Any, d: Any) -> Vec3:
    """`at` moved by `[dx, dy, dz]`."""
    return [at[0] + d[0], at[1] + d[1], at[2] + d[2]]


def mirrored(right: list[Any]) -> list[Any]:
    """A whole symmetric outline from its right half (+X), which runs from a point on the axis at
    the front to a point on the axis at the back: the left half is its mirror image."""
    left = reversed_copy(flip_x(right))
    result: list[Any] = []
    result.extend(right)
    result.extend(left[1 : len(left) - 1])
    return result


def sided(outline: list[Any], side: float) -> list[Any]:
    """The outline mirrored left to right when `side` is -1, as it is when `side` is 1."""
    return outline if side > 0 else flip_x(outline)


def strip(
    builder: Any,
    a: list[Any],
    b: list[Any],
    width: float,
    heights: list[Any],
    color: Rgb,
) -> None:
    """A light strip `width` wide from `a` to `b` (seen from above), between heights `heights[0]`
    and `heights[1]`: neon along a wing's edge or a slit in an armour plate."""
    ax = a[0]
    az = a[1]
    bx = b[0]
    bz = b[1]
    length = hypot2(bx - ax, bz - az) or 1
    nx = ((az - bz) / length) * (width / 2)
    nz = ((bx - ax) / length) * (width / 2)
    outline = [
        [ax + nx, az + nz],
        [bx + nx, bz + nz],
        [bx - nx, bz - nz],
        [ax - nx, az - nz],
    ]
    builder.slab(outline, heights, color)


def edge_strips(
    builder: Any,
    points: list[Any],
    width: float,
    heights: list[Any],
    color: Rgb,
) -> None:
    """Strips along the edges of a polyline `points` (open: the last point does not join the
    first)."""
    for i in range(len(points) - 1):
        strip(builder, points[i], points[i + 1], width, heights, color)


def barrels(
    parts: Any,
    at: Vec3,
    counts: list[Any],
    sizes: list[Any],
    fires: Any = "gun",
) -> None:
    """Gun barrels pointing forward (+Z) from `at`, `counts[1]` apart, `sizes[1]` long, with a
    charge light at each muzzle (it brightens as the next shot charges); they fire `fires`
    (`EnemyParts.muzzle`). `counts` is `[count, gap]` and `sizes` is `[radius, length]`.
    """
    hull = parts.hull
    charge = parts.charge
    muzzle = parts.muzzle
    count = counts[0]
    gap = counts[1]
    radius = sizes[0]
    length = sizes[1]
    for i in range(count):
        x = (i - (count - 1) / 2) * gap
        hull.cylinder(
            radius,
            length,
            6,
            H.dark,
            Placement(shift(at, [x, 0, 0]), 0, QUARTER),
            radius * 0.8,
        )
        charge.cylinder(
            radius * 0.9,
            radius * 1.4,
            6,
            WHITE,
            Placement(shift(at, [x, 0, length]), 0, QUARTER),
        )
        muzzle(shift(at, [x, 0, length + radius * 1.4]), fires)


# A turret's armoured base and dome (a lathe profile, around its centre).
TURRET_DOME = [
    [1, 0],
    [1, 0.35],
    [0.78, 0.75],
    [0.4, 1],
    [0, 1.05],
]


def turret(
    p: Any,
    at: Vec3,
    radius: float,
    neon_spec: list[Any],
    fires: Any = "gun",
) -> None:
    """A gun turret `radius` wide on its base at `at`: a faceted dome, a neon ring around its base,
    and `count` barrels pointing forward from its front. `neon_spec` is `[count, neon]`."""
    count = neon_spec[0]
    neon = neon_spec[1]
    height = radius * 0.55
    dome: list[Any] = []
    turret_dome: list[Any] = TURRET_DOME
    for point in turret_dome:
        dome.append([point[0] * radius, point[1] * height])
    p.hull.lathe(dome, 8, H.panel, Placement(at))
    p.neon.ring(radius * 1.02, radius * 0.1, 8, neon, Placement(shift(at, [0, height * 0.2, 0])))
    p.hull.box(
        [radius * 0.5, radius * 0.08, radius * 0.4],
        H.dark,
        Placement(shift(at, [0, height * 1.02, -radius * 0.2])),
    )
    gun = shift(at, [0, height * 0.5, radius * 0.6])
    barrels(p, gun, [count, radius * 0.38], [radius * 0.13, radius * 0.9], fires)


def missile_tips(
    parts: Any,
    at: Vec3,
    grid: list[Any],
    spacing_radius: list[Any],
) -> None:
    """Missile tips standing in a launcher at `at`, `grid` is `[rows, cols]` of them `spacing`
    apart, pointing up (towards the camera) out of their tubes; the tips light up as a salvo
    charges. `spacing_radius` is `[spacing, radius]`."""
    hull = parts.hull
    charge = parts.charge
    muzzle = parts.muzzle
    rows = grid[0]
    cols = grid[1]
    spacing = spacing_radius[0]
    radius = spacing_radius[1]
    for r in range(rows):
        for c in range(cols):
            x = (c - (cols - 1) / 2) * spacing
            z = (r - (rows - 1) / 2) * spacing
            tube = shift(at, [x, 0, z])
            hull.ring(radius * 1.3, radius * 0.9, 6, H.dark, Placement(tube))
            charge.cylinder(
                radius,
                radius * 2.2,
                6,
                WHITE,
                Placement(shift(tube, [0, radius * 0.4, 0])),
                0,
            )
            muzzle(shift(tube, [0, radius * 2.6, 0]), "missile")


def open_hatch(parts: Any, at: Vec3, size: list[Any]) -> None:
    """An open hatch at `at` in a deck: a dark well `[w, d]` big, its two doors swung up on either
    side (along Z), and a glowing floor that brightens as the next launch charges."""
    hull = parts.hull
    charge = parts.charge
    w = size[0]
    d = size[1]
    hull.box([w, 0.3, d], H.dark, Placement(at))
    charge.box([w * 0.7, 0.3, d * 0.8], WHITE, Placement(shift(at, [0, 0.12, 0])))
    for s in [-1, 1]:
        # A door hinged on the well's side, leaning outwards.
        door = [
            [0, -d / 2],
            [w * 0.42, -d / 2],
            [w * 0.42, d / 2],
            [0, d / 2],
        ]
        hull.slab(
            door,
            [-0.4, 0.4],
            H.panel,
            Placement(shift(at, [(s * w) / 2, 0.3, 0]), 0 if s > 0 else math.pi, 0, 1),
        )
