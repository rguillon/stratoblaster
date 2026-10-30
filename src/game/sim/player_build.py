"""Builds the core types of the player's ships and weapons (P02, P03) from their config records:
the one place where the config meets `core/` for them. Mapping rules are in `config_build.py`.

`PLAYER_SHIPS` and `PLAYER_WEAPONS` keep the TypeScript's camelCase shape; `core/` dispatches
projectile and beam weapons with `isinstance`, so a weapon is built as its class here.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.player_ship import PlayerShipDefinition, PlayerShipRoster
from core.entities.weapon import (
    BeamLevel,
    BeamWeaponDefinition,
    ProjectileWeaponDefinition,
    ShotStream,
)
from game.sim.config_build import mapped

__pragma__("skip")
from typing import Any  # noqa: E402

from core.entities.weapon import WeaponDefinition  # noqa: E402

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
__pragma__("noskip")


def _ship(ship: ConfigRecord) -> PlayerShipDefinition:
    return PlayerShipDefinition(
        ship.id,
        ship["name"],
        ship.maxSpeedFactor,
        ship.maxHealth,
    )


def player_roster(config: ConfigRecord) -> PlayerShipRoster:
    """The ships the player can fly, as `core/` reads them (P02-R01..R03)."""
    return PlayerShipRoster(config.baseSpeedPxPerSec, mapped(config.ships, _ship))


def _stream(stream: ConfigRecord) -> ShotStream:
    return ShotStream(stream.offsetX, stream.angleDeg)


def _projectile(weapon: ConfigRecord) -> ProjectileWeaponDefinition:
    levels: list[list[ShotStream]] = []
    for streams in weapon.levels:
        levels.append(mapped(streams, _stream))
    launch_back = weapon.launchBack
    if launch_back == None:  # noqa: E711 (omitted: 0, as the TypeScript)
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
    """The core class of a config weapon, by its `kind`."""
    kind = weapon.kind
    if kind == "projectile":
        return _projectile(weapon)
    if kind == "beam":
        return _beam(weapon)
    raise ValueError("Unknown weapon kind " + kind)


def player_weapons(configs: list[ConfigRecord]) -> list[WeaponDefinition]:
    """The weapons every player ship can fire, as `core/` reads them (P03)."""
    result: list[WeaponDefinition] = []
    for weapon in configs:
        result.append(_weapon(weapon))
    return result
