# Copyright (c) 2026 Renaud Guillon
"""MB-PRISM-GATE-01 to MB-PRISM-GATE-05, Lab L-6: the Prism Gate.

A hollow equilateral triangle of heavy metal girders, its nose pointing down the screen, a big
faceted crystal emitter on each corner's hub and a crystal prism hung on cables in its middle. A
machine, not a creature (the Lab's second set, 2026-11-06). Logical pixels, nose +Z, Y up (towards
the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.prism_gate import (
    CROWN_RADIUS,
    CROWN_TOP,
    GATE_RADIUS,
    GIRDER_BOTTOM,
    GIRDER_TOP,
    GIRDER_WIDTH,
    HOUSING,
    HUB_TOP,
    LEFT_AT,
    NOSE_AT,
    PRISM_BOTTOM,
    PRISM_GATE,
    PRISM_RADIUS,
    PRISM_TOP,
    RIGHT_AT,
    ROTOR_AT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import rod
from game.view.bosses.mini_boss_mechanism import GEAR
from game.view.bosses.mini_boss_shapes import SHADE, H
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


ICE = BOSS_LOOK.neon["prism-gate"]
# Crystal: dark ice glass, its facets catching the light (BOSS-50 keeps ice blue body shades).
GLASS = [0.07, 0.15, 0.2]
GLASS_LIGHT = [0.13, 0.26, 0.33]
CABLE = [0.05, 0.05, 0.06]

CORNERS: list[Any] = [NOSE_AT, LEFT_AT, RIGHT_AT]
# A hub's radius (a heavy hexagonal node where two girders meet).
HUB_RADIUS = 10
# The prism's corners on the gate's plane (it points the other way from the gate: one corner at
# its back, two at its front).
PRISM_CORNERS = [
    [PRISM_RADIUS * math.sin(a * math.pi / 180), PRISM_RADIUS * math.cos(a * math.pi / 180)]
    for a in [0, 120, 240]
]


def unit(a: list[Any], b: list[Any]) -> list[float]:
    """Return the unit vector from config point `a` to `b`, and its length (`[ux, uy, length]`)."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy) or 1
    return [dx / length, dy / length, length]


def beam(
    builder: Any, a: list[Any], b: list[Any], width: float, heights: list[Any], color: Any
) -> None:
    """Add a box from config point `a` to `b`, `width` across, from `heights[0]` to `heights[1]`."""
    u = unit(a, b)
    mid = boss_point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, heights[0])
    # Model space: +Z is config -Y, +X config -X; the box's length lies along its local +Z.
    yaw = math.atan2(-u[0], -u[1])
    builder.box([width, heights[1] - heights[0], u[2]], color, Placement(mid, yaw))


def shifted(a: list[Any], u: list[Any], across: float, along_: float) -> list[float]:
    """Return config point `a` moved `along_` its direction `u` and `across` to its left."""
    return [a[0] + u[0] * along_ - u[1] * across, a[1] + u[1] * along_ + u[0] * across]


