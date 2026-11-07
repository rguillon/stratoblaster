# Copyright (c) 2026 Renaud Guillon
"""FB-STAR-ENGINE-01 to FB-STAR-ENGINE-04, Lab L-10: the Star Engine.

Logical pixels, nose +Z, Y up (towards the camera). A five-pointed star of a reactor: a pentagonal
deck, a spiky pentagonal core on it under a domed reactor, five long armoured thruster arms
radiating out to the emitters at their tips (its parts, `star_engine_parts`), and a containment
ring clamped over the arms round the core. Dark metal, crimson light; a machine, no creature (the
user's request of 2026-11-06).
"""

import math

from game.config.bosses.lab.star_engine import (
    ARM_ANGLES,
    ARM_REACH,
    ARM_ROOT,
    ARM_TIP,
    ARM_TOP,
    CORE_RADIUS,
    DECK_RADIUS,
    DECK_TOP,
    DOME_TOP,
    RING_AXIS,
    RING_GIRTH,
    RING_RADIUS,
    STAR_ENGINE,
    STAR_GUN_AT,
    STAR_GUN_HEIGHT,
    TIP_IDS,
    TIP_ROTOR_HEIGHT,
    star_point,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.monolith_array_kit import BASALT, PALE, STEEL, STONE
from game.view.bosses.lab.star_engine_parts import (
    N,
    emitter,
    model_xz,
    star_armour,
    star_model,
)
from game.view.bosses.mini_boss_shapes import neon_band
from game.view.enemies.enemy_shapes import decal
from render.geometry.organic import tendril
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The corners of the deck and of the core pentagons: between the arms.
CORNERS = [36, 108, 180, 252, 324]
# The core pentagon's top.
CORE_TOP = 13
# The reactor dome (a lathe profile, radius and height), from the core's top up to the rotor's seat.
DOME = [
    [15.5, CORE_TOP - 0.5],
    [15, 16],
    [12.5, 20.5],
    [8.5, 24.5],
    [6.8, DOME_TOP],
    [0, DOME_TOP],
]
# Where an arm starts and ends (its emitter's housing covers its end).
ARM_FROM = 16
ARM_TO = ARM_REACH - 5


def _pentagon(radius: float, cut: float) -> list[list[float]]:
    """Return a pentagon (model `[x, z]`) with its corners `radius` out between the arms.

    Each corner cut `cut` degrees either side along its edges.
    """
    apothem = radius * math.cos(math.radians(36))
    result: list[list[float]] = []
    for c in CORNERS:
        for d in [-cut, cut]:
            r = apothem / math.cos(math.radians(36 - cut))
            result.append(model_xz(star_point(c + d, r)))
    return result


def _arm_outline(angle: float) -> list[list[float]]:
    """Return an arm's outline (model `[x, z]`): a long trapezoid from the core to its tip."""
    a = math.radians(angle)
    # Across the arm, config: its direction turned a right angle.
    cx = math.cos(a)
    cy = math.sin(a)
    root = star_point(angle, ARM_FROM)
    tip = star_point(angle, ARM_TO)
    return [
        model_xz([root[0] - cx * ARM_ROOT, root[1] - cy * ARM_ROOT]),
        model_xz([tip[0] - cx * ARM_TIP, tip[1] - cy * ARM_TIP]),
        model_xz([tip[0] + cx * ARM_TIP, tip[1] + cy * ARM_TIP]),
        model_xz([root[0] + cx * ARM_ROOT, root[1] + cy * ARM_ROOT]),
    ]


def _arm_width(r: float) -> float:
    """Return an arm's half width `r` px out."""
    k = (r - ARM_FROM) / (ARM_TO - ARM_FROM)
    return float(ARM_ROOT + (ARM_TIP - ARM_ROOT) * k)


def _band(angle: float, r0: float, r1: float, inset: float) -> list[list[float]]:
    """Return the stretch of an arm's top from `r0` to `r1` out, `inset` px in from its sides."""
    a = math.radians(angle)
    cx = math.cos(a)
    cy = math.sin(a)
    result: list[list[float]] = []
    for r, side in [[r0, -1], [r1, -1], [r1, 1], [r0, 1]]:
        q = star_point(angle, r)
        w = (_arm_width(r) - inset) * side
        result.append(model_xz([q[0] + cx * w, q[1] + cy * w]))
    return result


def _draw_arm(p: Any, angle: float) -> None:
    """Draw a thruster arm (FB-STAR-ENGINE-02): a long armoured housing out to its emitter.

    Three armour plates along its top, a channel of light between them, thruster nozzles along its
    flanks and the containment ring's clamp over it.
    """
    p.hull.bevel_slab(
        _arm_outline(angle), [1.5, ARM_TOP - 2.6, ARM_TOP], [1.2, 1.4], BASALT, None, STONE
    )
    for k in range(3):
        r0 = 24 + k * 11
        p.hull.bevel_slab(
            _band(angle, r0, r0 + 9, 1.4),
            [ARM_TOP - 0.3, ARM_TOP + 0.6, ARM_TOP + 1.3],
            [0, 0.6],
            STEEL,
            None,
            STONE,
        )
    decal(p.neon, _band(angle, 20, ARM_TO - 2, _arm_width(ARM_TO) - 0.5), ARM_TOP + 0.05, N)
    yaw = -math.radians(angle)
    for r in [30, 41]:
        w = _arm_width(r)
        for s in [-1, 1]:
            at = star_model(angle + s * math.degrees(math.atan2(w, r)), math.hypot(r, w), 5)
            p.hull.cylinder(
                1.6, 2.2, 6, STEEL, Placement(at, yaw + s * math.pi / 2, math.pi / 2), 2.2
            )
            p.neon.cylinder(
                1.25,
                0.3,
                6,
                N,
                Placement(
                    _offset(at, yaw + s * math.pi / 2, 2.2), yaw + s * math.pi / 2, math.pi / 2
                ),
            )
    # The emitter's mast inside its housing, up to its rotor's seat: it stays once the emitter is
    # destroyed, its gun's stump on it (BOSS-18).
    mast = star_model(angle, ARM_REACH, ARM_TOP - 1)
    p.hull.cylinder(4.4, TIP_ROTOR_HEIGHT - ARM_TOP + 0.6, 6, BASALT, Placement(mast, yaw), 3.8)
    p.neon.ring(4.05, 0.5, 6, N, Placement([mast[0], TIP_ROTOR_HEIGHT - 3, mast[2]], yaw))
    clamp = star_model(angle, RING_RADIUS, ARM_TOP - 0.4)
    height = RING_AXIS + RING_GIRTH * 0.5 - ARM_TOP + 0.4
    p.hull.box([_arm_width(RING_RADIUS) * 1.5, height, 4.2], STEEL, Placement(clamp, yaw), PALE)


def _offset(at: Vec3, yaw: float, distance: float) -> Vec3:
    """Return `at` moved `distance` along the model heading `yaw` (+Z turned by `yaw`)."""
    return [at[0] + math.sin(yaw) * distance, at[1], at[2] + math.cos(yaw) * distance]


def _draw_deck(p: Any) -> None:
    """Draw the deck (FB-STAR-ENGINE-02): a low pentagon under the core, between the arms.

    A rim of light round its edge, vents and reactor nozzles at its back.
    """
    deck = _pentagon(DECK_RADIUS, 8)
    p.hull.bevel_slab(deck, [0, DECK_TOP - 2, DECK_TOP], [2, 1.2], BASALT, None, STONE)
    neon_band(p.neon, deck, [DECK_TOP - 2.2, DECK_TOP - 1.6], [1.003, 1.003], N)
    for k in range(3):
        r = 30 + k * 2.6
        decal(p.hull, [model_xz(q) for q in _wedge(180, r, r + 1.2, 10)], DECK_TOP + 0.05, PALE)
    for d in [-9, 0, 9]:
        at = star_model(180 + d, 38, 3.4)
        p.reactor(at, 2.2 if d == 0 else 1.6)
        p.hull.cylinder(2.8 if d == 0 else 2.2, 4, 8, STEEL, Placement(at, 0, math.pi / 2))


def _wedge(angle: float, r0: float, r1: float, half: float) -> list[list[float]]:
    """Return a band from `r0` to `r1` out, `half` degrees either side of `angle` (config)."""
    return [
        star_point(angle - half, r0),
        star_point(angle + half, r0),
        star_point(angle + half, r1),
        star_point(angle - half, r1),
    ]


def _draw_core(p: Any) -> None:
    """Draw the core (FB-STAR-ENGINE-02): a spiky pentagon under the reactor dome.

    Spikes rising from its five corners, bands of light round the dome, the heart rotor's seat on
    its crown and the star turret's seat on its front (their mounts, BOSS-58).
    """
    core = _pentagon(CORE_RADIUS, 6)
    p.hull.bevel_slab(core, [DECK_TOP - 0.5, CORE_TOP - 2, CORE_TOP], [0, 1.4], STEEL, None, STONE)
    neon_band(p.neon, core, [CORE_TOP - 2.6, CORE_TOP - 2], [1.004, 1.004], N)
    for c in CORNERS:
        root = star_model(c, CORE_RADIUS - 6, CORE_TOP - 0.5)
        tip = star_model(c, CORE_RADIUS - 1, CORE_TOP + 8)
        tendril(p.hull, [root, tip], [2.6, 0], 4, STONE)
        tendril(p.neon, [star_model(c, CORE_RADIUS - 2.2, CORE_TOP + 5.5), tip], [0.6, 0], 4, N)
    p.hull.lathe(DOME, 10, STEEL, Placement(None, math.pi / 10))
    for h, r in [[16.4, 14.9], [21.2, 11.8]]:
        p.neon.ring(r + 0.15, 0.6, 10, N, Placement([0, h, 0], math.pi / 10))
    p.hull.cylinder(5.6, 0.5, 10, PALE, Placement([0, DOME_TOP - 0.05, 0]))
    seat = boss_point(STAR_GUN_AT[0], STAR_GUN_AT[1], CORE_TOP - 1)
    p.hull.box([12, STAR_GUN_HEIGHT - CORE_TOP + 1, 9], STEEL, Placement(seat), STONE)
    p.neon.box([12.4, 0.4, 9.4], N, Placement([seat[0], STAR_GUN_HEIGHT - 1.2, seat[2]]))


def _draw_ring(p: Any) -> None:
    """Draw the containment ring (FB-STAR-ENGINE-02): a dark hoop over the arms, lit round."""
    path = [
        [
            RING_RADIUS * math.cos(2 * math.pi * k / 40),
            RING_AXIS,
            RING_RADIUS * math.sin(2 * math.pi * k / 40),
        ]
        for k in range(41)
    ]
    tendril(p.hull, path, [RING_GIRTH, RING_GIRTH], 6, STEEL)
    p.neon.ring(RING_RADIUS + RING_GIRTH * 0.9, 0.7, 40, N, Placement([0, RING_AXIS - 0.35, 0]))


def build_star_engine(scene: Any) -> Any:
    """FB-STAR-ENGINE-01, FB-STAR-ENGINE-04: the Star Engine.

    A five-pointed reactor 4.5 L across, crimson light on dark metal: its five emitters carry its
    rotors, its reactor dome the heart rotor and, before it, the star turret (their mounts,
    BOSS-58). Its vanes burst off for a pair of orbs at its first transformation, its cowls and its
    keel for a pair of gatlings and a lance at its second (FB-STAR-ENGINE-05).
    """

    def core(p: Any) -> None:
        _draw_deck(p)
        for angle in ARM_ANGLES:
            _draw_arm(p, angle)
        _draw_core(p)
        _draw_ring(p)

    parts: dict[str, Any] = {}
    for part_id in TIP_IDS:
        parts[part_id] = emitter
    return build_boss_model(
        STAR_ENGINE,
        scene,
        N,
        {"core": core, "parts": parts, "armour": star_armour()},
    )
