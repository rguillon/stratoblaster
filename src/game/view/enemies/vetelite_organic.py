"""P16-R04: Cyber-Organic pieces shared by the veteran and elite models Logical pixels, nose +Z, Y
up."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from render.geometry.organic import curve, tendril  # noqa: E402

F = ENEMY_LOOK.flesh

# A lean rounded cross-section (7 points instead of 9): a swollen body on fewer triangles.
LEAN_SECTION = [  # type: list[list[float]]
    [0.5, 0],
    [1, 0.4],
    [0.6, 0.9],
    [0, 1],
    [-0.6, 0.9],
    [-1, 0.4],
    [-0.5, 0],
]


def _with_wing(wing: Any, root: list[float], tips: list[list[float]]) -> Any:
    """`{ ...wing, root, tips }`: a copy of a membrane wing with other points."""
    __pragma__("js", "{}", "return Object.assign({}, wing, {root: root, tips: tips});")
    return None


def sided(wing: Any, s: int) -> Any:
    """`wing` (drawn on the right) mirrored to side `s`."""
    root = [s * wing["root"][0], wing["root"][1]]
    tips = [[s * p[0], p[1]] for p in wing["tips"]]
    return _with_wing(wing, root, tips)


def membrane_draw(w: Any, span: float) -> Any:
    """What a membrane wing draws in its model space (factory: no loop closure)."""

    def draw(parts: Any) -> None:
        # A `membrane` skin, and one `bone` strut along its leading tip (lean on triangles).
        root = w["root"]
        tips = w["tips"]
        y = w["y"]
        thickness = w["thickness"]
        strut = w["strut"]
        parts.flesh.slab([root] + tips, [y - thickness / 2, y + thickness / 2], F.membrane)
        tip = tips[0] if len(tips) > 0 else root
        path = curve([root[0], y, root[1]], [tip[0], y, tip[1]], [0, thickness * 2, 0], 2)
        tendril(parts.flesh, path, [strut, strut * 0.2], 3, F.bone)

    return draw


def membrane_pair(p: Any, wing: Any, span: float) -> None:
    """P16-R04: a pair of membrane wings (`wing` is the right one), a `membrane` skin on a `bone`
    strut, each fluttering on its root (P16-R07)."""
    for s in SIDES:
        w = sided(wing, s)
        p.flap([w["root"][0], w["y"], w["root"][1]], s, span, membrane_draw(w, span))


def mandibles(b: Any, at: Vec3, size: Any) -> None:
    """A pair of mandibles hooking forward and in from `at`, in bone."""
    x = at[0]
    y = at[1]
    z = at[2]
    spread = size[0]
    length = size[1]
    radius = size[2]
    for s in SIDES:
        path = curve(
            [x + s * spread * 0.5, y, z],
            [x + s * spread * 0.3, y, z + length],
            [s * spread * 0.6, 0, 0],
            2,
        )
        tendril(b, path, [radius, 0], 3, F.bone)


def sinew(b: Any, start: Vec3, end: Vec3, radii: Any, color: Any = None, bow: Any = None) -> None:
    """A sinew (a thin flesh tendril, 4 facets) from `start` to `end`, bowed by `bow`."""
    tint = color if color != None else F.sinew  # noqa: E711
    bend = bow if bow != None else [0, 0.6, 0]  # noqa: E711
    tendril(b, curve(start, end, bend, 2), [radii[0], radii[1]], 4, tint)
