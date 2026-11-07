# Copyright (c) 2026 Renaud Guillon
"""FB-ORBITAL-FOUNDRY-02, FB-ORBITAL-FOUNDRY-03, FB-ORBITAL-FOUNDRY-05, Lab L-6: its pieces.

The Orbital Foundry's turning track ring, its rotor carriages and crucibles (its parts) and the
fairings it sheds. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.orbital_foundry import (
    CRUCIBLE_TOP,
    FAIRING_HEIGHTS,
    INNER_DECK,
    INNER_RADIUS,
    ORBITAL_FOUNDRY,
    OUTER_HALF,
    OUTER_RADIUS,
    OUTER_TOP,
    REACTOR_ROTOR_AT,
    REACTOR_ROTOR_HEIGHT,
    ROTOR_ANGLES,
    ROTOR_HEIGHT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_mechanism import GEAR
from game.view.bosses.mini_boss_shapes import SHADE, H
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


COPPER = BOSS_LOOK.neon["orbital-foundry"]
# Burnished metal: the warm dark plating of the foundry (greyed by the boss look, BOSS-50).
BRONZE = [0.13, 0.11, 0.09]
# A ring's facets.
RING_SIDES = 32
OUTER_BOTTOM = OUTER_TOP - 4


def around(radius: float, angle: float, height: float) -> Vec3:
    """Return the model point `radius` from the centre, `angle` radians round from the nose."""
    return boss_point(radius * math.sin(angle), -radius * math.cos(angle), height)


def _spoke_box(
    builder: Any, angle: float, radii: list[Any], heights: list[Any], width: float, color: Any
) -> None:
    """Add a box along the radius `angle` radians round, from `radii[0]` to `radii[1]` out."""
    mid = around((radii[0] + radii[1]) / 2, angle, heights[0])
    builder.box(
        [width, heights[1] - heights[0], radii[1] - radii[0]],
        color,
        Placement(mid, -angle),
    )


def draw_track(p: Any) -> None:
    """Draw the turning track ring (FB-ORBITAL-FOUNDRY-02): a heavy annulus round the station.

    Rails along its top, a light line along its outer lip, ribs across it between them, and
    tie-down blocks where the carriages run.
    """
    inner = OUTER_RADIUS - OUTER_HALF
    outer = OUTER_RADIUS + OUTER_HALF
    p.hull.lathe(
        [
            [inner, OUTER_BOTTOM],
            [outer, OUTER_BOTTOM],
            [outer + 0.6, OUTER_TOP - 1.2],
            [outer, OUTER_TOP],
            [inner, OUTER_TOP],
            [inner, OUTER_BOTTOM],
        ],
        RING_SIDES,
        H.panel,
        None,
        False,
    )
    p.neon.ring(outer + 0.65, 0.5, RING_SIDES, COPPER, Placement([0, OUTER_TOP - 1.6, 0]))
    for r in [inner + 1.2, outer - 1.2]:
        p.bare.ring(r, 0.7, RING_SIDES, SHADE["edge"], Placement([0, OUTER_TOP, 0]))
    for k in range(24):
        a = (k + 0.5) * 2 * math.pi / 24
        _spoke_box(p.bare, a, [inner + 2, outer - 2], [OUTER_TOP - 0.2, OUTER_TOP + 0.4], 1.2, GEAR)
    for k in range(6):
        a = (k + 0.5) * math.pi / 3
        _spoke_box(
            p.hull, a, [inner - 0.6, outer + 0.6], [OUTER_TOP - 1, OUTER_TOP + 1.4], 5, BRONZE
        )
        p.charge.box([1, 0.5, 1], [1, 1, 1], Placement(around(OUTER_RADIUS, a, OUTER_TOP + 1.4)))
    # The carriages' pedestals, inside their housings: what their stumps stand on once they are
    # destroyed (BOSS-18).
    for angle in ROTOR_ANGLES:
        p.hull.cylinder(
            4.4,
            ROTOR_HEIGHT - OUTER_TOP - 0.1,
            6,
            H.dark,
            Placement(around(OUTER_RADIUS, angle * math.pi / 180, OUTER_TOP)),
        )


def rotor_carriage(p: Any, at: Vec3) -> None:
    """Add a rotor carriage (FB-ORBITAL-FOUNDRY-03): a turret block riding the track ring.

    A hexagonal housing clamped over the ring, skirts down its edges, a light ring round its waist,
    its six-barrelled rotor (its mount) on top.
    """
    angle = math.atan2(-at[0], at[2])
    p.hull.lathe(
        [
            [8.6, OUTER_TOP - 0.6],
            [8.6, OUTER_TOP + 2],
            [7.4, ROTOR_HEIGHT - 1],
            [5.6, ROTOR_HEIGHT],
            [0, ROTOR_HEIGHT],
        ],
        6,
        BRONZE,
        Placement([at[0], 0, at[2]], angle + math.pi / 6),
    )
    p.neon.ring(8.65, 0.6, 6, COPPER, Placement([at[0], OUTER_TOP + 1, at[2]], angle + math.pi / 6))
    for s in [-1, 1]:
        r = OUTER_RADIUS + s * (OUTER_HALF + 0.6)
        foot = around(r, angle, OUTER_BOTTOM - 0.4)
        p.hull.box([9, OUTER_TOP - OUTER_BOTTOM + 1.6, 1.2], H.dark, Placement(foot, -angle))
    for s in [-1, 1]:
        p.bare.box(
            [1.6, 1.2, 3],
            GEAR,
            Placement(around(OUTER_RADIUS, angle + s * 0.1, ROTOR_HEIGHT - 0.6), -angle),
        )


def crucible_pillar(p: Any, at: Vec3) -> None:
    """Add a crucible's trunnion pillar on the deck, inside its pot (a part of the core).

    What its mortar's stump stands on once the pot is destroyed (BOSS-18).
    """
    p.hull.cylinder(
        4.6, CRUCIBLE_TOP - INNER_DECK - 0.2, 8, H.dark, Placement([at[0], INNER_DECK, at[2]])
    )
    p.hull.ring(5.2, 1.2, 8, GEAR, Placement([at[0], CRUCIBLE_TOP - 3, at[2]]))


def crucible(p: Any, at: Vec3) -> None:
    """Add a crucible (FB-ORBITAL-FOUNDRY-03): a squat pot on the inner ring, glowing at its mouth.

    Banded with hoops, a pouring lip on its outer side, trunnions in an A-frame on the deck either
    side, a lake of molten metal in its mouth, its mortar's turntable sunk in it (its mount).
    """
    side = 1 if at[0] > 0 else -1
    p.hull.lathe(
        [
            [7, INNER_DECK - 0.4],
            [9.2, INNER_DECK + 2],
            [10, CRUCIBLE_TOP - 3],
            [9.6, CRUCIBLE_TOP - 0.6],
            [8.4, CRUCIBLE_TOP],
            [7.4, CRUCIBLE_TOP - 0.4],
        ],
        10,
        BRONZE,
        Placement([at[0], 0, at[2]], math.pi / 10),
    )
    p.vein.cylinder(
        7.5, 0.3, 10, COPPER, Placement([at[0], CRUCIBLE_TOP - 0.6, at[2]], math.pi / 10)
    )
    for h in [INNER_DECK + 3.4, CRUCIBLE_TOP - 3.4]:
        p.hull.ring(
            10.05 if h > INNER_DECK + 4 else 9.6,
            1,
            10,
            H.dark,
            Placement([at[0], h, at[2]], math.pi / 10),
        )
    lip = [at[0] + side * 9.6, CRUCIBLE_TOP - 1.4, at[2]]
    p.hull.box([3.2, 1.6, 4], BRONZE, Placement(lip), SHADE["edge"])
    p.neon.box([1.6, 0.3, 2.4], COPPER, Placement([lip[0], lip[1] + 1.62, lip[2]]))
    for s in [-1, 1]:
        z = at[2] + s * 10.2
        for d in [-1, 1]:
            p.hull.box(
                [1.4, 7.5, 1.6],
                H.dark,
                Placement([at[0] + d * 3.2, INNER_DECK - 0.2, z], 0, 0, d * 0.35),
            )
        p.hull.box([4.8, 1.8, 2.6], GEAR, Placement([at[0], INNER_DECK + 5.6, z]), SHADE["edge"])


def _housing(p: Any, outline: list[Any]) -> None:
    """Add an armoured fairing over the inner ring's deck, its outline `outline` (config)."""
    model = [[-q[0], -q[1]] for q in outline]
    low = FAIRING_HEIGHTS[0]
    high = FAIRING_HEIGHTS[1]
    p.hull.bevel_slab(model, [INNER_DECK - 4, high - 1.4, high], [0, 1.1], BRONZE, None, H.panel)
    n = len(outline)
    mid = [0.0, 0.0]
    for q in outline:
        mid = [mid[0] + q[0] / n, mid[1] + q[1] / n]
    angle = math.atan2(mid[0], -mid[1])
    for k in [-1, 0, 1]:
        p.bare.box(
            [7, 0.4, 1],
            H.dark,
            Placement(around(INNER_RADIUS, angle + k * 0.07, high - 0.1), -angle),
        )
    p.neon.box(
        [0.8, 0.4, 11],
        COPPER,
        Placement(around(INNER_RADIUS + 5, angle, high - 0.15), -angle + math.pi / 2),
    )
    p.charge.box([1, 0.5, 1], [1, 1, 1], Placement(around(INNER_RADIUS - 4.5, angle, low + 4.8)))


