"""Unit tests of `src/game/config/world_4/props.py`."""

from game.config.world_4.props import WORLD_4_ROADS


def test_the_roads_of_world_4_have_main_roads_and_tiles() -> None:
    assert WORLD_4_ROADS.mainRoads >= 1
    assert WORLD_4_ROADS.tiles
    assert WORLD_4_ROADS.mainWidth > WORLD_4_ROADS.crossWidth > 0
