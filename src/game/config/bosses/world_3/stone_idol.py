# Copyright (c) 2026 Renaud Guillon
"""3-3.

The Stone Idol, the mini boss of the Lost temples level (specs/bosses/mini/3-3-stone-idol.md).

Offsets in px from the boss's centre, X right and Y up (its chin points down, at -Y). The stage
patterns are the agent's design (MB-STONE-IDOL-09): the eyes and the mouth fire the same while they
stand, the core fires something new at every stage, and its last stage (only the core left) a spiral
used by no earlier stage. Health (MB-STONE-IDOL-07) tuned for WLD-3-20 with the D-055 bot.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")

__pragma__("noskip")

MAGENTA = bullet("magenta", 205)
ORANGE = bullet("orange", 210)
PURPLE = bullet("purple", 200)
# The mouth's boulders (MB-STONE-IDOL-08): slow and big.
BOULDER = bullet("purple", 115, 9)

# Where its parts stand (MB-STONE-IDOL-07): the eyes either side of the nose, the mouth under it.
IDOL_PARTS = record({"eye": [32, -4], "mouth": [0, -34]})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The right eye's lens, at the front of its eyeball as it rests (its laser, on a turret).
IDOL_EYE = [[32, -11.5, 12]]
# The two nostrils, under the nose's tip (the core's fans).
IDOL_NOSTRILS = twin(4, -21, 14.5)
# The throat, deep in the open mouth (the mouth's rings of boulders).
IDOL_THROAT = [[0, -35, 12.8]]
# The jewel set in the forehead (the core's last-stage spiral).
IDOL_JEWEL = [[0, 27, 19]]

EX = IDOL_PARTS.eye[0]
EY = IDOL_PARTS.eye[1]

# 3-3: a flying stone head with neon cracks, glowing eyes and mouth; its two eyes turn to aim
# lasers and shield the core, its mouth spits rings of slow boulders (MB-STONE-IDOL-08). The ground
# stops over the temple while it fights (x0).
_STONE_IDOL = record({
    "id": "stone-idol",
    # Angry after each destroyed part (phase 7 review, MB-STONE-IDOL-10).
    "rage": rage.flower(6.5, "magenta", "orange"),
    # Its core and parts, and its points (MB-STONE-IDOL-13).
    "stats": stats(
        record({
            "id": "stone-idol",
            "name": "Stone Idol",
            "size": 3,
            "coreRadius": 22,
            "coreHealth": 1550,
            "points": 7500,
            "groundSpeed": 0,
            "parts": [
                part("eye-left", [-EX, EY], 13, 950),
                part("eye-right", [EX, EY], 13, 950),
                part("mouth", list(IDOL_PARTS.mouth), 13, 750, {"shields": False}),
            ],
        })
    ),
    # Where it stops and how it moves in place, the ground stopped (MB-STONE-IDOL-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 60, "period": 7.5},
    "bob": {"amplitude": 8, "period": 3.6},
    "guns": {
        "core": {"gun": IDOL_NOSTRILS, "ring": IDOL_JEWEL},
        # The eyeballs turn to aim at the player during the warning line, and hold still while
        # their beam fires (D-073).
        "eye-left": {"laser": mirror(IDOL_EYE), "turret": [-EX, EY], "turretLaser": True},
        "eye-right": {"laser": IDOL_EYE, "turret": [EX, EY], "turretLaser": True},
        "mouth": {"ring": IDOL_THROAT},
    },
    # The parts' volleys, then the core's pattern per stage (MB-STONE-IDOL-09).
    "stages": stages(
        [
            volley.laser("eye-left", 6.5, 1.5, 2),
            volley.laser("eye-right", 6.5, 1.5, 5.25),
            volley.ring("mouth", 3, 9, 20, BOULDER, 1.4),
        ],
        [
            [volley.fan("core", 2.6, 3, 16, MAGENTA, 1.2)],
            [volley.fan("core", 2.4, 5, 13, MAGENTA, 0.8)],
            [
                volley.fan("core", 2.6, 5, 12, ORANGE, 0.6, -18),
                volley.fan("core", 2.6, 5, 12, ORANGE, 1.9, 18),
            ],
            [
                volley.ring("core", 0.45, 5, 17, PURPLE, 0.3),
                volley.fan("core", 2.2, 7, 11, MAGENTA, 1),
            ],
        ],
    ),
})

# Its transformation (D-230, MB-STONE-IDOL-11): the back of its head flips up and back on a hinge
# across its crown, like a lid, showing a dark metal ring round a great sweeper eye between two
# mortars (MB-STONE-IDOL-12).
STONE_IDOL = with_weapons(
    _STONE_IDOL,
    [
        hidden_weapon("third-eye", "sweeper", [0, 24], 13, 760, 1, "purple", 1.6, 12),
        hidden_weapon("mortar-left", "mortar", [-30, 30], 8, 760, 1, "purple", 1.2, 13),
        hidden_weapon("mortar-right", "mortar", [30, 30], 8, 760, 1, "purple", 2.6, 13),
    ],
    moving_region(
        "crown",
        1,
        [[-54, 4], [54, 4], [54, 56], [-54, 56]],
        swing([0, 50, 7], "across", [0, -75]),
        "ring",
        [7, 1000],
        False,
    ),
)
