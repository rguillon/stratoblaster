"""How the World 4 levels look (P10-R04, R08; reworked at the reviewer's request, 2026-10-27),
ported from `config/world-4/looks.ts`.

World 3's ground where it ended, grass and gardens giving way to the concrete of the city (the
sections raise the `paved` cover level after level), the river flowing down the screen; and for each
level its time of day, clouds (back at the reviewer's request, 2026-10-29), weather and the glow of
the city from below along its length, as before the rework. Every look draws the enemy shots with a
contrast core (P10-R07). Gamma-space RGB, 0..1.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK
from game.config.record import merge, record
from game.config.world_3.looks import town

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Reviewer, 2026-10-28: World 4 at midday, brighter, the windows and the cars lit as at night;
# 2026-10-29: its clouds white on every level, whatever the storm, tint or glow.
DAYLIGHT = record({"groundLights": 1.5, "brightness": 1.3, "plainClouds": True})


def bright(atmosphere: Any) -> Any:
    """`atmosphere` with the World 4 daylight set on its start and on every change."""
    start = atmosphere["start"]
    changes = atmosphere["changes"]
    result = record({"start": merge(start, DAYLIGHT)})
    if changes:
        result["changes"] = [
            merge(change, {"look": merge(change["look"], DAYLIGHT)}) for change in changes
        ]
    return result


def city(atmosphere: Any) -> Any:
    """A World 4 look: World 3's town ground and water, the sky script, contrast shots (P10-R07).

    The flat ground casts no shadows (reviewer, 2026-10-28: it has nothing to shade).
    """
    look = town(bright(atmosphere))
    return merge(
        look,
        {
            "terrain": merge(look["terrain"], {"castsShadows": False}),
            "shotStyle": ENEMY_LOOK["contrast"]["style"],
        },
    )


def ash(strength: float) -> Any:
    """Falling ash of `strength`."""
    return record({"kind": "ash", "strength": strength})


def embers(strength: float) -> Any:
    """Falling embers of `strength`."""
    return record({"kind": "embers", "strength": strength})


# Ash-tinted pink and grey clouds of the 4-1 dawn.
ASH_PINK = [0.95, 0.84, 0.86]
# The smoke haze and steam of 4-1: the haze close, a little paler.
SMOKE_HAZE = record({"fog": 0.75, "white": 0.2})

# 4-1: a red dawn behind a smoke haze over the garden town.
LEVEL_4_1_LOOK = city(
    {
        "start": {
            "timeOfDay": "midday",
            "clouds": [0.4, 0.3],
            "cloudTint": ASH_PINK,
            "mist": SMOKE_HAZE,
        }
    }
)

# Brown-grey clouds of the ash cloud over 4-2.
ASH_BROWN = [0.8, 0.72, 0.62]
# The dim, flat, yellowish light under the ash cloud.
ASH_LIGHT = [1.04, 0.96, 0.74]

# 4-2: midday under an ash cloud, ash falling.
LEVEL_4_2_LOOK = city(
    {
        "start": {
            "timeOfDay": "midday",
            "clouds": [0.9, 0.9],
            "cloudTint": ASH_BROWN,
            "tint": ASH_LIGHT,
            "weather": ash(0.5),
        }
    }
)

# The orange glow of the town's lights under the clouds of 4-3.
LAVA_GLOW = [1, 0.42, 0.12]

# 4-3: the sunset fades while the glow of midtown's lights takes over.
LEVEL_4_3_LOOK = city(
    {
        "start": {
            "timeOfDay": "midday",
            "clouds": [0.5, 0.4],
            "storm": 0.5,
            "underglow": {"color": LAVA_GLOW, "strength": 0.25},
            "weather": embers(0.4),
        },
        "changes": [
            {
                "from": 60,
                "to": 280,
                "look": {
                    "timeOfDay": "midday",
                    "clouds": [0.5, 0.4],
                    "storm": 0.5,
                    "underglow": {"color": LAVA_GLOW, "strength": 0.8},
                    "weather": embers(0.4),
                },
            }
        ],
    }
)

# The glow of the business district under the smoke of 4-4.
FURNACE_GLOW = [1, 0.5, 0.15]

# 4-4: a night lit by the towers, ash and embers falling and rising.
LEVEL_4_4_LOOK = city(
    {
        "start": {
            "timeOfDay": "midday",
            "clouds": [0.6, 0.5],
            "storm": 0.6,
            "underglow": {"color": FURNACE_GLOW, "strength": 0.7},
            "weather": ash(0.3),
            "secondWeather": embers(0.3),
        }
    }
)

# The deep red of the eruption over 4-5.
ERUPTION_RED = [1, 0.16, 0.08]

# 4-5: a volcano erupts beyond downtown, the sky turning deep red and the embers growing to the
# final boss.
LEVEL_4_5_LOOK = city(
    {
        "start": {
            "timeOfDay": "midday",
            "clouds": [0.7, 0.6],
            "underglow": {"color": ERUPTION_RED, "strength": 0.6},
            "weather": embers(0.6),
        },
        "changes": [
            {
                "from": 180,
                "to": 300,
                "look": {
                    "timeOfDay": "midday",
                    "clouds": [0.7, 0.6],
                    "underglow": {"color": ERUPTION_RED, "strength": 1},
                    "weather": embers(1),
                },
            }
        ],
    }
)
