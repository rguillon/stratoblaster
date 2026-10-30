"""How the `props/` page groups the prop models (reviewer, 2026-10-28; phase 15: the road kit
and the tiles)"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from game.config.cars import CAR_IDS  # noqa: E402
from game.config.tile_buildings import LOT_MODELS, TILE_GROUPS  # noqa: E402
from game.view.props.prop_models import PROP_MODELS  # noqa: E402
from game.view.props.road_kit import ROAD_KIT, ROAD_KIT_NOTES, ROAD_SAMPLE_ID  # noqa: E402
from render.game_view import PropGroup  # noqa: E402


def tile_notes(models: list[Any]) -> dict[str, str]:
    """P15-R10: the tiles a model of the grid stands on, after its name."""
    result: dict[str, str] = {}
    for m in models:
        result[m.id] = str(m.tiles[0]) + "×" + str(m.tiles[1]) + " tiles"
    return result


def make_road_kit_group() -> PropGroup:
    """The road kit and its sample, for the `props/` page."""
    ids = [kit.id for kit in ROAD_KIT]
    ids.append(ROAD_SAMPLE_ID)
    notes = {}
    for key in ROAD_KIT_NOTES.keys():  # noqa: SIM118 (Transcrypt: `for k in dict` is broken)
        notes[key] = ROAD_KIT_NOTES[key]
    notes[ROAD_SAMPLE_ID] = "every piece joined to straights"
    return PropGroup("Road kit", ids, notes)


def make_tile_page() -> list[PropGroup]:
    """P15-R10: the road kit and its sample, then the models of the grid, by building group."""
    page: list[PropGroup] = [make_road_kit_group()]
    for group_id in TILE_GROUPS.keys():  # noqa: SIM118 (Transcrypt: `for k in dict` is broken)
        group = TILE_GROUPS[group_id]
        page.append(
            PropGroup(
                "Tiles: " + group_id,
                [m.id for m in group.models],
                tile_notes(group.models),
                True,
            )
        )
    page.append(
        PropGroup(
            "Tiles: lots",
            [m.id for m in LOT_MODELS],
            tile_notes(LOT_MODELS),
            True,
        )
    )
    return page


def unique(items: list[str]) -> list[str]:
    """The items once each, in their first order."""
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def make_prop_groups() -> list[PropGroup]:
    """The groups of the `props/` page: the tiles, the buildings, the cars (D-207: the shared and
    World 1 props are gone)."""
    models = list(PROP_MODELS.keys())
    cars = PropGroup(
        "Cars",
        [i for i in unique([CAR_IDS[key] for key in CAR_IDS.keys()]) if i in models],  # noqa: SIM118 (Transcrypt: iterate .keys())
    )
    tile_page = make_tile_page()
    taken: list[str] = list(cars.ids)
    for group in tile_page:
        taken.extend(group.ids)
    buildings = [model_id for model_id in models if model_id not in taken]
    result: list[PropGroup] = []
    result.extend(tile_page)
    result.append(PropGroup("Buildings", buildings))
    result.append(cars)
    return [g for g in result if len(g.ids) > 0]


PROP_GROUPS = make_prop_groups()
