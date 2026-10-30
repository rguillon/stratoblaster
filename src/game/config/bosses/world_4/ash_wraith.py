"""P10-R11, 4-2: the Ash Wraith, the mini boss of the Ash plains level, a chase over the plains
(ported from `config/bosses/world-4/ash-wraith.ts`).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). The stage
patterns are the agent's design (P07-R04): the parts fire the same while they stand, the core
spirals in a new way at every stage, and its last stage (only the core left) twin spirals used by
no earlier stage. Health tuned with the D-055 bot for P10-R12 (fight 43.75-53.75 s, full health
3 800-4 200).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")

__pragma__("noskip")

BLUE = bullet("blue", 205)
PURPLE = bullet("purple", 200)
MAGENTA = bullet("magenta", 210)

# Where its parts sit: the right shroud pod (the left one mirrors it) and the eye cannon.
WRAITH_POD = [36, 6]
WRAITH_EYE = [0, -32]

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turret at rest.

# The right shroud pod's two fan barrels, under the front lip of its shroud.
WRAITH_POD_GUNS = twin(WRAITH_POD[0], -8.2, 2, 2.6)
# The eye cannon's lens, at the front of its barrel (on its turret): the laser leaves there.
WRAITH_EYE_LENS = [[0, -47.4, 5]]
# The ash vent on its back, behind the canopy: the core's spirals leave from there.
WRAITH_VENT = [[0, 8, 14]]

PX = WRAITH_POD[0]
PY = WRAITH_POD[1]
EX = WRAITH_EYE[0]
EY = WRAITH_EYE[1]

# 4-2: a ragged, grey stealth gunship trailing ash, pale cyan neon (P10-R11). Its two shroud pods
# (ducted fans) fire fans and shield the core; the eye cannon under its nose, on a turret, aims a
# laser after its warning line; the core spirals. The eye hangs in front of the core, so it can
# always be shot.
ASH_WRAITH = record(
    {
        "id": "ash-wraith",
        # Angry after each destroyed part (phase 7 review, D-063): heat 9, as 3-5.
        "rage": rage.vortex(10.5, "blue", "purple"),
        "stats": stats(
            record(
                {
                    "id": "ash-wraith",
                    "name": "Ash Wraith",
                    "size": 3,
                    "coreRadius": 17,
                    "coreHealth": 1860,
                    "points": 7000,
                    "groundSpeed": 1.5,
                    "parts": [
                        part("pod-left", [-PX, PY], 13, 820),
                        part("pod-right", [PX, PY], 13, 820),
                        part("eye", [EX, EY], 12, 680, {"shields": False}),
                    ],
                }
            )
        ),
        "stopFraction": 0.73,
        "sway": {"amplitude": 60, "period": 6.5},
        "bob": {"amplitude": 8, "period": 3.4},
        "guns": {
            "core": {"ring": WRAITH_VENT},
            "pod-left": {"gun": mirror(WRAITH_POD_GUNS)},
            "pod-right": {"gun": WRAITH_POD_GUNS},
            "eye": {"laser": WRAITH_EYE_LENS, "turret": [EX, EY], "turretLaser": True},
        },
        "stages": stages(
            [
                # The pods' fans lean outwards, sweeping the ash plains on either side of the ship.
                volley.fan("pod-left", 2.4, 3, 14, BLUE, 0.9, -8),
                volley.fan("pod-right", 2.4, 3, 14, BLUE, 2.1, 8),
                volley.laser("eye", 6, 1.4, 3),
            ],
            [
                [volley.ring("core", 0.6, 3, 19, PURPLE, 0.6)],
                [volley.ring("core", 0.55, 4, -23, PURPLE, 0.5)],
                [volley.ring("core", 0.8, 6, 11, MAGENTA, 0.5)],
                [
                    volley.ring("core", 0.45, 5, 14, PURPLE, 0.4),
                    volley.ring("core", 0.45, 5, -17, BLUE, 0.62),
                ],
            ],
        ),
    }
)
