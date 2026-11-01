"""The Narwhal (2-1's final boss, specs/bosses/final/2-1-narwhal.md)

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Stage
patterns as for the World 1 bosses (FB-NARWHAL-11): the parts fire the same while they stand, the
core fires something new at every stage, and its last stage (only the core left) spirals used by no
earlier stage. Its core always drops a bonus (FB-NARWHAL-15). Health values (FB-NARWHAL-15) are
placeholders for the World 2 tuning (WLD-2-25, WLD-2-27).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402 (after the Transcrypt skip block, ENG-153)

__pragma__("noskip")


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (FB-NARWHAL-15, `part_drop_chance`)."""
    extra = {} if options == None else options  # noqa: E711 (absent value is undefined in the browser, ENG-161)
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


MAGENTA = bullet("magenta", 185)
GREEN = bullet("green", 180)
BLUE = bullet("blue", 190)
PURPLE = bullet("purple", 195)

# The guns' muzzles (phase 7 review, FB-NARWHAL-03): the tips of the barrels its model draws, from
# the boss's centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The tip of the spiral horn, where the lance's laser leaves from.
NARWHAL_HORN = [[0, -90, 4.5]]
# The right torpedo tube's two mouths, on the hull's flank.
NARWHAL_TUBE = twin(22, -47.02, 5, 2.5)
# The right ballast pod's two fan guns, at its front.
NARWHAL_POD = twin(40, -5.68, 6, 2.5)
# The deck gun's two barrels, on the forward deck (the core's aimed shots, bursts and fans).
NARWHAL_DECK_GUN = twin(1.33, -43.77, 18.42)
# The spiral emitter on top of the sail (the core's last-stage spirals).
NARWHAL_EMITTER = [[0, -10, 31]]

# 2-1: a long flying submarine with a spiral horn and teal neon along its back. Its horn lance
# fires a laser (FB-NARWHAL-08), two torpedo tubes homing missiles (FB-NARWHAL-09), and two ballast
# pods fans; the ballast pods shield the core (FB-NARWHAL-10). It chases the ground over the ice
# floes (×1.5).
_NARWHAL = record(
    {
        "id": "narwhal",
        # Angry after each destroyed part (phase 7 review, FB-NARWHAL-12).
        "rage": rage.vortex(3, "magenta", "blue"),
        "stats": stats(
            {
                "id": "narwhal",
                "name": "Narwhal",
                "size": 5,
                "coreRadius": 22,
                "coreHealth": 2300,
                "points": 16000,
                "groundSpeed": 1.5,
                "coreDrop": 1,
                "parts": [
                    fpart("lance", [0, -70], 13, 1100, {"shields": False}),
                    fpart("tube-left", [-22, -32], 10, 650, {"shields": False}),
                    fpart("tube-right", [22, -32], 10, 650, {"shields": False}),
                    fpart("pod-left", [-40, 18], 14, 900),
                    fpart("pod-right", [40, 18], 14, 900),
                ],
            }
        ),
        # Where it stops and how it moves in place; its ground speed is a chase (FB-NARWHAL-07).
        "stopFraction": 0.74,
        "sway": {"amplitude": 45, "period": 8},
        "bob": {"amplitude": 10, "period": 4},
        "guns": {
            "core": {"gun": NARWHAL_DECK_GUN, "turret": [0, -32], "ring": NARWHAL_EMITTER},
            "lance": {"laser": NARWHAL_HORN},
            "tube-left": {"missile": mirror(NARWHAL_TUBE)},
            "tube-right": {"missile": NARWHAL_TUBE},
            "pod-left": {"gun": mirror(NARWHAL_POD)},
            "pod-right": {"gun": NARWHAL_POD},
        },
        # The parts' volleys, then the core's pattern per stage (FB-NARWHAL-11).
        "stages": stages(
            [
                volley.laser("lance", 6.5, 1.4, 2.5),
                volley.missiles("tube-left", 5.5, 2, 30, 3.5),
                volley.missiles("tube-right", 5.5, 2, 30, 6.25),
                volley.fan("pod-left", 2.2, 3, 15, GREEN, 0.8, -12),
                volley.fan("pod-right", 2.2, 3, 15, GREEN, 1.9, 12),
            ],
            [
                [volley.aimed("core", 3, 1, 0, MAGENTA, 1.6)],
                [volley.aimed("core", 2.6, 3, 12, MAGENTA, 0.8)],
                [volley.burst("core", 2.4, 4, 0.14, MAGENTA, 0.6)],
                [volley.fan("core", 2.4, 5, 14, MAGENTA, 0.6)],
                [
                    volley.fan("core", 2.2, 7, 12, MAGENTA, 0.6),
                    volley.aimed("core", 2.6, 1, 0, PURPLE, 1.2),
                ],
                [
                    volley.ring("core", 1.2, 10, 13, BLUE, 0.4),
                    volley.ring("core", 1.2, 10, -17, PURPLE, 1),
                ],
            ],
        ),
    }
)

# Its hidden weapons (boss transformations, D-224): at transformation 1 its back plating bursts off,
# baring a dark metal frame, and a pair of laser lances unfold (FB-NARWHAL-13); at transformation 2
# its spine plating bursts off, baring a dark metal frame, and a pair of missile racks unfold
# (FB-NARWHAL-14). The regions it sheds: FB-NARWHAL-06.
NARWHAL = with_weapons(
    _NARWHAL,
    [
        hidden_weapon("lance-left", "lance", [-12, 11], 10, 880, 1, "green", 1.2, 21.1),
        hidden_weapon("lance-right", "lance", [12, 11], 10, 880, 1, "green", 2.0, 21.1),
        hidden_weapon("rack-left", "rack", [-9, -13], 7, 1100, 2, "green", 1.2, 26.1),
        hidden_weapon("rack-right", "rack", [9, -13], 7, 1100, 2, "green", 2.0, 26.1),
    ],
    [
        armour_region(
            "back", 1, [[-30, -2.5], [30, -2.5], [30, 41], [-30, 41]], "shell", [5.3, 1000], False
        ),
        armour_region(
            "spine",
            2,
            [[-24, -40], [24, -40], [24, -2.5], [-24, -2.5]],
            "shell",
            [7.8, 1000],
            False,
        ),
    ],
)
