# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-5 final boss, the Crescent Halo (specs/bosses/lab/L-5-crescent-halo.md).

A living station shaped as a crescent open at its front, its horns pointing down the screen, its
core a floating organ in the hollow tethered to the ring. Lab boss: in the dev viewer only (no level
brings it in). Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y);
angles round the ring in degrees from its nose, positive towards its right (+X).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEG = math.pi / 180

# FB-CRESCENT-HALO-01: the ring's centre line (its radius), its tube's girth and the height of its
# axis over the playfield (its top is the axis plus the girth).
HALO_RADIUS = 56
HALO_GIRTH = 10
HALO_AXIS = 8
# The fixed ring runs round the back from `HALO_ARC[0]` to `HALO_ARC[1]` either side of the nose.
HALO_ARC = [60, 180]
# A horn (FB-CRESCENT-HALO-05): an armoured sleeve over the ring's end, from its tip at
# `HORN_ARC[0]` back to `HORN_ARC[1]`, `HORN_GIRTH` round (over the ring's), tapering to
# `HORN_TIP` at its tip over `HORN_TAPER` degrees; it swings `HORN_SWING` degrees round the centre
# to close the halo at its nose.
HORN_ARC = [40, 104]
HORN_GIRTH = 13
HORN_TIP = 4
HORN_TAPER = 22
HORN_SWING = 40


def ring_point(angle: float, radius: float) -> list[float]:
    """Return the point `radius` px from the centre, `angle` degrees round from the nose."""
    a = angle * DEG
    return [radius * math.sin(a), -radius * math.cos(a)]


def horn_girth(angle: float) -> float:
    """Return a horn's girth (its half width seen from above) `angle` degrees round the ring."""
    k = min(1, max(0, (angle - HORN_ARC[0]) / HORN_TAPER))
    return float(HORN_TIP + (HORN_GIRTH - HORN_TIP) * k)


def _horn_outline() -> list[list[float]]:
    """Return the right horn's outline as drawn (at rest): its outer edge, then its inner one."""
    angles = [HORN_ARC[0] + (HORN_ARC[1] - HORN_ARC[0]) * k / 8 for k in range(9)]
    outer = [ring_point(a, HALO_RADIUS + horn_girth(a)) for a in angles]
    inner = [ring_point(a, HALO_RADIUS - horn_girth(a)) for a in angles]
    result: list[list[float]] = []
    result.extend(outer)
    result.extend([inner[8 - k] for k in range(9)])
    return result


def _arc_outline(angles: list[Any], radii: list[Any]) -> list[list[float]]:
    """Return the outline of the ring's stretch between `angles`, from `radii[0]` to `radii[1]`."""
    steps = 4
    span = [angles[0] + (angles[1] - angles[0]) * k / steps for k in range(steps + 1)]
    result: list[list[float]] = [ring_point(a, radii[1]) for a in span]
    result.extend([ring_point(span[steps - k], radii[0]) for k in range(steps + 1)])
    return result


def ring_spot(angle: float) -> list[float]:
    """Return the spot on the ring's centre line `angle` degrees round from the nose."""
    return ring_point(angle, HALO_RADIUS)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


GOLD = bullet("orange", 180)
MAGENTA = bullet("magenta", 185)
RED = bullet("red", 190)

# Where its parts stand round the crescent (FB-CRESCENT-HALO-03): on the horns, on the flanks and
# either side of the back.
HORN_AT = 54
FLANK_AT = 120
BACK_AT = 150

