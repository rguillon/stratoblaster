"""P09-R09, 3-2: the Toucan, the mini boss of the Rainforest level ().

Offsets in px from the boss's centre, X right and Y up (its nose, the beak, points down, at -Y).
The stage patterns are the agent's design (P07-R04): the parts fire the same while they stand, the
core fires something new at every stage, and its last stage (only the core left) a spiral used by
no earlier stage. Health tuned with the D-055 bot for P09-R10 (fight 38.75-48.75 s, full health
3 550-3 900).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")

__pragma__("noskip")

ORANGE = bullet("orange", 195)
RED = bullet("red", 205)
MAGENTA = bullet("magenta", 210)
PURPLE = bullet("purple", 200)

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The beak cannon's emitter, at the tip of the beak: its laser leaves from there.
TOUCAN_BEAK_TIP = [[0, -55.6, 5]]
# The right wing pod's two fan barrels, under the front of its fan duct.
TOUCAN_POD_GUNS = twin(38, -11.4, 2, 2.6)
# The two cheek guns either side of the beak's root (the core's aimed bursts).
TOUCAN_CHEEK_GUNS = twin(11, -24.4, 3.5)
# The crest emitter on its head (the core's last-stage spiral).
TOUCAN_CREST = [[0, -6, 17]]

# 3-2: a stubby gunship with a huge bright beak, yellow and orange neon (P09-R09). Its beak cannon
# fires a laser after its warning line, two wing pods fire fans and shield the core. The beak
# hangs in front of the core, so it can always be shot.
TOUCAN = record(
    {
        "id": "toucan",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.curtain(5.5, "orange", "red"),
        "stats": stats(
            record(
                {
                    "id": "toucan",
                    "name": "Toucan",
                    "size": 3,
                    "coreRadius": 17,
                    "coreHealth": 1640,
                    "points": 6000,
                    "groundSpeed": 0.6,
                    "parts": [
                        part("pod-left", [-38, 2], 13, 780),
                        part("pod-right", [38, 2], 13, 780),
                        part("beak", [0, -38], 12, 580, {"shields": False}),
                    ],
                }
            )
        ),
        "stopFraction": 0.73,
        "sway": {"amplitude": 60, "period": 7},
        "bob": {"amplitude": 8, "period": 3.6},
        "guns": {
            "core": {"gun": TOUCAN_CHEEK_GUNS, "ring": TOUCAN_CREST},
            "pod-left": {"gun": mirror(TOUCAN_POD_GUNS)},
            "pod-right": {"gun": TOUCAN_POD_GUNS},
            "beak": {"laser": TOUCAN_BEAK_TIP},
        },
        "stages": stages(
            [
                # The pods' fans cross under the gunship, each leaning towards the other side.
                volley.fan("pod-left", 2.4, 3, 14, ORANGE, 0.9, 10),
                volley.fan("pod-right", 2.4, 3, 14, ORANGE, 2.1, -10),
                volley.laser("beak", 6, 1.4, 3),
            ],
            [
                [volley.burst("core", 2.8, 3, 0.15, RED, 1.4)],
                [volley.burst("core", 2.5, 4, 0.13, RED, 0.8)],
                [
                    volley.burst("core", 2.6, 4, 0.12, RED, 0.6),
                    volley.aimed("core", 2.6, 3, 12, MAGENTA, 1.9),
                ],
                [
                    volley.ring("core", 1.3, 12, 11, PURPLE, 0.4),
                    volley.burst("core", 2.4, 3, 0.14, RED, 1),
                ],
            ],
        ),
    }
)
