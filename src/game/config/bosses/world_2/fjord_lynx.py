"""The Fjord Lynx (2-2's mini boss, specs/bosses/mini/2-2-fjord-lynx.md)

The mini boss of the Fjords. Offsets in px from the boss's centre, X right and Y up (its nose
points down, at -Y). Its radar mast aims its guns (MB-FJORD-LYNX-09): while the mast stands, the
paws and the core fire at the player; once it is destroyed, they fire fans at preset headings
instead (`only_while` / `only_after`).
"""

from game.config.bosses.boss_kit import (
    bullet,
    mirror,
    only_after,
    only_while,
    part,
    stages,
    stats,
    volley,
)
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import record

BLUE = bullet("blue", 185)
MAGENTA = bullet("magenta", 190)
PURPLE = bullet("purple", 175)

# The part whose loss blinds the guns.
RADAR = "radar-mast"

# The left paw's centre (the right one mirrors it).
PAW = [-30, -26]

# The guns' muzzles (phase 7 review, MB-FJORD-LYNX-03): the tips of the barrels its model draws,
# from the boss's centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at
# rest.

# The right paw cannon's two barrels.
PAW_CANNON = [
    [31.8, -39.12, 5.74],
    [28.2, -39.12, 5.74],
]
# The chin cannon's barrel, under the head.
CHIN = [[0, -41.64, 6.68]]

# 2-2: a fast, low gunship crouched like a lynx, two forward paws and tufted antennas, white and
# cyan neon. Both paw cannons (MB-FJORD-LYNX-08) and the radar mast shield the core.
_FJORD_LYNX = record(
    {
        "id": "fjord-lynx",
        # Angry after each destroyed part (phase 7 review, MB-FJORD-LYNX-11).
        "rage": rage.vortex(3.5, "blue", "magenta"),
        # Its core, paws, radar mast and points (MB-FJORD-LYNX-13).
        "stats": stats(
            {
                "id": "fjord-lynx",
                "name": "Fjord Lynx",
                "size": 3,
                "coreRadius": 18,
                "coreHealth": 1080,
                "points": 3500,
                "groundSpeed": 0.6,
                "parts": [
                    part("paw-left", PAW, 13, 600),
                    part("paw-right", [-PAW[0], PAW[1]], 13, 600),
                    part(RADAR, [-25, 22], 11, 600),
                ],
            }
        ),
        # Where it stops and how it moves in place (MB-FJORD-LYNX-07).
        "stopFraction": 0.72,
        "sway": {"amplitude": 75, "period": 6},
        "bob": {"amplitude": 8, "period": 3},
        "guns": {
            "core": {"gun": CHIN, "turret": [0, -30]},
            "paw-left": {"gun": mirror(PAW_CANNON), "turret": PAW},
            "paw-right": {"gun": PAW_CANNON, "turret": [-PAW[0], PAW[1]]},
        },
        # The paws' volleys, then the core's pattern per stage (MB-FJORD-LYNX-10).
        "stages": stages(
            [
                # Aimed spreads while the radar stands, then fans crossing in front of the nose.
                only_while(volley.aimed("paw-left", 2.2, 3, 10, BLUE, 1), RADAR),
                only_while(volley.aimed("paw-right", 2.2, 3, 10, BLUE, 2.1), RADAR),
                only_after(volley.fan("paw-left", 2.2, 3, 12, BLUE, 1, 18), RADAR),
                only_after(volley.fan("paw-right", 2.2, 3, 12, BLUE, 2.1, -18), RADAR),
            ],
            [
                [only_while(volley.aimed("core", 3, 1, 0, MAGENTA, 1.5), RADAR)],
                [
                    only_while(volley.aimed("core", 2.6, 3, 12, MAGENTA, 0.8), RADAR),
                    only_after(volley.fan("core", 2.6, 3, 16, MAGENTA, 0.8), RADAR),
                ],
                [
                    only_while(volley.burst("core", 2.4, 4, 0.14, MAGENTA, 0.6), RADAR),
                    only_after(volley.fan("core", 2.2, 5, 14, MAGENTA, 0.6), RADAR),
                ],
                [
                    volley.fan("core", 2.4, 7, 12, MAGENTA, 0.6),
                    volley.ring("core", 1.6, 12, 9, PURPLE, 0.4),
                ],
            ],
        ),
    }
)

# Its hidden weapons (boss transformations, D-224, MB-FJORD-LYNX-12): at transformation 1 its back
# plating bursts off, baring a dark metal frame (MB-FJORD-LYNX-06), and a pair of ring emitters
# unfold.
FJORD_LYNX = with_weapons(
    _FJORD_LYNX,
    [
        hidden_weapon("orb-left", "orb", [-7, -35], 5, 480, 1, "blue", 1.2, 7.2),
        hidden_weapon("orb-right", "orb", [7, -35], 5, 480, 1, "blue", 2.0, 7.2),
    ],
    [
        armour_region(
            "back", 1, [[-20, -48], [20, -48], [20, -10], [-20, -10]], "shell", [7.5, 1000], False
        ),
    ],
)
