# Copyright (c) 2026 Renaud Guillon
"""MB-MOTH-LANTERN-05: the Moth Lantern's wings, drawn as moving pieces of its own (BOSS-45).

Each wing is drawn spread wide open, the pose it swings into as it transforms (the config's
`FOREWING` and `HINDWING`): a soft membrane with a darker, furry base, glowing veins fanning out
from its root, a fringe of scales along its outer margin and an eye-spot ring; a grafted hinge
plate at its root. The engine poses them folded back at rest. Logical pixels, nose +Z, Y up
(towards the camera); `s` is the model side (-1: the config's right, +X).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.moth_lantern import (
    EYE_HEIGHT,
    EYE_SPOT,
    FORE_PIVOT,
    FORE_Y,
    FOREWING,
    HIND_PIVOT,
    HIND_Y,
    HINDWING,
)
from game.view.bosses.world_1_organic_kit import F, M, graft, polygon, vein_line
from render.geometry.organic import organ, tendril
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["moth-lantern"]

# The forewing's veins: from near its root out to its margin (config x, y of their ends).
FORE_VEINS = [
    [[16, -18], [76, -36]],
    [[17, -14], [84, -27]],
    [[18, -10], [78, -11]],
    [[18, -7], [64, -2]],
    [[16, -5], [40, -1.5]],
]
# The forewing's leading edge (lit) and its outer margin (fringed), as indices into `FOREWING`.
FORE_LEAD = [0, 5]
FORE_MARGIN = [4, 11]
# The hindwing's veins, its fringed margin and its eye-spot (config x, y).
HIND_VEINS = [
    [[16, -3], [58, 3]],
    [[17, 2], [65, 16]],
    [[17, 7], [58, 32]],
    [[16, 12], [38, 40]],
]
HIND_MARGIN = [2, 10]
HIND_EYE = [44, 20]


def _xz(s: float, point: list[Any]) -> list[Any]:
    """Return the config point `[x, y]` of the right wing as a model `[x, z]` on side `s`."""
    return [s * point[0], -point[1]]


def _at(s: float, point: list[Any], h: float) -> Vec3:
    """Return the config point `[x, y]` of the right wing at height `h`, in model space."""
    xz = _xz(s, point)
    return [xz[0], h, xz[1]]


def _outline(s: float, outline: list[Any]) -> list[Any]:
    """Return a right wing's outline (config) as a model outline on side `s`."""
    return [_xz(s, q) for q in outline]


def _toward(point: list[Any], target: list[Any], k: float) -> list[Any]:
    """`point` moved `k` of the way to `target`."""
    return [point[0] + (target[0] - point[0]) * k, point[1] + (target[1] - point[1]) * k]


def _base(outline: list[Any], pivot: list[Any], k: float) -> list[Any]:
    """Return the wing's base: its outline drawn in `k` of the way to its root."""
    return [_toward(q, pivot, 1 - k) for q in outline]


def _washer(p: Any, at: Vec3, radii: list[Any], thickness: float, color: Any) -> None:
    """Add a flat ring of light `radii[0]` to `radii[1]` round, `thickness` thick, at `at`."""
    y0 = at[1]
    y1 = at[1] + thickness
    p.neon.lathe(
        [[radii[1], y0], [radii[1], y1], [radii[0], y1]],
        12,
        color,
        Placement([at[0], 0, at[2]]),
        False,
    )


def _fringe(p: Any, s: float, outline: list[Any], span: list[Any], h: float) -> None:
    """Add a fringe of scales along the outline's margin from `span[0]` to `span[1]`."""
    cx = 0.0
    cy = 0.0
    for q in outline:
        cx += q[0]
        cy += q[1]
    cx = cx / len(outline)
    cy = cy / len(outline)
    for k in range(span[0], span[1]):
        a = outline[k]
        b = outline[k + 1]
        mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
        out = math.hypot(mid[0] - cx, mid[1] - cy) or 1
        tip = [mid[0] + (mid[0] - cx) / out * 3.5, mid[1] + (mid[1] - cy) / out * 3.5]
        tendril(p.flesh, [_at(s, mid, h), _at(s, tip, h - 0.4)], [1.6, 0], 3, F.sinew)


