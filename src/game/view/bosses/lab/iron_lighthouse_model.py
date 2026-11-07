# Copyright (c) 2026 Renaud Guillon
"""MB-IRON-LIGHTHOUSE-01, MB-IRON-LIGHTHOUSE-02: the Iron Lighthouse, the Lab's L-22 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying lighthouse seen from above: a
round riveted iron platform (its two side leaves are pieces of their own, `iron_lighthouse_parts`),
a ring of four ducted propellers under its rim, a striped lighthouse tower with its gallery rail and
lantern room, two whitewashed keeper's cottages on its front, a landing stage at its bow. Its
propellers and its revolving lens turn on a rig of their own (`iron_lighthouse_rig`). A machine, not
a creature (the Lab's fifth round, user request 2026-11-06).
"""

import math

from game.config.bosses.lab.iron_lighthouse import (
    BOW_AT,
    BOW_TOP,
    COTTAGE_AT,
    COTTAGE_HALF,
    COTTAGE_WALL,
    DECK,
    DECK_LOW,
    GALLERY,
    GALLERY_R,
    HOOP_H,
    IRON_LIGHTHOUSE,
    LAMP_TOP,
    LANTERN_R,
    LANTERN_TOP,
    LEAF_X,
    LEAF_Y,
    PLATFORM_R,
    PROP_OUT,
    PROP_R,
    PROPS,
    TOWER_AT,
    TOWER_FOOT,
    TOWER_NECK,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, rect
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.iron_lighthouse_parts import (
    BAND,
    DECK_TOP,
    IRON,
    PALE,
    WASH,
    N,
    beam,
    buttress,
    dynamo,
    lighthouse_armour,
    pt,
    rivet_row,
    strut,
)
from game.view.bosses.lab.iron_lighthouse_rig import build_lighthouse_rig, rig_triangles
from game.view.enemies.enemy_shapes import decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


DEG = math.pi / 180
# The platform's underside: `[radius, height]` from the rim's foot down to the keel's hub.
UNDERSIDE = [  # type: list[list[float]]
    [PLATFORM_R - 0.5, DECK_LOW],
    [PLATFORM_R - 4, DECK_LOW - 4],
    [24, DECK_LOW - 9],
    [10, DECK_LOW - 14],
    [5, DECK_LOW - 17],
    [0, DECK_LOW - 18],
]
# The tower's bands: `[height, radius]` stations from its foot to its neck, painted in turn.
TOWER_BANDS = 5
# The propeller ring: its hoop's radius.
HOOP_R = PROP_OUT


def _rim_point(deg: float) -> list[float]:
    a = deg * DEG
    return [PLATFORM_R * math.cos(a), PLATFORM_R * math.sin(a)]


def _arc(d0: float, d1: float, steps: int) -> list[list[float]]:
    """Return the rim's points from `d0` to `d1` degrees (config, from +X counter-clockwise)."""
    return [_rim_point(d0 + (d1 - d0) * k / steps) for k in range(steps + 1)]


def deck_outline() -> list[list[float]]:
    """Return the core deck's outline (config): the round platform without its two leaves."""
    a0 = math.asin(LEAF_Y[0] / PLATFORM_R) / DEG
    a1 = math.asin(LEAF_Y[1] / PLATFORM_R) / DEG
    result: list[list[float]] = []
    result.append([LEAF_X, LEAF_Y[0]])
    result.append([LEAF_X, LEAF_Y[1]])
    result.extend(_arc(a1, 180 - a1, 9))
    result.append([-LEAF_X, LEAF_Y[1]])
    result.append([-LEAF_X, LEAF_Y[0]])
    result.extend(_arc(180 - a0, 360 + a0, 11))
    return result


def _draw_platform(p: Any) -> None:
    """Draw the platform (MB-IRON-LIGHTHOUSE-01): a riveted iron deck, its rim, its underside.

    Plate seams in rings round the tower, rivet rows, a lit line round the rim's arcs (the leaves
    have their own), and the underside's cone down to the keel's hub with its ribs.
    """
    outline = deck_outline()
    p.flesh.slab([pt(q[0], q[1]) for q in outline], [DECK_LOW, DECK], IRON, None, DECK_TOP)
    p.flesh.lathe(UNDERSIDE, 16, SHADE["dark"], Placement([0, 0, 0]))
    for k in range(8):
        a = (k + 0.5) * math.pi / 4
        mid = [math.cos(a) * 26, DECK_LOW - 8.5, math.sin(a) * 26]
        p.hull.box([1.4, 2, 22], SHADE["mid"], Placement(mid, math.pi / 2 - a, 0.42))
    # The rim: a lit line and a dark band on the core's two arcs (front and back).
    a0 = math.asin(LEAF_Y[0] / PLATFORM_R) / DEG
    a1 = math.asin(LEAF_Y[1] / PLATFORM_R) / DEG
    for arc in [_arc(a1 + 2, 178 - a1, 8), _arc(182 - a0, 358 + a0, 10)]:
        edge_strips(
            p.neon, [pt(q[0] * 0.985, q[1] * 0.985) for q in arc], 0.55, [DECK, DECK + 0.25], N
        )
        edge_strips(
            p.hull, [pt(q[0], q[1]) for q in arc], 1.2, [DECK_LOW - 0.6, DECK - 0.4], SHADE["dark"]
        )
    # Seams across the deck, rivets along them, and a ring of plates round the tower's foot.
    for y in [-26, -12, 22]:
        half = math.sqrt(PLATFORM_R * PLATFORM_R - y * y) - 1
        half = min(half, LEAF_X - 0.5) if y > LEAF_Y[0] and y < LEAF_Y[1] else half
        decal(p.bare, rect(pt(0, y), [2 * half, 0.35]), DECK + 0.02, SHADE["dark"])
        rivet_row(p, [-half, y + 0.8], [half, y + 0.8], 12, DECK + 0.03)
    for x in [-9, 9]:
        decal(p.bare, rect(pt(x, -27), [0.35, 18]), DECK + 0.02, SHADE["dark"])
    tower = boss_point(TOWER_AT[0], TOWER_AT[1], 0)
    p.hull.cylinder(TOWER_FOOT + 2.5, 0.6, 12, SHADE["mid"], Placement([tower[0], DECK, tower[2]]))
    p.neon.ring(TOWER_FOOT + 2.55, 0.25, 12, N, Placement([tower[0], DECK + 0.3, tower[2]]))


def _draw_prop_ring(p: Any) -> None:
    """Draw the propeller ring under the rim (MB-IRON-LIGHTHOUSE-06): a hoop and four ducts.

    The hoop hangs under the rim on struts; each duct is an iron ring round its propeller's hub,
    its lit lip showing past the rim (the blades spin on the rig).
    """
    p.hull.lathe(
        [
            [HOOP_R - 1.2, HOOP_H],
            [HOOP_R + 1.2, HOOP_H],
            [HOOP_R + 1.2, HOOP_H + 1.4],
            [HOOP_R - 1.2, HOOP_H + 1.4],
        ],
        24,
        SHADE["mid"],
        Placement([0, 0, 0]),
        False,
    )
    for k in range(8):
        a = (k * 45 + 22.5) * DEG
        foot = [math.cos(a) * (PLATFORM_R - 3), DECK_LOW - 2.5, math.sin(a) * (PLATFORM_R - 3)]
        hoop = [math.cos(a) * HOOP_R, HOOP_H + 0.7, math.sin(a) * HOOP_R]
        strut(p, hoop, foot, 1.1, SHADE["dark"])
    for deg in PROPS:
        a = deg * DEG
        c = boss_point(PROP_OUT * math.cos(a), PROP_OUT * math.sin(a), 0)
        p.hull.lathe(
            [
                [PROP_R, HOOP_H - 1],
                [PROP_R + 1.4, HOOP_H - 0.5],
                [PROP_R + 1.4, HOOP_H + 2.6],
                [PROP_R, HOOP_H + 3],
            ],
            12,
            SHADE["base"],
            Placement([c[0], 0, c[2]]),
            False,
        )
        p.neon.ring(PROP_R + 0.6, 0.3, 12, N, Placement([c[0], HOOP_H + 3, c[2]]))
        p.hull.cylinder(1.8, 3, 8, SHADE["panel"], Placement([c[0], HOOP_H - 1.4, c[2]]), 1.2)
        for k in range(3):
            b = k * math.pi * 2 / 3
            mid = [c[0] + math.cos(b) * PROP_R / 2, HOOP_H - 0.8, c[2] + math.sin(b) * PROP_R / 2]
            p.hull.box([0.8, 0.8, PROP_R], SHADE["dark"], Placement(mid, math.pi / 2 - b))


def _draw_tower(p: Any) -> None:
    """Draw the lighthouse tower (MB-IRON-LIGHTHOUSE-02, the core): painted bands to its gallery.

    A tapering iron tower in pale and dark bands, a lit door and windows climbing it, the corbelled
    gallery with its rail, the lantern room's iron mullions and dark glass, its roof plate (the dome
    over it is a hatch, `iron_lighthouse_parts`).
    """
    at = boss_point(TOWER_AT[0], TOWER_AT[1], 0)
    neck = GALLERY - 2.5
    for k in range(TOWER_BANDS):
        h0 = DECK + (neck - DECK) * k / TOWER_BANDS
        h1 = DECK + (neck - DECK) * (k + 1) / TOWER_BANDS
        r0 = TOWER_FOOT + (TOWER_NECK - TOWER_FOOT) * k / TOWER_BANDS
        r1 = TOWER_FOOT + (TOWER_NECK - TOWER_FOOT) * (k + 1) / TOWER_BANDS
        color = PALE if k % 2 == 0 else BAND
        p.flesh.lathe([[r0, h0], [r1, h1]], 12, color, Placement([at[0], 0, at[2]]), False)
    # The corbels flaring to the gallery's floor, its floor and its rail.
    p.hull.lathe(
        [[TOWER_NECK, neck], [GALLERY_R - 0.4, GALLERY - 0.6], [GALLERY_R, GALLERY], [0, GALLERY]],
        12,
        BAND,
        Placement([at[0], 0, at[2]]),
    )
    p.hull.ring(GALLERY_R - 0.2, 1.8, 12, SHADE["dark"], Placement([at[0], GALLERY, at[2]]))
    p.neon.ring(GALLERY_R - 0.15, 0.3, 12, N, Placement([at[0], GALLERY + 1.8, at[2]]))
    # The lantern room: dark glass between iron mullions, a lit sill, its roof plate.
    p.hull.lathe(
        [[LANTERN_R, GALLERY], [LANTERN_R, LANTERN_TOP - 0.6]],
        8,
        [0.05, 0.09, 0.11],
        Placement([at[0], 0, at[2]], math.pi / 8),
        False,
    )
    for k in range(8):
        a = k * math.pi / 4
        q = [at[0] + math.cos(a) * LANTERN_R, GALLERY, at[2] + math.sin(a) * LANTERN_R]
        p.hull.box([0.6, LANTERN_TOP - GALLERY, 0.6], SHADE["mid"], Placement(q, -a))
    p.neon.ring(LANTERN_R + 0.05, 0.35, 8, N, Placement([at[0], GALLERY + 0.6, at[2]], math.pi / 8))
    p.hull.cylinder(LANTERN_R + 0.8, 0.8, 12, BAND, Placement([at[0], LANTERN_TOP - 0.6, at[2]]))
    # The lamp's pedestal in the lantern (its laser's seat, BOSS-58).
    p.hull.cylinder(2.2, LAMP_TOP - GALLERY, 8, SHADE["mid"], Placement([at[0], GALLERY, at[2]]))
    # The door at its foot, windows climbing it (on its front and sides).
    door = boss_point(TOWER_AT[0], TOWER_AT[1] - TOWER_FOOT - 0.05, DECK)
    p.neon.box([2.4, 3.4, 0.3], N, Placement(door))
    for k in range(3):
        h = DECK + 6 + k * 6.5
        r = TOWER_FOOT + (TOWER_NECK - TOWER_FOOT) * (h - DECK) / (neck - DECK) + 0.05
        a = -math.pi / 2 + (k - 1) * 0.9
        q = [at[0] + math.cos(a) * r, h, at[2] + math.sin(a) * r]
        p.neon.box([0.9, 1.8, 0.3], N, Placement(q, math.pi / 2 - a))


def _draw_cottages(p: Any) -> None:
    """Draw the keeper's cottages (MB-IRON-LIGHTHOUSE-02): whitewashed walls, lit windows, a door.

    Their slate roofs are hatches (`iron_lighthouse_parts`); the seat of a turret on their walls'
    top is under each (BOSS-58). A walk joins them to the tower's door.
    """
    for s in [-1, 1]:
        x = s * COTTAGE_AT[0]
        y = COTTAGE_AT[1]
        hx = COTTAGE_HALF[0]
        hy = COTTAGE_HALF[1]
        q = boss_point(x, y, DECK)
        p.flesh.box([2 * hx, COTTAGE_WALL - DECK, 2 * hy], WASH, Placement(q))
        p.hull.box([2 * hx + 0.6, 1, 2 * hy + 0.6], SHADE["dark"], Placement(q))
        p.hull.cylinder(3.2, 0.4, 8, SHADE["dark"], Placement([q[0], COTTAGE_WALL, q[2]]))
        # A door on its front, two lit windows either side, one on its outer gable.
        front = boss_point(x, y - hy - 0.05, DECK)
        p.hull.box([1.8, 3, 0.3], BAND, Placement(front))
        for dx in [-3.2, 3.2]:
            w = boss_point(x + dx, y - hy - 0.05, DECK + 2.2)
            p.neon.box([1.3, 1.3, 0.3], N, Placement(w))
        g = boss_point(x + s * (hx + 0.05), y, DECK + 2.2)
        p.neon.box([0.3, 1.3, 1.3], N, Placement(g))
    # The walk from the tower's door down the deck, between the cottages, to the bow.
    for k in range(5):
        wy = TOWER_AT[1] - TOWER_FOOT - 3 - k * 4.2
        decal(p.bare, rect(pt(0, wy), [3.2, 2.8]), DECK + 0.03, SHADE["light"])


def _draw_bow(p: Any) -> None:
    """Draw the landing stage at the bow: a jutting iron jetty, its davit, its lit edge.

    The gun's hatch on it is a piece of its own (BOSS-58).
    """
    y0 = -PLATFORM_R + 2
    y1 = -PLATFORM_R - 6
    outline: list[Any] = [[-7, y0], [7, y0], [5.5, y1], [-5.5, y1]]
    p.flesh.slab([pt(q[0], q[1]) for q in outline], [DECK_LOW, DECK - 0.1], SHADE["mid"])
    edge_strips(p.neon, [pt(-5.6, y1 - 0.05), pt(5.6, y1 - 0.05)], 0.5, [DECK - 0.3, DECK], N)
    # The davit: a mast and its jib out over the stage's side, a hook block.
    foot = boss_point(8, BOW_AT[1] - 3, DECK)
    p.hull.cylinder(0.9, 9, 6, SHADE["mid"], Placement(foot))
    jib_a = [foot[0], DECK + 8.5, foot[2]]
    jib_b = boss_point(4, BOW_AT[1] - 9, DECK + 7.5)
    strut(p, jib_a, jib_b, 0.8, SHADE["mid"])
    p.hull.box([1.2, 1.2, 1.2], BAND, Placement([jib_b[0], jib_b[1] - 3, jib_b[2]]))
    p.neon.box([0.6, 0.6, 0.6], N, Placement([foot[0], DECK + 9, foot[2]]))
    seat = boss_point(BOW_AT[0], BOW_AT[1], 0)
    p.hull.cylinder(
        4.6, BOW_TOP - DECK + 0.1, 8, SHADE["dark"], Placement([seat[0], DECK, seat[2]])
    )
    beam(p, [-6, BOW_AT[1] - 6], [6, BOW_AT[1] - 6], [0.8, DECK, DECK + 0.6], SHADE["dark"])


def build_iron_lighthouse(scene: Any) -> Any:
    """MB-IRON-LIGHTHOUSE-01, MB-IRON-LIGHTHOUSE-02: the Iron Lighthouse.

    Riveted iron and painted bands, lamp-yellow light lines (shown yellow) in its windows and seams.
    """

    def core(p: Any) -> None:
        _draw_platform(p)
        _draw_prop_ring(p)
        _draw_tower(p)
        _draw_cottages(p)
        _draw_bow(p)

    return build_boss_model(
        IRON_LIGHTHOUSE,
        scene,
        N,
        {
            "core": core,
            "parts": {"buttress-left": buttress, "buttress-right": buttress, "dynamo": dynamo},
            "armour": lighthouse_armour(),
            "rig": {"build": build_lighthouse_rig, "triangles": rig_triangles},
        },
    )
