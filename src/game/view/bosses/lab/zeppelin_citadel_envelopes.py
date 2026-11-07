# Copyright (c) 2026 Renaud Guillon
"""FB-ZEPPELIN-CITADEL-05: the Zeppelin Citadel's gas envelopes.

Logical pixels, nose +Z, Y up (towards the camera); shapes are given in config coordinates (X
right, Y up the screen, Z height) and turned into model space here. Each envelope is a long, round
hull of stretched skin: a blunt nose, a tapering tail with cross fins, dark girder hoops round it
and a lit line along its ridge. The outer ones are moving pieces (BOSS-45): each rides on two
telescoping booms that lie inside the gondola's hull at rest and slide out with it, a pylon up from
each to its keel, a gun saddle on its back. The middle one is a shed region: it bursts off, baring
the town's central plaza and the cradle that held it (its frame).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.zeppelin_citadel import (
    BOOM_H,
    BOOM_X,
    BOOM_YS,
    DECK,
    DORSAL_AT,
    DORSAL_HEIGHT,
    MIDDLE,
    OUTER,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import SHADE, rod
from game.view.bosses.final_boss_shapes import edge_strips
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["zeppelin-citadel"]
# The envelope's skin, a pale fabric grey, and its girders'.
SKIN = SHADE["light"]
SKIN_DARK = SHADE["panel"]
# A round section, counter-clockwise seen from the nose: `[across, up]` (0..1 up).
SIDES = 10
SECTION = [
    [math.cos(math.pi * 2 * k / SIDES), (math.sin(math.pi * 2 * k / SIDES) + 1) / 2]
    for k in range(SIDES)
]
# The envelope's radius along it, from its tail (0) to its nose (1): `[t, share of its radius]`.
PROFILE: list[Any] = [
    [0, 0],
    [0.05, 0.3],
    [0.15, 0.62],
    [0.3, 0.88],
    [0.5, 1],
    [0.72, 0.98],
    [0.86, 0.86],
    [0.95, 0.6],
    [1, 0.22],
]
# Where its hoops are (shares of its length from the tail).
HOOPS = [0.22, 0.4, 0.58, 0.76]


def pt(x: float, y: float, h: float) -> Vec3:
    """Return the config point `(x, y)` at height `h` in model space."""
    return boss_point(x, y, h)


def model_outline(outline: list[Any]) -> list[Any]:
    """Return a config outline as a model outline (`[x, z]` points)."""
    return [[-q[0], -q[1]] for q in outline]


def radius_at(t: float) -> float:
    """Return the share of an envelope's radius `t` of its length from its tail."""
    for i in range(len(PROFILE) - 1):
        a = PROFILE[i]
        b = PROFILE[i + 1]
        if t <= b[0]:
            k = (t - a[0]) / (b[0] - a[0])
            share: float = a[1] + (b[1] - a[1]) * k
            return share
    last: float = PROFILE[len(PROFILE) - 1][1]
    return last


class Envelope:
    """One envelope: its centre line's `x`, `radius`, `nose` and `tail` y, and `centre` height."""

    def __init__(self, spec: list[Any], side: float) -> None:
        self.x: float = spec[0] * side
        self.radius: float = spec[1]
        self.nose: float = spec[2]
        self.tail: float = spec[3]
        self.centre: float = spec[4]

    def y_at(self, t: float) -> float:
        """Return the config y `t` of its length from its tail."""
        return self.tail + (self.nose - self.tail) * t

    def bottom_at(self, t: float, dx: float) -> float:
        """Return the height of its skin's underside `t` along it, `dx` px off its centre line."""
        r = self.radius * radius_at(t)
        return self.centre - math.sqrt(max(0.0, r * r - dx * dx))


def draw_envelope(p: Any, e: Envelope, cell: bool = False) -> None:
    """Draw an envelope (FB-ZEPPELIN-CITADEL-05): its skin, hoops, ridge line and tail fins.

    With `cell`, its skin only, round its own centre (the gas cell the rig deflates).
    """
    stations: list[Any] = []
    for q in PROFILE:
        r = e.radius * q[1]
        y = e.y_at(q[0])
        z = -y
        h = 0 if cell else e.centre
        stations.append([z, r, h - r, h + r])
    at: list[Any] = [0, 0, 0] if cell else [-e.x, 0, 0]
    p.flesh.loft(SECTION, stations, SKIN_DARK if cell else SKIN, Placement(at))
    if cell:
        return
    # The hoops: dark girder rings round it, a lit one in the middle.
    for k in range(len(HOOPS)):
        t = HOOPS[k]
        r = e.radius * radius_at(t) + 0.25
        ring_at = pt(e.x, e.y_at(t), e.centre)
        lit = 1 <= k <= 2
        p.hull.ring(r, 1.6, SIDES, SKIN_DARK, Placement(ring_at, 0, math.pi / 2))
        if lit:
            p.neon.ring(r + 0.08, 0.5, SIDES, N, Placement(ring_at, 0, math.pi / 2))
    # A lit line along its ridge, from its tail's taper to its nose.
    ridge = [0.2, 0.35, 0.5, 0.65, 0.8, 0.9]
    for i in range(len(ridge) - 1):
        a = ridge[i]
        b = ridge[i + 1]
        rod(
            p.neon,
            pt(e.x, e.y_at(a), e.centre + e.radius * radius_at(a) + 0.1),
            pt(e.x, e.y_at(b), e.centre + e.radius * radius_at(b) + 0.1),
            0.4,
            N,
        )
    _fins(p, e)


