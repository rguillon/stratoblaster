"""1-3, the green country of World 1 (P06-R05, reviewer, 2026-10-26)

From the farmland 1-2 ended on, through woods, green hills and a market town, to where the grass
turns dry and yellow. No sea. Its `seconds` add up to 240 (P06-R04).
"""

from game.config.record import merge, record
from game.config.world_1.props import WORLD_1_GROUPS, WORLD_1_PROPS, WORLD_1_ROADS
from game.config.world_1.scenery_coast import FARMLAND, smooth

G = WORLD_1_GROUPS

# Streets of a market town: wide blocks, few crossings.
TOWN_STREETS = record({"rows": [60, 110], "columns": [70, 130], "links": 0.55})

# Dry grassland, where 1-3 ends and 1-4 begins: a little grass left on the dry earth.
DRY_GRASSLAND = record(
    {
        "name": "dry grassland",
        "seconds": 30,
        "relief": smooth(28, 10, 560),
        "buildingDensity": 0.75,
        # D-212: trees on the little grass left, few.
        "treeDensity": 1,
        "surface": {"lush": 0.2},
        "groups": [G.villages, G.outposts],
    }
)

COUNTRY = [
    merge(FARMLAND, {"seconds": 30}),
    merge(
        FARMLAND,
        {
            "name": "woods",
            "seconds": 35,
            "relief": smooth(34, 18, 460, 5),
            "buildingDensity": 0.4,
            "treeDensity": 1,
            "groups": [G.farms],
        },
    ),
    merge(
        FARMLAND,
        {
            "name": "green hills",
            "seconds": 35,
            "relief": smooth(46, 36, 420, 5),
            "buildingDensity": 0.5,
            "treeDensity": 1,
            "groups": [G.villages],
        },
    ),
    merge(FARMLAND, {"seconds": 50, "buildingDensity": 0.75}),
    merge(
        FARMLAND,
        {
            "name": "market town",
            "seconds": 30,
            "relief": smooth(28, 4, 600, 3),
            "buildingDensity": 1,
            "treeDensity": 1,
            "surface": {"lush": 0.65, "paved": 0.3},
            "streets": TOWN_STREETS,
            "groups": [G.villages],
        },
    ),
    merge(
        DRY_GRASSLAND,
        {
            "name": "yellowing grass",
            "surface": {"lush": 0.5},
            "buildingDensity": 0.7,
            "treeDensity": 1,
            "groups": [G.villages, G.farms],
        },
    ),
    DRY_GRASSLAND,
]

# 1-3 (P06-R05): the green country, starting on the farmland 1-2 ended on.
LEVEL_1_3 = record(
    {
        "id": "world-1-3",
        "name": "1-3 Green country",
        "seed": 1301,
        "scrollSpeed": 60,
        "transition": 420,
        "sections": COUNTRY,
        "roads": WORLD_1_ROADS,
        "props": WORLD_1_PROPS,
    }
)
