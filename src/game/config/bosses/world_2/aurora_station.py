"""The Aurora Station (P08-R10, 2-3)

The final boss of the Tundra level. Offsets in px from the boss's centre, X right and Y up (its
nose points down, at -Y). The stage patterns are the agent's design (P07-R04): the parts fire the
same while they stand, the core fires something new at every stage, and its last stage (only the
core left) spirals used by no earlier stage. Health values are placeholders for the P08-R11
tuning.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import (
    bullet,
    bursting,
    mirror,
    part,
    stages,
    stats,
    twin,
    volley,
)
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    extra = {} if options == None else options  # noqa: E711
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


RED = bullet("red", 190)
MAGENTA = bullet("magenta", 185)
GREEN = bullet("green", 180)
PURPLE = bullet("purple", 175)
# A cryo shell: slow and big, it bursts into a small ring of blue bullets (P08-R10).
CRYO_SHELL = bursting("purple", 95, 8, [1.3, 8, bullet("blue", 150)])

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The right dish emitter's projector, at the focus of its dish (its laser, on a turret).
AURORA_EMITTER = [[36, -54, 7]]
# The right cryo cannon's barrel tip, as its turret rests (barrel down the screen).
AURORA_CRYO = [[66, -15.36, 9.08]]
# The two hub guns either side of the hangar's spine (the core's aimed shots, bursts, fans).
AURORA_HUB_GUNS = twin(8, -27, 4)
# The emitter collar under the dish's mast (the core's last-stage spirals).
AURORA_COLLAR = [[0, 0, 14]]

# 2-3: a flying research station with green and violet neon and a slowly turning dish on top;
# two dish emitters aim lasers from turrets and two cryo cannons fire shells that burst into
# rings, all four shielding the core; a drone hangar at its nose launches Hornets (P08-R10).
_AURORA_STATION = record(
    {
        "id": "aurora-station",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.spirals(5, "green", "purple"),
        "stats": stats(
            {
                "id": "aurora-station",
                "name": "Aurora Station",
                "size": 5,
                "coreRadius": 22,
                "coreHealth": 3000,
                "points": 13000,
                "groundSpeed": 0.4,
                "coreDrop": 1,
                "parts": [
                    fpart("emitter-left", [-36, -40], 13, 1250),
                    fpart("emitter-right", [36, -40], 13, 1250),
                    fpart("cryo-left", [-66, 4], 15, 1150),
                    fpart("cryo-right", [66, 4], 15, 1150),
                    fpart("hangar", [0, -56], 14, 800, {"shields": False}),
                ],
            }
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 35, "period": 10},
        "bob": {"amplitude": 6, "period": 5},
        # Its dish turns slowly on top (drawn on the model's ring); no part orbits.
        "spinRate": 0.35,
        "launches": [{"from": "hangar", "kind": "hornets", "count": 2, "every": 6.5, "first": 3.5}],
        "guns": {
            "core": {"gun": AURORA_HUB_GUNS, "ring": AURORA_COLLAR},
            "emitter-left": {
                "laser": mirror(AURORA_EMITTER),
                "turret": [-36, -40],
                "turretLaser": True,
            },
            "emitter-right": {
                "laser": AURORA_EMITTER,
                "turret": [36, -40],
                "turretLaser": True,
            },
            "cryo-left": {"gun": mirror(AURORA_CRYO), "turret": [-66, 4]},
            "cryo-right": {"gun": AURORA_CRYO, "turret": [66, 4]},
        },
        "stages": stages(
            [
                # The two projectors turn to aim at the player, one after the other, and hold
                # still while their beam fires.
                volley.laser("emitter-left", 6.5, 1.8, 2),
                volley.laser("emitter-right", 6.5, 1.8, 5.25),
                volley.aimed("cryo-left", 3.6, 1, 0, CRYO_SHELL, 1.4),
                volley.aimed("cryo-right", 3.6, 1, 0, CRYO_SHELL, 3.2),
            ],
            [
                [volley.aimed("core", 3, 1, 0, RED, 1.6)],
                [volley.aimed("core", 2.6, 3, 12, RED, 0.8)],
                [volley.burst("core", 2.4, 4, 0.14, RED, 0.6)],
                [volley.fan("core", 2.4, 5, 14, MAGENTA, 0.6)],
                [
                    volley.fan("core", 2.2, 7, 12, MAGENTA, 0.6),
                    volley.aimed("core", 2.6, 1, 0, RED, 1.2),
                ],
                [
                    volley.ring("core", 0.5, 5, 14, GREEN, 0.4),
                    volley.ring("core", 0.5, 5, -19, PURPLE, 0.65),
                ],
            ],
        ),
    }
)

# Its hidden weapons (boss transformations, D-224): at transformation 1 its flank armour bursts off,
# baring a dark metal frame, and a pair of missile racks unfold; at transformation 2 its spine
# plating bursts off, baring a dark metal frame, and a pair of gatling turrets unfold.
AURORA_STATION = with_weapons(
    _AURORA_STATION,
    [
        hidden_weapon("rack-left", "rack", [-47, 35], 11, 1000, 1, "purple", 1.2, 6.0),
        hidden_weapon("rack-right", "rack", [47, 35], 11, 1000, 1, "purple", 2.0, 6.0),
        hidden_weapon("gatling-left", "gatling", [-7, -21], 5, 1250, 2, "purple", 1.2, 9.6),
        hidden_weapon("gatling-right", "gatling", [7, -21], 5, 1250, 2, "purple", 2.0, 9.6),
    ],
    [
        armour_region("flanks", 1, [[28, 2], [86.5, 2], [86.5, 58], [28, 58]], "wing"),
        armour_region("spine", 2, [[-20, -46], [20, -46], [20, 4], [-20, 4]], "shell", None, False),
    ],
)
