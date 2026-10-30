"""How the World 3 levels look (P09-R04, R06; reworked at the reviewer's request, 2026-10-27),
ported from `config/world-3/looks.ts`.

World 2's stained industrial concrete where it ended, slowly giving way to the grass of gardens and
parks (the `lush` cover the sections raise level after level), damp dark earth between them, grey
stone on the canal walls and mud along the water, grey-green canal and river water flowing down the
screen, asphalt roads; and for each level its time of day, clouds and weather along its length.
Gamma-space RGB, 0..1.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import merge, record
from game.config.scenery_look import BASE_SCENERY_LOOK, texture
from game.config.world_1.looks import GRASS
from game.config.world_2.looks import INDUSTRIAL_PAVING

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Damp, dark earth: the ground of the yards and gardens wherever nothing covers it.
DAMP_EARTH = texture(
    [
        [0.17, 0.15, 0.11],
        [0.24, 0.21, 0.15],
        [0.31, 0.27, 0.19],
    ],
    12,
    {"speckle": 0.04, "speckleColor": [0.18, 0.24, 0.12]},
)

# Grey-brown mud along the canals and rivers.
MUD = texture(
    [
        [0.24, 0.21, 0.16],
        [0.32, 0.28, 0.21],
        [0.4, 0.35, 0.27],
    ],
    14,
    {"speckle": 0.03, "speckleColor": [0.18, 0.16, 0.12]},
)

# Grey stone of the canal walls and embankments, layered.
STONE = texture(
    [
        [0.26, 0.26, 0.25],
        [0.35, 0.35, 0.33],
        [0.44, 0.43, 0.41],
    ],
    8,
    {"strata": 0.35, "speckle": 0.03, "speckleColor": [0.2, 0.26, 0.16]},
)

# Grey-green water of the canals and rivers.
WATER = [0.1, 0.13, 0.12]

# The ground of World 3: concrete at the start, grass and gardens by the end.
TOWN_TERRAIN = merge(
    BASE_SCENERY_LOOK.terrain,
    {
        "ground": DAMP_EARTH,
        "low": MUD,
        "steep": STONE,
        "high": GRASS,
        "lush": GRASS,
        "paved": INDUSTRIAL_PAVING,
        "sand": MUD,
        "lowHeight": 3,
        "heightBlend": 3,
        # Only the canal walls and embankments are bare stone.
        "steepSlope": [0.6, 0.9],
        "tints": [
            [1.03, 1.03, 0.98],
            [0.88, 0.9, 0.86],
        ],
        "shore": merge(
            BASE_SCENERY_LOOK.terrain.shore,
            {
                "sand": [0.34, 0.3, 0.24],
                "beach": 2,
                "shallow": [0.2, 0.23, 0.19],
                "deep": WATER,
                "foam": merge(BASE_SCENERY_LOOK.terrain.shore.foam, {"color": [0.78, 0.8, 0.76]}),
            },
        ),
    },
)

# The water flows down the screen, the way the player came from (P09-R06).
RIVER_FLOW = [0, 16]


def town(atmosphere: Any) -> Any:
    """A World 3 look: the town ground, its water and the sky script (P09-R04)."""
    return record(
        merge(
            BASE_SCENERY_LOOK,
            {
                "terrain": TOWN_TERRAIN,
                "sea": merge(
                    BASE_SCENERY_LOOK.sea,
                    {
                        "color": WATER,
                        "alpha": 0.6,
                        "sunGlint": 1.2,
                        "drift": RIVER_FLOW,
                    },
                ),
                "glow": {"intensity": 0.45, "blurKernelSize": 16},
                "atmosphere": atmosphere,
            },
        )
    )


def rain(strength: float) -> Any:
    """Rain of `strength`."""
    return record({"kind": "rain", "strength": strength})


# The 3-1 morning: white clouds, a low warm sun.
MORNING = record({"timeOfDay": "morning", "clouds": [0.3, 0.2]})
# The morning mist of 3-1 (`morning_mist`): the haze close and white over the factories.
MORNING_MIST = record({"fog": 0.4, "white": 0.8})

# 3-1: a morning mist over the factories and canals, lifting over the first half.
LEVEL_3_1_LOOK = town(
    record(
        {
            "start": merge(MORNING, {"mist": MORNING_MIST}),
            "changes": [{"from": 0, "to": 150, "look": MORNING}],
        }
    )
)

# Bright, humid midday light under tall white cumulus.
MIDDAY = record({"timeOfDay": "midday", "clouds": [0.5, 0.3]})

# 3-2: a rain shower over the middle third, then clearing.
LEVEL_3_2_LOOK = town(
    record(
        {
            "start": MIDDAY,
            "changes": [
                {"from": 92, "to": 108, "look": merge(MIDDAY, {"weather": rain(0.4)})},
                {"from": 192, "to": 208, "look": MIDDAY},
            ],
        }
    )
)

# The 3-3 thunderstorm: dark blue-grey clouds, heavy rain, lightning.
THUNDERSTORM = record(
    {
        "timeOfDay": "afternoon",
        "clouds": [0.9, 0.9],
        "storm": 1,
        "weather": rain(0.8),
        "lightning": 1,
    }
)

# 3-3: the storm builds over the first quarter, from half-covered skies without rain.
LEVEL_3_3_LOOK = town(
    record(
        {
            "start": {"timeOfDay": "afternoon", "clouds": [0.5, 0.5], "storm": 0.3},
            "changes": [{"from": 0, "to": 75, "look": THUNDERSTORM}],
        }
    )
)

# 3-4: a rainy dusk over the terraces and suburbs, their windows and streets lit.
LEVEL_3_4_LOOK = town(
    record({"start": {"timeOfDay": "dusk", "clouds": [0.6, 0.4], "weather": rain(0.3)}})
)

# 3-5: a rainy night over the lit garden villages, the rain stopping and the clouds opening before
# the final boss.
LEVEL_3_5_LOOK = town(
    record(
        {
            "start": {"timeOfDay": "night", "clouds": [0.6, 0.4], "weather": rain(0.5)},
            "changes": [
                {"from": 250, "to": 275, "look": {"timeOfDay": "night", "clouds": [0.2, 0.1]}}
            ],
        }
    )
)
