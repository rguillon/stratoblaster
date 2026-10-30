"""P10-R11, 4-3: the Magma Salamander's parts (its back fins and its tail) and its molten look.
Logical pixels, nose +Z, Y up (towards the
camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_4.magma_salamander import (  # noqa: E402
    SALAMANDER_FIN_GUNS,
    SALAMANDER_STINGER,
    SALAMANDER_TAIL,
)
from game.config.record import record  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.final_boss_shapes import sided  # noqa: E402
from game.view.bosses.mini_boss_greebles import seam  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H, offset  # noqa: E402
from game.view.bosses.world_3.toucan_jungle import segment  # noqa: E402
from game.view.bosses.world_4.living_forge import SKIN, glands  # noqa: E402
from game.view.enemies.enemy_shapes import POD_SECTION  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

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


def _sign(v: float) -> float:
    """`Math.sign`."""
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


# The Salamander's orange-yellow neon.
SALAMANDER_NEON = _neon_or("magma-salamander", [1, 0.62, 0.08])
# The molten glow between its plates (World 4: magma seams), hotter and redder than its neon.
MOLTEN = [1.0, 0.36, 0.04]
# Soot-blackened, heat-blued metal on its plates (World 4: heavy industry).
SCORCH = [0.05, 0.045, 0.05]


def barrel(p: Any, tip: Vec3, dims: list[float], fires: str = "gun") -> None:
    """A gun barrel along +Z ending at `tip`, `radius` thick and `length` long: dark steel, a charge
    light at its mouth, the muzzle marked there (`fires`: what it fires)."""
    radius = dims[0]
    length = dims[1]
    x = tip[0]
    y = tip[1]
    z = tip[2]
    p.hull.cylinder(radius, length, 6, H.dark, Placement([x, y, z - length - 0.6], 0, QUARTER))
    p.charge.cylinder(radius * 1.05, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
    p.muzzle(tip, fires)


def molten_seam(neon: Any, dims: list[float]) -> None:
    """A molten seam between two armour plates: a glowing band `width` across at height `y`, at `z`,
    sunk a little under the plates around it."""
    neon.box([dims[0], 0.6, 1.4], MOLTEN, Placement([0, dims[1], dims[2]]))


# The left fin seen from above (model +X), from its root's leading edge out and back.
FIN = [
    [20.0, 8.0],
    [33.0, 10.0],
    [46.0, 6.0],
    [53.0, 0.0],
    [49.0, -4.0],
    [52.0, -10.0],
    [44.0, -12.0],
    [46.0, -18.0],
    [34.0, -16.0],
    [22.0, -12.0],
]
# The fin's spines, root to tip (left fin): each lit along its ridge.
SPINES = [
    [
        [22.0, 6.0],
        [52.0, 0.0],
    ],
    [
        [22.0, -2.0],
        [50.0, -9.0],
    ],
    [
        [22.0, -9.0],
        [45.0, -17.0],
    ],
]
# Height of the fin: a thick, heat-scarred frill over its gun pod.
FIN_Y = 6
# The gun pod under the fin's leading edge (loft stations around the part's centre).
POD = [
    [-6.0, 3.0, -2.0, 2.0],
    [0.0, 4.4, -2.5, 3.0],
    [7.0, 3.8, -2.0, 2.6],
    [11.0, 2.4, -1.0, 1.6],
]


def fin(p: Any, at: Vec3) -> None:
    """A back fin around its centre `at` (P10-R11): a spiny frill of soot-black armour, its spines
    lit orange, a molten glow at its root, and under its leading edge a pod with two fan barrels."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    s = _sign(at[0])
    # P16-R05: a membrane frill on bone spines, a gland at its root.
    flesh.bevel_slab(
        sided(FIN, s),
        [FIN_Y - 1.4, FIN_Y, FIN_Y + 1.2],
        [0.4, 0.6],
        SKIN.dark,
        None,
        SKIN.base,
    )
    glands(p, [[s * 22, FIN_Y + 0.8, 4]], 1.5, MOLTEN)
    for pair in SPINES:
        a = pair[0]
        b = pair[1]
        seam(flesh, [s * a[0], a[1]], [s * b[0], b[1]], [FIN_Y + 1.1, 1.4, 0.8], SKIN.bone)
        seam(neon, [s * a[0], a[1]], [s * b[0], b[1]], [FIN_Y + 1.8, 0.45, 0.3], SALAMANDER_NEON)
    neon.box([3, 0.8, 18], MOLTEN, Placement([s * 20, FIN_Y + 0.6, -2]))
    hull.loft(POD_SECTION, POD, H.panel, Placement([at[0], 0, at[2]]))
    # The left fin (screen left) is on the model's +X side.
    guns = SALAMANDER_FIN_GUNS if s > 0 else mirror(SALAMANDER_FIN_GUNS)
    for m in guns:
        barrel(p, boss_point(m[0], m[1], m[2]), [0.9, 5])


