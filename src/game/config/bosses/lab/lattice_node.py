# Copyright (c) 2026 Renaud Guillon
"""The Lattice Node, the Lab's L-9 mini boss (specs/bosses/lab/L-9-lattice-node.md).

Lab boss: in the dev viewer only, no level brings it in. An open, asymmetric space frame floating
over the playfield: two layers of a triangular lattice of dark metal struts and node spheres (an
octet truss), its core a glowing cluster of nodes at its heart, a weapon node at three of its
joints. Their aimed bursts and narrow fans cross under it; once two of them are gone the armoured
cells on its rear flanks burst open on a pair of cannons.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# MB-LATTICE-NODE-01: the lattice's pitch (a strut's length in a layer), the heights of its upper
# and lower layers, and its rows (y px apart).
PITCH = 22
UPPER_H = 16
LOWER_H = 5
ROW = PITCH * math.sqrt(3) / 2

# The upper layer's joints, `[column, row]`: x = PITCH * column / 2, y = ROW * row. Open and
# lopsided: an arm out to the front right, a spur to the rear right, the left flank cut short.
UPPER_JOINTS = [
    [2, -2],
    [4, -2],
    [-3, -1],
    [-1, -1],
    [1, -1],
    [3, -1],
    [-4, 0],
    [-2, 0],
    [0, 0],
    [2, 0],
    [-3, 1],
    [-1, 1],
    [1, 1],
    [3, 1],
    [0, 2],
    [2, 2],
]


def joint_spot(joint: list[Any]) -> list[float]:
    """Return the `[x, y]` px of a lattice joint `[column, row]`."""
    return [PITCH * joint[0] / 2, ROW * joint[1]]


# The weapon nodes (MB-LATTICE-NODE-03) stand on three of its upper joints; the core's cluster on
# the joint at its centre.
NODE_LEFT = joint_spot([-4, 0])
NODE_RIGHT = joint_spot([4, -2])
NODE_REAR = joint_spot([2, 2])
# The heavy hub under each weapon node (the core's: it stays once the node is gone) and the height
# its gun stands at.
HUB_RADIUS = 6
NODE_GUN_HEIGHT = UPPER_H + HUB_RADIUS + 1.5

# The cannon cells (MB-LATTICE-NODE-05): a hex deck in the lower layer under each rear flank's
# triangle of joints, an armoured cell on it until the transformation.
CELL_AT = [PITCH, ROW * 2 / 3]
CELL_RADIUS = 9.5
DECK_TOP = LOWER_H
CELL_TOP = 12.5

# The core's cluster (MB-LATTICE-NODE-02): its radius, its turret on its front node and its rotor
# on its crown, under a hatch until its last stage.
CLUSTER_RADIUS = 13
CLUSTER_GUN_AT = [0, -12]
CLUSTER_GUN_HEIGHT = 19
ROTOR_AT = [0, 3]
ROTOR_HEIGHT = 24

# The weapon nodes' guns: twin barrels on the fan nodes, three on the rear node's burst turret.
FAN_GUN = {"size": 4.5, "barrels": 2, "gap": 2.6, "bore": 1, "length": 7}
BURST_GUN = {"size": 4.5, "barrels": 3, "gap": 1.1, "bore": 1, "length": 6.5}
CLUSTER_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7}
CLUSTER_ROTOR = {"size": 5, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.4}

GREEN = bullet("green", 185)
BLUE = bullet("blue", 175)
ORANGE = bullet("orange", 180)

_LATTICE_NODE = record({
    "id": "lattice-node",
    # Its points and its parts' drops (MB-LATTICE-NODE-11).
    "stats": stats({
        "id": "lattice-node",
        "name": "Lattice Node",
        "size": 3.5,
        "coreRadius": 14,
        "coreHealth": 1300,
        "points": 4500,
        "groundSpeed": 0.5,
        "parts": [
            part("node-left", NODE_LEFT, 11, 780),
            part("node-right", NODE_RIGHT, 11, 780),
            part("node-rear", NODE_REAR, 11, 780),
        ],
    }),
    # Where it stops and how it moves in place (MB-LATTICE-NODE-06): a slow, level drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 45, "period": 10},
    "bob": {"amplitude": 5, "period": 3.4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-LATTICE-NODE-03): a twin-barrelled turret on each fan node, a
    # three-barrelled one on the rear node, and the core's: a three-barrelled turret on the
    # cluster's front node (its aimed shots, fans and bursts) and a rotor on its crown (its last
    # ring), under a hatch until then.
    "mounts": [
        gun_mount("node-left", "node-left", NODE_LEFT, NODE_GUN_HEIGHT, FAN_GUN),
        gun_mount("node-right", "node-right", NODE_RIGHT, NODE_GUN_HEIGHT, FAN_GUN),
        gun_mount("node-rear", "node-rear", NODE_REAR, NODE_GUN_HEIGHT, BURST_GUN),
        gun_mount("cluster-gun", "core", CLUSTER_GUN_AT, CLUSTER_GUN_HEIGHT, CLUSTER_GUN),
        gun_mount("cluster-rotor", "core", ROTOR_AT, ROTOR_HEIGHT, CLUSTER_ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-LATTICE-NODE-08): the fan nodes'
    # narrow fans cut across the screen from either side, crossing under it, and the rear node's
    # bursts go at the player; the core crosses fans of its own, one each way in turn.
    "stages": stages(
        [
            volley.fan("node-left", 2.6, 4, 5, GREEN, 0.8, -22),
            volley.fan("node-right", 2.6, 4, 5, GREEN, 2.1, 22),
            volley.burst("node-rear", 2.6, 4, 0.12, BLUE, 1.4),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, BLUE, 1.2)],
            [
                volley.fan("core", 3, 5, 6, GREEN, 0.6, -14),
                volley.fan("core", 3, 5, 6, GREEN, 2.1, 14),
            ],
            [
                volley.burst("core", 2.2, 5, 0.1, BLUE, 0.6),
                volley.fan("core", 2.6, 7, 6, GREEN, 1.6, 0),
            ],
            [
                volley.ring("core", 1.5, 12, 11, GREEN, 0.4),
                volley.aimed("core", 2.4, 3, 8, BLUE, 1.1),
            ],
        ],
    ),
})

# Its transformation (MB-LATTICE-NODE-10): once two of its weapon nodes are gone, the armoured
# cells on its rear flanks burst off and a cannon unfolds on each cell's deck. The hatch over the
# cluster's rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
LATTICE_NODE = with_weapons(
    _LATTICE_NODE,
    [
        hidden_weapon(
            "cannon-left",
            "cannon",
            [-CELL_AT[0], CELL_AT[1]],
            7,
            620,
            1,
            "orange",
            1.2,
            [DECK_TOP, DECK_TOP + 3.5],
        ),
        hidden_weapon(
            "cannon-right",
            "cannon",
            [CELL_AT[0], CELL_AT[1]],
            7,
            620,
            1,
            "orange",
            2.0,
            [DECK_TOP, DECK_TOP + 3.5],
        ),
    ],
    [
        armour_region(
            "cells",
            1,
            [
                [
                    CELL_AT[0] + CELL_RADIUS * math.cos(k * math.pi / 3),
                    CELL_AT[1] + CELL_RADIUS * math.sin(k * math.pi / 3),
                ]
                for k in range(6)
            ],
            "shell",
            [DECK_TOP, CELL_TOP + 2],
        ),
        armour_region(
            "rotor-hatch",
            None,
            [
                [
                    ROTOR_AT[0] + 6.5 * math.cos(k * math.pi / 4),
                    ROTOR_AT[1] + 6.5 * math.sin(k * math.pi / 4),
                ]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "cluster-rotor",
        ),
    ],
)
