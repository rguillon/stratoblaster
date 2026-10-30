"""Unit tests of `src/core/systems/bonus_world.py`."""

from types import SimpleNamespace

import pytest

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.math.rng import create_rng
from core.systems.bonus_world import BonusChance, BonusRules, BonusWorld, LifeAndBomb, drop_chance
from core.systems.boss_fights import BossFightRules, LevelBoss
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip
from core.systems.player_bombs import BombRules
from core.systems.player_flight import FlightInput
from core.systems.player_hull import HullDamage, HullRules
from core.systems.wave_runner import Wave


class _Source:
    """A destroyed thing that may drop a bonus (DropSource)."""

    def __init__(
        self,
        x: float = 50,
        y: float = 50,
        max_health: float = 10,
        drop: float | None = None,
    ) -> None:
        self.id = 0
        self.x = x
        self.y = y
        self.radius = 3
        self.health = 0
        self.max_health = max_health
        self.drop_chance = drop
        self.points = None


class _Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def _rules(
    per_health: float = 0.1,
    lo: float = 0.0,
    hi: float = 1.0,
    special: LifeAndBomb | None = None,
    overflow: LifeAndBomb | None = None,
) -> BonusRules:
    return BonusRules(
        BonusChance(per_health, lo, hi),
        fall_speed=10,
        pickup_radius=5,
        special=special,
        overflow_points=overflow,
    )


def _always(value: float) -> object:
    return lambda: value


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


class FakeBoss(Enemy):
    """A boss as the run sees it: it stays until destroyed."""

    expires = False
    rammable = False

    def __init__(self, x: float, y: float, health: float = 100, points: float = 500) -> None:
        super().__init__(x, y, EnemyStats("boss", 6, health, points))
        self.name = "Hulk"
        self.ground_speed = 0.5
        self.parts: list = []
        self.full_health = health
        self.breaks = 0

    @property
    def remaining_health(self) -> float:
        return self.health

    def update(self, ctx: object, dt: float) -> None:  # type: ignore[override]
        pass

    def break_next(self) -> None:
        self.breaks += 1


class FakeBossKind:
    id = "hulk"
    name = "Hulk"

    def spawn(self, area: object) -> FakeBoss:
        return FakeBoss(50, 60)


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


def test_gd31_a_target_with_its_own_chance_uses_it() -> None:
    assert drop_chance(_rules(), _Source(drop=0.7)) == 0.7


def test_gd31_the_chance_grows_with_health_within_its_limits() -> None:
    rules = _rules(per_health=0.1, lo=0.2, hi=0.6)
    assert drop_chance(rules, _Source(max_health=1)) == pytest.approx(0.2)
    assert drop_chance(rules, _Source(max_health=4)) == pytest.approx(0.4)
    assert drop_chance(rules, _Source(max_health=100)) == pytest.approx(0.6)


def test_gd31_a_destroyed_enemy_drops_a_weapon_bonus_when_the_draw_succeeds() -> None:
    world = BonusWorld(_rules(), create_rng(1), (0, 100), 10)
    world.drop([_Source(drop=1.0)])
    assert [b.kind for b in world.bonuses] == ["weapon"]
    assert world.dropped == 1


def test_gd31_no_bonus_drops_when_the_draw_fails() -> None:
    world = BonusWorld(_rules(), _always(0.99), (0, 100), 10)  # type: ignore[arg-type]
    world.drop([_Source(drop=0.5)])
    assert world.bonuses == []
    assert world.dropped == 0


def test_p11_r07_a_special_enemy_may_drop_a_life_before_a_bomb_or_weapon() -> None:
    odds = LifeAndBomb(0.5, 0.5)
    world = BonusWorld(
        _rules(special=odds),
        _always(0.0),
        (0, 100),
        10,  # type: ignore[arg-type]
        _always(0.0),
    )  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert [b.kind for b in world.bonuses] == ["life"]


def test_p11_r07_a_special_enemy_drops_a_bomb_when_the_life_draw_fails() -> None:
    odds = LifeAndBomb(0.1, 0.5)
    world = BonusWorld(
        _rules(special=odds),
        _always(0.0),
        (0, 100),
        10,  # type: ignore[arg-type]
        _always(0.3),
    )  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert [b.kind for b in world.bonuses] == ["bomb"]


def test_p11_r07_the_weapon_draw_always_happens_even_when_a_special_bonus_is_dropped() -> None:
    calls: list[float] = []

    def weapon_draw() -> float:
        calls.append(0)
        return 0.0

    odds = LifeAndBomb(1.0, 1.0)
    world = BonusWorld(_rules(special=odds), weapon_draw, (0, 100), 10, _always(0.0))  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert calls == [0]
    assert [b.kind for b in world.bonuses] == ["life"]


def test_p11_r07_an_ordinary_enemy_never_drops_a_special_bonus() -> None:
    odds = LifeAndBomb(1.0, 1.0)
    # The weapon draw (0.99) succeeds against a 100% chance; the special draws are never made.
    world = BonusWorld(
        _rules(special=odds),
        _always(0.99),
        (0, 100),
        10,  # type: ignore[arg-type]
        _always(0.0),
    )  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: False)
    assert [b.kind for b in world.bonuses] == ["weapon"]


def test_p11_r07_a_special_draw_on_a_rules_without_special_odds_is_skipped() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10, _always(0.0))  # type: ignore[arg-type]
    world.drop([_Source()], special=lambda t: True)
    assert [b.kind for b in world.bonuses] == ["weapon"]


