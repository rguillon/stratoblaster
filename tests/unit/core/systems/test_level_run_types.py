"""Tests of the data a level run takes and gives (P06-R03), `core/systems/level_run_types.py`."""

from core.entities.muzzle import PlanePoint
from core.systems.level_run_types import (
    LandedHit,
    LevelCheckpoint,
    LevelControls,
    LevelResult,
    LevelRunOptions,
    RunShip,
    Supplies,
)
from core.systems.player_flight import FlightInput
from core.systems.run_arsenal import WeaponLevels


def test_p06_r03_a_run_ship_has_a_health_only_when_given_one() -> None:
    ship = RunShip(PlanePoint(1, 2), 100, 0.5, 6)
    assert (ship.start.x, ship.start.y, ship.max_speed) == (1, 2, 100)
    assert (ship.acceleration_seconds, ship.muzzle_offset) == (0.5, 6)
    assert ship.max_health is None
    assert RunShip(PlanePoint(0, 0), 1, 0, 0, 80).max_health == 80


def test_p06_r03_the_controls_switch_weapon_and_bomb_are_optional() -> None:
    controls = LevelControls(FlightInput(1, 0), True)
    assert (controls.move.x, controls.fire) == (1, True)
    assert controls.switch_weapon is None
    assert controls.bomb is None


def test_p06_r03_a_level_result_is_complete_without_a_checkpoint_or_high_score() -> None:
    result = LevelResult("L1", 3, 5, "complete", 200)
    assert (result.level_id, result.destroyed, result.spawned) == ("L1", 3, 5)
    assert (result.outcome, result.score) == ("complete", 200)
    assert result.new_high_score is None
    assert result.checkpoint is None


def test_p07_r08_a_checkpoint_keeps_where_the_run_can_resume_from() -> None:
    weapons = WeaponLevels("gun", {"gun": 2})
    checkpoint = LevelCheckpoint(120, 1, weapons, 900)
    assert (checkpoint.progress, checkpoint.bosses_passed) == (120, 1)
    assert checkpoint.weapons is weapons
    assert checkpoint.score == 900


def test_p06_r03_a_landed_hit_records_what_it_did() -> None:
    hit = LandedHit("laser", 1, 2, "hit")
    assert (hit.kind, hit.x, hit.y, hit.event) == ("laser", 1, 2, "hit")


def test_p06_r03_supplies_carry_lives_and_bombs_between_levels() -> None:
    supplies = Supplies(2, 1)
    assert (supplies.lives, supplies.bombs) == (2, 1)


def test_p06_r03_the_options_default_their_optional_parts_to_none() -> None:
    options = LevelRunOptions(
        screen=None,  # type: ignore[arg-type]
        level=None,  # type: ignore[arg-type]
        kinds=[],
        weapon=None,  # type: ignore[arg-type]
        weapon_level=1,
        ship=None,  # type: ignore[arg-type]
        bounds=None,  # type: ignore[arg-type]
        cull_margin=10,
        max_enemy_age=60,
        end_wait=2,
        seed=7,
    )
    assert (options.cull_margin, options.max_enemy_age, options.end_wait, options.seed) == (
        10,
        60,
        2,
        7,
    )
    for name in (
        "weapons",
        "start_weapons",
        "start_supplies",
        "eye",
        "in_view",
        "bonuses",
        "bombs",
        "hull",
        "boss_kinds",
        "boss_rules",
        "checkpoint",
        "journey",
    ):
        assert getattr(options, name) is None