# The horns' rotors: six barrels each, spinning their spirals against each other.
HORN_ROTOR = {"size": 4.5, "barrels": 6, "layout": "ring", "bore": 1, "length": 5}
# The horns' height: flat-topped armoured sleeves standing over the ring's ends.
HORN_TOP = 23
HORN_BOTTOM = -3
# The flanks' laser emitters, built into the ring and firing straight down the screen.
FLANK_LASER = {"size": 5, "bore": 2.4, "length": 11}
# The back's twin-barrelled turrets, sweeping their aimed fans.
BACK_GUN = {"size": 6, "barrels": 2, "gap": 3, "bore": 1.2, "length": 8}
# The core's rotor on the organ's crown (its spirals and its last ring) and its eye turret on the
# organ's front (its aimed shots, bursts and fans).
HALO_ROTOR = {"size": 6, "barrels": 12, "layout": "ring", "bore": 0.9, "length": 5}
EYE_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7}
# The organ: its centre's height, its radius, its crown's height (the rotor stands on it) and the
# spot and height of the eye's seat on its front.
ORGAN_RADIUS = 19
ORGAN_CROWN = 25
EYE_AT = [0, -17]
EYE_HEIGHT = 14

_SPOTS: dict[str, Any] = {
    "horn-left": ring_spot(-HORN_AT),
    "horn-right": ring_spot(HORN_AT),
    "flank-left": ring_spot(-FLANK_AT),
    "flank-right": ring_spot(FLANK_AT),
    "back-left": ring_spot(-BACK_AT),
    "back-right": ring_spot(BACK_AT),
}

# FB-CRESCENT-HALO-07: six parts, all shielding the core.
_CRESCENT_HALO = record({
    "id": "crescent-halo",
    # Its points, its core's drop and its parts' drops (FB-CRESCENT-HALO-13).
    "stats": stats({
        "id": "crescent-halo",
        "name": "Crescent Halo",
        "size": 4.5,
        "coreRadius": 22,
        "coreHealth": 5200,
        "points": 15000,
        "groundSpeed": 0.4,
        "coreDrop": 1,
        "parts": [
            fpart("horn-left", _SPOTS["horn-left"], 12, 1500),
            fpart("horn-right", _SPOTS["horn-right"], 12, 1500),
            fpart("flank-left", _SPOTS["flank-left"], 13, 1700),
            fpart("flank-right", _SPOTS["flank-right"], 13, 1700),
            fpart("back-left", _SPOTS["back-left"], 12, 1900),
            fpart("back-right", _SPOTS["back-right"], 12, 1900),
        ],
    }),
    # Where it stops and how it moves in place (FB-CRESCENT-HALO-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 30, "period": 10},
    "bob": {"amplitude": 6, "period": 5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-CRESCENT-HALO-03): a six-barrelled rotor on each horn's growth, a
    # laser emitter in each flank's gland, a twin-barrelled turret on each back growth, and the
    # core's: the twelve-barrelled rotor on the organ's crown and the eye turret on its front.
    "mounts": [
        gun_mount("horn-left", "horn-left", _SPOTS["horn-left"], 27, HORN_ROTOR),
        gun_mount("horn-right", "horn-right", _SPOTS["horn-right"], 27, HORN_ROTOR),
        laser_mount("flank-left", "flank-left", _SPOTS["flank-left"], 19, FLANK_LASER),
        laser_mount("flank-right", "flank-right", _SPOTS["flank-right"], 19, FLANK_LASER),
        gun_mount("back-left", "back-left", _SPOTS["back-left"], 20.2, BACK_GUN),
        gun_mount("back-right", "back-right", _SPOTS["back-right"], 20.2, BACK_GUN),
        gun_mount("halo-rotor", "core", [0, 0], ORGAN_CROWN, HALO_ROTOR),
        gun_mount("eye", "core", EYE_AT, EYE_HEIGHT, EYE_GUN),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-CRESCENT-HALO-08): the horns spin
    # their spirals against each other, the flanks' lasers wall the player in, the back turrets
    # sweep aimed fans; the core's rotor spirals one way then the other, a new turn and pace at
    # every stage, and its eye adds aimed shots, bursts and fans (12° apart, BOSS-58).
    "stages": stages(
        [
            volley.ring("horn-left", 1.6, 6, 15, MAGENTA, 0.6),
            volley.ring("horn-right", 1.6, 6, -15, MAGENTA, 1.4),
            volley.laser("flank-left", 6.5, 1.6, 2),
            volley.laser("flank-right", 6.5, 1.6, 5.25),
            volley.aimed("back-left", 2.2, 3, 12, RED, 1),
            volley.aimed("back-right", 2.2, 3, 12, RED, 2.1),
        ],
        [
            [volley.ring("core", 1.8, 12, 10, GOLD, 0.8), volley.aimed("core", 3, 1, 0, RED, 1.6)],
            [
                volley.ring("core", 1.5, 12, -12, GOLD, 0.6),
                volley.aimed("core", 2.6, 3, 12, RED, 1.2),
            ],
            [
                volley.ring("core", 0.85, 12, 14, GOLD, 0.5),
                volley.aimed("core", 2.2, 3, 12, RED, 1),
            ],
            [
                volley.ring("core", 1, 12, -9, GOLD, 0.5),
                volley.burst("core", 2.4, 4, 0.13, RED, 1),
            ],
            [
                volley.ring("core", 1, 12, 16, GOLD, 0.5),
                volley.fan("core", 2.4, 5, 12, RED, 1),
            ],
            [
                volley.ring("core", 0.9, 12, -18, GOLD, 0.4),
                volley.burst("core", 2.2, 4, 0.12, RED, 1),
            ],
            [
                volley.ring("core", 0.6, 12, 7, GOLD, 0.4),
                volley.fan("core", 2.2, 7, 12, RED, 1),
            ],
        ],
    ),
})

