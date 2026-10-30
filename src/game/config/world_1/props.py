"""The props of World 1 (P06-R05, R06), ported from `config/world-1/props.ts`.

The props of World 1: the building groups the sections pick from, and the plants. Lone huts and
masts are also listed with the plants: they stand alone on the islands of 1-1, where no road goes,
so they are scattered like plants instead of placed along roads.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.cars import CAR_RULES
from game.config.prop_ids import PROP_IDS
from game.config.record import record
from game.config.tile_buildings import LOT_KINDS, TILE, tile_kinds

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Ids of the props added for World 1 (P06-R06).
WORLD_1_PROP_IDS = record(
    {
        "desertHome": "desert-home",
        "beachHut": "beach-hut",
        "palm": "palm-tree",
        "dryBush": "dry-bush",
        "cactus": "cactus",
        # The farms of the green land (reviewer, 2026-10-26).
        "farmhouse": "farmhouse",
        "greenhouse": "greenhouse",
        "grainSilos": "grain-silos",
        # The wind turbines of the farms, also placed in World 2.
        "windTurbine": "wind-turbine",
    }
)

P = PROP_IDS
W = WORLD_1_PROP_IDS

# Building groups of World 1; each section lists the ones that stand on it.
WORLD_1_GROUPS = record(
    {
        # Fishing huts and masts of the coast villages.
        "fishing": "fishing",
        # Coastal villages: huts and white homes.
        "coastHomes": "coast-homes",
        # Villages of the green land: futuristic homes among the farms (reviewer, 2026-10-26).
        "villages": "villages",
        # Farms of the green land: farmhouses, greenhouses, grain silos, wind turbines.
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

# Props are drawn small next to the ships, as in Level Zero.
BUILDING_SCALE = [0.5, 0.65]
TREE_SCALE = [0.45, 0.75]
# Lone huts and masts scattered on the islands, where no road goes (see `scatter` below).
LONE_SCALE = [0.5, 0.6]


def building(prop_id: str, weight: float, footprint: float) -> Any:
    """A building kind of the groups, drawn at the building scale."""
    return record(
        {"id": prop_id, "weight": weight, "footprint": footprint, "scale": BUILDING_SCALE}
    )


def tree(prop_id: str, weight: float, footprint: float) -> Any:
    """A plant kind of the trees, drawn at the tree scale."""
    return record({"id": prop_id, "weight": weight, "footprint": footprint, "scale": TREE_SCALE})


# The props of World 1 (P06-R05, R06): the building groups the sections pick from, and the plants.
# Lone huts and masts are also listed with the plants: they stand alone on the islands of 1-1,
# where no road goes, so they are scattered like plants instead of placed along roads.
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
                "kinds": [building(W.beachHut, 4, 5), building(P.antenna, 0.5, 6)],
            },
            {
                "id": G.coastHomes,
                "weight": 2,
                "kinds": [
                    building(W.beachHut, 2, 5),
                    building(P.cubeHome, 2, 7.5),
                    building(P.domeHome, 1, 7),
                    building(W.desertHome, 1, 7.5),
                ],
            },
            {
                "id": G.villages,
                "weight": 3,
                "kinds": tile_kinds("homes"),
            },
            {
                "id": G.farms,
                "weight": 2,
                "kinds": [
                    building(W.farmhouse, 3, 8.5),
                    building(W.greenhouse, 2, 9.5),
                    building(W.grainSilos, 2, 9.5),
                    building(W.windTurbine, 1, 6),
                ],
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
        "trees": [
            tree(P.deadTree, 1, 1.5),
            tree(P.forkedTree, 1, 1.5),
            tree(W.palm, 2, 4),
            tree(W.dryBush, 3, 2.5),
            tree(W.cactus, 2, 2),
            tree(P.bush, 1, 3.5),
            tree(P.broadleaf, 2, 4.5),
            tree(P.conifer, 1, 3.5),
            {"id": W.beachHut, "weight": 0.3, "footprint": 4.5, "scale": LONE_SCALE},
            {"id": P.antenna, "weight": 0.1, "footprint": 5, "scale": LONE_SCALE},
        ],
        "treesPerCell": 4,
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

# Plants of the sections, and the lone huts of the islands.
PLANTS = record(
    {
        "islands": [W.palm, P.bush, W.beachHut, P.antenna],
        "coast": [W.palm, P.bush, P.broadleaf],
        # The green land (reviewer, 2026-10-26): meadows, then woods and groves.
        "meadow": [P.broadleaf, P.bush],
        "woods": [P.broadleaf, P.conifer, P.bush],
        # Where the grass turns dry and yellow.
        "dryGrass": [W.dryBush, P.broadleaf, P.forkedTree],
        "dry": [W.dryBush, P.deadTree, P.forkedTree],
        "desert": [W.cactus, W.dryBush, P.deadTree],
        "oasis": [W.palm, P.bush, W.dryBush],
        "town": [W.palm, W.dryBush],
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
