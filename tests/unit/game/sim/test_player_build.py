# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/player_build.py`."""

import pytest

from core.entities.player_ship import PlayerShipRoster
from core.entities.weapon import (
    BeamWeaponDefinition,
    ProjectileWeaponDefinition,
)
from game.config.player_ships import PLAYER_SHIPS
from game.config.player_weapons import PLAYER_WEAPONS
from game.config.record import record
from game.sim.player_build import player_roster, player_weapons


def _check_roster(roster: PlayerShipRoster) -> None:
    """GAME-SHIP-08: ships, unique ids, positive speeds and positive whole healths."""
    ids = [ship.id for ship in roster.ships]
    assert ids, "a roster needs at least one player ship"
    assert len(set(ids)) == len(ids), "duplicate player ship ids: " + str(ids)
    assert roster.base_speed_px_per_sec > 0
    for ship in roster.ships:
        assert ship.max_speed_factor > 0, ship.id
        assert ship.max_health > 0, ship.id
        assert float(ship.max_health).is_integer(), ship.id


def _check_projectile(weapon: ProjectileWeaponDefinition) -> None:
    positive = {
        "shots_per_second": weapon.shots_per_second,
        "launch_speed": weapon.launch_speed,
        "radius": weapon.radius,
        "damage": weapon.damage,
    }
    for key, value in positive.items():
        assert value > 0, weapon.id + ": " + key
    non_negative = {
        "acceleration": weapon.acceleration,
        "homing_turn_rate_deg": weapon.homing_turn_rate_deg,
        "homing_range": weapon.homing_range,
        "blast_radius": weapon.blast_radius,
        "launch_back": weapon.launch_back,
    }
    for key, value in non_negative.items():
        assert value >= 0, weapon.id + ": " + key
    if weapon.acceleration > 0:
        assert weapon.max_speed >= weapon.launch_speed, weapon.id
    for streams in weapon.levels:
        assert streams, weapon.id + ": every level needs at least one stream"


def _check_weapons(weapons: list[ProjectileWeaponDefinition | BeamWeaponDefinition]) -> None:
    """GAME-WPN-19: unique ids, levels, and numbers a shot can fly with."""
    ids = [weapon.id for weapon in weapons]
    assert len(set(ids)) == len(ids), "duplicate weapon ids: " + str(ids)
    for weapon in weapons:
        assert weapon.levels, weapon.id + " has no level"
        if isinstance(weapon, ProjectileWeaponDefinition):
            _check_projectile(weapon)
        else:
            for level in weapon.levels:
                assert level.damage_per_second > 0, weapon.id
                assert level.width > 0, weapon.id


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
    _check_roster(player_roster(PLAYER_SHIPS))


def test_game_wpn_19_the_real_player_weapons_pass_their_validation() -> None:
    """GAME-WPN-19: the shipped weapons have unique ids, levels and valid values."""
    _check_weapons(player_weapons(PLAYER_WEAPONS))