# Where the mortars end up, on the closed halo's horns either side of the nose (they ride the
# horns in, FB-CRESCENT-HALO-10), and where the batteries stand on the flanks of the ring the horns
# bared (FB-CRESCENT-HALO-11).
MORTAR_AT = 30
BATTERY_AT = 84

# The armour plates over the ring's flanks, under the horns at rest (shed at the second
# transformation), and the crest over the back of the ring (likewise).
PLATES_ARC = [68, 100]
CREST_ARC = [168, 192]
PLATES_HEIGHTS = [16, 21]

# Its transformations (FB-CRESCENT-HALO-05, FB-CRESCENT-HALO-10, FB-CRESCENT-HALO-11): once both
# horns' growths are gone its horns swing closed round the centre into a full halo, riding a pair
# of mortars in; once both flanks are gone the armour plates the horns bared and the crest of the
# ring burst off for a pair of batteries and a gatling on the centre line.
CRESCENT_HALO = with_weapons(
    merge(
        _CRESCENT_HALO,
        {"transformParts": [["horn-left", "horn-right"], ["flank-left", "flank-right"]]},
    ),
    [
        hidden_weapon(
            "mortar-left", "mortar", ring_spot(-MORTAR_AT), 10, 1520, 1, "orange", 1.2, [20, 25.5]
        ),
        hidden_weapon(
            "mortar-right", "mortar", ring_spot(MORTAR_AT), 10, 1520, 1, "orange", 2.0, [20, 25.5]
        ),
        hidden_weapon(
            "battery-left", "battery", ring_spot(-BATTERY_AT), 8, 1900, 2, "red", 1.2, [14, 20]
        ),
        hidden_weapon(
            "battery-right", "battery", ring_spot(BATTERY_AT), 8, 1900, 2, "red", 2.0, [14, 20]
        ),
        hidden_weapon(
            "gatling", "gatling", [0, HALO_RADIUS + 1], 8, 1900, 2, "magenta", 1.6, [14, 20]
        ),
    ],
    concat(
        # FB-CRESCENT-HALO-05: the horns, swinging round the centre to meet at the nose.
        moving_region(
            "horns",
            1,
            _horn_outline(),
            swing([0, 0, HALO_AXIS], "up", [0, -HORN_SWING]),
        ),
        [
            armour_region(
                "plates",
                2,
                _arc_outline(PLATES_ARC, [HALO_RADIUS - 11, HALO_RADIUS + 11]),
                "shell",
                PLATES_HEIGHTS,
            ),
            armour_region(
                "crest",
                2,
                _arc_outline(CREST_ARC, [HALO_RADIUS - 11, HALO_RADIUS + 11]),
                "shell",
                None,
                False,
            ),
        ],
    ),
)
