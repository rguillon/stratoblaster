# Copyright (c) 2026 Renaud Guillon
"""MB-LATTICE-NODE-01 to MB-LATTICE-NODE-05: the Lattice Node, the Lab's L-9 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). An open space frame floating over the
playfield: two layers of a triangular lattice (an octet truss) of dark metal struts meeting at node
spheres, light bands on some struts; its core a cluster of glowing nodes caged at its heart; a hex
deck in its lower layer on each rear flank, under an armoured cell until it transforms; its weapon
nodes armoured shells round three of its upper joints. A machine, not a creature: the Lab's second
round drops the animal look (user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.lattice_node import (
    CELL_AT,
    CELL_RADIUS,
    CELL_TOP,
    CLUSTER_GUN_AT,
    CLUSTER_GUN_HEIGHT,
    CLUSTER_RADIUS,
    DECK_TOP,
    HUB_RADIUS,
    LATTICE_NODE,
    LOWER_H,
    NODE_GUN_HEIGHT,
    PITCH,
    ROTOR_AT,
    ROTOR_HEIGHT,
    ROW,
    UPPER_H,
    UPPER_JOINTS,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.organic import tendril
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["lattice-node"]
# Struts: the layers' and the diagonals' radii, their facets.
STRUT = 1.1
DIAGONAL = 0.8
STRUT_SIDES = 4
# A plain joint's sphere radius.
JOINT_RADIUS = 2.6


def _key(c: float, r: float) -> str:
    return str(round(c)) + "," + str(round(r * 3))


def _upper_set() -> dict[str, Any]:
    """Return the upper joints by key, each `[column, row]`."""
    result: dict[str, Any] = {}
    for j in UPPER_JOINTS:
        result[_key(j[0], j[1])] = j
    return result


def _cells() -> list[list[float]]:
    """Return the cannon cells' centres `[x, y]` (MB-LATTICE-NODE-05)."""
    return [[-CELL_AT[0], CELL_AT[1]], [CELL_AT[0], CELL_AT[1]]]


def _is_cell(x: float, y: float) -> bool:
    for c in _cells():
        if abs(c[0] - x) < 1 and abs(c[1] - y) < 1:
            return True
    return False


def _lower_joints(upper: dict[str, Any]) -> list[list[float]]:
    """Return the lower layer's joints `[column, row]` (rows in thirds).

    The centre of every triangle of upper joints pointing to the nose (one joint on row j, two on
    row j + 1).
    """
    result: list[list[float]] = []
    for j in UPPER_JOINTS:
        c = j[0]
        r = j[1]
        if _key(c - 1, r + 1) in upper and _key(c + 1, r + 1) in upper:
            result.append([c, r + 2 / 3])
    return result


def _spot(c: float, r: float, h: float) -> Vec3:
    """Return the model point of the lattice spot `[column, row]` at height `h`."""
    return boss_point(PITCH * c / 2, ROW * r, h)


def _sphere(b: Any, at: Vec3, r: float, color: Any, sides: int = 6) -> None:
    """Add a faceted sphere of radius `r` centred on `at`."""
    k = 0.72
    profile = [[0, -r], [r * k, -r * k], [r, 0], [r * k, r * k], [0, r]]
    b.lathe(profile, sides, color, Placement(at, math.pi / sides))


def _strut(p: Any, a: Vec3, b: Vec3, r: float, lit: bool) -> None:
    """Add a strut from `a` to `b`: a dark tube, a thin light line along its top.

    The struts have no edge trim (only the parts' outlines glow, BOSS-48): the light lines tie the
    frame together, joint to joint; `lit` (every third strut): a brighter, thicker line.
    """
    tendril(p.bare, [a, b], [r, r], STRUT_SIDES, M.base)
    up = r * 0.9
    w = 0.42 if lit else 0.26
    tendril(p.neon, [[a[0], a[1] + up, a[2]], [b[0], b[1] + up, b[2]]], [w, w], 3, N)


def _toward(at: Vec3, to: Vec3, distance: float, h: float) -> Vec3:
    """Return the point `distance` from `at` towards `to` (in the plane), at height `h`."""
    dx = to[0] - at[0]
    dz = to[2] - at[2]
    n = math.sqrt(dx * dx + dz * dz)
    return [at[0] + dx / n * distance, h, at[2] + dz / n * distance]


def _draw_lattice(p: Any) -> None:
    """Draw the space frame (MB-LATTICE-NODE-01): two layers of struts and their diagonals.

    Node spheres at the joints (heavier hubs under the weapon nodes), light bands on every third
    strut, the struts of a cannon cell's triangle ending on its deck's rim.
    """
    upper = _upper_set()
    count = 0
    for j in UPPER_JOINTS:
        c = j[0]
        r = j[1]
        at = _spot(c, r, UPPER_H)
        for n in [[c + 2, r], [c + 1, r + 1], [c - 1, r + 1]]:
            if _key(n[0], n[1]) in upper:
                count += 1
                _strut(p, at, _spot(n[0], n[1], UPPER_H), STRUT, count % 3 == 0)
        if c == 0 and r == 0:
            continue
        _sphere(p.bare, at, JOINT_RADIUS, M.panel, 5)
    lower = _lower_joints(upper)
    lower_keys: dict[str, bool] = {}
    for q in lower:
        lower_keys[_key(q[0], q[1])] = True
    for q in lower:
        _draw_lower_joint(p, q, lower_keys)