def _region(region_id: str) -> Any:
    for region in ORBITAL_FOUNDRY.armour:
        if region.id == region_id:
            return region
    return None


def fairings_drawer(region_id: str) -> Any:
    """Return the drawing of the fairings of region `region_id` (FB-ORBITAL-FOUNDRY-05)."""

    def draw(p: Any) -> None:
        for outline in _region(region_id).outlines:
            _housing(p, outline)

    return draw


def draw_hatch(p: Any) -> None:
    """Draw the hatch over the reactor's rotor (BOSS-58): an armoured cap on the sphere's crown."""
    at = boss_point(REACTOR_ROTOR_AT[0], REACTOR_ROTOR_AT[1], REACTOR_ROTOR_HEIGHT - 0.6)
    p.hull.lathe([[7, -2.8], [7, 1.4], [5.2, 2.4], [0, 2.4]], 8, BRONZE, Placement(at, math.pi / 8))
    p.neon.ring(7.05, 0.4, 8, COPPER, Placement([at[0], at[1] + 0.6, at[2]], math.pi / 8))


def draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(REACTOR_ROTOR_AT[0], REACTOR_ROTOR_AT[1], REACTOR_ROTOR_HEIGHT - 2.4)
    p.hull.ring(6.6, 2.2, 16, H.base, Placement(at))
    p.neon.ring(6.6, 0.4, 16, COPPER, Placement([at[0], at[1] + 1.8, at[2]]))
