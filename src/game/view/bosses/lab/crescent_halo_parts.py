# Copyright (c) 2026 Renaud Guillon
"""FB-CRESCENT-HALO-03, FB-CRESCENT-HALO-05: the Crescent Halo's horns, armour and parts.

Logical pixels, nose +Z, Y up (towards the camera). The horns are flat-topped armoured sleeves over
the ring's ends (the `horns` moving pieces, drawn at rest); the plates over the ring's flanks and
the crest over its back are the armour it sheds at its second transformation; its parts are growths
on the ring carrying their guns' seats (their mounts are drawn by the engine, BOSS-58).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.crescent_halo import (
    CREST_ARC,
    HALO_AXIS,
    HALO_GIRTH,
    HALO_RADIUS,
    HORN_ARC,
    HORN_BOTTOM,
    HORN_TOP,
    PLATES_ARC,
    horn_girth,
    ring_point,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_1_organic_kit import F, M, gland, graft, polygon, vein_line
from render.geometry.organic import organ, tendril, vein
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["crescent-halo"]
# The ring's top over its centre line.
RING_TOP = HALO_AXIS + HALO_GIRTH


def ring_model(angle: float, radius: float, height: float) -> Vec3:
    """Return the model point `radius` px out, `angle` degrees from the nose, `height` high."""
    p = ring_point(angle, radius)
    return boss_point(p[0], p[1], height)


def arc(angles: list[Any], radius: float, height: float, step: float = 6) -> list[Vec3]:
    """Return model points along the arc between `angles` (degrees), about `step` degrees apart."""
    count = max(1, math.ceil(abs(angles[1] - angles[0]) / step))
    return [
        ring_model(angles[0] + (angles[1] - angles[0]) * k / count, radius, height)
        for k in range(count + 1)
    ]


def tangent_yaw(angle: float) -> float:
    """Return the model yaw along the ring (towards growing angles) at `angle` degrees."""
    a = math.radians(angle)
    # Config tangent (cos a, sin a); model (-x, -y) in (X, Z).
    return math.atan2(-math.cos(a), -math.sin(a))


def _horn_outline(s: float) -> list[list[float]]:
    """Return the horn's outline on side `s` (1: config right, +X), model XZ, as drawn at rest."""
    steps = 12
    angles = [HORN_ARC[0] + (HORN_ARC[1] - HORN_ARC[0]) * k / steps for k in range(steps + 1)]
    result: list[list[float]] = []
    for a in angles:
        p = ring_point(a, HALO_RADIUS + horn_girth(a))
        result.append([-s * p[0], -p[1]])
    for k in range(steps + 1):
        a = angles[steps - k]
        p = ring_point(a, HALO_RADIUS - horn_girth(a))
        result.append([-s * p[0], -p[1]])
    return result


def horn(s: float) -> Any:
    """Return the drawing of the horn on side `s` (1: config right, +X) (FB-CRESCENT-HALO-05).

    A flat-topped sleeve of armour over the ring's end, tapering to its tip, a bony ridge along its
    top with barbs, metal bands across it and the neon of its outer edge.
    """

    def draw(p: Any) -> None:
        p.flesh.bevel_slab(
            _horn_outline(s),
            [HORN_BOTTOM, HORN_TOP - 5, HORN_TOP],
            [3.2, 1.6],
            F.membrane,
            None,
            F.graphite,
        )
        ridge = [_sided(q, s) for q in arc([HORN_ARC[0] + 2, HORN_ARC[1] - 2], HALO_RADIUS, 23.2)]
        tendril(p.flesh, ridge, [0.8, 2.2], 5, F.bone)
        outer = [
            _sided(ring_model(a, HALO_RADIUS + horn_girth(a) - 0.6, HORN_TOP - 3), s)
            for a in _angles(HORN_ARC[0] + 1, HORN_ARC[1], 6)
        ]
        vein(p.vein, outer, 1.3, N)
        inner = [
            _sided(ring_model(a, HALO_RADIUS - horn_girth(a) + 0.6, HORN_TOP - 3), s)
            for a in _angles(HORN_ARC[0] + 3, HORN_ARC[1], 8)
        ]
        vein(p.vein, inner, 0.9, N)
        for a in [74, 88, 100]:
            g = horn_girth(a)
            band = [
                _sided(ring_model(a, HALO_RADIUS - g - 0.3, HORN_TOP + 0.4), s),
                _sided(ring_model(a, HALO_RADIUS + g + 0.3, HORN_TOP + 0.4), s),
            ]
            tendril(p.hull, band, [0.9, 0.9], 4, M.base)
        for a in [62, 80, 94]:
            root = _sided(ring_model(a, HALO_RADIUS, HORN_TOP + 1), s)
            tip = offset(root, 0, 4, 0)
            tendril(p.flesh, [root, offset(tip, 0, 0, -1.5)], [1.2, 0], 4, F.bone)
        gland(p, _sided(ring_model(HORN_ARC[0] + 6, HALO_RADIUS, HORN_TOP - 1.5), s), 1.2, N)

    return draw


