"""P10-R11, 4-4: the Furnace Drake, the mini boss of the forge belt ().

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Its two wings
beat on their joints (D-061) and shield the core, each firing fans from the gun pod under it; its
head sways on its neck and breathes a short flame of dense bullets at the player from its jaw. The
stage patterns are the agent's design (P07-R04): the parts fire the same while they stand, the core
fires a spiral that changes at every stage, and twin spirals of its own, used by no earlier stage,
once it stands alone. Health tuned for P10-R12.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

RED = bullet("red", 215)
ORANGE = bullet("orange", 210)
PURPLE = bullet("purple", 205)
# The flame's sparks: small, fast and close together.
FLAME = bullet("orange", 240, 3)
FLAME_EDGE = bullet("red", 215, 3)

# Where the left wing (at -X) turns at its root and where its gun pod sits (mirrored on the right).
DRAKE_WING = record({"root": [-12, 2], "pod": [-40, 2]})
# Where the neck turns, and where the head (the jaw) is.
DRAKE_NECK = [0, -18]
DRAKE_JAW = [0, -38]
# Where the tail turns at the hips (a limb drawn on the core, not a part).
DRAKE_TAIL = [0, 20]

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.

# The left wing pod's twin fan barrels, under the wing's leading edge (mirrored on the right).
DRAKE_WING_GUNS = twin(-40, -13, 2, 2.6)
# The flame nozzle in the drake's open jaw.
DRAKE_MAW = [[0, -57, 4]]
# The furnace heart on its back, its grate open to the sky (the core's spirals).
DRAKE_HEART = [[0, 4, 14]]

# How the wings beat (D-061): a wide, slow stroke, the two together, as a bird's.
BEAT = record({"amplitudeDeg": 13, "period": 1.3, "phase": 0})
# How the head sways on its neck, and the tail at the hips (out of step with each other).
SWAY = record({"amplitudeDeg": 9, "period": 3.4, "phase": 0.1})
LASH = record({"amplitudeDeg": 12, "period": 2.6, "phase": 0.6})


def wing_joint(side: str) -> Any:
    """A wing's joint at its root, the left one at -X; the right one mirrors it."""
    s = 1 if side == "left" else -1
    x = DRAKE_WING.root[0]
    y = DRAKE_WING.root[1]
    joints: dict[str, Any] = {}
    joints["wing-" + side] = {
        "x": s * x,
        "y": y,
        "swing": merge(BEAT, {"amplitudeDeg": s * BEAT.amplitudeDeg}),
    }
    return joints


POD_X = DRAKE_WING.pod[0]
POD_Y = DRAKE_WING.pod[1]


def flame(first: float) -> Any:
    """The jaw's flame: a stream of sparks at the player, a spray of slower ones around it."""
    return [
        volley.burst("jaw", 3.2, 9, 0.045, FLAME, first),
        volley.aimed("jaw", 3.2, 4, 9, FLAME_EDGE, first + 0.2),
    ]


# 4-4: a dragon-shaped gunship of soot-black plates with red and orange neon and a furnace glowing
# in its chest (P10-R11); its two beating wings fire fans and shield the core, its jaw breathes
# flame, its core spirals. The head hangs in front of the core, so it can always be shot.
FURNACE_DRAKE = record(
    {
        "id": "furnace-drake",
        # Angry after each destroyed part (phase 7 review, D-063): heat 12.5, on from World 3.
        "rage": rage.flower(12.5, "orange", "red"),
        "stats": stats(
            record(
                {
                    "id": "furnace-drake",
                    "name": "Furnace Drake",
                    "size": 3.5,
                    "coreRadius": 16,
                    "coreHealth": 2150,
                    "points": 8500,
                    "groundSpeed": 0.5,
                    "parts": [
                        part("wing-left", [POD_X, POD_Y], 14, 1100, {"joint": "wing-left"}),
                        part("wing-right", [-POD_X, POD_Y], 14, 1100, {"joint": "wing-right"}),
                        part("jaw", list(DRAKE_JAW), 11, 800, {"shields": False, "joint": "neck"}),
                    ],
                    "joints": merge(
                        merge(wing_joint("left"), wing_joint("right")),
                        {
                            "neck": {"x": DRAKE_NECK[0], "y": DRAKE_NECK[1], "swing": SWAY},
                            "tail": {"x": DRAKE_TAIL[0], "y": DRAKE_TAIL[1], "swing": LASH},
                        },
                    ),
                }
            )
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 60, "period": 6.4},
        "bob": {"amplitude": 8, "period": 2.9},
        "guns": {
            "core": {"ring": DRAKE_HEART},
            "wing-left": {"gun": DRAKE_WING_GUNS},
            "wing-right": {"gun": mirror(DRAKE_WING_GUNS)},
            "jaw": {"gun": DRAKE_MAW},
        },
        "stages": stages(
            concat(
                [
                    # The wings' fans lean outwards, one after the other, on each down stroke.
                    volley.fan("wing-left", 2.4, 3, 14, RED, 0.9, -12),
                    volley.fan("wing-right", 2.4, 3, 14, RED, 2.1, 12),
                ],
                flame(1.6),
            ),
            [
                [volley.ring("core", 0.5, 3, 17, ORANGE, 0.6)],
                [volley.ring("core", 0.48, 4, -21, ORANGE, 0.5)],
                [volley.ring("core", 0.46, 5, 25, PURPLE, 0.5)],
                [
                    volley.ring("core", 0.44, 5, 14, ORANGE, 0.4),
                    volley.ring("core", 0.44, 6, -16, RED, 0.62),
                ],
            ],
        ),
    }
)
