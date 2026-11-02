# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/entities/weapon.py`."""

from typing import Any

import pytest

from core.entities.weapon import (
    BeamLevel,
    BeamWeaponDefinition,
    ProjectileWeaponDefinition,
    ShotStream,
)
from core.systems.shot_world import ShotWorld, ShotWorldOptions


def bullet(**overrides: Any) -> ProjectileWeaponDefinition:
    values: dict[str, Any] = {
        "id_": "gun",
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
    values: dict[str, Any] = {"id_": "laser", "name": "Laser", "levels": [BeamLevel(10, 2)]}
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


def _weapon(
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


def test_game_wpn_02_selecting_a_weapon_clamps_its_level_to_the_levels_it_has() -> None:
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


def test_game_wpn_11_streams_of_a_level_fire_one_after_another_in_order() -> None:
    weapon = _weapon(
        [[ShotStream(-5, 0), ShotStream(5, 0)]],
        sps=1,
    )
    world = _world(weapon)
    # Both streams fall due within 0.7 s, one shot each, in the listed order.
    world.step(0.7)
    offsets = [round(p.x - 50, 6) for p in world.projectiles]
    assert offsets == [-5, 5]


def test_game_wpn_17_a_zero_damage_hit_is_reported_as_blocked() -> None:
    weapon = ProjectileWeaponDefinition(
        "z", "Z", "muzzle", 5, 10, 0, 100, 0, 0, 1, 0, 0, [[ShotStream(0, 0)]]
    )
    world = _world(weapon)
    world.targets = [_Target(50, 20.5)]
    world.step(0.05)
    assert world.impacts[0].blocked is True
    assert world.total_damage == 0


def test_game_wpn_06_a_beam_damages_what_it_touches_and_reports_its_segments() -> None:
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


def test_game_wpn_06_a_beam_stops_firing_when_the_weapon_is_off() -> None:
    beam = BeamWeaponDefinition("b", "B", [BeamLevel(10, 4)])
    world = _world(beam)
    world.targets = [_Target(50, 30, radius=5)]
    world.firing = False
    world.step(0.5)
    assert world.beam == []
    assert world.total_damage == 0


def test_game_wpn_06_a_beam_with_nothing_in_its_way_runs_to_the_top() -> None:
    beam = BeamWeaponDefinition("b", "B", [BeamLevel(10, 4)])
    world = _world(beam)
    world.step(0.5)
    assert len(world.beam) == 1
    assert world.beam[0].y1 == pytest.approx(110)
    assert world.total_damage == 0
