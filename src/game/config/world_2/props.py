"""The props of World 2 (P08-R03, R07; reworked at the reviewer's request, 2026-10-27), ported from
`config/world-2/props.ts`.

World 1's desert homes, outposts and plants, Level Zero's industrial buildings, the industrial
buildings made of parts, and the oil pumpjacks; each section picks the groups that stand on it, so
the industry slowly takes over the desert.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.cars import CAR_RULES
from game.config.prop_ids import PROP_IDS
from game.config.record import record
from game.config.tile_buildings import LOT_KINDS, tile_kinds
from game.config.world_1.props import WORLD_1_PROP_IDS, WORLD_1_ROADS

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

P = PROP_IDS
W1 = WORLD_1_PROP_IDS

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

TREE_SCALE = [0.45, 0.75]


def tree(prop_id: str, weight: float, footprint: float) -> Any:
    """A plant kind of the trees, drawn at the tree scale."""
    return record({"id": prop_id, "weight": weight, "footprint": footprint, "scale": TREE_SCALE})


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
        "trees": [
            tree(P.deadTree, 1, 1.5),
            tree(P.forkedTree, 0.6, 1.5),
            tree(W1.palm, 2, 4),
            tree(W1.dryBush, 3, 2.5),
            tree(W1.cactus, 2, 2),
        ],
        "treesPerCell": 4,
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

# Plants of the sections, from the oases to the last dead trees between the factories.
DESERT_PLANTS = record(
    {
        "oasis": [W1.palm, W1.dryBush, P.bush],
        "desert": [W1.cactus, W1.dryBush, P.deadTree],
        "rock": [W1.dryBush, P.deadTree, P.forkedTree],
        "town": [W1.palm, W1.dryBush],
        "industry": [P.deadTree, W1.dryBush],
    }
)

# Roads of World 2: as in World 1 (no crossings, phase 6 review).
WORLD_2_ROADS = WORLD_1_ROADS