def _veins(p: Any, s: float, veins: list[Any], h: float) -> None:
    """Add the glowing veins fanning out over a wing, just over its top at `h`."""
    for v in veins:
        vein_line(p, _at(s, v[0], h), _at(s, v[1], h), [0, 0.3, 0], 0.8, N)


def _hinge(p: Any, s: float, pivot: list[Any], h: float) -> None:
    """Add the grafted hinge at a wing's root: a knuckle on its pivot and a riveted plate."""
    at = _at(s, pivot, h - 3)
    p.hull.cylinder(2.2, 4, 8, M.base, Placement(at))
    p.neon.ring(2.3, 0.5, 8, N, Placement([at[0], h + 0.6, at[2]]))


def forewing(s: float) -> Any:
    """Return the drawing of the forewing on side `s` (the `forewings` moving piece)."""
    top = FORE_Y[2]

    def draw(p: Any) -> None:
        p.flesh.bevel_slab(_outline(s, FOREWING), FORE_Y, [1.0, 1.4], F.membrane, None, F.slate)
        # Its furry base, darker, over the inner part of the wing.
        base = _base(FOREWING, FORE_PIVOT, 0.42)
        p.flesh.bevel_slab(
            _outline(s, base), [top - 0.3, top - 0.3, top + 0.5], [0, 0.6], F.graphite
        )
        _veins(p, s, FORE_VEINS, top + 0.1)
        lead = [FOREWING[k] for k in range(FORE_LEAD[0], FORE_LEAD[1] + 1)]
        for k in range(len(lead) - 1):
            vein_line(p, _at(s, lead[k], top), _at(s, lead[k + 1], top), [0, 0.2, 0], 1.3, N)
        _fringe(p, s, FOREWING, FORE_MARGIN, FORE_Y[1])
        # The eye-spot's ring, round the eye-spot gun that stands on it at rest.
        eye = _at(s, EYE_SPOT, top)
        organ(p.flesh, 9.5, 8, F.graphite, Placement(eye), 0.06)
        _washer(p, [eye[0], top + 0.9, eye[2]], [8.4, 10], 0.4, N)
        # The eye-spot gun's stalk (its stump stays on it once the gun is gone).
        p.hull.cylinder(3, EYE_HEIGHT - top, 8, M.base, Placement(eye), 2.4)
        _hinge(p, s, FORE_PIVOT, top)
        graft(p, polygon(5, 3.4, [1, 1.4]), [top, top + 1.4], _at(s, [19, -14], 0))

    return draw


def hindwing(s: float) -> Any:
    """Return the drawing of the hindwing on side `s` (the `hindwings` moving piece)."""
    top = HIND_Y[2]

    def draw(p: Any) -> None:
        p.flesh.bevel_slab(_outline(s, HINDWING), HIND_Y, [0.8, 1.2], F.membrane, None, F.slate)
        base = _base(HINDWING, HIND_PIVOT, 0.38)
        p.flesh.bevel_slab(
            _outline(s, base), [top - 0.3, top - 0.3, top + 0.4], [0, 0.5], F.graphite
        )
        _veins(p, s, HIND_VEINS, top + 0.1)
        _fringe(p, s, HINDWING, HIND_MARGIN, HIND_Y[1])
        # Its great eye-spot, bared once the wings open: a ring of light round a dark iris and a
        # glowing pupil.
        eye = _at(s, HIND_EYE, top)
        organ(p.flesh, 8, 8, F.graphite, Placement(eye), 0.08)
        _washer(p, [eye[0], top + 0.7, eye[2]], [6.4, 8], 0.4, N)
        organ(p.vein, 2.8, 6, N, Placement([eye[0], top + 0.6, eye[2]]), 0.35)
        _hinge(p, s, HIND_PIVOT, top)

    return draw


def moth_wings() -> Any:
    """Return the wings' drawings by region id (`drawing.armour`); the config's right is -X."""
    return {
        "forewings-right": {"whole": forewing(-1)},
        "forewings-left": {"whole": forewing(1)},
        "hindwings-right": {"whole": hindwing(-1)},
        "hindwings-left": {"whole": hindwing(1)},
    }
