"""Data-only description of player weapons (`core.entities.weapon`)."""

from typing import Any

import pytest

from core.entities.weapon import (
    BeamLevel,
    BeamWeaponDefinition,
    ProjectileWeaponDefinition,
    ShotStream,
    find_weapon,
    validate_weapons,
    weapon_level_count,
)


def bullet(**overrides: Any) -> ProjectileWeaponDefinition:
    values: dict[str, Any] = {
        "id": "gun",
        "name": "Gun",
        "launch_point": "muzzle",
        "shots_per_second": 5,
        "launch_speed": 400,
        "acceleration": 0,
        "max_speed": 400,
        "homing_turn_rate_deg": 0,
        "homing_range": 0,
        "radius": 3,
        "damage": 1,
        "blast_radius": 0,
        "levels": [[ShotStream(0, 0)]],
    }
    values.update(overrides)
    return ProjectileWeaponDefinition(**values)


def beam(**overrides: Any) -> BeamWeaponDefinition:
    values: dict[str, Any] = {"id": "laser", "name": "Laser", "levels": [BeamLevel(10, 2)]}
    values.update(overrides)
    return BeamWeaponDefinition(**values)


def test_a_projectile_weapon_keeps_its_fields_and_defaults_its_launch_back() -> None:
    weapon = bullet()
    assert weapon.kind == "projectile"
    assert weapon.launch_point == "muzzle"
    assert weapon.launch_back == 0
    assert weapon.levels[0][0].offset_x == 0


def test_a_beam_weapon_keeps_its_levels() -> None:
    weapon = beam()
    assert weapon.kind == "beam"
    assert (weapon.levels[0].damage_per_second, weapon.levels[0].width) == (10, 2)


def test_a_valid_set_of_weapons_passes() -> None:
    validate_weapons([bullet(), beam()])
    validate_weapons([])


def test_weapon_ids_must_be_unique() -> None:
    with pytest.raises(ValueError, match='Duplicate weapon id "gun"'):
        validate_weapons([bullet(), bullet()])


def test_a_weapon_needs_a_level() -> None:
    with pytest.raises(ValueError, match="has no level"):
        validate_weapons([bullet(levels=[])])
    with pytest.raises(ValueError, match="has no level"):
        validate_weapons([beam(levels=[])])


@pytest.mark.parametrize("field", ["shots_per_second", "launch_speed", "radius", "damage"])
@pytest.mark.parametrize("value", [0, -1, float("nan")])
def test_positive_projectile_fields_must_be_positive(field: str, value: float) -> None:
    with pytest.raises(ValueError, match=field + " must be positive"):
        validate_weapons([bullet(**{field: value})])


@pytest.mark.parametrize(
    "field", ["acceleration", "homing_turn_rate_deg", "homing_range", "blast_radius"]
)
def test_other_projectile_fields_cannot_be_negative(field: str) -> None:
    with pytest.raises(ValueError, match=field + " must be >= 0"):
        validate_weapons([bullet(**{field: -1})])


def test_launch_back_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="launch_back must be >= 0"):
        validate_weapons([bullet(launch_back=-1)])


def test_an_accelerating_shot_cannot_be_capped_below_its_launch_speed() -> None:
    with pytest.raises(ValueError, match="max_speed must be >= launch_speed"):
        validate_weapons([bullet(acceleration=10, max_speed=300)])


def test_a_shot_that_does_not_accelerate_ignores_its_cap() -> None:
    validate_weapons([bullet(acceleration=0, max_speed=300)])


def test_every_level_of_a_projectile_weapon_needs_a_stream() -> None:
    with pytest.raises(ValueError, match="every level needs at least one stream"):
        validate_weapons([bullet(levels=[[ShotStream(0, 0)], []])])


@pytest.mark.parametrize(("damage", "width"), [(0, 2), (10, 0), (-1, 2)])
def test_beam_damage_and_width_must_be_positive(damage: float, width: float) -> None:
    with pytest.raises(ValueError, match="damage and width must be positive"):
        validate_weapons([beam(levels=[BeamLevel(damage, width)])])


def test_weapon_level_count_is_the_number_of_levels() -> None:
    assert (
        weapon_level_count(
            bullet(levels=[[ShotStream(0, 0)], [ShotStream(-5, 0), ShotStream(5, 0)]])
        )
        == 2
    )
    assert weapon_level_count(beam()) == 1


def test_find_weapon_returns_the_weapon_with_the_id() -> None:
    laser = beam()
    assert find_weapon([bullet(), laser], "laser") is laser


def test_find_weapon_raises_for_an_unknown_id() -> None:
    with pytest.raises(ValueError, match='Unknown weapon "nope"'):
        find_weapon([bullet()], "nope")
