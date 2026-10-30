"""Unit tests of `src/game/sim/player_build.py`."""

import pytest

from core.entities.weapon import BeamWeaponDefinition, ProjectileWeaponDefinition
from game.config.player_ships import PLAYER_SHIPS
from game.config.player_weapons import PLAYER_WEAPONS
from game.config.record import record
from game.sim.player_build import player_roster, player_weapons


def test_p02_r01_the_roster_has_the_configured_ships_and_base_speed() -> None:
    roster = player_roster(PLAYER_SHIPS)
    assert roster is not None


def test_p02_r01_each_configured_weapon_is_built_as_its_core_class() -> None:
    built = player_weapons(PLAYER_WEAPONS)
    assert [type(w) for w in built] == [
        ProjectileWeaponDefinition,
        BeamWeaponDefinition,
        ProjectileWeaponDefinition,
    ]


def test_p02_r01_an_unknown_weapon_kind_is_an_error() -> None:
    bad = record({"id": "x", "name": "X", "kind": "plasma"})
    with pytest.raises(ValueError, match="Unknown weapon kind"):
        player_weapons([bad])