def _angles(start: float, end: float, step: float) -> list[float]:
    count = max(1, math.ceil(abs(end - start) / step))
    return [start + (end - start) * k / count for k in range(count + 1)]


def _sided(point: Vec3, s: float) -> Vec3:
    """Return `point` (drawn on the config right, model -X) on side `s` (1: config right)."""
    return [point[0] * s, point[1], point[2]]


def _plates_side(p: Any, s: float) -> None:
    """Draw the flank plates on side `s` (1: config right): shell plates over the ring's flank."""
    count = 3
    span = (PLATES_ARC[1] - PLATES_ARC[0]) / count
    for k in range(count):
        a = PLATES_ARC[0] + span * (k + 0.5)
        at = _sided(ring_model(a, HALO_RADIUS, 0), s)
        p.flesh.bevel_slab(
            polygon(6, HALO_GIRTH + 0.6, [1, 0.62]),
            [16, 19.4, 20.6],
            [0, 1.2],
            F.slate if k % 2 == 0 else F.membrane,
            Placement(at, _sided_yaw(tangent_yaw(a), s)),
            F.graphite,
        )
    seam = [_sided(q, s) for q in arc(PLATES_ARC, HALO_RADIUS, 20.8, 4)]
    vein(p.vein, seam, 1, N)
    for a in [PLATES_ARC[0] + 4, PLATES_ARC[1] - 4]:
        gland(p, _sided(ring_model(a, HALO_RADIUS + 6, 19.6), s), 1, N)


def _sided_yaw(yaw: float, s: float) -> float:
    """Return a yaw drawn on the config right, mirrored onto side `s`."""
    return yaw if s > 0 else -yaw


def draw_plates(p: Any) -> None:
    """Draw the flank plates (FB-CRESCENT-HALO-05): both sides, under the horns at rest."""
    _plates_side(p, 1)
    _plates_side(p, -1)


def draw_crest(p: Any) -> None:
    """Draw the crest over the back of the ring (FB-CRESCENT-HALO-05): a ridged shell plate.

    Bone spines along it and a neon seam down its middle; the gatling lies folded under it.
    """
    for k in range(2):
        a = CREST_ARC[0] + (CREST_ARC[1] - CREST_ARC[0]) * (k + 0.5) / 2
        at = ring_model(a, HALO_RADIUS, 0)
        p.flesh.bevel_slab(
            polygon(6, HALO_GIRTH + 0.8, [1, 1.05]),
            [16, 19.6, 21],
            [0, 1.4],
            F.slate,
            Placement(at, tangent_yaw(a)),
            F.graphite,
        )
    graft(p, polygon(4, 5, [1.3, 1]), [20.6, 21.8], ring_model(180, HALO_RADIUS, 0))
    for a in [172, 180, 188]:
        root = ring_model(a, HALO_RADIUS + 5, 20.5)
        tendril(p.flesh, [root, offset(root, 0, 4.5, -2.5)], [1.2, 0], 4, F.bone)
    seam = arc([CREST_ARC[0] + 2, CREST_ARC[1] - 2], HALO_RADIUS - 4, 21.2, 4)
    vein(p.vein, seam, 1, N)


