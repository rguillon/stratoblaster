"""Building groups of the districts on the grid of tiles, ported from `config/tile-buildings.ts`.

Phase 15 (reviewer, 2026-10-28): the districts are laid on a grid of 10 m tiles. A one-lane-each-way
street with its two sidewalks is one tile; every building stands on whole tiles.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record
from game.config.tile_model import model

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# P15-R01, R02: tiles of 10 world units, sidewalks of 2 (a 6-unit roadway, two 3-unit lanes).
TILE = record({"size": 10, "sidewalk": 2})

# P15-R07: gap from a model to the edges of its tiles.
BUILDING_MARGIN = 0.5

HOMES = [[1, 1], [2, 2]]
FLATS = [[1, 2], [2, 3]]
CITY = [[2, 2], [3, 3]]
WORKS = [[1, 1], [3, 4]]

# The building groups of the districts and their models (P15-R09, footprint table). Each group has
# `range`, its smallest and largest footprints either way round, and its `models`.
TILE_GROUPS = record(
    {
        "heavyIndustry": {
            "range": [[3, 3], [4, 6]],
            "models": [
                model("foundry", 3, 3),
                model("foundry", 4, 4),
                model("plant", 3, 4),
                model("plant", 4, 6),
                model("foundry", 3, 5, 2),
                model("plant", 4, 4, 2),
            ],
        },
        "desertHomes": {
            "range": HOMES,
            "models": [
                model("adobe", 1, 1),
                model("adobe", 1, 1, 2),
                model("adobe", 1, 2),
                model("courtyard", 2, 2),
                model("adobe", 2, 2, 3),
            ],
        },
        "outposts": {
            "range": HOMES,
            "models": [
                model("waterTower", 1, 1),
                model("solar", 1, 2),
                model("radio", 1, 1),
                model("depot", 2, 2),
                model("depot", 1, 2, 2),
            ],
        },
        # Reviewer, 2026-10-28: the villages and the worker homes, one group of small homes of the
        # future on paved plots, each model of a different silhouette (`tile-homesteads.ts`).
        "homes": {
            "range": [[1, 1], [2, 3]],
            "models": [
                model("homestead", 2, 1, 1),
                model("homestead", 1, 1, 2),
                model("homestead", 1, 1, 3),
                model("homestead", 1, 2, 4),
                model("homestead", 2, 2, 5),
                model("homestead", 2, 1, 6),
                model("homestead", 1, 2, 7),
                model("homestead", 2, 3, 10),
            ],
        },
        # Reviewer, 2026-10-28: the mines, the oil fields, the refineries and the industrial works
        # as one group.
        "industrial": {
            "range": WORKS,
            "models": [
                model("headframe", 2, 2),
                model("oreSilos", 1, 2),
                model("mineWorks", 3, 3),
                model("mineWorks", 2, 3, 2),
                model("headframe", 3, 3, 2),
                model("pumpjack", 1, 1),
                model("pumpjack", 1, 2, 2),
                model("oilTanks", 2, 2),
                model("oilTanks", 2, 3, 2),
                model("flare", 1, 1),
                model("tanks", 2, 2),
                model("tanks", 3, 3, 2),
                model("refinery", 2, 3),
                model("refinery", 3, 4, 2),
                model("flare", 1, 1, 2),
                model("tanks", 1, 2, 5),
                model("factory", 2, 3),
                model("factory", 3, 4),
                model("warehouse", 2, 3),
                model("containers", 2, 2),
                model("coolingTower", 3, 3),
                model("tanks", 2, 2, 3),
            ],
        },
        "docks": {
            "range": WORKS,
            "models": [
                model("containers", 2, 3),
                model("dockCrane", 1, 3),
                model("warehouse", 2, 4, 2),
                model("tanks", 2, 2, 4),
                model("containers", 3, 3, 2),
            ],
        },
        "workshops": {
            "range": FLATS,
            "models": [
                model("workshop", 1, 2),
                model("workshop", 2, 2),
                model("workshop", 2, 3),
                model("warehouse", 2, 2, 3),
                model("workshop", 2, 3, 2),
            ],
        },
        "workerFlats": {
            "range": FLATS,
            "models": [
                model("flats", 1, 2),
                model("flats", 2, 3, 3),
                model("flats", 2, 2, 2),
                model("flats", 2, 3, 2),
                model("flats", 2, 2, 3),
            ],
        },
        # Reviewer, 2026-10-28: the terraces and the suburbs, one group of homes of the future on
        # paved plots, each model of a different silhouette (`tile-residences.ts`).
        "residences": {
            "range": [[1, 1], [2, 4]],
            "models": [
                model("residence", 1, 2, 1),
                model("residence", 1, 1, 2),
                model("residence", 1, 4, 3),
                model("residence", 2, 2, 4),
                model("residence", 2, 2, 5),
                model("residence", 1, 2, 6),
                model("residence", 2, 3, 7),
                model("residence", 1, 3, 9),
            ],
        },
        "townCentre": {
            "range": CITY,
            "models": [
                model("midrise", 2, 2, 2),
                model("midrise", 2, 3),
                model("midrise", 3, 3, 6),
                model("flats", 2, 3, 4),
                model("office", 3, 3, 4),
            ],
        },
        "midrise": {
            "range": CITY,
            "models": [
                model("midrise", 2, 2, 3),
                model("midrise", 2, 3, 5),
                model("midrise", 3, 3, 4),
                model("office", 2, 3, 2),
                model("midrise", 2, 2),
            ],
        },
        "offices": {
            "range": CITY,
            "models": [
                model("office", 2, 2, 3),
                model("office", 2, 3, 4),
                model("office", 3, 3, 2),
                model("tower", 2, 2, 6),
                model("office", 3, 3),
            ],
        },
        "towers": {
            "range": CITY,
            "models": [
                model("tower", 2, 2, 3),
                model("tower", 3, 3, 2),
                model("tower", 2, 3, 4),
                model("tower", 2, 2, 5),
                model("skyscraper", 3, 3),
            ],
        },
        "skyscrapers": {
            "range": CITY,
            "models": [
                model("skyscraper", 2, 2),
                model("skyscraper", 3, 3, 2),
                model("skyscraper", 2, 3, 3),
                model("skyscraper", 3, 3, 5),
                model("skyscraper", 2, 2, 6),
            ],
        },
        "downtown": {
            "range": [[3, 3], [4, 4]],
            "models": [
                model("skyscraper", 3, 3, 3),
                model("skyscraper", 3, 4, 4),
                model("skyscraper", 4, 4),
                model("skyscraper", 3, 3, 6),
                model("skyscraper", 4, 4, 2),
            ],
        },
    }
)

# The keys of TILE_GROUPS in their order (`Object.values` order in the TS).
TILE_GROUP_IDS = [
    "heavyIndustry",
    "desertHomes",
    "outposts",
    "homes",
    "industrial",
    "docks",
    "workshops",
    "workerFlats",
    "residences",
    "townCentre",
    "midrise",
    "offices",
    "towers",
    "skyscrapers",
    "downtown",
]

# P15-R09: the lots, for the tiles no building fits, in every world.
LOT_MODELS = [
    model("carPark", 1, 2),
    model("yard", 1, 1),
    model("plaza", 2, 2),
    model("park", 2, 2),
    model("park", 1, 1, 2),
]


def unique_by_id(models: list[Any]) -> list[Any]:
    """Each model once, in the order of its first id; the last model of each id wins (as a Map)."""
    order: list[str] = []
    by_id: dict[str, Any] = {}
    for m in models:
        if m.id not in order:
            order.append(m.id)
        by_id[m.id] = m
    return [by_id[i] for i in order]


def all_models() -> list[Any]:
    """Every model of every group and the lots, in order (before the unique-by-id step)."""
    models: list[Any] = []
    for group_id in TILE_GROUP_IDS:
        models.extend(TILE_GROUPS[group_id].models)
    models.extend(LOT_MODELS)
    return models


# Every model made for the grid, once each.
TILE_MODELS = unique_by_id(all_models())


def tile_kind(m: Any, weight: float) -> Any:
    """The placement rule of a model made for the grid (P15-R07: scale 1, its tiles)."""
    w = m.tiles[0]
    d = m.tiles[1]
    return record(
        {
            "id": m.id,
            "weight": weight,
            "footprint": (math.hypot(w, d) * TILE.size) / 2,
            "scale": [1, 1],
            "tiles": m.tiles,
        }
    )


def tile_kinds(group_id: str, weight: float = 1) -> list[Any]:
    """The kinds of group `group_id`, sharing `weight` between them."""
    models = TILE_GROUPS[group_id].models
    return [tile_kind(m, weight / len(models)) for m in models]


# P15-R08: the lots of every world.
LOT_KINDS = [tile_kind(m, 1) for m in LOT_MODELS]
