"""P07-R05: pieces shared by the World 1 mini boss models
Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402
from render.geometry.outline import reversed_copy  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")

# Hull shades (dark metal, tinted towards the boss's neon colour by its material).
H = ENEMY_LOOK.hull

# Hull shades beyond `ENEMY_LOOK.hull`: worn edges, weathered patches, hazard paint, soot.
SHADE = {  # type: Any
    # Worn, lighter metal: plate edges, new repair plates.
    "edge": [0.24, 0.24, 0.27],
    # Weathered, slightly warm metal: old patches.
    "patch": [0.14, 0.12, 0.1],
    # Faded hazard paint.
    "hazard": [0.36, 0.3, 0.08],
    # Burnt metal: scars and exhaust soot.
    "soot": [0.025, 0.025, 0.03],
}

# Charge lights are drawn white: their material tints them with the boss's neon colour.
WHITE = [1, 1, 1]  # type: list[float]
# A quarter turn: pitched by it, a lathe's axis (+Y) points along +Z, to the nose.
QUARTER = math.pi / 2


def offset(at: Any, dx: float, dy: float, dz: float) -> Vec3:
    """`at` moved by `[dx, dy, dz]`."""
    return [at[0] + dx, at[1] + dy, at[2] + dz]


def scaled(outline: list[Any], k: float, dx: float = 0, dz: float = 0) -> list[Any]:
    """The outline scaled by `k` around the origin, then moved by `[dx, dz]`."""
    result: list[Any] = []
    for q in outline:
        result.append([q[0] * k + dx, q[1] * k + dz])
    return result


def _double_area(outline: list[Any]) -> float:
    """Twice the signed area of an outline in (x, z): positive when counter-clockwise."""
    total = 0.0
    n = len(outline)
    for i in range(n):
        p = outline[i]
        q = outline[(i + 1) % n]
        total = total + p[0] * q[1] - q[0] * p[1]
    return total


def neon_band(
    builder: Any,
    outline: list[Any],
    heights: list[Any],
    scales: list[Any],
    color: Rgb,
    place: Any = None,
) -> None:
    """An open band of light around an outline (centred on the origin): from the outline scaled
    `scales[0]` at height `heights[0]` to the outline scaled `scales[1]` at `heights[1]`, facing
    out. A neon ring under a rim that, unlike a slab, hides nothing inside the hull (glow layers
    draw lights without occluders).
    """
    y0 = heights[0]
    y1 = heights[1]
    k0 = scales[0]
    k1 = scales[1]
    ring = reversed_copy(outline) if _double_area(outline) <= 0 else outline
    n = len(ring)
    for i in range(n):
        p = ring[i]
        q = ring[(i + 1) % n]
        px = p[0]
        pz = p[1]
        qx = q[0]
        qz = q[1]
        builder.face(
            [
                [px * k0, y0, pz * k0],
                [px * k1, y1, pz * k1],
                [qx * k1, y1, qz * k1],
                [qx * k0, y0, qz * k0],
            ],
            color,
            place,
        )


# The turret's domed, faceted housing (a lathe profile, in units of its radius).
TURRET_DOME = [
    [0.95, 0],
    [1, 0.12],
    [0.82, 0.32],
    [0.5, 0.46],
    [0, 0.5],
]


def turret(parts: Any, at: Vec3, spec: Any) -> None:
    """A gun turret centred on `at` (P07-R05): a faceted dome, a neon ring around its foot and its
    barrels pointing along `yaw`, a charge light at every muzzle. `spec` is a `TurretSpec`:
    `radius`, `barrels`, `gap`, `bore`, `length`, `neon`, and optionally `yaw`, `elevation`,
    `hatch` and `fires`.
    """
    hull = parts.hull
    neon = parts.neon
    charge = parts.charge
    muzzle = parts.muzzle
    r = spec.radius
    yaw = opt(spec, "yaw", 0)
    dome = []
    for point in TURRET_DOME:
        dome.append([point[0] * r * 0.8, point[1] * r])
    hull.lathe(dome, 8, H.panel, Placement(at, yaw + math.pi / 8))
    neon.ring(
        r * 0.84,
        r * 0.08,
        8,
        spec.neon,
        Placement(offset(at, 0, r * 0.05, 0), yaw + math.pi / 8),
    )
    pitch = QUARTER - opt(spec, "elevation", 0)
    length = spec.length + r * 0.5
    for i in range(spec.barrels):
        across = (i - (spec.barrels - 1) / 2) * spec.gap
        foot = [across, r * 0.28, r * 0.3]
        hull.cylinder(
            spec.bore,
            length,
            6,
            H.dark,
            Placement(turned(at, foot, 0, pitch, yaw), yaw, pitch),
            spec.bore * 0.85,
        )
        charge.cylinder(
            spec.bore * 1.05,
            spec.bore * 0.6,
            6,
            WHITE,
            Placement(turned(at, foot, length, pitch, yaw), yaw, pitch),
        )
        muzzle(
            turned(at, foot, length + spec.bore * 0.6, pitch, yaw),
            opt(spec, "fires", None),
        )
    dressing(hull, at, spec)


def dressing(hull: Any, at: Vec3, spec: Any) -> None:
    """The turret's dressing: a mantlet over the barrels' roots, a hatch off to one side, a vent."""
    r = spec.radius
    yaw = opt(spec, "yaw", 0)
    width = (spec.barrels - 1) * spec.gap + spec.bore * 4
    hull.box(
        [width, r * 0.3, r * 0.4],
        H.dark,
        Placement(put(at, 0, r * 0.12, r * 0.5, yaw), yaw),
        H.panel,
    )
    side = opt(spec, "hatch", 1)
    hull.cylinder(
        r * 0.17,
        r * 0.07,
        6,
        SHADE["edge"],
        Placement(put(at, side * r * 0.24, r * 0.44, -r * 0.18, yaw)),
    )
    hull.box(
        [r * 0.55, r * 0.08, r * 0.14],
        H.dark,
        Placement(put(at, 0, r * 0.36, -r * 0.5, yaw), yaw),
    )
    hull.box(
        [r * 0.55, r * 0.08, r * 0.06],
        SHADE["edge"],
        Placement(put(at, 0, r * 0.4, -r * 0.5, yaw), yaw),
    )


def put(at: Vec3, x: float, y: float, z: float, yaw: float) -> Vec3:
    """The point `[x, y, z]` turned by `yaw`, then moved to `at`."""
    d = yawed([x, y, z], yaw)
    return offset(at, d[0], d[1], d[2])


def yawed(p: Any, yaw: float) -> Vec3:
    """Turns `[x, y, z]` by `yaw` around +Y."""
    x = p[0]
    y = p[1]
    z = p[2]
    return [
        x * math.cos(yaw) + z * math.sin(yaw),
        y,
        -x * math.sin(yaw) + z * math.cos(yaw),
    ]


def turned(at: Vec3, foot: Any, along: float, pitch: float, yaw: float) -> Vec3:
    """Where a barrel standing on `foot` (around the turret's centre `at`), pitched and yawed, is
    `along` its axis: its base (0) or its muzzle (its length).
    """
    axis = yawed([0, along * math.cos(pitch), along * math.sin(pitch)], yaw)
    f = yawed(foot, yaw)
    return offset(at, f[0] + axis[0], f[1] + axis[1], f[2] + axis[2])


def socket(hull: Any, at: Vec3, radius: float, height: float) -> None:
    """A dark round socket on the core where a part was mounted (left once the part is gone)."""
    hull.cylinder(radius, height, 8, H.dark, Placement(at, math.pi / 8), radius * 0.85)


def sign_of(x: float) -> float:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def radius_of(parts: Any, index: int, fallback: float) -> Any:
    """`parts[index]?.radius ?? fallback`: the radius of a config part, or `fallback`."""
    if index < len(parts) and parts[index] != None and parts[index].radius != None:  # noqa: E711
        return parts[index].radius
    return fallback