def _draw_lower_joint(p: Any, q: list[float], lower_keys: dict[str, bool]) -> None:
    """Draw a lower joint `q` (a node, or a cannon cell's deck), its diagonals and its struts."""
    c = q[0]
    r = q[1]
    at = _spot(c, r, LOWER_H)
    cell = _is_cell(PITCH * c / 2, ROW * r)
    for n in [[c, r - 2 / 3], [c - 1, r + 1 / 3], [c + 1, r + 1 / 3]]:
        top = _spot(n[0], n[1], UPPER_H)
        start = _toward(at, top, CELL_RADIUS - 1, DECK_TOP) if cell else at
        _strut(p, start, top, DIAGONAL, False)
    k = 0
    for n in [[c + 2, r], [c + 1, r + 1], [c - 1, r + 1]]:
        k += 1
        if _key(n[0], n[1]) not in lower_keys:
            continue
        end = _spot(n[0], n[1], LOWER_H)
        a = _toward(at, end, CELL_RADIUS - 1, LOWER_H) if cell else at
        b = end
        if _is_cell(PITCH * n[0] / 2, ROW * n[1]):
            b = _toward(end, at, CELL_RADIUS - 1, LOWER_H)
        _strut(p, a, b, STRUT, (k + round(c)) % 3 == 0)
    if cell:
        _draw_deck(p, at)
    else:
        _sphere(p.bare, at, JOINT_RADIUS * 0.85, M.panel, 5)


def _draw_deck(p: Any, at: Vec3) -> None:
    """Draw a cannon cell's deck (MB-LATTICE-NODE-05): a hex plate in the lower layer."""
    p.hull.bevel_slab(
        polygon(6, CELL_RADIUS),
        [DECK_TOP - 2.4, DECK_TOP - 1.2, DECK_TOP],
        [1.2, 0.6],
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 6),
        M.base,
    )
    p.neon.ring(CELL_RADIUS + 0.05, 0.4, 6, N, Placement([at[0], DECK_TOP - 1.4, at[2]], 0))


def _draw_cluster(p: Any) -> None:
    """Draw the core (MB-LATTICE-NODE-02): a cluster of glowing nodes caged at its heart.

    A big glowing node in the middle and six smaller ones round it, on short dark spokes, inside a
    cage of struts; the turret's seat on its front node and the pedestal of its crown hatch.
    """
    centre = boss_point(0, 0, UPPER_H - 2)
    _sphere(p.vein, centre, 6, N, 8)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        h = UPPER_H - 2 + (3 if k % 2 == 0 else -2.5)
        q = boss_point(9.5 * math.cos(a), 9.5 * math.sin(a), h)
        tendril(p.hull, [centre, q], [0.9, 0.9], 4, M.base)
        _sphere(p.vein, q, 3.3 if k % 2 == 0 else 2.7, N)
    # The cage: two hexagonal hoops and their uprights.
    hoops = [UPPER_H - 8, UPPER_H + 5]
    for h in hoops:
        ring = [
            boss_point(
                CLUSTER_RADIUS * math.cos(2 * math.pi * k / 6),
                CLUSTER_RADIUS * math.sin(2 * math.pi * k / 6),
                h,
            )
            for k in range(7)
        ]
        tendril(p.bare, ring, [0.8, 0.8], 4, M.panel)
    for k in range(6):
        a = 2 * math.pi * k / 6
        x = CLUSTER_RADIUS * math.cos(a)
        y = CLUSTER_RADIUS * math.sin(a)
        tendril(
            p.bare,
            [boss_point(x, y, hoops[0]), boss_point(x * 0.55, y * 0.55, ROTOR_HEIGHT - 3)],
            [0.8, 0.8],
            4,
            M.panel,
        )
        _sphere(p.bare, boss_point(x, y, hoops[0]), 1.4, M.base, 5)
    # The crown: a collar the rotor hatch sits on, held by the cage's uprights.
    crown = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.ring(
        CLUSTER_RADIUS * 0.55, 1.4, 8, M.panel, Placement([crown[0], ROTOR_HEIGHT - 3.7, crown[2]])
    )
    p.hull.cylinder(5.5, 2, 8, M.base, Placement([crown[0], ROTOR_HEIGHT - 2, crown[2]]))
    tendril(p.hull, [centre, [crown[0], ROTOR_HEIGHT - 3, crown[2]]], [1.6, 1.6], 6, M.base)
    # The front node: the turret's seat.
    front = boss_point(CLUSTER_GUN_AT[0], CLUSTER_GUN_AT[1], CLUSTER_GUN_HEIGHT - 4)
    _sphere(p.hull, front, 3.8, M.panel, 8)
    p.hull.cylinder(4.6, 1.6, 8, M.base, Placement([front[0], CLUSTER_GUN_HEIGHT - 1.6, front[2]]))
    p.neon.ring(4.7, 0.35, 8, N, Placement([front[0], CLUSTER_GUN_HEIGHT - 0.9, front[2]]))
    tendril(p.hull, [centre, front], [1.4, 1.4], 6, M.base)


