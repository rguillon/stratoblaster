"""The props of World 2 (P08-R03, R07; reworked at the reviewer's request, 2026-10-27)

World 1's desert homes, outposts and plants, Level Zero's industrial buildings, the industrial
buildings made of parts, and the oil pumpjacks; each section picks the groups that stand on it, so
the industry slowly takes over the desert.
"""

from game.config.cars import CAR_RULES
from game.config.record import record
from game.config.tile_buildings import LOT_KINDS, tile_kinds
from game.config.world_1.props import WORLD_1_ROADS

# Building groups of World 2; each section lists the ones that stand on it.
WORLD_2_GROUPS = record(
    {
        # Oasis and desert homes: World 1's flat-roofed homes and wind catchers.
        "desertHomes": "w2-desert-homes",
        # Caravan and desert outposts: water towers, solar farms, antennas, radars.
        "outposts": "w2-outposts",
        # Mines: headframes, their tanks and sheds.
        "mines": "w2-mines",
        # Mining and company towns: homes of the workers between mine and oil buildings.
        "workerHomes": "w2-worker-homes",
        # Oil fields: pumpjacks and storage tanks.
        "oil": "w2-oil",
        # Refineries and tank farms.
        "refinery": "w2-refinery",
        # The industrial belt: factories, warehouses, yards, cooling towers.
        "industrial": "w2-industrial",
        # Dense heavy industry: large plants and works made of parts.
        "heavyIndustry": "w2-heavy-industry",
    }
)

G = WORLD_2_GROUPS


# The props of World 2 (P08-R03, R07; reworked at the reviewer's request, 2026-10-27): World 1's
# desert homes, outposts and plants, Level Zero's industrial buildings, the industrial buildings
# made of parts, and the oil pumpjacks; each section picks the groups that stand on it, so the
# industry slowly takes over the desert.
WORLD_2_PROPS = record(
    {
        # Phase 15 (P15-R08): lots for the tiles of the districts no building fits.
        "lots": LOT_KINDS,
        "cellSize": 50,
        "treeClearance": 3,
        "maxSlope": 0.12,
        "treeMaxSlope": 0.45,
        "minHeight": 4,
        "zoneFrequency": 1 / 700,
        "groups": [
            {
                "id": G.desertHomes,
                "weight": 3,
                "kinds": tile_kinds("desertHomes"),
            },
            {
                "id": G.outposts,
                "weight": 2,
                "kinds": tile_kinds("outposts"),
            },
            {
                "id": G.mines,
                "weight": 2,
                "kinds": tile_kinds("industrial"),
            },
            {
                "id": G.workerHomes,
                "weight": 3,
                "kinds": tile_kinds("homes"),
            },
            {
                "id": G.oil,
                "weight": 2,
                "kinds": tile_kinds("industrial"),
            },
            {
                "id": G.refinery,
                "weight": 2,
                "kinds": tile_kinds("industrial"),
            },
            {
                "id": G.industrial,
                "weight": 3,
                "kinds": tile_kinds("industrial"),
            },
            {
                "id": G.heavyIndustry,
                "weight": 1,
                "kinds": tile_kinds("heavyIndustry"),
            },
        ],
        # D-207: no plant grows.
        "trees": [],
        "treesPerCell": 0,
        "cars": CAR_RULES,
        "loners": {"cell": 150, "chance": 0.15, "clearance": 18},
        "hamlets": {
            "spacing": [700, 1400],
            "buildings": [5, 9],
            "radius": 32,
            "gap": 2,
            "clearance": 18,
        },
    }
)

# Roads of World 2: as in World 1 (no crossings, phase 6 review).
WORLD_2_ROADS = WORLD_1_ROADS
