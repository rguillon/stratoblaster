# Copyright (c) 2026 Renaud Guillon
"""FB-ORBITAL-FOUNDRY-01 to FB-ORBITAL-FOUNDRY-05, Lab L-6: the Orbital Foundry.

An industrial space station seen from above: an armoured reactor sphere, a fixed inner ring of
gantries and crucibles on four spokes, and an outer track ring turning round it on roller arms,
carrying three rotor carriages. A machine, not a creature (the Lab's second set, 2026-11-06).
Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.bosses.lab.orbital_foundry import (
    INNER_DECK,
    INNER_HALF,
    INNER_RADIUS,
    ORBITAL_FOUNDRY,
    OUTER_RADIUS,
    SPHERE_CENTRE,
    SPHERE_RADIUS,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.orbital_foundry_parts import (
    BRONZE,
    COPPER,
    OUTER_BOTTOM,
    around,
    crucible,
    crucible_pillar,
    draw_hatch,
    draw_hatch_frame,
    draw_track,
    fairings_drawer,
    rotor_carriage,
)
from game.view.bosses.mini_boss_mechanism import GEAR
from game.view.bosses.mini_boss_shapes import SHADE, H
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


DEG = math.pi / 180
# The inner ring's deck: its edges and its underside.
DECK_IN = INNER_RADIUS - INNER_HALF
DECK_OUT = INNER_RADIUS + INNER_HALF
DECK_BOTTOM = INNER_DECK - 5
# The spokes: four, at the nose, the flanks and the tail.
SPOKES = [0, 90, 180, 270]
SPHERE_SIDES = 12
# The inner ring's dark deck, so its fairings, crucibles and gantries stand out on it.
DECK = [0.07, 0.07, 0.08]


def _sphere_profile(radius: float, latitudes: list[Any]) -> list[list[float]]:
    """Return a lathe profile round the sphere's centre through `latitudes` (degrees)."""
    return [
        [radius * math.cos(a * DEG), SPHERE_CENTRE + radius * math.sin(a * DEG)] for a in latitudes
    ]


def _beam(builder: Any, a: Vec3, b: Vec3, size: list[Any], color: Any) -> None:
    """Add a box `size[0]` wide and `size[1]` high lying from model point `a` to `b`."""
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    mid = [(a[0] + b[0]) / 2, a[1], (a[2] + b[2]) / 2]
    builder.box([size[0], size[1], math.hypot(dx, dz)], color, Placement(mid, math.atan2(dx, dz)))


def _reactor(p: Any) -> None:
    """Add the reactor sphere (FB-ORBITAL-FOUNDRY-02): an armoured ball, glowing through its seams.

    Plated in two staggered bands of armour, a heavy belt round its waist, light seams between the
    bands and reactor ports glowing round its shoulders.
    """
    p.hull.lathe(
        _sphere_profile(SPHERE_RADIUS, [-50, -20, 0, 20, 42, 62, 80, 90]),
        SPHERE_SIDES,
        H.panel,
    )
    p.hull.lathe(
        _sphere_profile(SPHERE_RADIUS + 0.7, [6, 18, 30, 38]),
        SPHERE_SIDES,
        BRONZE,
        Placement(None, math.pi / SPHERE_SIDES),
        False,
    )
    p.hull.lathe(
        _sphere_profile(SPHERE_RADIUS + 0.6, [46, 56, 64]),
        SPHERE_SIDES,
        BRONZE,
        None,
        False,
    )
    p.hull.lathe(
        [
            [SPHERE_RADIUS + 0.4, SPHERE_CENTRE - 3],
            [SPHERE_RADIUS + 2.2, SPHERE_CENTRE - 2],
            [SPHERE_RADIUS + 2.2, SPHERE_CENTRE + 2],
            [SPHERE_RADIUS + 0.4, SPHERE_CENTRE + 3],
        ],
        SPHERE_SIDES,
        H.dark,
        None,
        False,
    )
    for lat in [41, 65]:
        r = SPHERE_RADIUS * math.cos(lat * DEG) + 0.75
        p.neon.ring(r, 0.5, SPHERE_SIDES, COPPER, Placement([0, _lat_height(lat), 0]))
    for k in range(8):
        a = (k + 0.5) * math.pi / 4
        if math.cos(a) > 0.9:
            continue
        port = around(SPHERE_RADIUS * 0.94, a, SPHERE_CENTRE + 6.5)
        p.vein.box([2.4, 3.2, 1.2], COPPER, Placement(port, -a, -0.35))
    for s in [-1, 1]:
        p.charge.box([1, 0.6, 1], [1, 1, 1], Placement(around(SPHERE_RADIUS + 2.3, s * 0.6, 7.5)))


def _lat_height(lat: float) -> float:
    return float(SPHERE_CENTRE + SPHERE_RADIUS * math.sin(lat * DEG))


def _deck(p: Any) -> None:
    """Add the inner ring (FB-ORBITAL-FOUNDRY-02): a fixed deck of plated girders round the sphere.

    Its deck plates, a rail along each edge, a light line along its outer lip.
    """
    p.hull.lathe(
        [
            [DECK_IN, DECK_BOTTOM],
            [DECK_OUT - 1, DECK_BOTTOM],
            [DECK_OUT, DECK_BOTTOM + 1.5],
            [DECK_OUT, INNER_DECK],
            [DECK_IN, INNER_DECK],
            [DECK_IN, DECK_BOTTOM],
        ],
        24,
        DECK,
        None,
        False,
    )
    p.neon.ring(DECK_OUT + 0.05, 0.5, 24, COPPER, Placement([0, INNER_DECK - 2.2, 0]))
    for r in [DECK_IN + 0.8, DECK_OUT - 0.8]:
        p.bare.ring(r, 0.6, 24, SHADE["edge"], Placement([0, INNER_DECK, 0]))
    for k in range(16):
        a = (k * 2 + 1) * math.pi / 16
        p.bare.box(
            [6, 0.4, INNER_HALF * 2 - 3.6],
            H.panel,
            Placement(around(INNER_RADIUS, a, INNER_DECK), -a),
        )


