"""Unit tests of `src/game/view/scenery_bindings.py`."""

from game.config.scenery_look import PLAYFIELD_CAMERA
from game.config.tile_buildings import TILE
from game.view.props.prop_groups import PROP_GROUPS
from game.view.props.prop_models import PROP_MODELS
from game.view.props.road_kit import ROAD_KIT_PIECES
from game.view.scenery_bindings import SCENERY_BINDINGS, WORLD_1_LOOKS, WORLD_4_LOOKS

LEVEL_IDS = [f"world-{world}-{level}" for world in range(1, 5) for level in range(1, 6)]


def test_p06_r05_every_level_of_every_world_has_a_look():
    assert sorted(SCENERY_BINDINGS["looks"]) == sorted(LEVEL_IDS)


def test_p08_r06_the_looks_of_a_world_are_the_ones_of_its_levels():
    assert set(WORLD_1_LOOKS) == {f"world-1-{level}" for level in range(1, 6)}
    assert set(WORLD_4_LOOKS) == {f"world-4-{level}" for level in range(1, 6)}


def test_p14_r01_each_look_is_toned_for_its_world():
    looks = SCENERY_BINDINGS["looks"]
    for look in looks.values():
        assert 0 < look.tone <= 1


def test_p04_r04_the_bindings_give_the_camera_the_props_and_the_tiles():
    bindings = SCENERY_BINDINGS
    assert bindings["camera"] is PLAYFIELD_CAMERA
    assert bindings["propModels"] is PROP_MODELS
    assert bindings["propGroups"] is PROP_GROUPS
    assert bindings["propTiles"]["tile"] is TILE
    assert bindings["propTiles"]["pieces"] is ROAD_KIT_PIECES