def _girder(p: Any, a: list[Any], b: list[Any]) -> None:
    """Add a heavy girder from hub `a` to hub `b` (MB-PRISM-GATE-02).

    A dark box web, two top chords with a zig-zag of braces between them, a neon line deep along
    its middle and riveted side plates.
    """
    u = unit(a, b)
    start = shifted(a, u, 0, HUB_RADIUS - 3)
    end = shifted(a, u, 0, u[2] - HUB_RADIUS + 3)
    span = u[2] - 2 * (HUB_RADIUS - 3)
    half = GIRDER_WIDTH / 2
    beam(p.hull, start, end, GIRDER_WIDTH - 2.4, [GIRDER_BOTTOM, GIRDER_TOP - 2], H.dark)
    for s in [-1, 1]:
        beam(
            p.bare,
            shifted(start, u, s * (half - 1.1), 0),
            shifted(end, u, s * (half - 1.1), 0),
            2.2,
            [GIRDER_BOTTOM + 0.5, GIRDER_TOP],
            H.panel,
        )
    p.neon.box(
        [0.9, 0.5, span],
        ICE,
        Placement(
            boss_point((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, GIRDER_TOP - 2),
            math.atan2(-u[0], -u[1]),
        ),
    )
    braces = 7
    for k in range(braces):
        s = -1 if k % 2 == 0 else 1
        p0 = shifted(start, u, s * (half - 1.6), span * k / braces)
        p1 = shifted(start, u, -s * (half - 1.6), span * (k + 1) / braces)
        beam(p.bare, p0, p1, 1.3, [GIRDER_TOP - 1.6, GIRDER_TOP - 0.4], GEAR)
    for k in range(3):
        at = shifted(start, u, 0, span * (k + 0.5) / 3)
        for s in [-1, 1]:
            side = shifted(at, u, s * (half - 0.2), 0)
            beam(
                p.bare,
                shifted(side, u, 0, -3.5),
                shifted(side, u, 0, 3.5),
                0.6,
                [GIRDER_BOTTOM + 1, GIRDER_TOP - 2.5],
                SHADE["edge"],
            )


def _hub(p: Any, corner: list[Any]) -> None:
    """Add a corner's hub: a heavy hexagonal node, a light round its waist, claws round its socket.

    Its crystal (the part) stands in the socket on its top; the claws stay once it is gone.
    """
    at = boss_point(corner[0], corner[1])
    p.hull.lathe(
        [
            [HUB_RADIUS - 1, GIRDER_BOTTOM - 1],
            [HUB_RADIUS, GIRDER_BOTTOM + 1],
            [HUB_RADIUS, HUB_TOP - 2],
            [HUB_RADIUS - 2, HUB_TOP],
            [0, HUB_TOP],
        ],
        6,
        H.panel,
        Placement(at, math.pi / 6),
    )
    p.neon.ring(HUB_RADIUS + 0.05, 0.7, 6, ICE, Placement([at[0], 5.5, at[2]], math.pi / 6))
    p.hull.cylinder(5, 0.8, 6, H.dark, Placement([at[0], HUB_TOP, at[2]]))
    out = unit([0, 0], corner)
    for s in [-1, 1]:
        a = math.atan2(out[0], out[1]) + s * 1.75
        foot = [corner[0] + math.sin(a) * 6.6, corner[1] + math.cos(a) * 6.6]
        claw = boss_point(foot[0], foot[1], HUB_TOP - 0.3)
        p.bare.box([2.4, 3.6, 1.8], GEAR, Placement(claw, a, 0.35), SHADE["edge"])


def _prism(p: Any) -> None:
    """Add the prism (MB-PRISM-GATE-02): an upright crystal of three faces, its crown on top.

    Pointed at its foot, its edges lit, a dark metal crown on its top seating the core's guns, its
    light ring round the crown.
    """
    p.hull.lathe(
        [
            [0, PRISM_BOTTOM - 5],
            [PRISM_RADIUS * 0.7, PRISM_BOTTOM],
            [PRISM_RADIUS, PRISM_BOTTOM + 3],
            [PRISM_RADIUS, PRISM_TOP],
            [PRISM_RADIUS * 0.8, PRISM_TOP + 0.6],
        ],
        3,
        GLASS,
        Placement([0, 0, 0], math.pi / 2),
    )
    for c in PRISM_CORNERS:
        rod(
            p.neon,
            boss_point(c[0], c[1], PRISM_BOTTOM + 3),
            boss_point(c[0], c[1], PRISM_TOP),
            0.45,
            ICE,
        )
    p.vein.ring(PRISM_RADIUS + 0.05, 1.2, 3, ICE, Placement([0, PRISM_BOTTOM + 6, 0], math.pi / 2))
    p.hull.lathe(
        [
            [CROWN_RADIUS - 1.5, PRISM_TOP - 0.5],
            [CROWN_RADIUS, PRISM_TOP + 0.8],
            [CROWN_RADIUS, CROWN_TOP - 0.8],
            [CROWN_RADIUS - 1, CROWN_TOP],
            [0, CROWN_TOP],
        ],
        8,
        H.panel,
        Placement(None, math.pi / 8),
    )
    p.neon.ring(CROWN_RADIUS + 0.05, 0.6, 8, ICE, Placement([0, PRISM_TOP + 1.2, 0], math.pi / 8))
    for s in [-1, 1]:
        p.bare.box([3, 0.8, 2.2], SHADE["edge"], Placement(boss_point(s * 7.5, -1, CROWN_TOP)))
        p.charge.box(
            [0.8, 0.4, 0.8], [1, 1, 1], Placement(boss_point(s * 7.5, -1, CROWN_TOP + 0.8))
        )


def _cables(p: Any) -> None:
    """Add the cables the prism hangs on: two from each hub's top to the prism's nearest corners.

    Each with a tensioner block at its hub and light beads along it.
    """
    for corner in CORNERS:
        reach = [math.hypot(c[0] - corner[0], c[1] - corner[1]) for c in PRISM_CORNERS]
        far = 0
        for k in range(3):
            if reach[k] > reach[far]:
                far = k
        near = [PRISM_CORNERS[k] for k in range(3) if k != far]
        u = unit(corner, [0, 0])
        anchor = shifted(corner, u, 0, 8)
        for c in [near[0], near[1]]:
            top = boss_point(c[0], c[1], PRISM_TOP - 1.5)
            foot = boss_point(anchor[0], anchor[1], HUB_TOP)
            rod(p.hull, foot, top, 0.45, CABLE)
            mid = [(foot[0] + top[0]) / 2, (foot[1] + top[1]) / 2 - 0.3, (foot[2] + top[2]) / 2]
            p.neon.box([0.9, 0.9, 0.9], ICE, Placement(mid))
        p.hull.box(
            [3.2, 2.2, 3.2],
            GEAR,
            Placement(boss_point(anchor[0], anchor[1], HUB_TOP - 0.5), math.atan2(-u[0], -u[1])),
            SHADE["edge"],
        )


def _draw_core(p: Any) -> None:
    """Draw the core (MB-PRISM-GATE-02): the gate's girders and hubs, the prism on its cables."""
    for k in range(3):
        _hub(p, CORNERS[k])
        _girder(p, CORNERS[k], CORNERS[(k + 1) % 3])
    _cables(p)
    _prism(p)


def _crystal(p: Any, at: Vec3) -> None:
    """Add a corner's crystal emitter (MB-PRISM-GATE-03): a big faceted crystal in its hub's socket.

    It leans a little outwards, its tip glowing, a light band round its widest, two smaller shards
    at its foot; its laser emitter (its mount) stands on the hub in front of it.
    """
    corner = [-at[0], -at[2]]
    out = unit([0, 0], corner)
    seat = shifted(corner, out, 0, -1.5)
    base = boss_point(seat[0], seat[1], HUB_TOP - 0.6)
    yaw = math.atan2(-out[0], -out[1])
    lean = 0.12
    lean_place = Placement(base, yaw, lean)
    p.hull.lathe([[4, 0], [6.2, 5], [5.6, 16], [2.6, 20]], 6, GLASS_LIGHT, lean_place, False)
    p.vein.lathe([[2.6, 20], [0, 25]], 6, ICE, lean_place)
    waist = [
        base[0] + math.sin(yaw) * 4.7 * math.sin(lean),
        base[1] + 4.7 * math.cos(lean),
        base[2] + math.cos(yaw) * 4.7 * math.sin(lean),
    ]
    p.neon.ring(6.15, 0.6, 6, ICE, Placement(waist, yaw, lean))
    for s in [-1, 1]:
        side = shifted(corner, out, s * 4.6, -3.5)
        foot = boss_point(side[0], side[1], HUB_TOP - 0.6)
        tilt = Placement(foot, yaw + s * 1.4, 0.45)
        p.hull.lathe([[1.8, 0], [2.2, 3], [0, 7.5]], 5, GLASS, tilt)


def _draw_housings(p: Any) -> None:
    """Draw the housings over the back girder (MB-PRISM-GATE-05): the armour it sheds.

    An armoured box over each half of the girder, its top bevelled, vent slats and a light stripe on
    it; the racks lie folded inside.
    """
    for s in [-1, 1]:
        outline = [[-s * q[0], -q[1]] for q in HOUSING]
        p.hull.bevel_slab(
            outline,
            [GIRDER_BOTTOM - 0.5, GIRDER_TOP + 3, GIRDER_TOP + 4.5],
            [0, 1.2],
            H.panel,
        )
        cx = s * 19
        cy = GATE_RADIUS * 0.5
        for k in range(4):
            p.bare.box(
                [1.1, 0.5, 8],
                H.dark,
                Placement(boss_point(s * (11 + k * 2.2), cy, GIRDER_TOP + 4.4)),
            )
        p.neon.box(
            [9, 0.4, 0.8], ICE, Placement(boss_point(cx + s * 5, cy - 4.5, GIRDER_TOP + 4.4))
        )
        p.charge.box(
            [1, 0.5, 1], [1, 1, 1], Placement(boss_point(cx + s * 5, cy + 4, GIRDER_TOP + 4.4))
        )


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the prism's rotor (BOSS-58): an armoured octagonal cap on the crown."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], CROWN_TOP - 0.2)
    p.hull.lathe(
        [[5.7, 0], [5.7, 1.2], [4.2, 2.4], [0, 2.4]], 8, H.panel, Placement(at, math.pi / 8)
    )
    p.neon.ring(5.75, 0.3, 8, ICE, Placement([at[0], at[1] + 0.8, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], CROWN_TOP - 0.3)
    p.hull.ring(5.5, 0.9, 16, H.base, Placement(at))
    p.neon.ring(5.5, 0.3, 16, ICE, Placement([at[0], at[1] + 0.8, at[2]]))


def build_prism_gate(scene: Any) -> Any:
    """MB-PRISM-GATE-01, MB-PRISM-GATE-04: the Prism Gate, with ice blue lights.

    A hollow triangle of heavy girders, a crystal emitter on each corner's hub, a crystal prism
    hung in its middle on cables.
    """
    return build_boss_model(
        PRISM_GATE,
        scene,
        ICE,
        {
            "core": _draw_core,
            "parts": {
                "crystal-left": _crystal,
                "crystal-right": _crystal,
                "crystal-nose": _crystal,
            },
            "armour": {
                "housings": {"whole": _draw_housings},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
