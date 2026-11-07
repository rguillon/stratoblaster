# Copyright (c) 2026 Renaud Guillon
"""The Cathedral Engine, the Lab's L-8 final boss (specs/bosses/lab/L-8-cathedral-engine.md).

A Lab boss, in the dev viewer only: no level brings it in. Offsets in px from the boss's centre,
X right and Y up (its nose points down, at -Y). A gothic machine-church seen from above: its west
front and twin spires at the front, its nave, a transept across, the rose window at the crossing,
the choir and the round apse at the back. 5 destroyable parts (BOSS-13): two spires, two organ-pipe
banks in the transept arms and the rose window. A choir: layered rings and spirals of different
speeds fired on one rhythm (a bar of `BAR` seconds), the rose window's laser over them
(FB-CATHEDRAL-ENGINE-08).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


# Its rhythm: every volley fires on beats of a bar this long (FB-CATHEDRAL-ENGINE-08).
BAR = 3.2
BEAT = BAR / 4

# Its voices: low, slow notes and high, fast ones.
LOW = bullet("purple", 110, 4.5)
MID = bullet("magenta", 135)
HIGH = bullet("orange", 175)
BELL = bullet("red", 200)

# FB-CATHEDRAL-ENGINE-01: its plan. The nave's central vessel's and aisles' half widths, from the
# west front (`NAVE[0]`) to the crossing (`NAVE[1]`); the crossing's half width; the transept's
# reach and half depth; the choir from the crossing to the apse's centre, its vessel's and aisles'
# half widths; the apse's radius.
NAVE = [-58, -16]
VESSEL = 11
AISLE = 24
CROSSING = 16
TRANSEPT = [64, 14]
CHOIR = [16, 48]
CHOIR_VESSEL = 10
CHOIR_AISLE = 23
APSE = 20
# The tops of its roofs: the aisles', the transept's and the high vessels'.
AISLE_TOP = 10
TRANSEPT_TOP = 14
VESSEL_TOP = 16

# Where its parts stand (FB-CATHEDRAL-ENGINE-03): a spire on each tower of the west front, an organ
# bank in each transept arm and the rose window over the crossing.
SPIRE_AT = [20, -63]
# A spire's bell gun stands at the front of its belfry, its needle behind it.
BELL_AT = [20, -67]
NEEDLE_AT = [20, -59]
ORGAN_AT = [44, 0]
ROSE_AT = [0, 0]
# The heights their guns stand at: the belfry's top, the organ's console and the rose's hub.
BELFRY_TOP = 15
CONSOLE_TOP = 17
ROSE_TOP = 19

# A spire's bell gun: one long barrel on a turret in the belfry.
BELL_GUN = {"size": 3.6, "barrels": 1, "bore": 1.2, "length": 8}
# The organ banks' rotors: their barrel counts are the rings' (eight and ten), the chords' notes.
ORGAN_ROTOR_LEFT = {"size": 5, "barrels": 8, "layout": "ring", "bore": 1, "length": 4}
ORGAN_ROTOR_RIGHT = {"size": 5.4, "barrels": 10, "layout": "ring", "bore": 1, "length": 4}
# The rose window's laser: a big emitter at its hub, on a turret (BOSS-31).
ROSE_LASER = {"size": 5.5, "bore": 2.6, "length": 12, "turret": True}

# The core's guns (BOSS-58): the portal gun over the west door (its aimed shots, fans and bursts),
# the apse rotor (its rings and spirals) and the lantern rotor over the choir, under a hatch until
# its last stage.
PORTAL_AT = [0, -66]
APSE_AT = [0, 50]
LANTERN_AT = [0, 31]


def _apse(shot: Any) -> Any:
    """Return the core's ring `shot` fired from its apse rotor."""
    return merge(shot, {"mount": "apse-rotor"})


