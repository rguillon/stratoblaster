# Copyright (c) 2026 Renaud Guillon
"""The Bunker Saucer, the Lab's L-24 mini boss (specs/bosses/lab/L-24-bunker-saucer.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying concrete pillbox shaped
like a thick saucer: stepped concrete rings, a parapet round its rim with slit embrasures, an
armoured pillbox turret on its front step, an observation cupola on its crown and two lift-jet
nacelles on its rim's back quarters. It starts with three guns: the pillbox's turret and the two
front slits' fixed guns. Each lost part opens two more slits (their shutters slide back and a
fixed gun rises in each, firing out along the rim's normal). Once two parts are gone the cupola
splits: its halves slide apart on the crown (they change shape, BOSS-45), a cannon riding each;
the last stage opens the rotor under the crown's back hatch.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import along, gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# MB-BUNKER-SAUCER-01: the saucer's rim (its widest radius), the rim deck's top, the parapet round
# it (`[inner radius, outer radius, top]`), the two concrete steps above it (`[radius, top]`) and
# the cupola on the crown (its radius and flat top).
RIM = 57
DECK = 8
PARAPET = [50, 56, 11.5]
STEP = [44, 14]
CROWN = [30, 19]
CUPOLA_RADIUS = 12
CUPOLA_TOP = 24

# The slit embrasures (MB-BUNKER-SAUCER-03): pairs of them either side of the nose, each `deg`
# degrees round from it; their guns sit in the parapet's notches `SLIT_RADIUS` out, on the rim
# deck, and fire out along the rim's normal (fixed: they never turn). The first pair is out from
# the start, the others open one pair a stage.
SLIT_DEGS = [15, 42, 70, 100]
SLIT_RADIUS = 51.5
SLIT_GUN = {"size": 2.8, "barrels": 2, "gap": 2.4, "bore": 0.9, "length": 5.6, "turret": False}
# The parapet's notch round each slit: its half width (px along the rim).
NOTCH_HALF = 4.6

# The pillbox on the front step (MB-BUNKER-SAUCER-04): its drum's centre, radius and top (the
# core's), its turret on it (the part's).
PILLBOX_AT = [0, -37]
PILLBOX_RADIUS = 7
PILLBOX_TOP = 18
PILLBOX_GUN = {"size": 4.2, "barrels": 2, "gap": 1.3, "bore": 1.0, "length": 6.5}
# The lift-jet nacelles on the rim's back quarters (MB-BUNKER-SAUCER-05): no gun.
JET_AT = [38, 38]
JET_RADIUS = 10
# The rotor under the crown's back hatch (its last spiral).
ROTOR_AT = [0, 22]
HATCH_RADIUS = 5.6
CORE_ROTOR = {"size": 4.2, "barrels": 14, "layout": "ring", "bore": 0.8, "length": 3.2}


def slit_deg(k: int, side: float) -> float:
    """Return where slit pair `k`'s gun on `side` (+1 the right, -1 the left) points.

    Degrees from the nose, positive towards the boss's right (the screen's left, -X).
    """
    return -side * SLIT_DEGS[k]


def slit_at(k: int, side: float) -> list[float]:
    """Return where slit pair `k`'s gun on `side` stands: in its notch, on the rim deck."""
    return along([0, 0], slit_deg(k, side), SLIT_RADIUS, 0)


def slit_id(k: int, side: float) -> str:
    """Return the mount id of slit pair `k`'s gun on `side`."""
    return "slit-" + str(SLIT_DEGS[k]) + ("-right" if side > 0 else "-left")


def _slit_mounts() -> list[Any]:
    result: list[Any] = []
    for k in range(len(SLIT_DEGS)):
        for side in [1, -1]:
            options = merge(SLIT_GUN, {"restDeg": slit_deg(k, side)})
            result.append(gun_mount(slit_id(k, side), "core", slit_at(k, side), DECK, options))
    return result


# Its bullets: the slits' red shots, the pillbox's magenta ones, the rotor's spiral.
SLIT_SHOT = bullet("red", 175)
TURRET_SHOT = bullet("magenta", 170)
SPIRAL = bullet("orange", 160)


def _slit_pair(k: int, every: float, first: float) -> list[Any]:
    """Return the volleys of slit pair `k`: both barrels of each gun at once, the right first."""
    return [
        merge(volley.fan("core", every, 2, 0, SLIT_SHOT, first), {"mount": slit_id(k, 1)}),
        merge(
            volley.fan("core", every, 2, 0, SLIT_SHOT, first + every / 2),
            {"mount": slit_id(k, -1)},
        ),
    ]


