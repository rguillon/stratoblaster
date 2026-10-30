"""Unit tests of `src/game/view/player_ship_models.py`."""

from game.config.player_ships import PLAYER_SHIPS
from game.view.player_ship_models import PLAYER_SHIP_MODELS


def test_each_player_ship_has_a_model_builder():
    assert set(PLAYER_SHIP_MODELS) == {"balanced", "heavy", "light"}
    assert all(callable(build) for build in PLAYER_SHIP_MODELS.values())


def test_the_models_are_keyed_by_the_ids_of_the_player_ships():
    assert set(PLAYER_SHIP_MODELS) <= {ship.id for ship in PLAYER_SHIPS["ships"]}
