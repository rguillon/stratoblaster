"""Unit tests of `src/core/entities/weapon.py`."""

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
from core.systems.shot_world import ShotWorld, ShotWorldOptions


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


class _Target:
    def __init__(self, x: float, y: float, radius: float = 2, health: float = 10) -> None:
        self.id = 0
        self.x = x
        self.y = y
        self.radius = radius
        self.health = health
        self.max_health = health


def _weapon(  # noqa: PLR0917 (positional fixtures)
    levels: list[list[ShotStream]] | None = None,
    sps: float = 5,
    damage: float = 5,
    blast: float = 0,
    radius: float = 1,
    launch_point: str = "muzzle",
    launch_back: float = 0,
) -> ProjectileWeaponDefinition:
    if levels is None:
        levels = [[ShotStream(0, 0)]]
    return ProjectileWeaponDefinition(
        "w",
        "W",
        launch_point,
        sps,
        10,
        0,
        100,
        0,
        0,
        radius,
        damage,
        blast,
        levels,
        launch_back,
    )


def _world(weapon: ProjectileWeaponDefinition | BeamWeaponDefinition) -> ShotWorld:
    world = ShotWorld(ShotWorldOptions(100, 100, 10), weapon)
    world.muzzle_x = 50
    world.muzzle_y = 20
    return world


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


def test_p03_r01_selecting_a_weapon_clamps_its_level_to_the_levels_it_has() -> None:
    weapon = _weapon([[ShotStream(0, 0)], [ShotStream(0, 0)]])
    world = _world(weapon)
    world.select(weapon, 0)
    assert world.level == 1
    world.select(weapon, 99)
    assert world.level == 2
    world.select(weapon, 1.4)
    assert world.level == 1
    world.select(weapon, 1.5)
    assert world.level == 2
    assert world.weapon is weapon


def test_p03_r01_streams_of_a_level_fire_one_after_another_in_order() -> None:
    weapon = _weapon(
        [[ShotStream(-5, 0), ShotStream(5, 0)]],
        sps=1,
    )
    world = _world(weapon)
    # Both streams fall due within 0.7 s, one shot each, in the listed order.
    world.step(0.7)
    offsets = [round(p.x - 50, 6) for p in world.projectiles]
    assert offsets == [-5, 5]


def test_p03_r01_a_zero_damage_hit_is_reported_as_blocked() -> None:
    weapon = ProjectileWeaponDefinition(
        "z", "Z", "muzzle", 5, 10, 0, 100, 0, 0, 1, 0, 0, [[ShotStream(0, 0)]]
    )
    world = _world(weapon)
    world.targets = [_Target(50, 20.5)]
    world.step(0.05)
    assert world.impacts[0].blocked is True
    assert world.total_damage == 0


def test_p03_r01_a_beam_damages_what_it_touches_and_reports_its_segments() -> None:
    beam = BeamWeaponDefinition("b", "B", [BeamLevel(10, 4), BeamLevel(20, 8)])
    world = _world(beam)
    target = _Target(50, 30, radius=5)
    world.targets = [target]
    world.select(beam, 1)
    world.step(0.5)
    assert target.health == 5
    assert world.total_damage == 5
    assert [s.hit for s in world.beam] == [True]
    assert world.projectiles == []


def test_p03_r02_a_beam_stops_firing_when_the_weapon_is_off() -> None:
    beam = BeamWeaponDefinition("b", "B", [BeamLevel(10, 4)])
    world = _world(beam)
    world.targets = [_Target(50, 30, radius=5)]
    world.firing = False
    world.step(0.5)
    assert world.beam == []
    assert world.total_damage == 0


def test_p03_r02_a_beam_with_nothing_in_its_way_runs_to_the_top() -> None:
    beam = BeamWeaponDefinition("b", "B", [BeamLevel(10, 4)])
    world = _world(beam)
    world.step(0.5)
    assert len(world.beam) == 1
    assert world.beam[0].y1 == pytest.approx(110)
    assert world.total_damage == 0
