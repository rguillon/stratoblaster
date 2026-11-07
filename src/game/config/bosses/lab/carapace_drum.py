# Copyright (c) 2026 Renaud Guillon
"""L-1 mini boss of the Lab: the Carapace Drum (specs/bosses/lab/L-1-carapace-drum.md).

A squat barnacle drum seen from above, its domed lid on a thick turning rim carrying three barnacle
rotor pods (BOSS-34). A bullet-curtain boss: the pods' rotors fire rings, spiralling as the rim
turns, and the core adds a new pattern at every stage (BOSS-21). Offsets in px from its centre,
X right and Y up (its nose points down, at -Y). Lab boss: in the dev viewer only.
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


GREEN = bullet("green", 165)
BLUE = bullet("blue", 180)

# The rim's three barnacle pods, 40 px out, 120 degrees apart (MB-CARAPACE-DRUM-03).
POD_REACH = 40
POD_SPOTS = [
    [POD_REACH * math.sin(k * 2 * math.pi / 3), -POD_REACH * math.cos(k * 2 * math.pi / 3)]
    for k in range(3)
]
# Each pod's rotor: six barrels round its hub, one per bullet of its rings (MB-CARAPACE-DRUM-03).
POD_ROTOR = {"size": 4, "barrels": 6, "layout": "ring", "bore": 0.9, "length": 4}
# Height of a rotor's base: on the crown of its barnacle cone.
POD_ROTOR_HEIGHT = 10.5

# The lid: a domed annulus from `LID_HOLE` to `LID_RADIUS` round the operculum (the hub at its
# middle, carrying the crown rotor under its hatch), MB-CARAPACE-DRUM-05.
LID_RADIUS = 23
LID_HOLE = 7
# Height of the drum's top (what the lid lies on), and of the operculum's top.
DRUM_TOP = 9
HUB_TOP = 17
# Height of the mouth turret's base: on the plate grafted on the drum's front shoulder.
MOUTH_HEIGHT = 9.4


def _half_annulus(inner: float, outer: float, steps: int) -> list[Any]:
    """Return the right half (x >= 0) of an annulus, round from the nose to the tail and back."""
    result: list[Any] = []
    for k in range(steps + 1):
        a = math.pi * k / steps
        result.append([outer * math.sin(a), -outer * math.cos(a)])
    for k in range(steps + 1):
        a = math.pi * (steps - k) / steps
        result.append([inner * math.sin(a), -inner * math.cos(a)])
    return result


_CARAPACE_DRUM = record({
    "id": "carapace-drum",
    # Its points and its parts' drops (MB-CARAPACE-DRUM-11).
    "stats": stats({
        "id": "carapace-drum",
        "name": "Carapace Drum",
        "size": 3,
        "coreRadius": 20,
        "coreHealth": 900,
        "points": 3000,
        "groundSpeed": 0.5,
        "parts": [
            part("pod-" + str(k + 1), POD_SPOTS[k], 13, 500, {"orbits": True}) for k in range(3)
        ],
    }),
    # Where it stops and how it moves in place (MB-CARAPACE-DRUM-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 55, "period": 9},
    "bob": {"amplitude": 6, "period": 4},
    # Its rim turns slowly, the pods with it (BOSS-34).
    "spinRate": 0.45,
    "guns": {},
    # Its gun mounts (BOSS-58, MB-CARAPACE-DRUM-03): a six-barrelled rotor on each pod's crown,
    # the core's mouth turret on the drum's front shoulder (its fans, aimed spreads and bursts) and
    # its crown rotor on the operculum, under a hatch until its last stage (its ring).
    "mounts": concat(
        [
            gun_mount(
                "pod-" + str(k + 1),
                "pod-" + str(k + 1),
                POD_SPOTS[k],
                POD_ROTOR_HEIGHT,
                merge(POD_ROTOR, {"restDeg": k * 120}),
            )
            for k in range(3)
        ],
        [
            gun_mount(
                "mouth",
                "core",
                [0, -26],
                MOUTH_HEIGHT,
                {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 5},
            ),
            gun_mount(
                "crown-rotor",
                "core",
                [0, 0],
                HUB_TOP + 0.4,
                {"size": 5, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.5},
            ),
        ],
    ),
    # The pods' rings in every stage, then the core's pattern per stage (MB-CARAPACE-DRUM-08). Its
    # fans are 12 degrees apart, as the mouth turret's barrels (BOSS-58).
    "stages": stages(
        [
            volley.ring("pod-1", 2.4, 6, 14, GREEN, 0.6),
            volley.ring("pod-2", 2.4, 6, 14, GREEN, 1.4),
            volley.ring("pod-3", 2.4, 6, 14, GREEN, 2.2),
        ],
        [
            [volley.fan("core", 3, 3, 12, BLUE, 1.5)],
            [volley.aimed("core", 2.6, 3, 12, BLUE, 0.8)],
            [
                volley.burst("core", 2.2, 4, 0.15, BLUE, 0.6),
                volley.fan("core", 2.6, 5, 12, BLUE, 1.6),
            ],
            [
                volley.ring("core", 1.6, 12, 11, GREEN, 0.4),
                volley.aimed("core", 2.8, 1, 0, BLUE, 1.2),
            ],
        ],
    ),
})

# Its transformation (D-224, MB-CARAPACE-DRUM-10): once two pods are gone its lid's armour bursts
# off, baring a dark metal lattice round the operculum, and a pair of cannons unfold on the drum.
CARAPACE_DRUM = with_weapons(
    _CARAPACE_DRUM,
    [
        hidden_weapon("cannon-left", "cannon", [-14.5, 3], 8, 400, 1, "blue", 1.2, [DRUM_TOP, 12]),
        hidden_weapon("cannon-right", "cannon", [14.5, 3], 8, 400, 1, "blue", 2.0, [DRUM_TOP, 12]),
    ],
    [
        # MB-CARAPACE-DRUM-05: the lid, two half-rings (the right one and its mirror image) from
        # the operculum out to its rim; the cannons lie under them.
        armour_region("lid", 1, _half_annulus(LID_HOLE, LID_RADIUS, 8), "ring"),
        # The hatch over the crown rotor (BOSS-58): it bursts as the rotor comes into use, in its
        # last stage, and the rotor rises out of it.
        armour_region(
            "crown-hatch",
            None,
            [[6.5 * math.cos(k * math.pi / 4), 6.5 * math.sin(k * math.pi / 4)] for k in range(8)],
            "ring",
            None,
            False,
            "crown-rotor",
        ),
    ],
)
