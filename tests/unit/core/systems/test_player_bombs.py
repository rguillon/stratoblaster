"""Unit tests of `src/core/systems/player_bombs.py`."""

from types import SimpleNamespace

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip
from core.systems.player_bombs import ActiveBomb, BombRules, PlayerBombs
from core.systems.player_flight import FlightInput
from core.systems.ship_journey import JourneyRules
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


def _rules(max_bombs: float | None = 5) -> BombRules:
    return BombRules(start=3, damage=50, seconds=2, max_bombs=max_bombs)


def test_p11_r05_a_bomb_is_not_set_off_while_the_ship_is_scripted() -> None:
    run = _run(
        level=_level([_wave(0)]),
        kinds=[_kind(health=100)],
        bombs=BombRules(1, 50, 1),
        journey=JourneyRules(0.5, 5, 1, 50, 50, 10),
    )
    _step(run, dt=0.1, bomb=True)
    assert run.bombs.count == 1
    assert run.enemies.enemies[0].health == 100


def test_gd32_a_new_run_starts_with_the_rule_bombs() -> None:
    bombs = PlayerBombs(_rules())
    assert bombs.count == 3
    assert bombs.active is None
    assert bombs.fired == 0


def test_gd32_bombs_kept_from_the_level_before_override_the_start() -> None:
    assert PlayerBombs(_rules(), count=1).count == 1


def test_p11_r05_a_press_sets_one_bomb_off_and_uses_one_up() -> None:
    bombs = PlayerBombs(_rules())
    assert bombs.fire(10, 20) is True
    assert bombs.count == 2
    assert bombs.fired == 1
    active = bombs.active
    assert isinstance(active, ActiveBomb)
    assert (active.x, active.y, active.age, active.seconds) == (10, 20, 0, 2)


def test_p11_r05_no_bomb_goes_off_while_one_is_active() -> None:
    bombs = PlayerBombs(_rules())
    bombs.fire(0, 0)
    assert bombs.fire(0, 0) is False
    assert bombs.count == 2


def test_p11_r05_no_bomb_goes_off_with_none_left() -> None:
    bombs = PlayerBombs(_rules(), count=0)
    assert bombs.fire(0, 0) is False
    assert bombs.fired == 0


def test_p11_r05_a_bomb_goes_off_for_its_seconds_then_another_can_fire() -> None:
    bombs = PlayerBombs(_rules())
    bombs.fire(0, 0)
    bombs.step(1)
    assert bombs.active is not None
    assert bombs.active.age == 1
    bombs.step(1)
    assert bombs.active is None
    assert bombs.fire(0, 0) is True


def test_p11_r05_stepping_with_no_bomb_does_nothing() -> None:
    bombs = PlayerBombs(_rules())
    bombs.step(5)
    assert bombs.active is None


def test_p11_r07_a_bomb_bonus_adds_one_up_to_the_most() -> None:
    bombs = PlayerBombs(_rules(max_bombs=4))
    assert bombs.add() is True
    assert bombs.count == 4
    assert bombs.add() is False
    assert bombs.count == 4


def test_p11_r07_a_bomb_bonus_has_no_limit_without_a_most() -> None:
    bombs = PlayerBombs(_rules(max_bombs=None))
    for _ in range(10):
        assert bombs.add() is True
    assert bombs.count == 13


def test_p11_r05_a_lost_life_tops_the_bombs_back_up_to_the_start() -> None:
    bombs = PlayerBombs(_rules(), count=0)
    bombs.refill()
    assert bombs.count == 3


def test_p11_r05_a_lost_life_keeps_more_bombs_than_the_start() -> None:
    bombs = PlayerBombs(_rules(), count=5)
    bombs.refill()
    assert bombs.count == 5
