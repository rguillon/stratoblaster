"""The props of World 3 (P09-R03, R06; reworked at the reviewer's request, 2026-10-27)

Level Zero's industrial buildings and those made of parts, then the workers' flats, terraces and
houses, and the farms of World 1's green land; each section picks the groups that stand on it, so
the homes slowly take over the factories. Small buildings only at the end: no tower.
"""

from game.config.cars import CAR_RULES
from game.config.record import merge, record
from game.config.tile_buildings import LOT_KINDS, tile_kinds
from game.config.world_1.props import WORLD_1_ROADS

# Building groups of World 3; each section lists the ones that stand on it.
WORLD_3_GROUPS = record(
    {
        # Dense heavy industry, where World 2 ended: large plants and works made of parts.
        "heavyIndustry": "w3-heavy-industry",
        # Factories, warehouses, yards, tanks and cooling towers.
        "industrial": "w3-industrial",
        # The canal docks: container yards, warehouses and tanks.
        "docks": "w3-docks",
        # Workshops and small works among the first flats.
        "workshops": "w3-workshops",
        # The workers' flats: small blocks, terraces.
        "workerFlats": "w3-worker-flats",
        # The residences (reviewer, 2026-10-28: the terraces and suburbs as one): homes of the
        # future.
        "residences": "w3-residences",
        # The garden villages: houses, farmhouses and greenhouses.
        "villages": "w3-villages",
    }
)

G = WORLD_3_GROUPS

# Plants are drawn small next to the ships, as in Worlds 1 and 2.


# The props of World 3 (P09-R03, R06; reworked at the reviewer's request, 2026-10-27): Level
# Zero's industrial buildings and those made of parts, then the workers' flats, terraces and
# houses, and the farms of World 1's green land; each section picks the groups that stand on it,
# so the homes slowly take over the factories. Small buildings only at the end: no tower.
WORLD_3_PROPS = record(
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
                "id": G.heavyIndustry,
                "weight": 1,
                "kinds": tile_kinds("heavyIndustry"),
            },
            {
                "id": G.industrial,
                "weight": 3,
                "kinds": tile_kinds("industrial"),
            },
            {
                "id": G.docks,
                "weight": 2,
                "kinds": tile_kinds("docks"),
            },
            {
                "id": G.workshops,
                "weight": 3,
                "kinds": tile_kinds("workshops"),
            },
            {
                "id": G.workerFlats,
                "weight": 3,
                "kinds": tile_kinds("workerFlats"),
            },
            {
                "id": G.residences,
                "weight": 3,
                "kinds": tile_kinds("residences"),
            },
            {
                "id": G.villages,
                "weight": 3,
                "kinds": tile_kinds("homes"),
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

# Roads of World 3: as in World 1 (no crossings, phase 6 review), but the street grids stop closer
# to the screen edges (reviewer, 2026-10-28): the ground is drawn twice as big, so only about +/-195
# of it shows, and the streets and buildings generated out to +/-420 were never seen.
WORLD_3_ROADS = merge(WORLD_1_ROADS, {"offscreenX": 240})
