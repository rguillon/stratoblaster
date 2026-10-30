"""Building groups and props of World 4 (P10-R03, R08)

World 3's houses, terraces and flats, then Level Zero's city blocks and towers made of parts, then
the skyscrapers; each section picks the groups that stand on it, so the buildings slowly grow from
the houses to the skyscrapers. World 3's plants (Level Zero's trees).
"""

from game.config.cars import CAR_RULES
from game.config.record import concat, merge, record
from game.config.tile_buildings import tile_kinds
from game.config.world_3.props import WORLD_3_GROUPS, WORLD_3_PROPS

# Building groups of World 4 (reviewer's rework, 2026-10-27); each section lists its own.
WORLD_4_GROUPS = record(
    {
        # World 3's garden villages and suburbs, where World 3 ended.
        "villages": WORLD_3_GROUPS["villages"],
        "residences": WORLD_3_GROUPS["residences"],
        "workerFlats": WORLD_3_GROUPS["workerFlats"],
        # A town centre: flats and terraces, the first mid-rise blocks.
        "townCentre": "w4-town-centre",
        # Mid-rise blocks of flats and offices.
        "midrise": "w4-midrise",
        # Office blocks and the city towers.
        "offices": "w4-offices",
        # City towers among the last office blocks.
        "towers": "w4-towers",
        # Skyscrapers among the last towers.
        "skyscrapers": "w4-skyscrapers",
        # Downtown: skyscrapers only.
        "downtown": "w4-downtown",
    }
)

G = WORLD_4_GROUPS

# World 3's rules for the home groups World 4 starts with.
HOME_GROUP_IDS = [G.villages, G.residences, G.workerFlats]
home_groups = []
for group in WORLD_3_PROPS["groups"]:
    if group["id"] in HOME_GROUP_IDS:
        home_groups.append(group)

# The props of World 4 (P10-R03, R08; reworked at the reviewer's request, 2026-10-27): World 3's
# houses, terraces and flats, then Level Zero's city blocks and towers made of parts, then the
# skyscrapers; each section picks the groups that stand on it, so the buildings slowly grow from the
# houses to the skyscrapers. World 3's plants (Level Zero's trees).
WORLD_4_PROPS = merge(
    WORLD_3_PROPS,
    {
        "groups": concat(
            home_groups,
            [
                {
                    "id": G.townCentre,
                    "weight": 3,
                    "kinds": tile_kinds("townCentre"),
                },
                {
                    "id": G.midrise,
                    "weight": 3,
                    "kinds": tile_kinds("midrise"),
                },
                {
                    "id": G.offices,
                    "weight": 3,
                    "kinds": tile_kinds("offices"),
                },
                {
                    "id": G.towers,
                    "weight": 3,
                    "kinds": tile_kinds("towers"),
                },
                {
                    "id": G.skyscrapers,
                    "weight": 3,
                    "kinds": tile_kinds("skyscrapers"),
                },
                {"id": G.downtown, "weight": 3, "kinds": tile_kinds("downtown")},
            ],
        ),
        "cars": CAR_RULES,
    },
)
