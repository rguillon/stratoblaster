"""The props of World 1 (P06-R05, R06): the building groups the sections pick from (D-207: the
buildings of the grid of tiles only; no plant grows any more)
"""

from game.config.cars import CAR_RULES
from game.config.record import record
from game.config.tile_buildings import LOT_KINDS, TILE, tile_kinds

# Building groups of World 1; each section lists the ones that stand on it.
WORLD_1_GROUPS = record(
    {
        # The harbours of the coast villages (D-207: the docks' buildings).
        "fishing": "fishing",
        # Coastal villages (D-207: the homes of the grid).
        "coastHomes": "coast-homes",
        # Villages of the green land: futuristic homes among the farms (reviewer, 2026-10-26).
        "villages": "villages",
        # Farms of the green land (D-207: the outposts' water towers, solar farms and depots).
        "farms": "farms",
        # Futuristic desert homes (P06-R06).
        "desertHomes": "desert-homes",
        # Desert outposts: water towers, solar farms, antennas.
        "outposts": "outposts",
        # Mines, refinery, tanks: the desert industry (1-4).
        "industrial": "industrial",
        "heavyIndustry": "heavy-industry",
    }
)

G = WORLD_1_GROUPS

# The props of World 1 (P06-R05, R06): the building groups the sections pick from. D-207: the
# hand-made huts, homes, masts and farms are gone, their groups drawing from the grid's buildings,
# and so are the plants.
WORLD_1_PROPS = record(
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
                "id": G.fishing,
                "weight": 1,
                "kinds": tile_kinds("docks"),
            },
            {
                "id": G.coastHomes,
                "weight": 2,
                "kinds": tile_kinds("homes"),
            },
            {
                "id": G.villages,
                "weight": 3,
                "kinds": tile_kinds("homes"),
            },
            {
                "id": G.farms,
                "weight": 2,
                "kinds": tile_kinds("outposts"),
            },
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
                "id": G.industrial,
                "weight": 2,
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
        # Phase 6 review: a few buildings away from the roads, and hamlets from time to time.
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

# Roads of World 1 (P04-R07): one winding 2x2 highway and a second road, paths every 260-560 units,
# starting and ending off screen, as in Level Zero; unlike there, no road crosses another (phase 6
# review).
WORLD_1_ROADS = record(
    {
        "mainRoads": 2,
        "spread": 200,
        "meander": {"amplitude": [80, 180], "wavelength": [1300, 2600]},
        "crossSpacing": [260, 560],
        "crossBend": 40,
        "mainWidth": 6,
        "crossWidth": 4,
        "dual": {"width": 12, "mainRoads": 1, "avenues": 0.25},
        "junction": {"width": 14, "length": 28},
        "offscreenX": 420,
        "turnRate": 0.05,
        "minHeight": 3,
        "maxSlope": 0.5,
        "minRun": 6,
        "step": 8,
        "slotSpacing": 24,
        "setback": 2,
        # Phase 6 review: roads never cross; paths only join roads.
        "noCrossings": {"gap": 30},
        # Phase 15: the districts on a grid of tiles.
        "tiles": TILE,
    }
)