def _fins(p: Any, e: Envelope) -> None:
    """Add its tail fins: two flat ones out of its sides, one standing on its back, lit edges."""
    root = e.y_at(0.22)
    end = e.y_at(0.02)
    for s in [-1, 1]:
        inner = e.radius * radius_at(0.12) - 1
        out = e.radius * 0.85
        fin = [
            [e.x + s * inner, root],
            [e.x + s * (inner + out), end - 6],
            [e.x + s * (inner + out), end + 1],
            [e.x + s * inner, end],
        ]
        p.hull.slab(model_outline(fin), [e.centre - 0.5, e.centre + 0.5], SKIN_DARK)
        edge_strips(
            p.neon,
            [[-(e.x + s * (inner + out)), -(end - 6)], [-(e.x + s * (inner + out)), -(end + 1)]],
            0.6,
            [e.centre + 0.5, e.centre + 0.65],
            N,
        )
    top = e.centre + e.radius * radius_at(0.12) - 1
    height = e.radius * 0.75
    p.hull.box(
        [0.9, height, root - end],
        SKIN_DARK,
        Placement(pt(e.x, (root + end) / 2, top)),
    )
    p.neon.box(
        [1, 0.5, (root - end) * 0.6], N, Placement(pt(e.x, (root + end) / 2 - 1, top + height))
    )


def _booms(p: Any, e: Envelope, side: float) -> None:
    """Add the telescoping booms an outer envelope rides on, and their pylons up to its keel.

    At rest the booms lie inside the gondola's hull; they slide out with the envelope.
    """
    for y in BOOM_YS:
        x0 = side * BOOM_X[0]
        x1 = side * BOOM_X[1]
        width = BOOM_X[1] - BOOM_X[0]
        mid = pt((x0 + x1) / 2, y, BOOM_H[0])
        p.hull.box([width, BOOM_H[1] - BOOM_H[0], 3.2], SHADE["base"], Placement(mid), SHADE["mid"])
        # A lit line along the boom's top, bared as it slides out of the hull.
        edge_strips(
            p.neon,
            [[-(x0 + side * 2), -y], [-(x1 - side * 1), -y]],
            0.6,
            [BOOM_H[1] + 0.01, BOOM_H[1] + 0.12],
            N,
        )
        # The pylon: up from the boom's outer end into the envelope's keel.
        px = e.x + side * 3
        keel = e.bottom_at((e.tail - y) / (e.tail - e.nose), 3) + 1.2
        p.hull.box([2.6, keel - BOOM_H[0], 2.6], SHADE["mid"], Placement(pt(px, y, BOOM_H[0])))
        p.neon.box(
            [0.5, (keel - BOOM_H[1]) * 0.6, 0.5], N, Placement(pt(px - side * 1.35, y, DECK + 0.5))
        )


def _saddle(p: Any, e: Envelope) -> None:
    """Add the gun saddle on its back: a plated pad hugging the skin, under the dorsal turret."""
    x = e.x
    y = DORSAL_AT[1]
    top = DORSAL_HEIGHT - 1.2
    skin = e.centre + e.radius * radius_at((e.tail - y) / (e.tail - e.nose))
    p.hull.cylinder(
        7.2, top - skin + 2.2, 8, SHADE["base"], Placement(pt(x, y, skin - 2.2), math.pi / 8), 6.2
    )
    for s in [-1, 1]:
        p.hull.box([1.2, 1.8, 14], SHADE["mid"], Placement(pt(x + s * 6.6, y, skin - 1.4)))


def outer_envelope(side: float) -> Any:
    """Return the drawing of the outer envelope on the config side `side` (a moving piece).

    The envelope, its booms and pylons and its gun saddle, drawn at rest.
    """

    def draw(p: Any) -> None:
        e = Envelope(OUTER, side)
        draw_envelope(p, e)
        _booms(p, e, side)
        _saddle(p, e)

    return draw


def middle_envelope(p: Any) -> None:
    """Draw the middle envelope (a shed region, FB-ZEPPELIN-CITADEL-11)."""
    draw_envelope(p, Envelope(MIDDLE, 1))


def middle_frame(p: Any) -> None:
    """Draw what the middle envelope leaves (BOSS-44): the bared central plaza.

    Dark paving within its outline, a lit border, and torn girder stubs of its keel along it.
    """
    half = MIDDLE[1] - 1
    plaza = [
        [-half, MIDDLE[2] + 4],
        [half, MIDDLE[2] + 4],
        [half, MIDDLE[3] - 2],
        [-half, MIDDLE[3] - 2],
    ]
    p.hull.slab(model_outline(plaza), [DECK - 0.2, DECK + 0.4], SHADE["dark"])
    loop = [[-q[0], -q[1]] for q in plaza]
    loop.append(loop[0])
    edge_strips(p.neon, loop, 0.5, [DECK + 0.4, DECK + 0.5], N)
    # The torn keel girder's stubs: short, dark lengths along the centre line, every third lit.
    stubs = [-42, -6, 24, 38]
    for k in range(len(stubs)):
        y = stubs[k]
        p.hull.box([2.4, 2.6, 5], SHADE["base"], Placement(pt(0, y, DECK + 0.3)))
        if k % 3 == 0:
            p.neon.box([0.5, 0.3, 4], N, Placement(pt(0, y, DECK + 2.95)))


def envelope_armour() -> Any:
    """Return the envelopes' drawings by region id (`drawing.armour`); config right is +X."""
    return {
        "outer-envelope-right": {"whole": outer_envelope(1)},
        "outer-envelope-left": {"whole": outer_envelope(-1)},
        "middle-envelope": {"whole": middle_envelope, "frame": middle_frame},
    }
