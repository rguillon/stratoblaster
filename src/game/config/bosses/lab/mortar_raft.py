# Copyright (c) 2026 Renaud Guillon
"""The Mortar Raft, the Lab's L-25 mini boss (specs/bosses/lab/L-25-mortar-raft.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying raft seen from above:
an old barge hull lashed to a jumble of pontoons and a second, boxy hull section, plank decks over
them, deck shacks, cargo under nets, a mast with a patched sail and a dozen small lift propellers
round its edges. Irregular and lopsided: nothing on it matches its other side. It comes in with
three guns (a row of two fixed mortar tubes on its forward hull section and a turret on its
wheelhouse); every part it loses uncovers more from under its tarpaulins (fixed bow guns, a deck
turret, a stern mortar, at last a flak rotor). Once two parts are lost, the lashings of its stern
outriggers snap and the two pontoons swing out like gates (BOSS-45), a missile rack riding each.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import move_point, moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# MB-MORTAR-RAFT-01: the barge hull down its middle (a little to the left, its bow skewed), its
# deck's height; the plank deck over the two left pontoons `[x0, x1, y0, y1]` and its top; the left
# pontoons `[x, y0, y1]` and the right one, their radius and their axis' height.
HULL = [
    [-13, -46],
    [5, -48],
    [13, -40],
    [15, 30],
    [10, 44],
    [-12, 44],
    [-16, 32],
    [-17, -36],
]  # type: list[list[float]]
DECK = 8
PLANKS = [-38, -17, -30, 20]  # type: list[float]
PLANK_TOP = 9
LEFT_PONTOONS = [[-23, -36, 20], [-33, -26, 14]]  # type: list[list[float]]
RIGHT_PONTOON = [24, -16, 12]  # type: list[float]
PONTOON_R = 4.6
PONTOON_AXIS = 4.6
# The little deck over the right pontoon `[x0, x1, y0, y1]` and its top (the flak rotor's).
SIDE_DECK = [17, 31, -11, 10]  # type: list[float]
SIDE_TOP = 9.5

# The mortar barge (MB-MORTAR-RAFT-03): the boxy hull section lashed on forward right
# `[x0, x1, y0, y1]`, its deck, and its two fixed mortar tubes in a row at its bow.
BARGE = [17, 40, -52, -20]  # type: list[float]
BARGE_TOP = 9.5
BARGE_AT = [28.5, -36]
MORTAR_ATS = [[23, -44], [34, -44]]  # type: list[list[float]]
# Their rest headings: splayed a little apart, out of the barge's bow.
MORTAR_DEGS = [6, -6]
MORTAR = {"size": 4.6, "barrels": 1, "bore": 2.9, "length": 4.4, "style": "mortar", "axis": 0.8}
# The wheelhouse (MB-MORTAR-RAFT-03): a deckhouse on the barge's after deck `[x0, x1, y0, y1]`
# (the hull's) and its top; on it the wheelhouse cabin (the part) from `CABIN_Y` aft to its roof,
# and the twin turret in front of the cabin.
WHEELHOUSE = [-13, 2, 15, 34]  # type: list[float]
DECKHOUSE_TOP = 12
CABIN_Y = 23.5
ROOF = 19
WHEELHOUSE_AT = [-5.5, 25]
WHEELHOUSE_GUN_AT = [-5.5, 19.5]
WHEELHOUSE_GUN = {"size": 4, "barrels": 2, "gap": 1.3, "bore": 0.95, "length": 6.5}
# The mast (MB-MORTAR-RAFT-03): its foot on the barge's deck, its top, its yard's height and half
# span (the sail hangs from it), its crow's nest.
MAST_AT = [3, -10]
MAST_TOP = 36
YARD = 31
YARD_HALF = 15
NEST = 27

# The core's guns (MB-MORTAR-RAFT-08), each under a tarpaulin until a stage first uses it: the
# fixed bow guns (three barrels pointing down the screen), the deck turret on the left planks, the
# stern mortar turret and, last, the flak rotor on the right pontoon's deck.
BOW_AT = [-3, -39]
BOW_GUN = {
    "size": 3.6,
    "barrels": 3,
    "gap": 2.6,
    "bore": 1,
    "length": 6,
    "turret": False,
    "restDeg": 0,
}
DECK_GUN_AT = [-27, -12]
DECK_GUN = {"size": 4.2, "barrels": 2, "gap": 1.3, "bore": 1, "length": 7}
STERN_AT = [7, 38]
STERN_MORTAR = {
    "size": 4.8,
    "barrels": 1,
    "bore": 3,
    "length": 4.4,
    "style": "mortar",
    "axis": 0.8,
}
ROTOR_AT = [24, 3]
ROTOR = {"size": 4.4, "barrels": 12, "layout": "ring", "bore": 0.75, "length": 3.2}
# The tarpaulins over them `[x0, x1, y0, y1]`, lashed down over their mounts (BOSS-58).
TARPS = {  # type: dict[str, list[float]]
    "bow-guns": [-10, 4, -45, -33],
    "deck-gun": [-34, -20, -19, -5],
    "stern-mortar": [2.8, 11.8, 33, 43.4],
    "flak-rotor": [18, 30, -3, 9],
}
TARP_TOP = 2.6

ORANGE = bullet("orange", 175)
RED = bullet("red", 195)
MAGENTA = bullet("magenta", 180)
# The mortars' flak (MB-MORTAR-RAFT-08): a big, slow shell bursting into a ring of 8.
FLAK = bursting("orange", 105, 7, [1.1, 8, bullet("red", 150)])
# The stern mortar's heavier one, into 10.
HEAVY_FLAK = bursting("orange", 95, 8, [1.3, 10, bullet("orange", 150)])

_MORTAR_RAFT = record({
    "id": "mortar-raft",
    # Its points and its parts' drops (MB-MORTAR-RAFT-11).
    "stats": stats({
        "id": "mortar-raft",
        "name": "Mortar Raft",
        "size": 3.6,
        "coreRadius": 14,
        "coreHealth": 1200,
        "points": 5300,
        "groundSpeed": 0.6,
        "parts": [
            part("mortar-barge", BARGE_AT, 12, 950),
            part("wheelhouse", WHEELHOUSE_AT, 10, 900),
            part("mast", MAST_AT, 10, 850),
        ],
    }),
    # Where it stops and how it moves in place (MB-MORTAR-RAFT-06): a heavy, lazy drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 36, "period": 8},
    "bob": {"amplitude": 4, "period": 3.6},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-MORTAR-RAFT-03, MB-MORTAR-RAFT-08).
    "mounts": [
        gun_mount(
            "mortar-1",
            "mortar-barge",
            MORTAR_ATS[0],
            BARGE_TOP,
            merge(MORTAR, {"turret": False, "restDeg": MORTAR_DEGS[0]}),
        ),
        gun_mount(
            "mortar-2",
            "mortar-barge",
            MORTAR_ATS[1],
            BARGE_TOP,
            merge(MORTAR, {"turret": False, "restDeg": MORTAR_DEGS[1]}),
        ),
        gun_mount("wheelhouse-gun", "wheelhouse", WHEELHOUSE_GUN_AT, DECKHOUSE_TOP, WHEELHOUSE_GUN),
        gun_mount("bow-guns", "core", BOW_AT, DECK, BOW_GUN),
        gun_mount("deck-gun", "core", DECK_GUN_AT, PLANK_TOP, DECK_GUN),
        gun_mount("stern-mortar", "core", STERN_AT, DECK, STERN_MORTAR),
        gun_mount("flak-rotor", "core", ROTOR_AT, SIDE_TOP, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-MORTAR-RAFT-08): the two fixed
    # mortars lob flak straight out of the bow, one after the other, the wheelhouse turret bursts
    # at the player. The core fires nothing as it comes in; then its bow guns' parallel streams and
    # the deck turret's aimed shots, then its stern mortar's heavy flak, then the flak rotor's
    # spiral.
    "stages": stages(
        [
            merge(
                volley.fan("mortar-barge", 3.4, 1, 0, FLAK, 1.2, -MORTAR_DEGS[0]),
                {"mount": "mortar-1"},
            ),
            merge(
                volley.fan("mortar-barge", 3.4, 1, 0, FLAK, 2.9, -MORTAR_DEGS[1]),
                {"mount": "mortar-2"},
            ),
            volley.burst("wheelhouse", 2.6, 3, 0.14, RED, 1.8),
        ],
        [
            [],
            [
                merge(volley.fan("core", 2.6, 3, 0, ORANGE, 0.8), {"mount": "bow-guns"}),
                merge(volley.aimed("core", 2.4, 1, 0, MAGENTA, 1.5), {"mount": "deck-gun"}),
            ],
            [
                merge(volley.fan("core", 2.2, 3, 0, ORANGE, 0.8), {"mount": "bow-guns"}),
                merge(volley.burst("core", 2.8, 3, 0.13, MAGENTA, 1.4), {"mount": "deck-gun"}),
                merge(volley.aimed("core", 3.8, 1, 0, HEAVY_FLAK, 2.2), {"mount": "stern-mortar"}),
            ],
            [
                merge(volley.ring("core", 1.5, 12, 9, ORANGE, 0.5), {"mount": "flak-rotor"}),
                merge(volley.fan("core", 2.6, 3, 0, RED, 1.2), {"mount": "bow-guns"}),
                merge(volley.burst("core", 3.0, 4, 0.12, MAGENTA, 1.8), {"mount": "deck-gun"}),
                merge(volley.aimed("core", 4.2, 1, 0, HEAVY_FLAK, 2.6), {"mount": "stern-mortar"}),
            ],
        ],
    ),
})

# MB-MORTAR-RAFT-05: the right stern outrigger as drawn (a pontoon under a strip of decking,
# lashed along the barge's stern), between its heights; its swing out about the vertical through
# its front inner corner, hinged to the barge's quarter, once its lashings snap (the left one is
# its mirror image).
OUTRIGGER = [[19, 24], [29, 24], [29, 60], [19, 60]]  # type: list[list[float]]
OUTRIGGER_Y = [-0.5, 9.5]  # type: list[float]
OUTRIGGER_TOP = 8.6
OUTRIGGER_PIVOT = [19, 25, 0]  # type: list[float]
OUTRIGGER_SWING = swing(OUTRIGGER_PIVOT, "up", [0, -60])
# Where its rack stands on it, as drawn, and where that is once swung out (MB-MORTAR-RAFT-10).
RACK_ON = [24, 49]
RACK_AT = move_point(OUTRIGGER_SWING, -60, [RACK_ON[0], RACK_ON[1], 0])
RACK_POD = [OUTRIGGER_TOP, OUTRIGGER_TOP + 3]


def _tarp(mount_id: str) -> Any:
    """Return the tarpaulin over the core gun `mount_id` (BOSS-58): it bursts as it comes in use."""
    box = TARPS[mount_id]
    outline = [[box[0], box[2]], [box[1], box[2]], [box[1], box[3]], [box[0], box[3]]]
    return armour_region(mount_id + "-tarp", None, outline, "shell", None, False, mount_id)


# Its transformation (BOSS-45, MB-MORTAR-RAFT-10): once two of its parts are lost, the lashings of
# its stern outriggers snap and they swing out, a rack riding each. Each core gun's tarpaulin bursts
# as the gun first comes into use (BOSS-58, MB-MORTAR-RAFT-09).
MORTAR_RAFT = with_weapons(
    _MORTAR_RAFT,
    [
        hidden_weapon(
            "rack-left", "rack", [-RACK_AT[0], RACK_AT[1]], 7, 760, 1, "orange", 1.0, RACK_POD
        ),
        hidden_weapon(
            "rack-right", "rack", [RACK_AT[0], RACK_AT[1]], 7, 760, 1, "orange", 2.4, RACK_POD
        ),
    ],
    concat(
        moving_region("outrigger", 1, OUTRIGGER, OUTRIGGER_SWING, None, OUTRIGGER_Y),
        [_tarp(mount_id) for mount_id in ["bow-guns", "deck-gun", "stern-mortar", "flak-rotor"]],
    ),
)
