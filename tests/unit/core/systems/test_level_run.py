"""Tests of one play of a level (P06-R02, R03, R07), `core/systems/level_run.py`."""

from types import SimpleNamespace

import pytest

from core.content.game_level import GameLevel
from core.entities.enemy import (
    Enemy,
    EnemyBulletSpec,
    EnemyKindDefinition,
    EnemyStats,
)
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.bonus_world import BonusChance, BonusRules, LifeAndBomb
from core.systems.boss_fights import BossFightRules, LevelBoss
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import (
    LevelCheckpoint,
    LevelControls,
    LevelRunOptions,
    RunShip,
    Supplies,
)
from core.systems.player_bombs import BombRules
from core.systems.player_flight import FlightInput
from core.systems.player_hull import HullDamage, HullRules
from core.systems.run_arsenal import WeaponLevels
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


def _supplies(run: LevelRun) -> tuple[float, float] | None:
    supplies = run.supplies
    return None if supplies is None else (supplies.lives, supplies.bombs)


def _wave(at: float = 0, count: int = 1) -> Wave:
    return Wave(at, "still", count, 0, ENTRY)  # type: ignore[arg-type]


def test_p06_r03_a_bad_wave_script_is_refused_when_the_run_starts() -> None:
    with pytest.raises(ValueError, match="unknown enemy kind"):
        _run(level=_level([Wave(0, "ghost", 1, 0, ENTRY)]))  # type: ignore[arg-type]


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


def test_p06_r02_the_ship_flies_with_the_controls() -> None:
    run = _run()
    _step(run, dt=0.1, move=FlightInput(1, 0))
    assert run.ship.x == pytest.approx(60)
    assert run.ship.y == pytest.approx(10)


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


def test_p06_r09_seeking_after_the_game_is_over_does_nothing() -> None:
    run = _run(hull=HullRules(1, 0, 3, HullDamage(200, 0, 0, 0), 0))
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run)
    assert run.phase == "over"
    before = run.track.progress
    run.seek(5)
    assert run.track.progress == before


def test_p06_r07_seeking_drops_the_bonuses_in_the_air() -> None:
    run = _run(bonuses=BonusRules(BonusChance(0, 0, 0), 0, 5))
    run.bonuses.place("weapon", PlanePoint(20, 20))
    run.seek(1)
    assert run.bonuses.bonuses == []


def test_p06_r02_the_ship_cannot_fly_once_the_game_is_over() -> None:
    run = _run(hull=HullRules(1, 0, 3, HullDamage(200, 0, 0, 0), 0))
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run)
    x = run.ship.x
    _step(run, move=FlightInput(1, 0))
    assert run.ship.x == x


def test_p06_r02_the_hull_takes_the_most_damaging_hit_and_then_is_invincible() -> None:
    run = _run(hull=HullRules(3, 1, 3, HullDamage(30, 0, 0, 0), 0))
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run, dt=0.1)
    assert [(h.kind, h.event) for h in run.hits] == [("bullet", "hit")]
    assert run.hull.health == 70
    run.enemies.shots.fire_bullet(50, 10, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run, dt=0.1)
    assert run.hits == []
    assert run.hull.health == 70


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


def test_p11_r05_a_bomb_damages_everything_on_screen_once_and_clears_the_enemy_shots() -> None:
    run = _run(
        level=_level([_wave(0)]),
        kinds=[_kind(health=100)],
        bombs=BombRules(1, 50, 1),
    )
    run.enemies.shots.fire_bullet(50, 90, 0, EnemyBulletSpec(0, 1, "s"))
    _step(run, dt=0.1, bomb=True)
    assert run.enemies.enemies[0].health == 50
    assert run.bombs.count == 0
    assert run.enemies.shots.count == 0
    _step(run, dt=0.1, bomb=True)
    assert run.enemies.enemies[0].health == 50


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


def test_p06_r03_the_run_switches_the_weapon_in_use_when_asked() -> None:
    run = _run(weapons=[GUN, GUN2])
    _step(run, switch_weapon=True)
    assert run.shots.weapon is GUN2


def test_p07_r08_a_run_can_start_with_the_weapons_kept_from_before() -> None:
    run = _run(weapons=[GUN, GUN2], start_weapons=WeaponLevels("gun2", {"gun": 2}))
    assert run.shots.weapon is GUN2
    _step(run, switch_weapon=True)
    assert run.shots.weapon is GUN
    assert run.shots.level == 2


def test_p11_r03_the_run_starts_with_the_lives_and_bombs_kept_before() -> None:
    run = _run(
        hull=HullRules(3, 0, 3, HullDamage(0, 0, 0, 0), 0),
        bombs=BombRules(1, 50, 1),
        start_supplies=Supplies(2, 0),
    )
    assert run.hull.lives == 2
    assert run.bombs.count == 0
    assert _supplies(run) == (2, 0)


def test_p07_r08_a_run_resumes_from_its_checkpoint() -> None:
    checkpoint = LevelCheckpoint(50, 0, WeaponLevels("gun", {"gun": 2}), 300)
    run = _run(checkpoint=checkpoint, weapon_level=1)
    assert run.track.progress == pytest.approx(50)
    assert run.score == 300
    assert run.shots.level == 2
    assert run.checkpoint is checkpoint


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


def test_p07_r06_a_final_boss_ends_the_level_when_it_is_destroyed() -> None:
    run = _run(
        level=_level(bosses=[LevelBoss("hulk", "final", 10)]),
        boss_kinds=[FakeBossKind()],
        boss_rules=BossFightRules(0, 1),
    )
    for _ in range(2):
        _step(run)
    assert run.fights.has_final is True
    run.fights.boss.health = 0
    _step(run)
    _step(run)
    assert run.phase == "complete"
    assert run.checkpoint is None


def test_p06_r02_a_run_with_a_journey_leaves_once_the_level_is_cleared() -> None:
    run = _run(journey=JourneyRules(0.5, 5, 1, 50, 50, 10))
    assert run.journey is not None
    assert run.journey.stage == "arriving"
    _step(run)
    assert run.journey.stage == "flying"
    for _ in range(400):
        _step(run, dt=0.5)
        if run.phase == "complete":
            break
    assert run.phase == "complete"
    assert run.journey.stage == "gone"


def test_p06_r02_a_journey_ship_is_flown_by_the_journey_not_the_player() -> None:
    run = _run(journey=JourneyRules(2, 10, 3, 50, 50, 10))
    _step(run, dt=0.5, move=FlightInput(1, 0), fire=True)
    assert run.ship.x == pytest.approx(50)
    assert run.journey.stage == "arriving"
    assert run.enemies.kills == 0
    run.seek(0)
    assert run.journey.stage == "flying"
    assert (run.ship.x, run.ship.y) == (50, 10)


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
