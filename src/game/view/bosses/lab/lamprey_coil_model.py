# Copyright (c) 2026 Renaud Guillon
"""MB-LAMPREY-COIL-01 to MB-LAMPREY-COIL-05, Lab L-5: the Lamprey Coil.

Logical pixels, nose +Z, Y up (towards the camera). A serpentine lamprey coiled in an S across the
screen: a round body tapering to its tail, metal collars grafted round it, a pink vein along its
back, seven gill pores a side behind its head and a round sucker mouth ringed with hooked teeth,
its rotor in the throat. Its dorsal armour over the middle of the S is drawn as a piece of its own
(the region it sheds, MB-LAMPREY-COIL-05).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.lamprey_coil import (
    ARMOUR_SPAN,
    LAMPREY_AXIS,
    LAMPREY_COIL,
    LAMPREY_MOUTH,
    LAMPREY_MOUTH_RADIUS,
    LAMPREY_SPINE,
    LAMPREY_THROAT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    gland,
    graft,
    polygon,
    vein_line,
)
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import curve, organ, tendril, vein
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["lamprey-coil"]
# Sub-steps of the smoothed centre line between two of its points.
STEPS = 3


def _catmull(a: Any, b: Any, c: Any, d: Any, t: float) -> list[float]:
    """Return the Catmull-Rom point `t` of the way from `b` to `c` (each `[x, y, r]`)."""
    t2 = t * t
    t3 = t2 * t
    return [
        0.5
        * (
            2 * b[i]
            + (c[i] - a[i]) * t
            + (2 * a[i] - 5 * b[i] + 4 * c[i] - d[i]) * t2
            + (3 * b[i] - a[i] - 3 * c[i] + d[i]) * t3
        )
        for i in range(3)
    ]


def smooth_spine(spine: list[Any]) -> list[list[float]]:
    """Return the centre line smoothed: `STEPS` points between each two (`[x, y, r]`)."""
    n = len(spine)
    result: list[list[float]] = []
    for i in range(n - 1):
        a = spine[max(0, i - 1)]
        d = spine[min(n - 1, i + 2)]
        result.extend([_catmull(a, spine[i], spine[i + 1], d, k / STEPS) for k in range(STEPS)])
    last = spine[n - 1]
    result.append([last[0], last[1], last[2]])
    return result


SMOOTH = smooth_spine(LAMPREY_SPINE)


def _model(point: Any, height: float) -> Vec3:
    """Return the model point over the config point `point` (`[x, y, ...]`), `height` high."""
    return boss_point(point[0], point[1], height)


def _heading(k: int) -> list[float]:
    """Return the way the centre line runs at its smoothed point `k` (a unit config `[x, y]`)."""
    n = len(SMOOTH)
    a = SMOOTH[max(0, k - 1)]
    b = SMOOTH[min(n - 1, k + 1)]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    d = math.hypot(dx, dy)
    return [dx / d, dy / d]


def _yaw(k: int) -> float:
    """Return the model yaw of the centre line at its smoothed point `k` (local +Z along it)."""
    h = _heading(k)
    return math.atan2(-h[0], -h[1])


def _top(k: int) -> float:
    """Return the height of the back over the smoothed point `k`."""
    return float(LAMPREY_AXIS + SMOOTH[k][2])


def _side(k: int, s: float, out: float, height: float) -> Vec3:
    """Return the point `out` of the girth to side `s` of smoothed point `k`, `height` high."""
    h = _heading(k)
    p = SMOOTH[k]
    r = p[2] * out
    return boss_point(p[0] - h[1] * r * s, p[1] + h[0] * r * s, height)


def _draw_body(p: Any) -> None:
    """Draw the body (MB-LAMPREY-COIL-02): a round tube along the S, segment by segment.

    Its girth tapering from the head to the tail, its segments in alternate shades.
    """
    n = len(SMOOTH)
    for i in range(len(LAMPREY_SPINE) - 1):
        first = i * STEPS
        last = min(n - 1, first + STEPS)
        path = [_model(SMOOTH[k], LAMPREY_AXIS) for k in range(first, last + 1)]
        color = F.slate if i % 2 == 0 else F.graphite
        tendril(p.flesh, path, [SMOOTH[first][2], SMOOTH[last][2]], 8, color)


def _in_armour(k: int) -> bool:
    """Whether the smoothed point `k` is under the dorsal armour (the region it sheds)."""
    return ARMOUR_SPAN[0] * STEPS <= k <= ARMOUR_SPAN[1] * STEPS


def _draw_back(p: Any) -> None:
    """Draw the back outside the dorsal armour: metal scutes, the vein along it, collars."""
    n = len(SMOOTH)
    for k in range(1, n - 2, 2):
        if _in_armour(k) or _in_armour(k + 1) or _in_armour(k - 1):
            continue
        r = SMOOTH[k][2]
        top = _top(k)
        p.hull.bevel_slab(
            polygon(6, r * 0.6, [1, 1.3]),
            [top - 1, top - 0.2, top + 0.9],
            [0, 0.7],
            M.panel if k % 4 == 1 else M.base,
            Placement(_model(SMOOTH[k], 0), _yaw(k)),
        )
    for span in [[0, ARMOUR_SPAN[0] * STEPS], [ARMOUR_SPAN[1] * STEPS, n - 2]]:
        path = [_model(SMOOTH[k], _top(k) + 0.7) for k in range(span[0], span[1] + 1)]
        vein(p.vein, path, 1.2, N)
    for k in [4, 22, 28, 31]:
        r = SMOOTH[k][2]
        h = _heading(k)
        at = _model([SMOOTH[k][0] - h[0] * 1.2, SMOOTH[k][1] - h[1] * 1.2], LAMPREY_AXIS)
        p.hull.cylinder(r + 0.7, 2.4, 8, M.base, Placement(at, _yaw(k), math.pi / 2))


def _draw_gills(p: Any) -> None:
    """Draw the gill pores (MB-LAMPREY-COIL-02): seven a side along the neck, each lit pink."""
    n = len(SMOOTH)
    for j in range(7):
        k = n - 4 - j
        for s in [-1, 1]:
            r = SMOOTH[k][2]
            at = _side(k, s, 0.62, LAMPREY_AXIS + r * 0.72)
            p.hull.cylinder(0.85, 1.4, 5, M.dark, Placement(offset(at, 0, -0.6, 0)))
            p.neon.ring(1.15, 0.5, 5, N, Placement(offset(at, 0, 0.3, 0)))


def _draw_head(p: Any) -> None:
    """Draw the head and its sucker mouth (MB-LAMPREY-COIL-02).

    A round disc of flesh in front of the head, a pink lip round its rim, a ring of hooked bone
    teeth curling into the dark throat (the rotor stands in it), a ring of smaller teeth round its
    outer rim; eyes on the head behind it.
    """
    n = len(SMOOTH)
    head = SMOOTH[n - 1]
    mouth = _model(LAMPREY_MOUTH, 0)
    r = LAMPREY_MOUTH_RADIUS
    # The neck runs into the disc.
    tendril(
        p.flesh,
        [_model(head, LAMPREY_AXIS), _model(LAMPREY_MOUTH, LAMPREY_AXIS - 1)],
        [head[2], r * 0.75],
        8,
        F.slate,
    )
    p.flesh.lathe(
        [[r * 0.8, 0], [r, 4.5], [r * 0.98, 8.4], [r * 0.82, LAMPREY_THROAT]],
        12,
        F.sinew,
        Placement(mouth),
    )
    p.hull.cylinder(r * 0.62, 0.4, 12, M.dark, Placement(offset(mouth, 0, LAMPREY_THROAT - 0.2, 0)))
    p.neon.ring(r * 0.93, 0.7, 12, N, Placement(offset(mouth, 0, 8.6, 0)))
    p.neon.ring(r * 0.5, 0.35, 12, N, Placement(offset(mouth, 0, LAMPREY_THROAT + 0.1, 0)))
    for j in range(14):
        a = 2 * math.pi * (j + 0.5) / 14
        c = math.cos(a)
        s = math.sin(a)
        root = offset(mouth, c * r * 0.78, LAMPREY_THROAT - 0.2, s * r * 0.78)
        tip = offset(mouth, c * r * 0.6, LAMPREY_THROAT + 2.2, s * r * 0.6)
        tendril(p.flesh, curve(root, tip, [c * 0.6, 0.8, s * 0.6], 2), [0.85, 0], 3, F.bone)
    for j in range(12):
        a = 2 * math.pi * j / 12
        c = math.cos(a)
        s = math.sin(a)
        root = offset(mouth, c * r * 0.98, 6.5, s * r * 0.98)
        tip = offset(mouth, c * (r + 2.6), 8, s * (r + 2.6))
        tendril(p.flesh, [root, tip], [0.8, 0], 3, F.bone)
    # A riveted plate grafted on the nape, behind the crown turret.
    nape = n - 7
    graft(
        p,
        polygon(5, SMOOTH[nape][2] * 0.7, [1.1, 1]),
        [_top(nape) - 0.6, _top(nape) + 1.1],
        _model(SMOOTH[nape], 0),
        {"yaw": _yaw(nape), "color": M.panel},
    )
    k = n - 2
    for s in [-1, 1]:
        eyes(p, _side(k, s, 0.45, _top(k) - 1.2), {"count": 1, "size": 1.2}, N)


def _draw_lateral_lines(p: Any) -> None:
    """Draw the lateral lines: a pink vein along each flank, from the gills to the tail."""
    n = len(SMOOTH)
    for s in [-1, 1]:
        path = [
            _side(k, s, 0.93, LAMPREY_AXIS + SMOOTH[k][2] * 0.3) for k in range(1, n - 9, STEPS)
        ]
        vein(p.vein, path, 0.8, N)


def _draw_organs(p: Any) -> None:
    """Glands and veins along the flanks, and the reactor sacs on the rising lobe."""
    for k in [10, 25]:
        for s in [-1, 1]:
            gland(p, _side(k, s, 0.7, LAMPREY_AXIS + SMOOTH[k][2] * 0.6), 1.2, N)
    for k in [26, 30]:
        top = _top(k)
        reactor_sac(p, offset(_model(SMOOTH[k], top - 2), 0, 0, -2), 2.4, N, F.graphite)
    p.reactor(_model(SMOOTH[1], LAMPREY_AXIS), 2.2)


def _draw_armour(p: Any) -> None:
    """Draw the dorsal armour (MB-LAMPREY-COIL-05): the armour it sheds at its transformation.

    Overlapping metal scutes down the middle of the S, a pink vein over them and a gland at each
    end.
    """
    first = ARMOUR_SPAN[0] * STEPS
    last = ARMOUR_SPAN[1] * STEPS
    for k in range(first, last + 1, 2):
        r = SMOOTH[k][2]
        top = _top(k)
        p.hull.bevel_slab(
            polygon(6, r * 0.8, [1, 1.75]),
            [top - 1.2, top + 0.6, top + 2],
            [0, 1],
            M.panel if k % 2 == 0 else M.base,
            Placement(_model(SMOOTH[k], 0), _yaw(k)),
        )
    path = [_model(SMOOTH[k], _top(k) + 2.3) for k in range(first, last + 1)]
    vein(p.vein, path, 1.1, N)
    for k in [first + 1, last - 1]:
        gland(p, _model(SMOOTH[k], _top(k) + 1.6), 1.1, N)
    for k in [first + 4, last - 4]:
        for s in [-1, 1]:
            vein_line(
                p,
                _side(k, s, 0.25, _top(k) + 1.9),
                _side(k, s, 0.8, _top(k) - 1),
                [0, 0.5, 0],
                0.8,
                N,
            )


def _gill(p: Any, at: Vec3) -> None:
    """Add a gill cluster (MB-LAMPREY-COIL-03): a swollen gill sac on the flank.

    Five lit gill pores round its crown, a vein ring at its foot and a metal seat on top for its
    twin-barrelled turret (its mount, BOSS-58).
    """
    organ(p.flesh, 10, 8, F.slate, Placement(at, math.pi / 8), 0.75)
    p.vein.ring(9.7, 0.6, 8, N, Placement(offset(at, 0, 2, 0), math.pi / 8))
    for j in range(6):
        a = 2 * math.pi * (j + 0.3) / 6
        spot = offset(at, math.cos(a) * 6.6, 11.4, math.sin(a) * 6.6)
        p.hull.cylinder(1.1, 1.4, 5, M.dark, Placement(offset(spot, 0, -0.5, 0)))
        p.neon.ring(1.45, 0.5, 5, N, Placement(offset(spot, 0, 0.6, 0)))
    p.hull.cylinder(5.6, 1.8, 8, M.base, Placement(offset(at, 0, 12.8, 0)))


def _stinger(p: Any, at: Vec3) -> None:
    """Add the tail stinger (MB-LAMPREY-COIL-03): a bony bulb on the tail's tip.

    A barbed spike of bone curling back from it, a metal seat on top for its rotor (its mount).
    """
    organ(p.flesh, 7, 8, F.graphite, Placement(at), 0.85)
    p.vein.ring(6.8, 0.45, 8, N, Placement(offset(at, 0, 1.4, 0)))
    p.hull.cylinder(4.4, 1.4, 8, M.base, Placement(offset(at, 0, 9.7, 0)))
    tip = offset(at, 9, 5, -10)
    tendril(p.flesh, curve(offset(at, 4, 5, -4), tip, [2, 2, 0], 3), [2.4, 0], 4, F.bone)
    for k in range(3):
        root = offset(at, 5 + k * 1.4, 5.5, -5 - k * 1.6)
        tendril(p.flesh, [root, offset(root, 2.4, 1.2, 0.6)], [0.6, 0], 3, F.bone)


def build_lamprey_coil(scene: Any) -> Any:
    """MB-LAMPREY-COIL-01, MB-LAMPREY-COIL-04: the Lamprey Coil.

    A lamprey 3.5 L across coiled in an S, pink veins along its back; its gill clusters on its
    flanks and its stinger at its tail's tip, its rotor in its sucker mouth and a turret on the
    crown of its head (its mounts, BOSS-58).
    """

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_back(p)
        _draw_gills(p)
        _draw_lateral_lines(p)
        _draw_head(p)
        _draw_organs(p)

    return build_boss_model(
        LAMPREY_COIL,
        scene,
        N,
        {
            "core": core,
            "parts": {"gill-left": _gill, "gill-right": _gill, "stinger": _stinger},
            "armour": {"back": {"whole": _draw_armour}},
        },
    )