def test_gd31_the_special_draw_defaults_to_the_weapon_draw() -> None:
    world = BonusWorld(_rules(), create_rng(3), (0, 100), 10)
    assert world._special_random is world._random


def test_gd31_a_bonus_falls_and_is_removed_below_the_playfield() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 0))
    world.step(1)
    assert world.bonuses[0].y == -10
    assert world.bonuses[0].age == 1
    world.step(1)
    assert world.bonuses == []


def test_gd31_a_bonus_is_kept_within_the_ships_reach_when_it_drops() -> None:
    world = BonusWorld(_rules(), _always(0.0), (20, 80), 10)  # type: ignore[arg-type]
    world.place("life", _Point(5, 30))
    world.place("bomb", _Point(99, 30))
    assert [b.x for b in world.bonuses] == [20, 80]
    assert [b.kind for b in world.bonuses] == ["life", "bomb"]
    assert [b.id for b in world.bonuses] == [1, 2]


def test_gd31_the_ship_picks_up_the_bonuses_it_touches() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 50))
    world.place("life", _Point(90, 50))
    world.step(0.1, _Point(52, 50))
    assert [b.kind for b in world.picked] == ["weapon"]
    assert [b.kind for b in world.bonuses] == ["life"]
    assert world.collected == 1
    world.step(0.1)
    assert world.picked == []
    assert world.collected == 1


def test_gd31_without_a_ship_nothing_is_picked_up() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 50))
    world.step(0.0, None)
    assert world.picked == []
    assert len(world.bonuses) == 1


def test_gd31_clearing_the_world_removes_the_bonuses_and_pickups() -> None:
    world = BonusWorld(_rules(), _always(0.0), (0, 100), 10)  # type: ignore[arg-type]
    world.place("weapon", _Point(50, 50))
    world.step(0, _Point(50, 50))
    world.clear()
    assert world.bonuses == []
    assert world.picked == []


def test_p06_r07_seeking_drops_the_bonuses_in_the_air() -> None:
    run = _run(bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5))
    run.bonuses.place("weapon", PlanePoint(20, 20))
    run.seek(1)
    assert run.bonuses.bonuses == []


def test_p11_r07_a_weapon_bonus_raises_the_weapon_in_use() -> None:
    run = _run(bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5))
    run.bonuses.place("weapon", PlanePoint(50, 10))
    _step(run, dt=0.1)
    assert run.shots.level == 2
    assert run.bonuses.collected == 1


def test_p11_r07_a_life_bonus_adds_a_life_or_scores_its_points_at_the_most() -> None:
    run = _run(
        hull=HullRules(2, 0, 3, HullDamage(0, 0, 0, 0), 0),
        bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5, None, LifeAndBomb(7, 3)),
    )
    run.bonuses.place("life", PlanePoint(50, 10))
    _step(run, dt=0.1)
    assert run.hull.lives == 3
    assert run.score == 0

    capped = _run(
        hull=HullRules(3, 0, 3, HullDamage(0, 0, 0, 0), 0, max_lives=3),
        bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5, None, LifeAndBomb(7, 3)),
    )
    capped.bonuses.place("life", PlanePoint(50, 10))
    _step(capped, dt=0.1)
    assert capped.hull.lives == 3
    assert capped.score == 7


def test_p11_r07_a_bomb_bonus_adds_a_bomb_or_scores_its_points_at_the_most() -> None:
    run = _run(
        bombs=BombRules(1, 50, 1, max_bombs=1),
        bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5, None, LifeAndBomb(7, 3)),
    )
    run.bonuses.place("bomb", PlanePoint(50, 10))
    _step(run, dt=0.1)
    assert run.bombs.count == 1
    assert run.score == 3


def test_gd31_a_destroyed_enemy_drops_a_bonus_when_bonuses_are_on() -> None:
    run = _run(
        level=_level([_wave(0)]),
        kinds=[_kind(health=5)],
        bonuses=BonusRules(BonusChance(0, 1, 1), 0, 5),
    )
    for _ in range(10):
        _step(run, dt=0.1, fire=True)
    assert run.enemies.kills == 1
    assert run.bonuses.dropped == 1


def test_p07_r06_a_mini_boss_comes_in_and_its_death_saves_a_checkpoint() -> None:
    run = _run(
        level=_level(bosses=[LevelBoss("hulk", "mini", 10)]),
        boss_kinds=[FakeBossKind()],
        boss_rules=BossFightRules(0, 1),
        bonuses=BonusRules(BonusChance(0, 1, 1), 0, 5, LifeAndBomb(1, 1)),
    )
    for _ in range(2):
        _step(run)
    boss = run.fights.boss
    assert isinstance(boss, FakeBoss)
    assert run.fights.active is True
    run.break_boss_part()
    assert boss.breaks == 1
    boss.health = 0
    _step(run)
    assert run.checkpoint is None
    _step(run)
    cp = run.checkpoint
    assert cp is not None
    assert cp.progress == pytest.approx(10)
    assert cp.bosses_passed == 1
    assert cp.score == 500
    assert run.score == 500


def test_p11_r07_a_mini_boss_drops_a_life_bonus_where_it_fell() -> None:
    run = _run(
        level=_level(bosses=[LevelBoss("hulk", "mini", 10)]),
        boss_kinds=[FakeBossKind()],
        boss_rules=BossFightRules(0, 1),
        bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5, LifeAndBomb(0, 0)),
    )
    for _ in range(2):
        _step(run)
    run.fights.boss.health = 0
    _step(run)
    assert [b.kind for b in run.bonuses.bonuses] == ["life"]