def _draw_hubs(p: Any) -> None:
    """Draw the heavy hubs at the weapon nodes' joints (they stay once the nodes are gone)."""
    for spot in [
        LATTICE_NODE.stats.parts[0],
        LATTICE_NODE.stats.parts[1],
        LATTICE_NODE.stats.parts[2],
    ]:
        at = boss_point(spot.x, spot.y, UPPER_H)
        _sphere(p.bare, at, HUB_RADIUS, M.panel, 8)
        p.bare.cylinder(3.2, 1.6, 8, M.base, Placement([at[0], UPPER_H + HUB_RADIUS - 1, at[2]]))


def _weapon_node(p: Any, at: Vec3) -> None:
    """Add a weapon node (MB-LATTICE-NODE-03): an armoured shell round a hub of the lattice.

    An octagonal armour collar round its hub, lit lenses round it, the seat its gun stands on.
    """
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, HUB_RADIUS + 2.6),
        [UPPER_H - 3.5, UPPER_H - 1, UPPER_H + 2.5],
        [1.6, 1.4],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(HUB_RADIUS + 2.65, 0.45, 8, N, Placement([x, UPPER_H - 0.4, z], math.pi / 8))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        q = [
            x + math.cos(a) * (HUB_RADIUS + 1.6),
            UPPER_H + 2.6,
            z + math.sin(a) * (HUB_RADIUS + 1.6),
        ]
        p.neon.box([1.3, 0.5, 1.3], N, Placement(q, a))
    p.hull.cylinder(
        HUB_RADIUS - 0.4,
        NODE_GUN_HEIGHT - UPPER_H - 1,
        8,
        M.base,
        Placement([x, UPPER_H + 1, z], math.pi / 8),
        4.6,
    )
    p.neon.ring(4.7, 0.35, 8, N, Placement([x, NODE_GUN_HEIGHT - 0.8, z], math.pi / 8))


def _draw_cell(p: Any) -> None:
    """Draw the armoured cells over the cannon decks (MB-LATTICE-NODE-05): shed as it transforms.

    Each a hex capsule of dark plates on its deck, a crystal pane glowing in its top, ribs down its
    sides.
    """
    for c in _cells():
        at = boss_point(c[0], c[1], 0)
        p.hull.bevel_slab(
            polygon(6, CELL_RADIUS - 0.4),
            [DECK_TOP, CELL_TOP - 3, CELL_TOP],
            [0.4, 2.6],
            M.panel,
            Placement(at, math.pi / 6),
            M.base,
        )
        p.vein.bevel_slab(
            polygon(6, 3.2),
            [CELL_TOP - 0.2, CELL_TOP + 0.4, CELL_TOP + 1.2],
            [0, 0.8],
            N,
            Placement(at, math.pi / 6),
        )
        for k in range(6):
            a = k * math.pi / 3
            top = [
                at[0] + math.cos(a) * (CELL_RADIUS - 3.4),
                CELL_TOP + 0.1,
                at[2] + math.sin(a) * (CELL_RADIUS - 3.4),
            ]
            foot = [
                at[0] + math.cos(a) * (CELL_RADIUS - 0.3),
                DECK_TOP + 0.6,
                at[2] + math.sin(a) * (CELL_RADIUS - 0.3),
            ]
            tendril(p.hull, [foot, top], [0.55, 0.55], 4, M.dark)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the cluster's rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.4),
        [ROTOR_HEIGHT, ROTOR_HEIGHT, ROTOR_HEIGHT + 1.6],
        [0, 0.8],
        M.panel,
        Placement(at),
    )
    p.hull.bevel_slab(
        polygon(8, 4.2),
        [ROTOR_HEIGHT + 1.6, ROTOR_HEIGHT + 1.6, ROTOR_HEIGHT + 2.6],
        [0, 0.6],
        M.base,
        Placement(at),
    )
    p.neon.ring(6.2, 0.25, 8, N, Placement([at[0], ROTOR_HEIGHT + 1.2, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6, 1.2, 16, M.base, Placement([at[0], ROTOR_HEIGHT - 0.4, at[2]]))
    p.neon.ring(6, 0.3, 16, N, Placement([at[0], ROTOR_HEIGHT + 0.6, at[2]]))


def build_lattice_node(scene: Any) -> Any:
    """MB-LATTICE-NODE-01, MB-LATTICE-NODE-04: the Lattice Node.

    An open space frame of struts and node spheres, its core a cluster of glowing nodes, mint
    light bands (shown green) on its struts; a weapon node at three of its joints.
    """

    def core(p: Any) -> None:
        _draw_lattice(p)
        _draw_hubs(p)
        _draw_cluster(p)

    return build_boss_model(
        LATTICE_NODE,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "node-left": _weapon_node,
                "node-right": _weapon_node,
                "node-rear": _weapon_node,
            },
            "armour": {
                "cells": {"whole": _draw_cell},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