def _seat(p: Any, at: Vec3, radius: float, top: float) -> None:
    """Add the metal seat a gun mount stands on, its top at `top`."""
    p.hull.cylinder(radius, 1.6, 8, M.base, Placement(offset(at, 0, top - 1.6, 0)))
    p.neon.ring(radius + 0.1, 0.35, 8, N, Placement(offset(at, 0, top - 0.9, 0)))


def horn_growth(p: Any, at: Vec3) -> None:
    """Add a horn's growth (FB-CRESCENT-HALO-03): a swollen node on the horn under its rotor."""
    organ(p.flesh, 8, 8, F.slate, Placement(offset(at, 0, HORN_TOP - 2, 0), math.pi / 8), 0.42)
    p.vein.ring(7.6, 0.5, 8, N, Placement(offset(at, 0, HORN_TOP + 0.4, 0), math.pi / 8))
    _seat(p, at, 4.6, 27)


def flank_gland(p: Any, at: Vec3) -> None:
    """Add a flank's gland (FB-CRESCENT-HALO-03): a lit organ on the ring under its laser."""
    organ(p.flesh, 9, 8, F.graphite, Placement(offset(at, 0, RING_TOP - 6, 0)), 0.45)
    p.vein.ring(8.6, 0.5, 8, N, Placement(offset(at, 0, RING_TOP - 3.5, 0)))
    for k in range(4):
        a = 2 * math.pi * (k + 0.5) / 4
        gland(p, offset(at, math.cos(a) * 6, RING_TOP + 0.8, math.sin(a) * 6), 1, N)
    _seat(p, at, 5.2, 19)


def back_growth(p: Any, at: Vec3) -> None:
    """Add a back growth (FB-CRESCENT-HALO-03): an armoured mound on the ring under its turret."""
    organ(p.flesh, 9, 8, F.slate, Placement(offset(at, 0, RING_TOP - 4, 0), math.pi / 8), 0.4)
    graft(p, polygon(6, 6.4), [RING_TOP + 1.8, RING_TOP + 2.6], at, {"color": M.base})
    p.vein.ring(8.6, 0.5, 8, N, Placement(offset(at, 0, RING_TOP - 2, 0), math.pi / 8))
    _seat(p, at, 6.2, 20.2)


def tether(p: Any, angle: float, organ_radius: float) -> None:
    """Add a tether from the organ out to the ring's inner side at `angle` degrees.

    A bowed sinew, a vein along it.
    """
    start = ring_model(angle, organ_radius - 2, 11)
    end = ring_model(angle, HALO_RADIUS - HALO_GIRTH + 2, HALO_AXIS + 1)
    tendril(p.flesh, _bowed(start, end, 4), [3, 2.2], 6, F.sinew)
    vein_line(p, offset(start, 0, 2.6, 0), offset(end, 0, 2.2, 0), [0, 4, 0], 0.8, N)


def _bowed(start: Vec3, end: Vec3, up: float) -> list[Vec3]:
    """Return points from `start` to `end` bowed `up` at their middle."""
    result: list[Vec3] = []
    for k in range(5):
        t = k / 4
        lift = 4 * t * (1 - t) * up
        result.append([
            start[0] + (end[0] - start[0]) * t,
            start[1] + (end[1] - start[1]) * t + lift,
            start[2] + (end[2] - start[2]) * t,
        ])
    return result


def halo_armour() -> Any:
    """Return the Crescent Halo's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "horns-right": {"whole": horn(1)},
        "horns-left": {"whole": horn(-1)},
        "plates": {"whole": draw_plates},
        "crest": {"whole": draw_crest},
    }
