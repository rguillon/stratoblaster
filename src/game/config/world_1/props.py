# Copyright (c) 2026 Renaud Guillon
"""The props of World 1 (WLD-1-13).

The building groups the sections pick from (D-207: the buildings of the grid of tiles only; no plant
grows any more).
"""

from game.config.cars import CAR_RULES
from game.config.cliffs import CRAG_CLIFFS, MESA_CLIFFS
from game.config.record import merge, record
from game.config.tile_buildings import LOT_KINDS, TILE, tile_kinds
from game.config.trees import FORESTS, TREE_KINDS, TREES_PER_CELL

# Building groups of World 1; each section lists the ones that stand on it.
WORLD_1_GROUPS = record({
    # The harbours of the coast villages (D-207: the docks' buildings).
    "fishing": "fishing",
    # Coastal villages (D-207: the homes of the grid).
    "coastHomes": "coast-homes",
    # Villages of the green land: futuristic homes among the farms (reviewer, 2026-10-26).
    "villages": "villages",
    # Farms of the green land (D-207: the outposts' water towers, solar farms and depots).
    "farms": "farms",
    # Futuristic desert homes (WLD-1-13).
    "desertHomes": "desert-homes",
    # Desert outposts: water towers, solar farms, antennas.
    "outposts": "outposts",
    # Mines, refinery, tanks: once the desert industry of 1-4; no section uses them now
    # (WLD-1-11).
    "industrial": "industrial",
    "heavyIndustry": "heavy-industry",
})

G = WORLD_1_GROUPS

# The props of World 1 (WLD-1-09, WLD-1-13): the building groups the sections pick from. D-207:
# the hand-made huts, homes, masts and farms are gone, their groups drawing from the grid's
# buildings, and so are the plants.
WORLD_1_PROPS = record({
    # WLD-1-31, GFX-PROP-19: the faces of the hills built of blocks of grey crag.
    "cliffs": CRAG_CLIFFS,
    # Phase 15 (GFX-BLDG-05): lots for the tiles of the districts no building fits.
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
    # D-212 (WLD-1-14): trees on the green land, gathered in woods, drawn as imposters (D-207:
    # the plants of before are gone).
    "trees": TREE_KINDS,
    "treesPerCell": TREES_PER_CELL,
    "forests": FORESTS,
    "cars": CAR_RULES,
    # Phase 6 review (WLD-1-15): a few buildings away from the roads, and hamlets from time to
    # time.
    "loners": {"cell": 150, "chance": 0.15, "clearance": 18},
    "hamlets": {
        "spacing": [700, 1400],
        "buildings": [5, 9],
        "radius": 32,
        "gap": 2,
        "clearance": 18,
    },
})

# Roads of World 1 (WLD-1-15; GFX-ROAD-01, GFX-ROAD-04): one winding 2x2 highway and a second road,
# paths every 260-560 units, starting and ending off screen, as in Level Zero; unlike there, no road
# crosses another (phase 6 review).
WORLD_1_ROADS = record({
    "mainRoads": 2,
    "spread": 200,
    "meander": {"amplitude": [80, 180], "wavelength": [1300, 2600]},
    "crossSpacing": [260, 560],
    "crossBend": 40,
    "mainWidth": 6,
    "crossWidth": 4,
    "dual": {"width": 12, "mainRoads": 1, "avenues": 0.25},
    "junction": {"width": 14, "length": 28},
    # D-252, D-263: the camera sees about +/-210 of ground across the playfield window (+/-235 at
    # the sea bed).
    "offscreenX": 420,
    "turnRate": 0.05,
    "minHeight": 3,
    "maxSlope": 0.5,
    "minRun": 6,
    "step": 8,
    # Buildings in slots along the roads, set back from them (GFX-BLDG-01).
    "slotSpacing": 24,
    "setback": 2,
    # Phase 6 review: roads never cross; paths only join roads.
    "noCrossings": {"gap": 30},
    # Phase 15: the districts on a grid of tiles.
    "tiles": TILE,
})


# The dry levels (WLD-1-31): the same props, their cliff faces built of red mesa rock.
DESERT_PROPS = merge(WORLD_1_PROPS, {"cliffs": MESA_CLIFFS})
