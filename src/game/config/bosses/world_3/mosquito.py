"""P09-R09, 3-4: the Mosquito, the mini boss of the swamp works ().

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Its two wings
buzz on their joints (D-061: a fast, small swing) and shield the core; its proboscis aims a laser
from a turret (D-073). The stage patterns are the agent's design (P07-R04): the parts fire the same
while they stand, the core fires aimed bursts that change at every stage, and its last stage (only
the core left) a ring used by no earlier stage. Health tuned for P09-R10.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

RED = bullet("red", 205)
MAGENTA = bullet("magenta", 200)
PURPLE = bullet("purple", 210)
BLUE = bullet("blue", 195)

# Where the left wing (at -X) turns at its root and where its fan pod sits (mirrored on the right).
MOSQUITO_WING = record({"root": [-11, 4], "pod": [-35, 2]})
# The proboscis: its socket under the head, where its turret turns.
MOSQUITO_PROBOSCIS = [0, -32]

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.

# The left wing pod's two fan barrels, on the wing's leading edge (mirrored on the right).
MOSQUITO_WING_GUNS = twin(-35, -9, 2, 2.4)
# The needle's tip, as its turret rests (pointing down the screen): its laser leaves from it.
MOSQUITO_NEEDLE = [[0, -53, 3]]
# The twin mandible guns either side of the head (the core's aimed bursts).
MOSQUITO_MANDIBLES = twin(6.5, -28, 2)
# The glowing blood sac on its back (the core's last-stage rings).
MOSQUITO_SAC = [[0, 16, 10]]

# How the wings buzz (D-061): a few degrees, five times a second, the two beating together.
BUZZ = record({"amplitudeDeg": 7, "period": 0.2, "phase": 0.2})


def wing_joint(side: str) -> Any:
    """A wing's joint at its root, the left one at -X; the right one mirrors it."""
    s = 1 if side == "left" else -1
    x = MOSQUITO_WING.root[0]
    y = MOSQUITO_WING.root[1]
    joints: dict[str, Any] = {}
    joints["wing-" + side] = {
        "x": s * x,
        "y": y,
        "swing": merge(BUZZ, {"amplitudeDeg": s * BUZZ.amplitudeDeg}),
    }
    return joints


POD_X = MOSQUITO_WING.pod[0]
POD_Y = MOSQUITO_WING.pod[1]

# 3-4: a thin, fast bio-drone with pink neon; its two buzzing wings fire fans and shield the core,
# its proboscis turns to aim a laser after its warning line (P09-R09). The proboscis hangs in
# front of the core, so it can always be shot.
MOSQUITO = record(
    {
        "id": "mosquito",
        # Angry after each destroyed part (phase 7 review, D-063).
        "rage": rage.vortex(7.5, "magenta", "purple"),
        "stats": stats(
            record(
                {
                    "id": "mosquito",
                    "name": "Mosquito",
                    "size": 3,
                    "coreRadius": 16,
                    "coreHealth": 1750,
                    "points": 7500,
                    "groundSpeed": 0.6,
                    "parts": [
                        part("wing-left", [POD_X, POD_Y], 13, 1000, {"joint": "wing-left"}),
                        part("wing-right", [-POD_X, POD_Y], 13, 1000, {"joint": "wing-right"}),
                        part("proboscis", list(MOSQUITO_PROBOSCIS), 10, 750, {"shields": False}),
                    ],
                    "joints": merge(wing_joint("left"), wing_joint("right")),
                }
            )
        ),
        "stopFraction": 0.74,
        # Fast: it darts from side to side.
        "sway": {"amplitude": 72, "period": 5.6},
        "bob": {"amplitude": 10, "period": 2.6},
        "guns": {
            "core": {"gun": MOSQUITO_MANDIBLES, "ring": MOSQUITO_SAC},
            "wing-left": {"gun": MOSQUITO_WING_GUNS},
            "wing-right": {"gun": mirror(MOSQUITO_WING_GUNS)},
            "proboscis": {
                "laser": MOSQUITO_NEEDLE,
                "turret": list(MOSQUITO_PROBOSCIS),
                "turretLaser": True,
            },
        },
        "stages": stages(
            [
                # The wings' fans cross under the drone, each leaning towards the other side.
                volley.fan("wing-left", 2.2, 3, 14, MAGENTA, 0.9, 10),
                volley.fan("wing-right", 2.2, 3, 14, MAGENTA, 2, -10),
                volley.laser("proboscis", 5.5, 1.4, 3),
            ],
            [
                [volley.burst("core", 2.6, 3, 0.14, RED, 1.4)],
                [volley.burst("core", 2.3, 4, 0.12, RED, 0.8)],
                [
                    volley.burst("core", 2.2, 5, 0.11, PURPLE, 0.6),
                    volley.aimed("core", 2.8, 3, 12, RED, 1.6),
                ],
                [
                    volley.ring("core", 1.4, 12, 8, BLUE, 0.4),
                    volley.burst("core", 2.4, 3, 0.12, RED, 1),
                ],
            ],
        ),
    }
)
