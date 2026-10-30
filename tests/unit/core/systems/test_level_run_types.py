"""Unit tests of `src/core/systems/level_run_types.py`."""

from types import SimpleNamespace

import pytest

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
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

SCREEN = SimpleNamespace(width=100, height=100)

SHIP = RunShip(PlanePoint(50, 10), 100, 0, 5)


class _Bounds:
    min_y = 0
    max_y = 100
    center_x = 50

    def half_width_at(self, y: float) -> float:
        return 50


class Still(Enemy):
    """An enemy that does nothing but stand where it is put."""

    def update(self, ctx: object, dt: float) -> None:  # type: ignore[override]
        pass


def _kind(health: float = 10, points: float = 100, y: float = 30) -> EnemyKindDefinition:
    return EnemyKindDefinition(
        "still",
        "Still",
        lambda area: [Still(50, y, EnemyStats("still", 4, health, points))],
    )


GUN = ProjectileWeaponDefinition(
    "gun", "Gun", "muzzle", 1, 50, 0, 50, 0, 0, 1, 5, 0, [[ShotStream(0, 0)], [ShotStream(0, 0)]]
)


def _level(
    waves: list | None = None,
    seconds: float = 10,
    bosses: list | None = None,
) -> GameLevel:
    scenery = SimpleNamespace(scroll_speed=10, sections=[SimpleNamespace(seconds=seconds)])
    return GameLevel("L1", scenery, waves or [], EnemyDifficulty(1, 1), bosses)  # type: ignore[arg-type]


def _run(**overrides: object) -> LevelRun:
    options: dict = dict(
        screen=SCREEN,
        level=_level(),
        kinds=[_kind()],
        weapon=GUN,
        weapon_level=1,
        ship=SHIP,
        bounds=_Bounds(),
        cull_margin=10,
        max_enemy_age=60,
        end_wait=1,
        seed=1,
    )
    options.update(overrides)
    return LevelRun(LevelRunOptions(**options))  # type: ignore[arg-type]


def test_p07_r08_a_run_resumes_from_its_checkpoint() -> None:
    checkpoint = LevelCheckpoint(50, 0, WeaponLevels("gun", {"gun": 2}), 300)
    run = _run(checkpoint=checkpoint, weapon_level=1)
    assert run.track.progress == pytest.approx(50)
    assert run.score == 300
    assert run.shots.level == 2
    assert run.checkpoint is checkpoint


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
