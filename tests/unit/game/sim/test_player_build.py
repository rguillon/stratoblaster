"""Unit tests of `src/game/sim/player_build.py`."""

import pytest

from core.entities.player_ship import validate_player_ship_roster
from core.entities.weapon import (
    BeamWeaponDefinition,
    ProjectileWeaponDefinition,
    validate_weapons,
)
from game.config.player_ships import PLAYER_SHIPS
from game.config.player_weapons import PLAYER_WEAPONS
from game.config.record import record
from game.sim.player_build import player_roster, player_weapons


def test_game_ship_01_the_roster_has_the_configured_ships_and_base_speed() -> None:
    roster = player_roster(PLAYER_SHIPS)
    assert roster is not None


def test_game_wpn_01_each_configured_weapon_is_built_as_its_core_class() -> None:
    built = player_weapons(PLAYER_WEAPONS)
    assert [type(w) for w in built] == [
        ProjectileWeaponDefinition,
        BeamWeaponDefinition,
        ProjectileWeaponDefinition,
    ]


def test_game_wpn_19_an_unknown_weapon_kind_is_an_error() -> None:
    bad = record({"id": "x", "name": "X", "kind": "plasma"})
    with pytest.raises(ValueError, match="Unknown weapon kind"):
        player_weapons([bad])


def test_game_ship_08_the_real_player_roster_passes_its_validation() -> None:
    """GAME-SHIP-08: the shipped ships have unique ids and valid stats."""
    validate_player_ship_roster(player_roster(PLAYER_SHIPS))


def test_game_wpn_19_the_real_player_weapons_pass_their_validation() -> None:
    """GAME-WPN-19: the shipped weapons have unique ids, levels and valid values."""
    validate_weapons(player_weapons(PLAYER_WEAPONS))