def tail_points() -> list[Any]:
    """The model-space points of the tail at rest: its root, its knuckle, its stinger's tip."""
    root_at = SALAMANDER_TAIL.root
    knuckle_at = SALAMANDER_TAIL.knuckle
    root = boss_point(root_at[0], root_at[1], 4)
    knuckle = boss_point(knuckle_at[0], knuckle_at[1], 4)
    if len(SALAMANDER_STINGER) > 0:
        m = SALAMANDER_STINGER[0]
        tip = boss_point(m[0], m[1], m[2])
    else:
        tip = knuckle
    return [root, knuckle, tip]


def _lerp(a: Vec3, b: Vec3, t: float) -> Vec3:
    """A point `t` of the way from `a` to `b`."""
    return [
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    ]


def _tail_root(p: Any) -> None:
    """The tail's root, on its root joint (D-061): two armoured rings tapering to the knuckle, a
    molten glow between them, a spine of neon studs along its back."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    points = tail_points()
    root = points[0]
    knuckle = points[1]
    segment(
        flesh,
        [offset(root, 0, -3, 0), offset(knuckle, 0, -2, 0)],
        [6.4, 4.8],
        SKIN.base,
        6,
    )
    for ring in [[0, 0.45, 7], [0.52, 0.95, 5.8]]:
        a = ring[0]
        b = ring[1]
        r = ring[2]
        segment(
            flesh, [_lerp(root, knuckle, a), _lerp(root, knuckle, b)], [r, r * 0.9], SKIN.panel, 6
        )
    for t in [0.2, 0.7]:
        neon.box(
            [1.2, 1, 1.2], SALAMANDER_NEON, Placement(offset(_lerp(root, knuckle, t), 0, 5.6, 0))
        )
    hull.cylinder(5.4, 3, 7, H.panel, Placement(offset(knuckle, 0, -2, 0)))


def tail_limbs() -> Any:
    """The limbs on its tail's joints: the root segment (the tip is the tail part itself)."""
    return {"tail-root": record({"draw": _tail_root})}


# The stinger's bulb at the tail's tip (a lathe profile around its axis, +Y).
BULB = [
    [0.0, -5.0],
    [4.4, -3.4],
    [5.2, 0.0],
    [4.0, 3.6],
    [0.0, 5.0],
]


def tail(p: Any, _at: Any = None) -> None:
    """The tail's tip around its centre (P10-R11), on its knuckle joint: a tapering, plated segment,
    a glowing bulb of magma at its end and the stinger barrel on top of it, pointing forward, that
    sweeps its lines of bullets across the screen."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    flesh = p.flesh
    points = tail_points()
    knuckle = points[1]
    tip = points[2]
    bulb = [tip[0], 3, tip[2] - 4]
    segment(flesh, [knuckle, bulb], [4.8, 3.6], SKIN.base, 6)
    segment(
        flesh,
        [_lerp(knuckle, bulb, 0.15), _lerp(knuckle, bulb, 0.55)],
        [5.4, 4.6],
        SKIN.panel,
        6,
    )
    neon.box(
        [5, 0.6, 1.2],
        MOLTEN,
        Placement(
            offset(_lerp(knuckle, bulb, 0.6), 0, 4, 0),
            math.atan2(bulb[0] - knuckle[0], bulb[2] - knuckle[2]),
        ),
    )
    flesh.lathe(BULB, 7, SKIN.dark, Placement(bulb, 0, QUARTER))
    charge.ring(5.3, 1, 7, WHITE, Placement(offset(bulb, 0, 0, -0.5), 0, QUARTER))
    hull.box([3.4, tip[1] - bulb[1] - 1, 5], H.panel, Placement(offset(bulb, 0, 1, 2)))
    barrel(p, tip, [1.2, 5])
    neon.ring(1.7, 0.7, 6, SALAMANDER_NEON, Placement(offset(tip, 0, 0, -4.4), 0, QUARTER))