_CATHEDRAL_ENGINE = record({
    "id": "cathedral-engine",
    # Its points, its core's drop and its parts' drops (FB-CATHEDRAL-ENGINE-13).
    "stats": stats({
        "id": "cathedral-engine",
        "name": "Cathedral Engine",
        "size": 4.5,
        "coreRadius": 22,
        "coreHealth": 2900,
        "points": 11000,
        "groundSpeed": 0,
        "coreDrop": 1,
        "parts": [
            fpart("spire-left", [-SPIRE_AT[0], SPIRE_AT[1]], 11, 950),
            fpart("spire-right", SPIRE_AT, 11, 950),
            fpart("organ-left", [-ORGAN_AT[0], ORGAN_AT[1]], 14, 1200),
            fpart("organ-right", ORGAN_AT, 14, 1200),
            fpart("rose", ROSE_AT, 15, 1400),
        ],
    }),
    # Where it stops and how it moves in place (FB-CATHEDRAL-ENGINE-06): slow and stately.
    "stopFraction": 0.72,
    "sway": {"amplitude": 26, "period": 12.8},
    "bob": {"amplitude": 4, "period": 6.4},
    "guns": {},
    # It transforms once both spires are gone, then once both organ banks are
    # (FB-CATHEDRAL-ENGINE-10, FB-CATHEDRAL-ENGINE-11).
    "transformParts": [["spire-left", "spire-right"], ["organ-left", "organ-right"]],
    # Its gun mounts (BOSS-58, FB-CATHEDRAL-ENGINE-03).
    "mounts": [
        gun_mount("spire-left", "spire-left", [-BELL_AT[0], BELL_AT[1]], BELFRY_TOP, BELL_GUN),
        gun_mount("spire-right", "spire-right", BELL_AT, BELFRY_TOP, BELL_GUN),
        gun_mount(
            "organ-left", "organ-left", [-ORGAN_AT[0], ORGAN_AT[1]], CONSOLE_TOP, ORGAN_ROTOR_LEFT
        ),
        gun_mount("organ-right", "organ-right", ORGAN_AT, CONSOLE_TOP, ORGAN_ROTOR_RIGHT),
        laser_mount("rose", "rose", ROSE_AT, ROSE_TOP, ROSE_LASER),
        gun_mount(
            "portal",
            "core",
            PORTAL_AT,
            10,
            {"size": 4.8, "barrels": 3, "gap": 1, "bore": 1, "length": 7},
        ),
        gun_mount(
            "apse-rotor",
            "core",
            APSE_AT,
            VESSEL_TOP,
            {"size": 5.5, "barrels": 12, "layout": "ring", "bore": 0.9, "length": 3.6},
        ),
        gun_mount(
            "lantern-rotor",
            "core",
            LANTERN_AT,
            VESSEL_TOP,
            {"size": 5.2, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-CATHEDRAL-ENGINE-08). Each organ
    # bank plays a chord: two rings at once from its rotor, one slow and one fast, along the same
    # barrels; the left bank on the bar's second beat, the right one on its fourth. The spires toll
    # aimed shots on the beats, the rose window's laser every two bars and a half.
    "stages": stages(
        [
            volley.aimed("spire-left", BAR / 2, 1, 0, BELL, BEAT * 0.5),
            volley.aimed("spire-right", BAR / 2, 1, 0, BELL, BEAT * 1.5),
            volley.ring("organ-left", BAR, 8, 11.25, LOW, BEAT),
            volley.ring("organ-left", BAR, 8, 11.25, HIGH, BEAT),
            volley.ring("organ-right", BAR, 10, -9, LOW, BEAT * 3),
            volley.ring("organ-right", BAR, 10, -9, HIGH, BEAT * 3),
            volley.laser("rose", BAR * 2.5, 1.8, BAR, 16),
        ],
        [
            [_apse(volley.ring("core", BAR, 12, 7.5, MID, BEAT * 2))],
            [_apse(volley.ring("core", BAR / 2, 12, -10, MID, BEAT))],
            [
                _apse(volley.ring("core", BAR, 12, 15, MID, BEAT * 2)),
                volley.aimed("core", BAR, 3, 10, BELL, BEAT),
            ],
            [
                _apse(volley.ring("core", BAR, 12, 7.5, LOW, BEAT * 2)),
                _apse(volley.ring("core", BAR, 12, 7.5, HIGH, BEAT * 2)),
                volley.burst("core", BAR, 3, 0.12, BELL, BEAT * 3),
            ],
            [
                _apse(volley.ring("core", 1, 12, 9, MID, 0.5)),
                volley.aimed("core", BAR, 3, 10, BELL, BEAT),
            ],
            [
                merge(
                    volley.ring("core", BAR / 2, 16, 11.25, MID, 0.4), {"mount": "lantern-rotor"}
                ),
                _apse(volley.ring("core", BAR / 2, 12, -7.5, HIGH, 0.4 + BEAT)),
                volley.aimed("core", BAR, 1, 0, BELL, BEAT * 3),
            ],
        ],
    ),
})

# Its aisles' roofs either side of the nave, the right one (FB-CATHEDRAL-ENGINE-05): lean-to roofs
# from the high vessel's wall out to the buttresses, the batteries under them; mirrored.
AISLE_ROOF: list[Any] = [[VESSEL, -56], [AISLE, -56], [AISLE, -18], [VESSEL, -18]]
# The choir aisles' roofs either side of the choir, the right one: the sweepers under them.
CHOIR_ROOF: list[Any] = [
    [CHOIR_VESSEL, 18],
    [CHOIR_AISLE, 18],
    [CHOIR_AISLE, 46],
    [CHOIR_VESSEL, 46],
]
# The nave's high vault, on the centre line (not mirrored): the orb under it.
VAULT: list[Any] = [[-VESSEL, -56], [VESSEL, -56], [VESSEL, -18], [-VESSEL, -18]]
# The heights of the aisles' roofs (over the aisles' vaults) and of the high vault.
AISLE_ROOF_HEIGHTS = [8, 13.5]
VAULT_HEIGHTS = [10, 17]
# The hatch over the lantern rotor: an octagon this wide round it.
HATCH_RADIUS = 6.5

# Its transformations (D-224; FB-CATHEDRAL-ENGINE-10, FB-CATHEDRAL-ENGINE-11): once both spires are
# gone its aisles' roofs burst off for a pair of batteries; once both organ banks are gone its choir
# aisles' roofs and its nave's high vault burst off for a pair of sweepers and an orb on the centre
# line.
CATHEDRAL_ENGINE = with_weapons(
    _CATHEDRAL_ENGINE,
    [
        hidden_weapon("battery-left", "battery", [-17.5, -37], 7, 1120, 1, "purple", 1.2, [8, 11]),
        hidden_weapon("battery-right", "battery", [17.5, -37], 7, 1120, 1, "purple", 2.0, [8, 11]),
        hidden_weapon("sweeper-left", "sweeper", [-16.5, 32], 7, 1400, 2, "purple", 1.2, [8, 11]),
        hidden_weapon("sweeper-right", "sweeper", [16.5, 32], 7, 1400, 2, "purple", 2.4, [8, 11]),
        hidden_weapon("orb", "orb", [0, -37], 8, 1400, 2, "magenta", 1.6, [10, 13.5]),
    ],
    [
        armour_region("aisles", 1, AISLE_ROOF, "shell", AISLE_ROOF_HEIGHTS),
        armour_region("choir-aisles", 2, CHOIR_ROOF, "shell", AISLE_ROOF_HEIGHTS),
        armour_region("vault", 2, VAULT, "wing", VAULT_HEIGHTS, False),
        armour_region(
            "lantern-hatch",
            None,
            [
                [
                    HATCH_RADIUS * math.cos(k * math.pi / 4),
                    LANTERN_AT[1] + HATCH_RADIUS * math.sin(k * math.pi / 4),
                ]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "lantern-rotor",
        ),
    ],
)
