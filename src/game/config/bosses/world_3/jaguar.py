"""P09-R09, 3-5's mini boss: the Jaguar (ported from `config/bosses/world-3/jaguar.ts`).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Stage
patterns as for the World 1 and 2 mini bosses (P07-R04, D-055): its claw guns fire aimed spreads
and its tail cannon a laser while they stand, the core fires a spiral that changes at every stage,
and twin spirals of its own, used by no earlier stage, once it stands alone.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")

__pragma__("noskip")

ORANGE = bullet("orange", 205)
RED = bullet("red", 200)
PURPLE = bullet("purple", 195)

# Where its parts stand: the claw guns at the front of the wing roots, the tail cannon aft.
JAGUAR_PARTS = record({"claw": [34, -22], "tail": [-30, 42]})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turrets at rest.

# The right claw gun's twin barrels, reaching forward between its talons.
JAGUAR_CLAW = twin(JAGUAR_PARTS.claw[0], -42, 6, 2.6)
# The tail cannon's lens, at the front of its barrel held high over the spine.
JAGUAR_TAIL = [[JAGUAR_PARTS.tail[0], 18, 17]]
# The core's twin fang guns, under the nose.
JAGUAR_FANGS = twin(4.5, -55, 3)
# The core's spiral emitter, the lit eye on its back behind the cockpit.
JAGUAR_EYE = [0, -6, 13]

KX = JAGUAR_PARTS.claw[0]
KY = JAGUAR_PARTS.claw[1]
TX = JAGUAR_PARTS.tail[0]
TY = JAGUAR_PARTS.tail[1]

# 3-5: a sleek stealth interceptor with spotted armour and amber neon (P09-R09); two claw guns on
# turrets shield the core, a tail cannon aims a laser, and the core fires spirals.
JAGUAR = record(
    {
        "id": "jaguar",
        # Angry after each destroyed part (phase 7 review): the hottest mini boss so far.
        "rage": rage.curtain(8.5, "orange", "red"),
        "stats": stats(
            record(
                {
                    "id": "jaguar",
                    "name": "Jaguar",
                    "size": 3.5,
                    "coreRadius": 20,
                    "coreHealth": 2000,
                    "points": 8000,
                    "groundSpeed": 0.6,
                    "parts": [
                        part("claw-left", [-KX, KY], 15, 1100),
                        part("claw-right", [KX, KY], 15, 1100),
                        part("tail-cannon", [TX, TY], 14, 900, {"shields": False}),
                    ],
                }
            )
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 60, "period": 6},
        "bob": {"amplitude": 8, "period": 3},
        "guns": {
            "core": {"gun": JAGUAR_FANGS, "ring": [JAGUAR_EYE]},
            "claw-left": {"gun": mirror(JAGUAR_CLAW), "turret": [-KX, KY]},
            "claw-right": {"gun": JAGUAR_CLAW, "turret": [KX, KY]},
            "tail-cannon": {"laser": JAGUAR_TAIL, "turret": [TX, TY], "turretLaser": True},
        },
        "stages": stages(
            [
                volley.aimed("claw-left", 2.1, 3, 11, ORANGE, 1),
                volley.aimed("claw-right", 2.1, 3, 11, ORANGE, 2.05),
                volley.laser("tail-cannon", 6, 1.4, 3),
            ],
            [
                [volley.ring("core", 0.55, 3, 17, RED, 0.6)],
                [volley.ring("core", 0.5, 4, -21, RED, 0.5)],
                [volley.ring("core", 0.5, 5, 25, PURPLE, 0.5)],
                [
                    volley.ring("core", 0.45, 5, 13, RED, 0.4),
                    volley.ring("core", 0.45, 5, -15, PURPLE, 0.62),
                ],
            ],
        ),
    }
)
