"""Unit tests of `src/core/systems/level_run.py`."""

from types import SimpleNamespace

import pytest

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip
from core.systems.player_flight import FlightInput
from core.systems.wave_runner import Wave

SCREEN = SimpleNamespace(width=100, height=100)

SHIP = RunShip(PlanePoint(50, 10), 100, 0, 5)

STILL = FlightInput(0, 0)


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

GUN2 = ProjectileWeaponDefinition(
    "gun2", "Gun 2", "muzzle", 1, 50, 0, 50, 0, 0, 1, 5, 0, [[ShotStream(0, 0)], [ShotStream(0, 0)]]
)

ENTRY = SimpleNamespace(side="top", position=0.5)


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


def _step(
    run: LevelRun,
    dt: float = 0.5,
    move: FlightInput = STILL,
    fire: bool = False,
    switch_weapon: bool | None = None,
    bomb: bool | None = None,
) -> None:
    run.step(dt, LevelControls(move, fire, switch_weapon, bomb))


def _wave(at: float = 0, count: int = 1) -> Wave:
    return Wave(at, "still", count, 0, ENTRY)  # type: ignore[arg-type]


def test_p06_r03_a_new_run_is_playing_with_nothing_scored() -> None:
    run = _run()
    assert run.phase == "playing"
    assert run.score == 0
    assert run.supplies is None
    assert run.checkpoint is None
    assert run.result.outcome == "complete"
    assert run.result.level_id == "L1"


def test_p06_r07_the_wave_script_brings_enemies_in_as_the_level_scrolls() -> None:
    run = _run(level=_level([_wave(0), _wave(50)]))
    _step(run)
    assert len(run.enemies.enemies) == 1
    assert run.waves.triggered == 1
    for _ in range(10):
        _step(run)
    assert run.waves.triggered == 2


def test_p06_r02_firing_destroys_an_enemy_in_the_line_of_fire_and_scores_it() -> None:
    # One shot a second, 5 damage a shot: a 5-health enemy falls to the first one.
    run = _run(level=_level([_wave(0)]), kinds=[_kind(health=5)])
    for _ in range(10):
        _step(run, dt=0.1, fire=True)
    assert run.enemies.kills == 1
    assert run.score == 100
    assert run.result.destroyed == 1
    assert run.result.spawned == 1


def test_p06_r02_nothing_is_shot_while_the_player_holds_fire_back() -> None:
    run = _run(level=_level([_wave(0)]))
    for _ in range(10):
        _step(run, dt=0.1, fire=False)
    assert run.enemies.kills == 0
    assert run.shots.active_count == 0


def test_p06_r02_only_what_is_in_view_can_be_hit() -> None:
    run = _run(level=_level([_wave(0)]), in_view=lambda x, y: False)
    for _ in range(10):
        _step(run, dt=0.1, fire=True)
    assert run.enemies.kills == 0


def test_p06_r03_a_level_whose_scroll_ends_is_cleared_at_once_when_empty() -> None:
    run = _run()
    for _ in range(19):
        _step(run)
    assert run.phase == "playing"
    _step(run)
    assert run.phase == "complete"
    assert run.result.outcome == "complete"
    before = run.track.progress
    _step(run)
    assert run.track.progress == before


def test_p06_r03_a_level_with_enemies_left_completes_after_its_end_wait() -> None:
    run = _run(level=_level([_wave(0)]))
    for _ in range(20):
        _step(run)
    assert run.phase == "clearing"
    _step(run)
    assert run.phase == "complete"


def test_p06_r07_the_waves_stop_once_the_level_is_clearing() -> None:
    run = _run(level=_level([_wave(0), _wave(10000)]))
    for _ in range(20):
        _step(run)
    assert run.phase == "clearing"
    assert run.waves.finished is True


def test_p06_r09_seeking_clears_the_playfield_and_skips_the_waves_before() -> None:
    run = _run(level=_level([_wave(0), _wave(80)]))
    _step(run)
    run.seek(5)
    assert run.track.progress == pytest.approx(50)
    assert run.enemies.enemies == []
    assert run.waves.triggered == 1
    for _ in range(6):
        _step(run)
    assert len(run.enemies.enemies) == 1


def test_p06_r03_the_run_switches_the_weapon_in_use_when_asked() -> None:
    run = _run(weapons=[GUN, GUN2])
    _step(run, switch_weapon=True)
    assert run.shots.weapon is GUN2


def test_p06_r02_the_break_key_does_nothing_without_a_boss() -> None:
    run = _run()
    run.break_boss_part()
    assert run.fights.boss is None


def test_p06_r09_seeking_clears_the_shots_in_flight() -> None:
    run = _run()
    _step(run, dt=0.1, fire=True)
    assert run.shots.active_count == 1
    run.seek(0)
    assert run.shots.active_count == 0
