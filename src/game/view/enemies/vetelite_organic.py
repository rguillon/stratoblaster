# Copyright (c) 2026 Renaud Guillon
"""Cyber-Organic pieces shared by the veteran and elite models.

They are the extra limbs and grafts that show their tier (ENM-02). Logical pixels, nose +Z, Y up.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK
from game.config.record import concat
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import curve, tendril

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.config.record import fields_of, record

type Vec3 = list[float]
type Rgb = list[float]
# __pragma__ ("noskip")


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
    __pragma__("skip")
    return record({**fields_of(wing), "root": root, "tips": tips})
    __pragma__("noskip")
    __pragma__("js", "{}", "return Object.assign({}, wing, {root: root, tips: tips});")
    return None


def sided(wing: Any, s: int) -> Any:
    """`wing` (drawn on the right) mirrored to side `s`."""
    root = [s * wing["root"][0], wing["root"][1]]
    tips = [[s * p[0], p[1]] for p in wing["tips"]]
    return _with_wing(wing, root, tips)


def membrane_draw(w: Any, _span: float) -> Any:
    """Return what a membrane wing draws in its model space (factory: no loop closure)."""

    def draw(parts: Any) -> None:
        # A `membrane` skin, and one `bone` strut along its leading tip (lean on triangles).
        root = w["root"]
        tips = w["tips"]
        y = w["y"]
        thickness = w["thickness"]
        strut = w["strut"]
        outline = concat([root], tips)
        parts.flesh.slab(outline, [y - thickness / 2, y + thickness / 2], F.membrane)
        tip = tips[0] if len(tips) > 0 else root
        path = curve([root[0], y, root[1]], [tip[0], y, tip[1]], [0, thickness * 2, 0], 2)
        tendril(parts.flesh, path, [strut, strut * 0.2], 3, F.bone)

    return draw


def membrane_pair(p: Any, wing: Any, span: float) -> None:
    """Add a pair of membrane wings (`wing` is the right one).

    A `membrane` skin on a `bone` strut, each fluttering on its root (ENM-42): the Wasp's wings
    (ENM-WASP-05).
    """
    for s in SIDES:
        w = sided(wing, s)
        p.flap([w["root"][0], w["y"], w["root"][1]], s, span, membrane_draw(w, span))


def sinew(b: Any, start: Vec3, end: Vec3, radii: Any, color: Any = None, bow: Any = None) -> None:
    """Add a sinew (a thin flesh tendril, 4 facets) from `start` to `end`, bowed by `bow`."""
    tint = color if color != None else F.sinew
    bend = bow if bow != None else [0, 0.6, 0]
    tendril(b, curve(start, end, bend, 2), [radii[0], radii[1]], 4, tint)