def _spoke(p: Any, angle: float) -> None:
    """Add a spoke (FB-ORBITAL-FOUNDRY-02): a box girder from the sphere's belt to the inner ring.

    It goes on, lower, as a roller arm under the turning ring, a roller truck at its end holding the
    ring up, a light down its back.
    """
    a = angle * DEG
    root = around(SPHERE_RADIUS - 2, a, SPHERE_CENTRE - 3)
    deck = around(DECK_IN + 1, a, SPHERE_CENTRE - 3)
    _beam(p.hull, root, deck, [6, INNER_DECK - SPHERE_CENTRE + 2.5], H.panel)
    _beam(p.neon, around(SPHERE_RADIUS + 2.5, a, INNER_DECK - 0.4), deck, [0.8, 0.5], COPPER)
    for s in [-1, 1]:
        _beam(
            p.bare,
            around(SPHERE_RADIUS + 1, a + s * 0.12, INNER_DECK - 0.6),
            around(DECK_IN, a + s * 0.07, INNER_DECK - 0.6),
            [1.2, 0.8],
            GEAR,
        )
    arm_from = around(DECK_OUT - 1, a, OUTER_BOTTOM - 3)
    arm_to = around(OUTER_RADIUS + 2, a, OUTER_BOTTOM - 3)
    _beam(p.hull, arm_from, arm_to, [5, 3], H.dark)
    truck = around(OUTER_RADIUS, a, OUTER_BOTTOM - 0.6)
    p.hull.box([11, 0.8, 7], GEAR, Placement(truck, -a), SHADE["edge"])
    for s in [-1, 1]:
        wheel = around(OUTER_RADIUS, a + s * 0.07, OUTER_BOTTOM - 2.6)
        p.hull.cylinder(1.9, 2.6, 8, H.panel, Placement(wheel, -a, math.pi / 2, 0))


def _gantry(p: Any, angle: float) -> None:
    """Add a gantry crane over the inner ring's deck (FB-ORBITAL-FOUNDRY-02).

    Two legs on the deck's edges, a girder across over them, a trolley and its hook block.
    """
    a = angle * DEG
    top = INNER_DECK + 11
    legs = [around(DECK_IN + 1.2, a, INNER_DECK), around(DECK_OUT - 1.2, a, INNER_DECK)]
    for s in [-1, 1]:
        for leg in legs:
            foot = around(math.hypot(leg[0], leg[2]), a + s * 0.09, INNER_DECK)
            p.hull.box([1.6, top - INNER_DECK, 1.6], H.panel, Placement(foot, -a), SHADE["edge"])
        span_a = around(DECK_IN, a + s * 0.09, top)
        span_b = around(DECK_OUT, a + s * 0.09, top)
        _beam(p.hull, span_a, span_b, [1.8, 1.8], BRONZE)
    trolley = around(INNER_RADIUS + 2, a, top - 0.6)
    p.hull.box([7, 2.8, 3.6], GEAR, Placement(trolley, -a), SHADE["edge"])
    p.charge.box([0.9, 0.5, 0.9], [1, 1, 1], Placement([trolley[0], top + 2.25, trolley[2]]))
    hook = around(INNER_RADIUS + 2, a, INNER_DECK + 4.5)
    p.hull.cylinder(0.3, top - INNER_DECK - 4.5, 4, H.dark, Placement(hook))
    p.hull.box([2.6, 2.4, 2.6], BRONZE, Placement([hook[0], hook[1] - 1.5, hook[2]]))


def _draw_core(p: Any) -> None:
    """Draw the core (FB-ORBITAL-FOUNDRY-02): the reactor, the inner ring, spokes and gantries."""
    _reactor(p)
    _deck(p)
    for angle in SPOKES:
        _spoke(p, angle)
    _gantry(p, 0)
    for s in [-1, 1]:
        crucible_pillar(p, around(INNER_RADIUS, s * math.pi / 2, 0))
    for s in [-1, 1]:
        _gantry(p, s * 157)


def build_orbital_foundry(scene: Any) -> Any:
    """FB-ORBITAL-FOUNDRY-01, FB-ORBITAL-FOUNDRY-04: the Orbital Foundry, with copper lights.

    An armoured reactor sphere, a fixed inner ring of gantries and crucibles, and a turning outer
    track ring carrying three rotor carriages.
    """
    return build_boss_model(
        ORBITAL_FOUNDRY,
        scene,
        COPPER,
        {
            "core": _draw_core,
            "ring": draw_track,
            "parts": {
                "crucible-left": crucible,
                "crucible-right": crucible,
                "rotor-1": rotor_carriage,
                "rotor-2": rotor_carriage,
                "rotor-3": rotor_carriage,
            },
            "armour": {
                "front-fairings": {"whole": fairings_drawer("front-fairings")},
                "rear-fairings": {"whole": fairings_drawer("rear-fairings")},
                "hangar-fairing": {"whole": fairings_drawer("hangar-fairing")},
                "rotor-hatch": {"whole": draw_hatch, "frame": draw_hatch_frame},
            },
        },
    )
