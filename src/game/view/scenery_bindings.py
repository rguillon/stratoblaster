"""How this game's generated levels look (P04, P06, P08, P09, P10), ported from
`scenery-bindings.ts`: the scenery looks of every level, toned by world, and the prop models,
groups and road tiles the scenery is built from.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.readability import READABILITY
from game.config.scenery_look import BASE_SCENERY_LOOK, PLAYFIELD_CAMERA
from game.config.tile_buildings import TILE
from game.config.world_1.looks import (
    LEVEL_1_1_LOOK,
    LEVEL_1_2_LOOK,
    LEVEL_1_3_LOOK,
    LEVEL_1_4_LOOK,
    LEVEL_1_5_LOOK,
)
from game.config.world_1.scenery_coast import LEVEL_1_1, LEVEL_1_2
from game.config.world_1.scenery_country import LEVEL_1_3
from game.config.world_1.scenery_desert import LEVEL_1_4, LEVEL_1_5
from game.config.world_2.looks import (
    LEVEL_2_1_LOOK,
    LEVEL_2_2_LOOK,
    LEVEL_2_3_LOOK,
    LEVEL_2_4_LOOK,
    LEVEL_2_5_LOOK,
)
from game.config.world_2.scenery import (
    LEVEL_2_1,
    LEVEL_2_2,
    LEVEL_2_3,
    LEVEL_2_4,
    LEVEL_2_5,
)
from game.config.world_3.looks import (
    LEVEL_3_1_LOOK,
    LEVEL_3_2_LOOK,
    LEVEL_3_3_LOOK,
    LEVEL_3_4_LOOK,
    LEVEL_3_5_LOOK,
)
from game.config.world_3.scenery import (
    LEVEL_3_1,
    LEVEL_3_2,
    LEVEL_3_3,
    LEVEL_3_4,
    LEVEL_3_5,
)
from game.config.world_4.looks import (
    LEVEL_4_1_LOOK,
    LEVEL_4_2_LOOK,
    LEVEL_4_3_LOOK,
    LEVEL_4_4_LOOK,
    LEVEL_4_5_LOOK,
)
from game.config.world_4.scenery import (
    LEVEL_4_1,
    LEVEL_4_2,
    LEVEL_4_3,
    LEVEL_4_4,
    LEVEL_4_5,
)
from game.sim.sky_build import sky_script
from game.view.props.prop_groups import PROP_GROUPS
from game.view.props.prop_models import PROP_MODELS
from game.view.props.road_kit import ROAD_KIT_PIECES
from game.view.readability_view import all_toned

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

TONES = READABILITY.tones
CAMERA = PLAYFIELD_CAMERA

# World 1 (P06-R05): one look per level.
WORLD_1_LOOKS = {
    LEVEL_1_1.id: LEVEL_1_1_LOOK,
    LEVEL_1_2.id: LEVEL_1_2_LOOK,
    LEVEL_1_3.id: LEVEL_1_3_LOOK,
    LEVEL_1_4.id: LEVEL_1_4_LOOK,
    LEVEL_1_5.id: LEVEL_1_5_LOOK,
}

# World 2 (P08-R06): one look per level, with its time of day and clouds.
WORLD_2_LOOKS = {
    LEVEL_2_1.id: LEVEL_2_1_LOOK,
    LEVEL_2_2.id: LEVEL_2_2_LOOK,
    LEVEL_2_3.id: LEVEL_2_3_LOOK,
    LEVEL_2_4.id: LEVEL_2_4_LOOK,
    LEVEL_2_5.id: LEVEL_2_5_LOOK,
}

# World 3 (P09-R04): one look per level, with its time of day, clouds, rain and lightning.
WORLD_3_LOOKS = {
    LEVEL_3_1.id: LEVEL_3_1_LOOK,
    LEVEL_3_2.id: LEVEL_3_2_LOOK,
    LEVEL_3_3.id: LEVEL_3_3_LOOK,
    LEVEL_3_4.id: LEVEL_3_4_LOOK,
    LEVEL_3_5.id: LEVEL_3_5_LOOK,
}

# World 4 (P10-R04): one look per level, with its time of day, clouds, ash and embers.
WORLD_4_LOOKS = {
    LEVEL_4_1.id: LEVEL_4_1_LOOK,
    LEVEL_4_2.id: LEVEL_4_2_LOOK,
    LEVEL_4_3.id: LEVEL_4_3_LOOK,
    LEVEL_4_4.id: LEVEL_4_4_LOOK,
    LEVEL_4_5.id: LEVEL_4_5_LOOK,
}


def _with_sky_script(look: Any) -> Any:
    """`look` (a copy, as `toned` makes it) with its sky script mapped to the core's classes
    (P08-R04): its `atmosphere` is read by `core/scenery/sky_look.py`.
    """
    if look.atmosphere != None:  # noqa: E711 (undefined: a look without a sky script)
        look.atmosphere = sky_script(look.atmosphere)
    return look


def _all_looks() -> dict[str, Any]:
    """The looks of every world, each world's ground and props darkened (Phase 14, P14-R01)."""
    looks: dict[str, Any] = {}
    looks.update(all_toned(WORLD_1_LOOKS, TONES.world1))
    looks.update(all_toned(WORLD_2_LOOKS, TONES.world2))
    looks.update(all_toned(WORLD_3_LOOKS, TONES.world3))
    looks.update(all_toned(WORLD_4_LOOKS, TONES.world4))
    for look_id, look in looks.items():
        looks[look_id] = _with_sky_script(look)
    return looks


# How this game's generated levels look (P04, P06, P08, P09, P10).
SCENERY_BINDINGS = {
    "camera": CAMERA,
    "looks": _all_looks(),
    "propModels": PROP_MODELS,
    "propGroups": PROP_GROUPS,
    "propTiles": {"tile": TILE, "look": BASE_SCENERY_LOOK.roads.tiles, "pieces": ROAD_KIT_PIECES},
}
