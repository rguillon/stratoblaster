# Copyright (c) 2026 Renaud Guillon
"""FB-SKYPORT-HUB-01, FB-SKYPORT-HUB-02: the Skyport Hub, the Lab's L-22 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying airport seen from above: an
octagonal apron, an X of four runways out of it (the rear two are pieces of their own,
`skyport_hub_parts`), a pier at its front with the concourse building, one at its back and one
either side, the round terminal in the middle (its roof halves are pieces of their own, sliding on
the rails drawn here) and the control tower behind it. Its lift fans and radar dish turn on a rig
of their own (`skyport_hub_rig`). A machine, not a creature (the Lab's fifth round, user request
2026-11-06).
"""

import math

from game.config.bosses.lab.skyport_hub import (
    APRON,
    BACK_PIER,
    CAB_FLOOR,
    CAB_R,
    CAB_TOP,
    CASEMATE_AT,
    DECK,
    DECK_LOW,
    FRONT_DEG,
    FRONT_PIER,
    GUN_AT,
    LANCE_AT,
    ROOF,
    ROOF_SLIDE,
    ROTOR_AT,
    RUNWAY_GUN_AT,
    SIDE_HALF,
    SIDE_PIER,
    SIDE_Y,
    SILO_AT,
    SKYPORT_HUB,
    TERMINAL,
    TERMINAL_WALL,
    TOWER_AT,
    TOWER_SHAFT,
    mirror_x,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, rect
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.skyport_hub_parts import (
    MARK,
    N,
    battery,
    beam,
    depot,
    hub_armour,
    model_outline,
    pt,
    radar,
    runway,
)
from game.view.bosses.lab.skyport_hub_rig import build_hub_rig, rig_triangles
from game.view.enemies.enemy_shapes import decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


DEG = math.pi / 180
OCTAGON = 1 / math.cos(math.pi / 8)


def octagon_outline(radius: float) -> list[list[float]]:
    """Return an octagon (config) whose flat sides are `radius` out, square to the axes."""
    r = radius * OCTAGON
    return [
        [r * math.cos(k * math.pi / 4 + math.pi / 8), r * math.sin(k * math.pi / 4 + math.pi / 8)]
        for k in range(8)
    ]


def _pier(p: Any, outline: list[Any]) -> None:
    """Add a pier: a metal deck on the outline, a dark skirt, a lit edge at its tip."""
    p.flesh.slab(model_outline(outline), [DECK_LOW, DECK - 0.05], SHADE["base"], None, SHADE["mid"])


def _draw_decks(p: Any) -> None:
    """Draw the apron, the piers and the front runways (FB-SKYPORT-HUB-01, FB-SKYPORT-HUB-02).

    The apron's octagon with its seams and a lit hold line round the terminal, the four piers out
    of it, the underside's keel cone, the two front runways with their batteries' plinths.
    """
    p.flesh.slab(
        model_outline(octagon_outline(APRON)), [DECK_LOW, DECK], SHADE["base"], None, SHADE["mid"]
    )
    p.flesh.lathe(
        [
            [APRON * OCTAGON - 1, DECK_LOW],
            [22, DECK_LOW - 7],
            [10, DECK_LOW - 12],
            [0, DECK_LOW - 13],
        ],
        8,
        SHADE["dark"],
        Placement([0, 0, 0], math.pi / 8),
    )
    f = FRONT_PIER
    _pier(p, [[-f[0], f[1]], [f[0], f[1]], [f[0] - 2, f[2]], [-f[0] + 2, f[2]]])
    b = BACK_PIER
    _pier(p, [[-b[0], b[1]], [b[0], b[1]], [b[0] - 3, b[2]], [-b[0] + 3, b[2]]])
    for s in [-1, 1]:
        x0 = s * SIDE_PIER[0]
        x1 = s * SIDE_PIER[1]
        _pier(
            p,
            [
                [x0, SIDE_Y - SIDE_HALF],
                [x1, SIDE_Y - SIDE_HALF + 2],
                [x1, SIDE_Y + SIDE_HALF - 2],
                [x0, SIDE_Y + SIDE_HALF],
            ],
        )
        edge_strips(
            p.neon,
            [pt(x1, SIDE_Y - SIDE_HALF + 2.5), pt(x1, SIDE_Y + SIDE_HALF - 2.5)],
            0.5,
            [DECK - 0.4, DECK + 0.05],
            N,
        )
    edge_strips(
        p.neon, [pt(-f[0] + 2.5, f[2]), pt(f[0] - 2.5, f[2])], 0.5, [DECK - 0.4, DECK + 0.05], N
    )
    edge_strips(
        p.neon, [pt(-b[0] + 3.5, b[2]), pt(b[0] - 3.5, b[2])], 0.5, [DECK - 0.4, DECK + 0.05], N
    )
    # The hold line round the terminal and the apron's seams.
    ring = octagon_outline(TERMINAL + 4)
    edge_strips(p.neon, [pt(q[0], q[1]) for q in concat_ring(ring)], 0.35, [DECK, DECK + 0.06], N)
    for k in range(4):
        a = (k * 90 + 45) * DEG
        a0 = [math.cos(a) * (TERMINAL + 6), math.sin(a) * (TERMINAL + 6)]
        a1 = [math.cos(a) * (APRON * OCTAGON - 2), math.sin(a) * (APRON * OCTAGON - 2)]
        decal(
            p.bare,
            rect(
                pt((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2),
                [0.4, 10],
                math.pi / 4 + k * math.pi / 2,
            ),
            DECK + 0.02,
            SHADE["dark"],
        )
    for s in [-1, 1]:
        runway(p, 180 - FRONT_DEG if s < 0 else FRONT_DEG)
        g = boss_point(s * GUN_AT[0], GUN_AT[1], 0)
        p.hull.cylinder(4.8, 0.5, 10, SHADE["dark"], Placement([g[0], DECK, g[2]]))


def concat_ring(ring: list[Any]) -> list[Any]:
    """Return a closed polyline of `ring`: its points and its first one again."""
    result = list(ring)
    result.append(ring[0])
    return result


def _draw_terminal(p: Any) -> None:
    """Draw the terminal (FB-SKYPORT-HUB-02, the core): an octagonal hall, glazed, lit.

    Its walls (their glazing a lit band), gates on its front, the rails its roof halves slide out
    on (FB-SKYPORT-HUB-11) on posts either side; its roof halves are pieces of their own.
    """
    r = TERMINAL * OCTAGON
    p.flesh.lathe(
        [[r, DECK], [r, TERMINAL_WALL - 0.4]],
        8,
        SHADE["panel"],
        Placement([0, 0, 0], math.pi / 8),
        False,
    )
    p.hull.ring(r + 0.05, 1.6, 8, [0.05, 0.09, 0.11], Placement([0, DECK + 4, 0], math.pi / 8))
    p.neon.ring(r + 0.1, 0.35, 8, N, Placement([0, DECK + 4.8, 0], math.pi / 8))
    p.hull.ring(r + 0.1, 0.6, 8, SHADE["mid"], Placement([0, TERMINAL_WALL - 0.6, 0], math.pi / 8))
    p.bare.slab(model_outline(octagon_outline(TERMINAL)), [DECK, DECK + 0.2], SHADE["dark"])
    # Its gates: jet bridges out of its front quarters.
    for s in [-1, 1]:
        a = boss_point(s * 7, -TERMINAL + 1, 0)
        b = boss_point(s * 11, -TERMINAL - 7, 0)
        beam(
            p,
            [s * 7, -TERMINAL + 1],
            [s * 11, -TERMINAL - 7],
            [2.2, DECK + 1.6, DECK + 3.8],
            SHADE["light"],
        )
        p.hull.box([0.8, 1.6, 0.8], SHADE["dark"], Placement([b[0], DECK, b[2]]))
        p.neon.box([0.6, 0.3, 0.6], N, Placement([a[0], DECK + 3.8, a[2]]))
    # The rails the roof halves slide on: from the hall's wall out over the apron, on posts.
    for s in [-1, 1]:
        for dy in [-9, 9]:
            x0 = s * (TERMINAL - 2)
            x1 = s * (TERMINAL + ROOF_SLIDE + 1)
            beam(p, [x0, dy], [x1, dy], [1.6, ROOF[0] - 1.6, ROOF[0] - 0.4], SHADE["mid"])
            decal(p.neon, rect(pt((x0 + x1) / 2, dy), [abs(x1 - x0) - 2, 0.3]), ROOF[0] - 0.35, N)
            post = boss_point(x1 - s * 1.5, dy, DECK)
            p.hull.box([1.4, ROOF[0] - 1.6 - DECK, 1.4], SHADE["dark"], Placement(post))


def _draw_tower(p: Any) -> None:
    """Draw the control tower behind the terminal (FB-SKYPORT-HUB-02, the core).

    A tapering shaft, a glazed cab with its lit sill and slanted windows, its roof (its turret's
    seat, BOSS-58), an antenna mast.
    """
    at = boss_point(TOWER_AT[0], TOWER_AT[1], 0)
    p.hull.box([12, 1.2, 10], SHADE["mid"], Placement([at[0], DECK, at[2]]))
    p.flesh.lathe(
        [[TOWER_SHAFT + 1.2, DECK], [TOWER_SHAFT, CAB_FLOOR - 2], [CAB_R, CAB_FLOOR]],
        10,
        SHADE["panel"],
        Placement([at[0], 0, at[2]]),
    )
    p.neon.ring(TOWER_SHAFT + 0.6, 0.4, 10, N, Placement([at[0], DECK + 8, at[2]]))
    p.hull.lathe(
        [[CAB_R, CAB_FLOOR], [CAB_R + 1, CAB_FLOOR + 3], [CAB_R + 0.4, CAB_TOP - 0.8]],
        10,
        [0.05, 0.09, 0.11],
        Placement([at[0], 0, at[2]]),
        False,
    )
    p.neon.ring(CAB_R + 0.05, 0.4, 10, N, Placement([at[0], CAB_FLOOR + 0.1, at[2]]))
    p.hull.cylinder(CAB_R + 1.2, 0.8, 10, SHADE["base"], Placement([at[0], CAB_TOP - 0.8, at[2]]))
    mast = boss_point(TOWER_AT[0] + 4, TOWER_AT[1] + 4, CAB_TOP)
    p.hull.cylinder(0.4, 6, 4, SHADE["light"], Placement(mast))
    p.charge.box([0.8, 0.8, 0.8], N, Placement([mast[0], CAB_TOP + 6, mast[2]]))


def _draw_concourse(p: Any) -> None:
    """Draw the concourse on the front pier: a long low building, lit windows, rooftop vents."""
    f = FRONT_PIER
    y0 = f[1] - 1
    y1 = -40
    outline = [[-6, y0], [6, y0], [6, y1], [-6, y1]]
    p.flesh.bevel_slab(
        model_outline(outline), [DECK, DECK + 4.2, DECK + 5], [0, 0.8], SHADE["panel"]
    )
    for s in [-1, 1]:
        edge_strips(
            p.neon, [pt(s * 6.05, y0 - 1), pt(s * 6.05, y1 + 1)], 0.4, [DECK + 2, DECK + 3], N
        )
    for k in range(3):
        decal(p.bare, rect(pt(0, y0 - 3 - k * 3.4), [6, 1.4]), DECK + 5.02, SHADE["dark"])


def _draw_seats(p: Any) -> None:
    """Draw the seats of the late guns under their hatches (BOSS-58): dark wells in the deck."""
    spots: list[Any] = [
        [RUNWAY_GUN_AT, 4.2],
        [mirror_x(RUNWAY_GUN_AT), 4.2],
        [CASEMATE_AT, 4.2],
        [mirror_x(CASEMATE_AT), 4.2],
        [LANCE_AT, 4],
        [SILO_AT, 5.5],
        [mirror_x(SILO_AT), 5.5],
        [ROTOR_AT, 5],
    ]
    for spot in spots:
        q = boss_point(spot[0][0], spot[0][1], 0)
        p.bare.cylinder(spot[1], 0.15, 8, SHADE["dark"], Placement([q[0], DECK, q[2]]))
    # Markings on the apron: a pale H for the hangar's spot under the roof, arrows.
    for s in [-1, 1]:
        decal(p.bare, rect(pt(s * 3, 0), [0.8, 6]), DECK + 0.25, MARK)
    decal(p.bare, rect(pt(0, 0), [6, 0.8]), DECK + 0.25, MARK)


def build_skyport_hub(scene: Any) -> Any:
    """FB-SKYPORT-HUB-01, FB-SKYPORT-HUB-02: the Skyport Hub.

    Dark metal decks and pale runway markings, aqua light lines (shown green).
    """

    def core(p: Any) -> None:
        _draw_decks(p)
        _draw_terminal(p)
        _draw_tower(p)
        _draw_concourse(p)
        _draw_seats(p)

    hatches = [
        ["runway-hatch-left", mirror_x(RUNWAY_GUN_AT), 5.5],
        ["runway-hatch-right", RUNWAY_GUN_AT, 5.5],
        ["lance-hatch", LANCE_AT, 5.5],
        ["silo-hatch-left", mirror_x(SILO_AT), 7],
        ["silo-hatch-right", SILO_AT, 7],
        ["casemate-hatch-left", mirror_x(CASEMATE_AT), 5.5],
        ["casemate-hatch-right", CASEMATE_AT, 5.5],
        ["rotor-hatch", ROTOR_AT, 6],
    ]
    return build_boss_model(
        SKYPORT_HUB,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "gun-left": battery,
                "gun-right": battery,
                "depot-left": depot,
                "depot-right": depot,
                "radar": radar,
            },
            "armour": hub_armour(hatches),
            "rig": {"build": build_hub_rig, "triangles": rig_triangles},
        },
    )
