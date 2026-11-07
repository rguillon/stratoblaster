# Copyright (c) 2026 Renaud Guillon
"""FB-CLOUD-DREADNOUGHT-01, FB-CLOUD-DREADNOUGHT-02: the Cloud Dreadnought, the Lab's L-12 final.

Logical pixels, nose +Z, Y up (towards the camera). A long flying battleship seen from above: a
sharp grey hull with a planked deck and lit edges, barbettes fore and aft, a two-tiered
superstructure and two raked smokestacks on its centre line, its starboard casemates' sponsons, tail
fins over its stern. Its parts and armour (turrets, bridge, lift engines, belts, plating) are in
`cloud_dreadnought_parts`. A warship, not a creature (the Lab's third round, user request
2026-11-06).
"""

import math

from game.config.bosses.lab.cloud_dreadnought import (
    AFT_AT,
    BARBETTE_RADIUS,
    BARBETTE_TOP,
    BELT_ROOT,
    BRIDGE_ROTOR_AT,
    CASEMATE_TOP,
    CASEMATE_YS,
    CLOUD_DREADNOUGHT,
    CORE_GUN_AT,
    CORE_GUN_TOP,
    DECK,
    FORE_AT,
    FUNNEL_RADIUS,
    FUNNEL_TOP,
    FUNNELS,
    HULL,
    KEEL,
    PLATING,
    ROTOR_AT,
    SUPERSTRUCTURE,
    casemate_at,
    half_width,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.cloud_dreadnought_parts import (
    DECKING,
    GREY,
    N,
    bridge,
    dreadnought_armour,
    engine,
    main_turret,
    pt,
)
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The hull's section (seen from its bow): a flat deck, flanks tumbling in to a narrow keel.
SECTION = [  # type: list[list[float]]
    [0.2, 0.0],
    [0.8, 0.35],
    [1.0, 0.72],
    [1.0, 1.0],
    [-1.0, 1.0],
    [-1.0, 0.72],
    [-0.8, 0.35],
    [-0.2, 0.0],
]
# The keel rises towards the bow over its first `RISE` px.
RISE = 34


def _stations() -> list[list[float]]:
    """Return the hull's loft stations `[z, half width, bottom, top]`, stern to bow."""
    result: list[list[float]] = []
    bow = HULL[0][0]
    for k in range(len(HULL)):
        q = HULL[len(HULL) - 1 - k]
        y = q[0]
        w = q[1]
        if w <= 0:
            result.append([-y, 0, DECK, DECK])
            continue
        lift = max(0, 1 - (y - bow) / RISE)
        result.append([-y, w, KEEL + (DECK - 1 - KEEL) * lift * lift, DECK])
    return result


def _edge_strip(p: Any, s: float, y0: float, y1: float, height: float, inset: float) -> None:
    """Add a lit strip along the hull's edge on side `s` between `y0` and `y1`, `inset` in."""
    a = boss_point(s * (half_width(y0) - inset), y0, height)
    b = boss_point(s * (half_width(y1) - inset), y1, height)
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    length = math.sqrt(dx * dx + dz * dz)
    mid = [(a[0] + b[0]) / 2, height, (a[2] + b[2]) / 2]
    p.neon.box([0.45, 0.35, length + 0.3], N, Placement(mid, math.atan2(dx, dz)))


def _draw_hull(p: Any) -> None:
    """Draw the hull (FB-CLOUD-DREADNOUGHT-01): a long lofted hull, its deck planked and lit.

    Lit strips along its deck's edges and its flanks, planking lines, the prow's chevrons and stem.
    """
    p.hull.loft(SECTION, _stations(), GREY)
    # The deck's planking, inset from its edges, from abaft the bow to the stern.
    stations = [q for q in HULL if q[0] >= -70]
    outline: list[Any] = [pt(q[1] - 2.2, q[0]) for q in stations]
    for k in range(len(stations)):
        q = stations[len(stations) - 1 - k]
        outline.append(pt(-(q[1] - 2.2), q[0]))
    p.bare.slab(outline, [DECK, DECK + 0.15], DECKING)
    for x in [-9, -3, 3, 9]:
        p.bare.box([0.2, 0.1, 120], M.base, Placement(boss_point(x, 5, DECK + 0.15)))
    for s in [-1, 1]:
        for k in range(len(HULL) - 1):
            y0 = HULL[k][0]
            y1 = HULL[k + 1][0]
            _edge_strip(p, s, y0 + 0.5, y1, DECK + 0.1, 0.5)
            if y0 > -76:
                _edge_strip(p, s, y0, y1, 2, -0.02)
    # The prow: lit chevrons on its deck and a stem post.
    for k in range(3):
        y = -78 + k * 5
        w = half_width(y) - 1.5
        for s in [-1, 1]:
            a = boss_point(0, y - 2, DECK + 0.2)
            b = boss_point(s * w, y + 3, DECK + 0.2)
            dx = b[0] - a[0]
            dz = b[2] - a[2]
            mid = [(a[0] + b[0]) / 2, DECK + 0.2, (a[2] + b[2]) / 2]
            p.neon.box(
                [0.5, 0.3, math.sqrt(dx * dx + dz * dz)], N, Placement(mid, math.atan2(dx, dz))
            )
    stem = boss_point(0, -84, DECK)
    p.hull.cylinder(0.4, 6, 4, M.base, Placement(stem))
    p.neon.box([0.8, 0.8, 0.8], N, Placement([stem[0], DECK + 6, stem[2]]))


def _draw_superstructure(p: Any) -> None:
    """Draw the superstructure's two tiers (FB-CLOUD-DREADNOUGHT-02), the core gun's deckhouse.

    Lit window bands, searchlight tubs at the lower tier's corners, the flak rotor's seat on the
    upper tier's back; the deckhouse under the core's twin turret.
    """
    for k in range(len(SUPERSTRUCTURE)):
        t = SUPERSTRUCTURE[k]
        low = DECK if k == 0 else SUPERSTRUCTURE[k - 1][3]
        outline = [pt(t[0], t[1]), pt(-t[0], t[1]), pt(-t[0], t[2]), pt(t[0], t[2])]
        p.hull.bevel_slab(outline, [low, t[3] - 1, t[3]], [0, 0.6], GREY, None, M.panel)
        band = (low + t[3]) / 2
        p.neon.box(
            [2 * t[0] + 0.3, 0.6, t[2] - t[1] + 0.3],
            N,
            Placement(boss_point(0, (t[1] + t[2]) / 2, band)),
        )
    t = SUPERSTRUCTURE[0]
    for sx in [-1, 1]:
        for y in [t[1] + 2.5, t[2] - 2.5]:
            q = boss_point(sx * (t[0] - 2), y, t[3])
            p.hull.cylinder(1.6, 1.2, 8, M.panel, Placement(q))
            p.neon.cylinder(0.9, 0.5, 8, N, Placement([q[0], t[3] + 1.2, q[2]]))
    seat = boss_point(BRIDGE_ROTOR_AT[0], BRIDGE_ROTOR_AT[1], 0)
    top = SUPERSTRUCTURE[1][3]
    p.hull.cylinder(5.2, 0.5, 10, M.base, Placement([seat[0], top - 0.2, seat[2]]))
    p.neon.ring(5.3, 0.3, 10, N, Placement([seat[0], top + 0.1, seat[2]]))
    house = boss_point(CORE_GUN_AT[0], CORE_GUN_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.4, [1, 1.1]),
        [DECK, CORE_GUN_TOP - 0.8, CORE_GUN_TOP],
        [0, 0.6],
        GREY,
        Placement([house[0], 0, house[2]], math.pi / 8),
        M.panel,
    )
    p.neon.ring(5.6, 0.3, 8, N, Placement([house[0], CORE_GUN_TOP + 0.05, house[2]], math.pi / 8))


