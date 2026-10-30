"""Unit tests of `src/core/systems/player_hull.py`."""

from types import SimpleNamespace

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyBulletSpec, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.bonus_world import BonusChance, BonusRules
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip, Supplies
from core.systems.player_bombs import BombRules
from core.systems.player_flight import FlightInput
from core.systems.player_hull import HullDamage, HullRules, PlayerHull
from core.systems.ship_journey import JourneyRules

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


def _supplies(run: LevelRun) -> tuple[float, float] | None:
    supplies = run.supplies
    return None if supplies is None else (supplies.lives, supplies.bombs)


def _rules(lives: float = 3, max_lives: float | None = None) -> HullRules:
    return HullRules(
        lives,
        2,
        3,
        HullDamage(bullet=10, missile=20, laser=5, collision=30),
        15,
        max_lives,
    )


def test_p06_r09_seeking_after_the_game_is_over_does_nothing() -> None:
    run = _run(hull=HullRules(1, 0, 3, HullDamage(200, 0, 0, 0), 0))
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run)
    assert run.phase == "over"
    before = run.track.progress
    run.seek(5)
    assert run.track.progress == before


def test_p06_r02_the_ship_cannot_fly_once_the_game_is_over() -> None:
    run = _run(hull=HullRules(1, 0, 3, HullDamage(200, 0, 0, 0), 0))
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run)
    x = run.ship.x
    _step(run, move=FlightInput(1, 0))
    assert run.ship.x == x


def test_p06_r02_running_out_of_lives_ends_the_game_and_keeps_the_checkpoint_empty() -> None:
    run = _run(hull=HullRules(1, 0, 3, HullDamage(200, 0, 0, 0), 0))
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run)
    assert run.phase == "over"
    assert run.hits[0].event == "gameOver"
    assert run.result.outcome == "over"
    assert run.result.checkpoint is None
    assert _supplies(run) == (0, 0)


def test_p11_r05_a_lost_life_tops_the_bombs_back_up() -> None:
    run = _run(
        hull=HullRules(3, 0, 3, HullDamage(100, 0, 0, 0), 0),
        bombs=BombRules(1, 50, 1),
        start_supplies=Supplies(3, 0),
    )
    assert run.bombs.count == 0
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run, dt=0.1)
    assert run.hits[0].event == "lifeLost"
    assert run.bombs.count == 1
    assert _supplies(run) == (2, 1)


def test_p11_r03_the_run_starts_with_the_lives_and_bombs_kept_before() -> None:
    run = _run(
        hull=HullRules(3, 0, 3, HullDamage(0, 0, 0, 0), 0),
        bombs=BombRules(1, 50, 1),
        start_supplies=Supplies(2, 0),
    )
    assert run.hull.lives == 2
    assert run.bombs.count == 0
    assert _supplies(run) == (2, 0)


def test_p11_r05_no_hit_lands_while_a_bomb_is_going_off() -> None:
    run = _run(
        hull=HullRules(3, 0, 3, HullDamage(30, 0, 0, 0), 0),
        bombs=BombRules(1, 0, 5),
    )
    run.bombs.fire(0, 0)
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run, dt=0.1)
    assert run.hits == []
    assert run.hull.health == 100


def test_p06_r02_no_hit_lands_while_the_journey_scripts_the_ship() -> None:
    run = _run(
        hull=HullRules(3, 0, 3, HullDamage(30, 0, 0, 0), 0),
        journey=JourneyRules(10, 5, 1, 50, 50, 10),
    )
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run, dt=0.1)
    assert run.journey.scripted is True
    assert run.hits == []


def test_p11_r07_a_life_bonus_without_overflow_points_scores_nothing_at_the_most() -> None:
    run = _run(
        hull=HullRules(3, 0, 3, HullDamage(0, 0, 0, 0), 0, max_lives=3),
        bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5),
    )
    run.bonuses.place("life", PlanePoint(50, 10))
    _step(run, dt=0.1)
    assert run.hull.lives == 3
    assert run.score == 0


def test_gd20_a_new_hull_starts_with_full_health_and_the_rule_lives() -> None:
    hull = PlayerHull(_rules(), 100)
    assert (hull.health, hull.max_health, hull.lives, hull.invincible) == (100, 100, 3, 0)
    assert hull.out is False


def test_gd20_lives_kept_from_the_level_before_override_the_rules() -> None:
    assert PlayerHull(_rules(), 100, lives=1).lives == 1


def test_gd22_a_hit_takes_health_and_makes_the_ship_invincible() -> None:
    hull = PlayerHull(_rules(), 100)
    assert hull.hit(40) == "hit"
    assert hull.health == 60
    assert hull.invincible == 2


def test_gd22_hits_are_ignored_while_invincible() -> None:
    hull = PlayerHull(_rules(), 100)
    hull.hit(40)
    assert hull.hit(40) == "ignored"
    assert hull.health == 60


def test_gd22_invincibility_counts_down_and_stops_at_zero() -> None:
    hull = PlayerHull(_rules(), 100)
    hull.hit(10)
    hull.step(0.5)
    assert hull.invincible == 1.5
    hull.step(5)
    assert hull.invincible == 0
    assert hull.hit(10) == "hit"


def test_gd20_running_out_of_health_loses_a_life_and_refills_health() -> None:
    hull = PlayerHull(_rules(), 100)
    assert hull.hit(100) == "lifeLost"
    assert hull.lives == 2
    assert hull.health == 100
    # Still invincible after the life is lost.
    assert hull.invincible == 2


def test_gd20_losing_the_last_life_ends_the_game() -> None:
    hull = PlayerHull(_rules(lives=1), 100)
    assert hull.hit(100) == "gameOver"
    assert hull.lives == 0
    assert hull.out is True
    assert hull.health == 0


def test_gd20_a_hit_on_a_ship_that_is_out_is_ignored() -> None:
    hull = PlayerHull(_rules(lives=0), 100)
    assert hull.out is True
    assert hull.hit(10) == "ignored"
    assert hull.health == 100


def test_gd20_damage_never_takes_health_below_zero() -> None:
    hull = PlayerHull(_rules(), 10)
    hull.hit(500)
    assert hull.lives == 2
    assert hull.health == 10


def test_p11_r07_a_life_bonus_adds_one_life_without_a_limit() -> None:
    hull = PlayerHull(_rules(), 100)
    assert hull.add_life() is True
    assert hull.lives == 4


def test_p11_r07_a_life_bonus_stops_at_the_most_lives() -> None:
    hull = PlayerHull(_rules(lives=2, max_lives=3), 100)
    assert hull.add_life() is True
    assert hull.lives == 3
    assert hull.add_life() is False
    assert hull.lives == 3


def test_p11_r07_a_life_bonus_does_nothing_once_the_game_is_over() -> None:
    hull = PlayerHull(_rules(lives=0), 100)
    assert hull.add_life() is False
    assert hull.lives == 0
