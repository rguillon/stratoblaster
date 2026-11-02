# Copyright (c) 2026 Renaud Guillon
"""Builds the core types of the player's ships and weapons from their config records.

The one place where the config meets `core/` for them, the weapons staying data (GAME-WPN-19).
Mapping rules are in `config_build.py`.

`PLAYER_SHIPS` and `PLAYER_WEAPONS` keep camelCase keys; `core/` dispatches
projectile and beam weapons with `isinstance`, so a weapon is built as its class here.
"""

from core.entities.player_ship import PlayerShipDefinition, PlayerShipRoster
from core.entities.weapon import (
    BeamLevel,
    BeamWeaponDefinition,
    ProjectileWeaponDefinition,
    ShotStream,
)
from game.sim.config_build import mapped

# isort: split
# __pragma__ ("skip")
from typing import Any

from core.entities.weapon import WeaponDefinition

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
# __pragma__ ("noskip")


def _ship(ship: ConfigRecord) -> PlayerShipDefinition:
    return PlayerShipDefinition(
        ship.id,
        ship["name"],
        ship.maxSpeedFactor,
        ship.maxHealth,
    )


def player_roster(config: ConfigRecord) -> PlayerShipRoster:
    """Return the ships the player can fly, as `core/` reads them (GAME-SHIP-01)."""
    return PlayerShipRoster(config.baseSpeedPxPerSec, mapped(config.ships, _ship))


def _stream(stream: ConfigRecord) -> ShotStream:
    return ShotStream(stream.offsetX, stream.angleDeg)


def _projectile(weapon: ConfigRecord) -> ProjectileWeaponDefinition:
    levels: list[list[ShotStream]] = [mapped(streams, _stream) for streams in weapon.levels]
    launch_back = weapon.launchBack
    if launch_back == None:
        launch_back = 0
    return ProjectileWeaponDefinition(
        weapon.id,
        weapon["name"],
        weapon.launchPoint,
        weapon.shotsPerSecond,
        weapon.launchSpeed,
        weapon.acceleration,
        weapon.maxSpeed,
        weapon.homingTurnRateDeg,
        weapon.homingRange,
        weapon.radius,
        weapon.damage,
        weapon.blastRadius,
        levels,
        launch_back,
    )


def _beam_level(level: ConfigRecord) -> BeamLevel:
    return BeamLevel(level.damagePerSecond, level.width)


def _beam(weapon: ConfigRecord) -> BeamWeaponDefinition:
    return BeamWeaponDefinition(weapon.id, weapon["name"], mapped(weapon.levels, _beam_level))


def _weapon(weapon: ConfigRecord) -> WeaponDefinition:
    """Return the core class of a config weapon, by its `kind`."""
    kind = weapon.kind
    if kind == "projectile":
        return _projectile(weapon)
    if kind == "beam":
        return _beam(weapon)
    raise ValueError("Unknown weapon kind " + kind)


def player_weapons(configs: list[ConfigRecord]) -> list[WeaponDefinition]:
    """Return the weapons every player ship can fire, as `core/` reads them (GAME-WPN-01)."""
    result: list[WeaponDefinition] = [_weapon(weapon) for weapon in configs]
    return result