def _draw_funnels(p: Any) -> None:
    """Draw the two smokestacks (FB-CLOUD-DREADNOUGHT-02): raked back, capped, lit bands, glowing.

    Each on a low casing, its mouth dark with a glow deep in it.
    """
    for f in FUNNELS:
        at = boss_point(f[0], f[1], DECK)
        r = FUNNEL_RADIUS
        rake = 0.18
        height = FUNNEL_TOP - DECK
        p.hull.box([r * 2 + 2, 1.2, r * 2 + 3], M.panel, Placement(at))
        p.hull.cylinder(r, height, 10, GREY, Placement(at, math.pi, rake), r * 0.92)
        top = [at[0], DECK + height * math.cos(rake), at[2] - height * math.sin(rake)]
        p.neon.cylinder(
            r * 0.97,
            1.2,
            10,
            N,
            Placement(
                [
                    at[0],
                    DECK + (height - 3.5) * math.cos(rake),
                    at[2] - (height - 3.5) * math.sin(rake),
                ],
                math.pi,
                rake,
            ),
        )
        p.bare.cylinder(
            r * 0.75, 0.3, 10, M.dark, Placement([top[0], top[1] - 0.05, top[2]], math.pi, rake)
        )
        p.hull.cylinder(
            r * 1.02, 0.8, 10, M.base, Placement([top[0], top[1] - 0.8, top[2]], math.pi, rake)
        )


def _draw_barbettes(p: Any) -> None:
    """Draw the main turrets' barbettes (FB-CLOUD-DREADNOUGHT-03): the drums their guns sit on."""
    for at_cfg in [FORE_AT, AFT_AT]:
        at = boss_point(at_cfg[0], at_cfg[1], 0)
        p.hull.lathe(
            [
                [BARBETTE_RADIUS + 1, DECK],
                [BARBETTE_RADIUS, DECK + 1],
                [BARBETTE_RADIUS, BARBETTE_TOP],
            ],
            12,
            M.panel,
            Placement([at[0], 0, at[2]], math.pi / 12),
        )


