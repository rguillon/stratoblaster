"""Tests of the player's shots (P03-R01..R03), `core/systems/shot_world.py`."""

import pytest

from core.entities.weapon import (
    BeamLevel,
    BeamWeaponDefinition,
    ProjectileWeaponDefinition,
    ShotStream,
)
from core.systems.shot_world import ShotWorld, ShotWorldOptions


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


def test_p03_r01_a_projectile_weapon_fires_at_its_rate() -> None:
    world = _world(_weapon(sps=5))
    world.step(0.3)
    # Two shots fall due in 0.3 s at 5 a second: one 0.3 s ago, one 0.1 s ago.
    assert [round(p.y, 6) for p in world.projectiles] == [23, 21]
    assert world.active_count == 2
    assert world.volleys == 2


def test_p03_r01_shots_leave_from_the_muzzle_or_the_centre() -> None:
    world = _world(_weapon(sps=5, launch_point="center", launch_back=2))
    world.center_x = 30
    world.center_y = 40
    world.step(0.05)
    shot = world.projectiles[0]
    assert shot.x == pytest.approx(30)
    assert shot.y == pytest.approx(38.5)


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


def test_p03_r01_a_level_without_streams_fires_nothing_but_counts_its_volleys() -> None:
    weapon = _weapon([[]], sps=5)
    world = _world(weapon)
    world.step(0.3)
    assert world.projectiles == []
    assert world.volleys == 2


def test_p03_r01_stopping_fire_clears_the_pending_shots_but_not_those_in_flight() -> None:
    world = _world(_weapon(sps=5))
    world.step(0.3)
    world.firing = False
    world.step(0.3)
    assert world.active_count == 2
    assert world.projectiles[0].y == pytest.approx(26)
    assert world.beam == []


def test_p03_r01_a_shot_that_leaves_the_playfield_is_removed() -> None:
    world = _world(_weapon(sps=1))
    world.muzzle_y = 100
    world.step(0.1)
    world.firing = False
    world.step(10)
    assert world.active_count == 0


def test_p03_r01_a_dead_shot_is_reused_for_the_next_one() -> None:
    world = _world(_weapon(sps=1))
    world.step(0.5)
    shot = world.projectiles[0]
    shot.alive = False
    world.step(0.5)
    assert len(world.projectiles) == 1
    assert world.projectiles[0] is shot
    assert shot.alive is True


def test_p03_r01_a_shot_hitting_a_target_damages_it_and_dies() -> None:
    world = _world(_weapon(sps=5, damage=5))
    target = _Target(50, 20.5)
    world.targets = [target]
    world.step(0.05)
    assert target.health == 5
    assert world.total_damage == 5
    assert world.projectiles[0].alive is False
    assert len(world.impacts) == 1
    impact = world.impacts[0]
    assert (impact.weapon_id, impact.blast_radius, impact.blocked) == ("w", 0, False)


def test_p03_r01_a_zero_damage_hit_is_reported_as_blocked() -> None:
    weapon = ProjectileWeaponDefinition(
        "z", "Z", "muzzle", 5, 10, 0, 100, 0, 0, 1, 0, 0, [[ShotStream(0, 0)]]
    )
    world = _world(weapon)
    world.targets = [_Target(50, 20.5)]
    world.step(0.05)
    assert world.impacts[0].blocked is True
    assert world.total_damage == 0


def test_p03_r02_a_blast_damages_every_target_within_its_radius() -> None:
    world = _world(_weapon(sps=5, damage=4, blast=10, radius=1))
    direct = _Target(50, 20.5)
    near = _Target(61, 20.5)
    far = _Target(64, 20.5)
    world.targets = [direct, near, far]
    world.step(0.05)
    assert (direct.health, near.health, far.health) == (6, 6, 10)
    assert world.total_damage == 8
    assert world.impacts[0].blast_radius == 10


def test_p03_r02_a_target_is_not_hit_by_a_shot_that_misses_its_radius() -> None:
    world = _world(_weapon(sps=5))
    world.targets = [_Target(60, 20.5)]
    world.step(0.05)
    assert world.targets[0].health == 10
    assert world.impacts == []
    assert world.projectiles[0].alive is True


def test_p03_r02_dead_targets_are_not_hit() -> None:
    world = _world(_weapon(sps=5))
    world.targets = [_Target(50, 20.5, health=0)]
    world.step(0.05)
    assert world.impacts == []


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


def test_p03_r01_the_shot_world_options_and_defaults_are_kept() -> None:
    options = ShotWorldOptions(100, 200, 15)
    assert (options.width, options.height, options.cull_margin) == (100, 200, 15)
    world = ShotWorld(options, _weapon())
    assert world.firing is True
    assert world.total_damage == 0
    assert world.impacts == []
