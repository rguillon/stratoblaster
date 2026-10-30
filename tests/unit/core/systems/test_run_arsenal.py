"""Unit tests of `src/core/systems/run_arsenal.py`."""

from types import SimpleNamespace

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelCheckpoint, LevelControls, LevelRunOptions, RunShip
from core.systems.player_flight import FlightInput
from core.systems.run_arsenal import RunArsenal, WeaponLevels
from core.systems.shot_world import ShotWorld, ShotWorldOptions

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


def _weapon(id: str, levels: int = 2) -> ProjectileWeaponDefinition:
    return ProjectileWeaponDefinition(
        id,
        id,
        "muzzle",
        5,
        10,
        0,
        100,
        0,
        0,
        1,
        1,
        0,
        [[ShotStream(0, 0)] for _ in range(levels)],
    )


A = _weapon("a")

B = _weapon("b")


def _arsenal(weapons: list[ProjectileWeaponDefinition], start_level: float = 1) -> RunArsenal:
    shots = ShotWorld(ShotWorldOptions(100, 100, 10), weapons[0] if weapons else A)
    shots.select(shots.weapon, start_level)
    return RunArsenal(shots, weapons, start_level)


def test_p07_r08_a_run_can_start_with_the_weapons_kept_from_before() -> None:
    run = _run(weapons=[GUN, GUN2], start_weapons=WeaponLevels("gun2", {"gun": 2}))
    assert run.shots.weapon is GUN2
    _step(run, switch_weapon=True)
    assert run.shots.weapon is GUN
    assert run.shots.level == 2


def test_p07_r08_a_checkpoint_keeps_where_the_run_can_resume_from() -> None:
    weapons = WeaponLevels("gun", {"gun": 2})
    checkpoint = LevelCheckpoint(120, 1, weapons, 900)
    assert (checkpoint.progress, checkpoint.bosses_passed) == (120, 1)
    assert checkpoint.weapons is weapons
    assert checkpoint.score == 900


def test_p06_r07_switching_moves_to_the_next_weapon_at_its_start_level() -> None:
    arsenal = _arsenal([A, B], start_level=2)
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 2


def test_p06_r07_switching_wraps_around_and_keeps_each_weapons_level() -> None:
    arsenal = _arsenal([A, B])
    arsenal.level_up(1)
    arsenal.switch_weapon()
    arsenal.level_up(1)
    assert arsenal._shots.level == 2
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 2


def test_p06_r07_a_single_weapon_switches_to_itself_with_its_level_kept() -> None:
    arsenal = _arsenal([A])
    arsenal.level_up(1)
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2


def test_p06_r07_switching_with_no_weapons_list_keeps_the_weapon() -> None:
    arsenal = _arsenal([])
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A


def test_p06_r07_a_weapon_not_in_the_list_switches_to_the_first_one() -> None:
    arsenal = _arsenal([B])
    arsenal._shots.select(A, 1)
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is B


def test_p06_r07_level_up_adds_levels_up_to_the_last_one() -> None:
    arsenal = _arsenal([A])
    arsenal.level_up(0)
    assert arsenal._shots.level == 1
    arsenal.level_up(-1)
    assert arsenal._shots.level == 1
    arsenal.level_up(5)
    assert arsenal._shots.level == 2


def test_p07_r08_a_snapshot_keeps_the_weapon_and_the_level_of_each_weapon_used() -> None:
    arsenal = _arsenal([A, B])
    arsenal.level_up(1)
    arsenal.switch_weapon()
    arsenal.level_up(1)
    arsenal.level_up(0)
    snap = arsenal.snapshot()
    assert snap.weapon == "b"
    assert snap.levels == {"a": 2, "b": 2}


def test_p07_r08_restore_brings_back_the_snapshot_weapons_and_levels() -> None:
    saved = WeaponLevels("b", {"a": 2, "b": 1})
    arsenal = _arsenal([A, B])
    arsenal.restore(saved)
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 1
    arsenal.switch_weapon()
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2


def test_p07_r08_restore_with_an_unknown_weapon_keeps_the_current_one() -> None:
    arsenal = _arsenal([A, B])
    arsenal.restore(WeaponLevels("zzz", {"a": 2}))
    assert arsenal._shots.weapon is A
    assert arsenal._shots.level == 2


def test_p07_r08_restore_without_a_saved_level_starts_the_weapon_at_its_start() -> None:
    arsenal = _arsenal([A, B], start_level=1)
    arsenal.restore(WeaponLevels("b", {}))
    assert arsenal._shots.weapon is B
    assert arsenal._shots.level == 1


def test_p07_r08_restoring_forgets_the_levels_held_before() -> None:
    arsenal = _arsenal([A, B])
    arsenal.level_up(1)
    arsenal.restore(WeaponLevels("a", {}))
    arsenal.switch_weapon()
    arsenal.switch_weapon()
    assert arsenal._shots.level == 1