def _draw_casemates(p: Any) -> None:
    """Draw the starboard casemates' sponsons (FB-CLOUD-DREADNOUGHT-11): their guns' seats.

    A half-round bulge out of the right flank for each, a lit lip; the guns rise out of them once
    the lance is out (BOSS-58).
    """
    for y in CASEMATE_YS:
        c = casemate_at(y)
        at = boss_point(c[0], c[1], 0)
        p.hull.bevel_slab(
            polygon(8, 3.8),
            [DECK - 5, CASEMATE_TOP - 0.6, CASEMATE_TOP],
            [1.6, 0.5],
            GREY,
            Placement([at[0], 0, at[2]], math.pi / 8),
            M.panel,
        )
        p.neon.ring(3.75, 0.3, 8, N, Placement([at[0], CASEMATE_TOP - 0.5, at[2]], math.pi / 8))


def _draw_stern(p: Any) -> None:
    """Draw its stern (FB-CLOUD-DREADNOUGHT-02): twin tail fins, lit edges, the hinges of its belts.

    And the vents on its after deck, round the rotor's hatch; the belts' hinge rails along the deck.
    """
    for s in [-1, 1]:
        root = boss_point(s * 6.5, 67, DECK)
        p.hull.box([1.2, 8, 13], GREY, Placement(root, s * 0.12), M.panel)
        p.neon.box([0.5, 0.4, 12], N, Placement([root[0], DECK + 8, root[2]], s * 0.12))
        p.hull.box([7, 0.8, 5], M.panel, Placement([root[0], DECK + 6, root[2] - 3]))
    for s in [-1, 1]:
        q = boss_point(s * (BELT_ROOT - 0.8), -2, DECK + 0.1)
        p.hull.box([1.2, 0.8, 44], M.base, Placement(q))
    vent = boss_point(ROTOR_AT[0], ROTOR_AT[1], DECK)
    for dz in [-9, 9]:
        p.bare.box([6, 0.3, 2.4], M.dark, Placement([vent[0], DECK + 0.1, vent[2] + dz]))
    plating_mid = boss_point(0, (PLATING[2] + PLATING[3]) / 2, DECK)
    p.bare.box(
        [PLATING[1] - PLATING[0] - 1, 0.2, PLATING[3] - PLATING[2] - 1],
        M.dark,
        Placement(plating_mid),
    )


def _draw_fittings(p: Any) -> None:
    """Draw its deck fittings (FB-CLOUD-DREADNOUGHT-02): launches, cowl vents, anchors, portholes.

    Launches in their davits either side of the smokestacks, cowl vents beside them, an anchor in
    each hawse at the bow, a row of lit portholes along each flank.
    """
    for sx in [-1, 1]:
        for y in [-3, 9]:
            at = boss_point(sx * 11, y - 3.5, DECK + 1.2)
            p.hull.cylinder(1.5, 7, 6, M.panel, Placement(at, 0, math.pi / 2), 1.1)
            p.neon.box([0.4, 0.3, 5], N, Placement([at[0], DECK + 2.6, at[2] + 3.5]))
            for dz in [1, 6]:
                p.hull.box([3.6, 1.6, 0.6], M.base, Placement([at[0], DECK, at[2] + dz]))
        for spot in [[8.0, -13.5], [14.0, 11.5]]:
            v = boss_point(sx * spot[0], spot[1], DECK)
            p.hull.cylinder(1, 3.2, 6, M.base, Placement(v))
            p.hull.cylinder(1.5, 1.4, 6, GREY, Placement([v[0], DECK + 3.2, v[2]], 0, 0.6), 0.9)
        hawse = boss_point(sx * (half_width(-68) - 0.6), -68, 2.5)
        p.hull.box([0.8, 3.2, 2.4], M.base, Placement(hawse))
        for k in range(14):
            py = -56 + k * 8.5
            if py > -26 and py < 22:
                continue
            port = boss_point(sx * (half_width(py) + 0.02), py, 4.5)
            p.charge.box([0.3, 0.9, 0.9], N, Placement(port))


def build_cloud_dreadnought(scene: Any) -> Any:
    """FB-CLOUD-DREADNOUGHT-01, FB-CLOUD-DREADNOUGHT-04: the Cloud Dreadnought.

    A long flying battleship, 5 L long, red light lines (shown yellow) along its edges.
    """

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_barbettes(p)
        _draw_superstructure(p)
        _draw_funnels(p)
        _draw_casemates(p)
        _draw_stern(p)
        _draw_fittings(p)

    return build_boss_model(
        CLOUD_DREADNOUGHT,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "engine-left": engine,
                "engine-right": engine,
                "turret-fore": main_turret,
                "turret-aft": main_turret,
                "bridge": bridge,
            },
            "armour": dreadnought_armour(),
        },
    )
