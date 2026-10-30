"""World 4 (P10-R03; reworked at the reviewer's request, 2026-10-27)

The five levels are one journey from the garden villages World 3 ended on, through the suburbs and a
town centre, the mid-rise blocks and the offices of midtown, the towers of the business district, to
a downtown of skyscrapers. The changes are slow, as in Worlds 2 and 3: the grass gives way to
concrete in small steps, the sections blend over World 2's long stretch (`TRANSITION`), and each
taller kind of building first comes in mixed with the one before it. Each level starts on the very
section the previous one ended on. No sea and no lava: World 3's river runs on through the town and
between the embankments of the city. Each level's `seconds` add up to 300 (P10-R02).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import merge, record
from game.config.world_2.scenery import TRANSITION
from game.config.world_3.props import TOWN_PLANTS
from game.config.world_3.scenery import (
    FLAT,
    GARDEN_VILLAGE_END,
    LANES,
    PONDS,
    ROLLING,
    STREETS,
    SUBURB_STREETS,
    VILLAGE_STREETS,
    river,
)
from game.config.world_4.city_props import WORLD_4_GROUPS, WORLD_4_PROPS
from game.config.world_4.props import WORLD_4_ROADS

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

PL = TOWN_PLANTS
G = WORLD_4_GROUPS


def quays(half_width: float) -> Any:
    """The river between the stone embankments of the city: steep walls, `half_width` at its bed."""
    return merge(river(half_width), {"wall": 14})


# Every block filled with buildings side by side, as in Level Zero's city centre.
FILLED_BLOCKS = record({"podiums": [], "podiumHeight": [0, 0], "towers": [16, 16]})


def section(name: str, seconds: float, extra: Any) -> Any:
    """A section of World 4: paved streets and offices, with `extra` set over the defaults."""
    return merge(
        record(
            {
                "name": name,
                "seconds": seconds,
                "relief": FLAT,
                "channel": quays(30),
                "buildingDensity": 1,
                "treeDensity": 0.2,
                "surface": {"paved": 0.7, "lush": 0.2},
                "streets": STREETS,
                "trees": PL["streets"],
                "groups": [G["offices"]],
            }
        ),
        extra,
    )


# The town centre, where 4-1 ends and 4-2 begins.
TOWN_CENTRE = section(
    "town centre",
    50,
    {
        "treeDensity": 0.3,
        "surface": {"paved": 0.45, "lush": 0.4},
        "groups": [G["workerFlats"], G["townCentre"]],
    },
)

# Mid-rise blocks giving way to the offices, where 4-2 ends and 4-3 begins.
MIDRISE_EDGE = section(
    "midrise edge",
    50,
    {
        "surface": {"paved": 0.68, "lush": 0.2},
        "groups": [G["midrise"], G["offices"]],
    },
)

# Offices giving way to the towers, where 4-3 ends and 4-4 begins.
TOWER_EDGE = section(
    "tower edge",
    50,
    {
        "treeDensity": 0.12,
        "surface": {"paved": 0.85, "lush": 0.06},
        "trees": PL["streets"],
        "groups": [G["towers"], G["offices"]],
    },
)

# The first skyline, where 4-4 ends and 4-5 begins.
SKYLINE_EDGE = section(
    "skyline edge",
    50,
    {
        "channel": quays(26),
        "treeDensity": 0.08,
        "surface": {"paved": 0.94, "lush": 0.02},
        "groups": [G["skyscrapers"]],
    },
)

# 4-1, Garden town: from the garden villages 3-5 ended on, suburban lanes, suburbs, terraced streets
# and flats, to the town centre.
GARDEN_TOWN = [
    # World 3 has no water (reviewer, 2026-10-28); World 4 keeps its river and ponds.
    merge(GARDEN_VILLAGE_END, {"channel": river(26), "lakes": PONDS, "seconds": 40}),
    section(
        "suburban lanes",
        55,
        {
            "relief": ROLLING,
            "channel": river(26),
            "treeDensity": 0.65,
            "surface": {"paved": 0.14, "lush": 0.78},
            "streets": LANES,
            "trees": PL["gardens"],
            "groups": [G["villages"], G["residences"]],
        },
    ),
    section(
        "suburbs",
        55,
        {
            "relief": ROLLING,
            "channel": river(28),
            "treeDensity": 0.55,
            "surface": {"paved": 0.2, "lush": 0.7},
            "streets": VILLAGE_STREETS,
            "trees": PL["gardens"],
            "groups": [G["residences"]],
        },
    ),
    section(
        "terraced streets",
        50,
        {
            "channel": river(28),
            "treeDensity": 0.45,
            "surface": {"paved": 0.28, "lush": 0.6},
            "streets": VILLAGE_STREETS,
            "groups": [G["residences"]],
        },
    ),
    section(
        "flats",
        50,
        {
            "treeDensity": 0.35,
            "surface": {"paved": 0.36, "lush": 0.5},
            "groups": [G["residences"], G["workerFlats"]],
        },
    ),
    TOWN_CENTRE,
]

# 4-2, Inner town: town streets, the ring road, mid-rise flats, a city park, then mid-rise blocks
# among the first offices.
INNER_TOWN = [
    merge(TOWN_CENTRE, {"seconds": 40}),
    section(
        "town streets",
        60,
        {
            "treeDensity": 0.28,
            "surface": {"paved": 0.5, "lush": 0.35},
            "groups": [G["townCentre"]],
        },
    ),
    section(
        "ring road",
        50,
        {
            "treeDensity": 0.25,
            "surface": {"paved": 0.56, "lush": 0.3},
            "groups": [G["townCentre"], G["midrise"]],
        },
    ),
    section(
        "mid-rise flats",
        55,
        {
            "treeDensity": 0.22,
            "surface": {"paved": 0.62, "lush": 0.25},
            "groups": [G["midrise"]],
        },
    ),
    section(
        "city park",
        45,
        {
            "channel": quays(36),
            "buildingDensity": 0.8,
            "treeDensity": 0.55,
            "surface": {"paved": 0.4, "lush": 0.5},
            "streets": SUBURB_STREETS,
            "trees": PL["parks"],
            "groups": [G["midrise"]],
        },
    ),
    MIDRISE_EDGE,
]

# 4-3, Midtown: offices among the mid-rise blocks, the river quays, plazas, the first towers.
MIDTOWN = [
    merge(MIDRISE_EDGE, {"seconds": 40}),
    section(
        "midtown",
        60,
        {
            "treeDensity": 0.18,
            "surface": {"paved": 0.72, "lush": 0.16},
            "groups": [G["offices"], G["midrise"]],
        },
    ),
    section(
        "office blocks",
        55,
        {
            "treeDensity": 0.15,
            "surface": {"paved": 0.76, "lush": 0.12},
        },
    ),
    section(
        "river quays",
        50,
        {
            "channel": quays(38),
            "treeDensity": 0.15,
            "surface": {"paved": 0.78, "lush": 0.1},
        },
    ),
    section(
        "plazas",
        45,
        {
            "treeDensity": 0.14,
            "surface": {"paved": 0.82, "lush": 0.08},
            "groups": [G["offices"], G["towers"]],
        },
    ),
    TOWER_EDGE,
]

# 4-4, Business district: city towers, a park among them, the financial district with the first
# skyscrapers, high rise, then the first skyline.
BUSINESS_DISTRICT = [
    merge(TOWER_EDGE, {"seconds": 40}),
    section(
        "business district",
        60,
        {
            "treeDensity": 0.1,
            "surface": {"paved": 0.88, "lush": 0.05},
            "groups": [G["towers"]],
        },
    ),
    section(
        "tower park",
        45,
        {
            "buildingDensity": 0.8,
            "treeDensity": 0.45,
            "surface": {"paved": 0.6, "lush": 0.3},
            "trees": PL["parks"],
            "groups": [G["towers"]],
        },
    ),
    section(
        "financial district",
        55,
        {
            "treeDensity": 0.08,
            "surface": {"paved": 0.9, "lush": 0.04},
            "groups": [G["towers"], G["skyscrapers"]],
        },
    ),
    section(
        "high rise",
        50,
        {
            "channel": quays(28),
            "treeDensity": 0.08,
            "surface": {"paved": 0.92, "lush": 0.03},
            "groups": [G["skyscrapers"], G["towers"]],
        },
    ),
    SKYLINE_EDGE,
]

# 4-5, Downtown: the skyline, a central park, then skyscrapers filling every block to the end.
DOWNTOWN = [
    merge(SKYLINE_EDGE, {"seconds": 40}),
    section(
        "skyscrapers",
        60,
        {
            "channel": quays(26),
            "treeDensity": 0.06,
            "surface": {"paved": 0.95, "lush": 0.02},
            "groups": [G["skyscrapers"]],
        },
    ),
    section(
        "central park",
        40,
        {
            "channel": quays(30),
            "buildingDensity": 0.7,
            "treeDensity": 0.5,
            "surface": {"paved": 0.55, "lush": 0.4},
            "trees": PL["parks"],
            "groups": [G["skyscrapers"]],
        },
    ),
    section(
        "downtown",
        70,
        {
            "channel": quays(24),
            "buildingDensity": 0.7,
            "treeDensity": 0.04,
            "surface": {"paved": 0.97},
            "groups": [G["skyscrapers"], G["downtown"]],
            "blocks": FILLED_BLOCKS,
        },
    ),
    section(
        "city heart",
        90,
        {
            "channel": quays(22),
            "buildingDensity": 0.7,
            "treeDensity": 0.02,
            "surface": {"paved": 1},
            "groups": [G["downtown"]],
            "blocks": FILLED_BLOCKS,
        },
    ),
]


def city_only(s: Any) -> Any:
    """`s` with only buildings and roads (reviewer, 2026-10-28): no river, flat paved ground, no
    grass or trees.
    """
    city = merge(
        s,
        {
            "relief": FLAT,
            "treeDensity": 0,
            "surface": {"paved": 1, "lush": 0},
        },
    )
    if "channel" in city:
        del city["channel"]
    if "lakes" in city:
        del city["lakes"]
    if "shore" in city:
        del city["shore"]
    if "flatten" in city:
        del city["flatten"]
    return city


def level(meta: list[Any], scroll_speed: float, sections: list[Any]) -> Any:
    """A World 4 level: its `[id, name, seed]`, its scroll speed and its sections, without water."""
    return record(
        {
            "id": meta[0],
            "name": meta[1],
            "seed": meta[2],
            "scrollSpeed": scroll_speed,
            "transition": TRANSITION,
            # No sea (reviewer, 2026-10-28): one under the flat ground never showed, but was drawn.
            "sections": [city_only(s) for s in sections],
            "roads": WORLD_4_ROADS,
            "props": WORLD_4_PROPS,
        }
    )


# 4-1 (P10-R03): the garden town, from the garden villages 3-5 ended on.
LEVEL_4_1 = level(["world-4-1", "4-1 Garden town", 4101], 70, GARDEN_TOWN)
# 4-2: the inner town, starting on the town centre 4-1 ended on.
LEVEL_4_2 = level(["world-4-2", "4-2 Inner town", 4201], 65, INNER_TOWN)
# 4-3: midtown, starting on the mid-rise blocks 4-2 ended on.
LEVEL_4_3 = level(["world-4-3", "4-3 Midtown", 4301], 60, MIDTOWN)
# 4-4: the business district, starting on the towers 4-3 ended on.
LEVEL_4_4 = level(["world-4-4", "4-4 Business district", 4401], 55, BUSINESS_DISTRICT)
# 4-5: downtown, starting on the skyline 4-4 ended on.
LEVEL_4_5 = level(["world-4-5", "4-5 Downtown", 4501], 55, DOWNTOWN)