_BUNKER_SAUCER = record({
    "id": "bunker-saucer",
    # Its points and its parts' drops (MB-BUNKER-SAUCER-11). The lift jets first: the debug key
    # breaks them first, and their loss splits the cupola (BOSS-36).
    "stats": stats({
        "id": "bunker-saucer",
        "name": "Bunker Saucer",
        "size": 3.6,
        "coreRadius": 18,
        "coreHealth": 1600,
        "points": 4000,
        "groundSpeed": 0.5,
        "parts": [
            part("jet-left", [-JET_AT[0], JET_AT[1]], JET_RADIUS, 660),
            part("jet-right", JET_AT, JET_RADIUS, 660),
            part("pillbox", PILLBOX_AT, 9, 720),
        ],
    }),
    # Where it stops and how it moves in place (MB-BUNKER-SAUCER-06): a heavy, slow drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 45, "period": 9},
    "bob": {"amplitude": 4, "period": 4.4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-BUNKER-SAUCER-03): the pillbox's twin turret, the slits' fixed
    # guns and the crown's rotor.
    "mounts": concat(
        [
            gun_mount("pillbox", "pillbox", PILLBOX_AT, PILLBOX_TOP, PILLBOX_GUN),
            gun_mount("core-rotor", "core", ROTOR_AT, CROWN[1], CORE_ROTOR),
        ],
        _slit_mounts(),
    ),
    # Its parts' volleys, then the core's pattern per stage (MB-BUNKER-SAUCER-08): the pillbox
    # sweeps aimed pairs; the slits fire both barrels out along the rim's normal, a new pair open at
    # each stage (15°, 42°, 70°, then 100° off the nose), the older pairs slower; the last stage
    # adds the rotor's spiral of 14.
    "stages": stages(
        [volley.aimed("pillbox", 2.4, 2, 8, TURRET_SHOT, 1.2)],
        [
            _slit_pair(0, 2.0, 0.8),
            concat(_slit_pair(0, 2.6, 0.8), _slit_pair(1, 2.0, 0.5)),
            concat(
                _slit_pair(0, 2.8, 1.0), concat(_slit_pair(1, 2.4, 0.6), _slit_pair(2, 1.8, 0.4))
            ),
            concat(
                [volley.ring("core", 1.4, 14, 360 / 28, SPIRAL, 0.4)],
                concat(_slit_pair(0, 2.6, 0.9), _slit_pair(3, 2.0, 0.6)),
            ),
        ],
    ),
})


def half_cupola() -> list[list[float]]:
    """Return the cupola's right half as drawn (closed): a half disc right of the centre line."""
    n = 8
    return [
        [
            CUPOLA_RADIUS * math.cos(-math.pi / 2 + math.pi * k / n),
            CUPOLA_RADIUS * math.sin(-math.pi / 2 + math.pi * k / n),
        ]
        for k in range(n + 1)
    ]


# MB-BUNKER-SAUCER-10: each half of the cupola slides out across the crown, `CUPOLA_SLIDE` px; the
# left one is its mirror image. A cannon rides each, on its flat top.
CUPOLA_SLIDE = 14
CUPOLA_MOTION = slide([[0, 0, 0], [CUPOLA_SLIDE, 0, 0]])
CUPOLA_HEIGHTS = [CROWN[1], CUPOLA_TOP]
CANNON_AT = [20, 0]
CANNON_POD = [CUPOLA_TOP, CUPOLA_TOP + 2]


def _hatch() -> list[list[float]]:
    return [
        [
            ROTOR_AT[0] + HATCH_RADIUS * math.cos(k * math.pi / 4 + math.pi / 8),
            ROTOR_AT[1] + HATCH_RADIUS * math.sin(k * math.pi / 4 + math.pi / 8),
        ]
        for k in range(8)
    ]


# Its transformation (BOSS-45, MB-BUNKER-SAUCER-10): once two parts are gone the cupola splits and
# its halves slide apart, a cannon unfolding on each. The hatch over the crown's rotor bursts as the
# rotor comes into use, in its last stage (BOSS-58).
BUNKER_SAUCER = with_weapons(
    _BUNKER_SAUCER,
    [
        hidden_weapon(
            "cannon-left",
            "cannon",
            [-CANNON_AT[0], CANNON_AT[1]],
            6.5,
            580,
            1,
            "red",
            1.2,
            CANNON_POD,
        ),
        hidden_weapon("cannon-right", "cannon", CANNON_AT, 6.5, 580, 1, "red", 2.0, CANNON_POD),
    ],
    concat(
        moving_region("cupola", 1, half_cupola(), CUPOLA_MOTION, None, CUPOLA_HEIGHTS),
        [armour_region("rotor-hatch", None, _hatch(), "ring", None, False, "core-rotor")],
    ),
)
