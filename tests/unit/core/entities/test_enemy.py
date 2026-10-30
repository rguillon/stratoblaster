"""Unit tests of `src/core/entities/enemy.py`."""

import math
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.fakes import FakeContext

from core.content.game_level import GameLevel
from core.entities.enemy import (
    Enemy,
    EnemyBulletSpec,
    EnemyBurstSpec,
    EnemyEntry,
    EnemyKindDefinition,
    EnemyLaserSpec,
    EnemyMissileSpec,
    EnemySpawnArea,
    EnemyStats,
    validate_enemy_kinds,
)
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.math.rng import create_rng
from core.systems.enemy_shots import EnemyShots, EnemyShotsOptions
from core.systems.enemy_world import (
    EnemyBlast,
    EnemyDifficulty,
    EnemyWorld,
    EnemyWorldOptions,
    _faster,
)
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip
from core.systems.player_bombs import BombRules
from core.systems.player_flight import FlightInput
from core.systems.player_hits import find_player_hits
from core.systems.player_hull import HullDamage, HullRules
from core.systems.wave_runner import Wave


class Walker(Enemy):
    """An enemy that does nothing when it updates."""

    def update(self, ctx: Any, dt: float) -> None:
        self.age += dt


class Gunner(Walker):
    """An enemy whose hit targets are overridden by the hook, as a subclass does."""

    def _hit_targets(self) -> list[Any]:
        return [self, "extra"]


def make_enemy(x: float = 100.0, y: float = 200.0, cls: type[Enemy] = Walker) -> Enemy:
    return cls(x, y, EnemyStats("drone", 8, 5, 10))


def _bullet(speed: float = 10, burst: EnemyBurstSpec | None = None) -> EnemyBulletSpec:
    return EnemyBulletSpec(speed, 2, "round", burst)


def _shots(eye: object = None) -> EnemyShots:
    return EnemyShots(EnemyShotsOptions(100, 100, 10, eye))  # type: ignore[arg-type]


Action = Callable[["WalkerEnemyWorld", object, float], None]


class WalkerEnemyWorld(Enemy):
    """An enemy whose update is a scripted action, so tests can make it do one thing."""

    def __init__(
        self,
        x: float,
        y: float,
        health: float = 10,
        points: float = 50,
        action: Action | None = None,
    ) -> None:
        super().__init__(x, y, EnemyStats("walker", 2, health, points))
        self.action = action
        self.updates: list[float] = []

    def update(self, ctx: object, dt: float) -> None:  # type: ignore[override]
        self.updates.append(dt)
        if self.action is not None:
            self.action(self, ctx, dt)


def _fields(blasts: list[EnemyBlast]) -> list[tuple[str, float, float, float]]:
    return [(b.kind, b.x, b.y, b.radius) for b in blasts]


def _world(difficulty: EnemyDifficulty | None = None, eye: object = None) -> EnemyWorld:
    options = EnemyWorldOptions(100, 100, 10, 60, eye)  # type: ignore[arg-type]
    return EnemyWorld(options, create_rng(1), difficulty)


BULLET = EnemyBulletSpec(10, 2, "round")

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


class _Ship:
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y


class _Owner:
    def __init__(self, emitter: PlanePoint, heading: float) -> None:
        self.emitter = emitter
        self.heading = heading
        self.gone = False
        self.health = 10


RULES = HullRules(
    3,
    1,
    3,
    HullDamage(bullet=10, missile=20, laser=5, collision=30),
    15,
)


def _world_hits(enemies: list[Enemy] | None = None) -> SimpleNamespace:
    shots = EnemyShots(EnemyShotsOptions(100, 100, 10))
    return SimpleNamespace(shots=shots, enemies=enemies if enemies is not None else [])


def _enemy(x: float, y: float, health: float = 10, rammable: bool = True) -> Enemy:
    enemy = Enemy(x, y, EnemyStats("e", 4, health, 1))
    enemy.rammable = rammable
    return enemy


def test_enemy_stats_keep_their_fields() -> None:
    stats = EnemyStats("drone", 8, 5, 10)
    assert (stats.model, stats.radius, stats.health, stats.points) == ("drone", 8, 5, 10)


def test_a_new_enemy_starts_at_full_health_facing_down() -> None:
    enemy = make_enemy()
    assert enemy.health == enemy.max_health == 5
    assert enemy.heading == pytest.approx(math.pi)
    assert enemy.id == 0
    assert enemy.age == 0
    assert enemy.charge == 0
    assert enemy.gone is False
    assert enemy.drop_chance is None
    assert enemy.model == "drone"
    assert enemy.points == 10


def test_enemy_kinds_of_the_base_class_expire_and_can_be_rammed() -> None:
    assert Enemy.expires is True
    assert Enemy.rammable is True
    assert Enemy.on_destroyed is None


def test_the_base_update_is_abstract() -> None:
    with pytest.raises(NotImplementedError):
        make_enemy(cls=Enemy).update(FakeContext(), 0.1)


def test_a_muzzle_of_a_facing_down_enemy_keeps_its_offset() -> None:
    point = make_enemy().place((0, 10, 3))
    assert (point.x, point.y, point.height) == pytest.approx((100, 210, 3))


def test_place_ignores_the_turret_flag() -> None:
    with_turret = make_enemy().place((0, 10, 3), on_turret=True)
    without = make_enemy().place((0, 10, 3))
    assert (with_turret.x, with_turret.y) == pytest.approx((without.x, without.y))


def test_the_emitter_is_one_radius_ahead_of_the_centre() -> None:
    emitter = make_enemy().emitter
    assert (emitter.x, emitter.y) == pytest.approx((100, 192))


def test_the_emitter_follows_the_heading() -> None:
    enemy = make_enemy()
    enemy.heading = math.pi / 2
    emitter = enemy.emitter
    assert (emitter.x, emitter.y) == pytest.approx((108, 200))


def test_an_enemy_is_its_own_hit_target() -> None:
    enemy = make_enemy()
    assert enemy.hit_targets == [enemy]
    assert enemy.shot_targets == [enemy]


def test_shot_targets_follow_the_hit_target_hook() -> None:
    gunner = make_enemy(cls=Gunner)
    assert gunner.shot_targets == [gunner, "extra"]
    assert gunner.hit_targets == [gunner, "extra"]


def test_p06_r07_an_entry_is_an_edge_and_a_position_along_it() -> None:
    entry = EnemyEntry("left", 0.25)
    assert (entry.side, entry.position) == ("left", 0.25)
    area = EnemySpawnArea(400, 600, create_rng(1), entry=entry, top_range=(10, 300))
    assert area.entry is entry
    assert area.top_range == (10, 300)


def test_an_enemy_kind_keeps_its_name_and_spawn() -> None:
    def spawn(area: EnemySpawnArea) -> list[Enemy]:
        return []

    kind = EnemyKindDefinition("drone", "Drone", spawn)
    assert (kind.id, kind.name, kind.spawn) == ("drone", "Drone", spawn)


def test_the_kinds_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="at least one enemy kind"):
        validate_enemy_kinds([])


def test_the_kind_ids_must_be_unique() -> None:
    kinds = [
        EnemyKindDefinition("drone", "A", lambda area: []),
        EnemyKindDefinition("drone", "B", lambda area: []),
    ]
    with pytest.raises(ValueError, match='Duplicate enemy kind id "drone"'):
        validate_enemy_kinds(kinds)


def test_valid_kinds_pass() -> None:
    validate_enemy_kinds([EnemyKindDefinition("drone", "A", lambda area: [])])


def test_bullet_missile_and_laser_specs_keep_their_fields() -> None:
    bullet = EnemyBulletSpec(120, 3, "dot")
    assert (bullet.speed, bullet.radius, bullet.style, bullet.burst) == (120, 3, "dot", None)

    burst = EnemyBurstSpec(1.0, 8, bullet)
    assert (burst.after, burst.count, burst.bullet) == (1.0, 8, bullet)

    missile = EnemyMissileSpec(150, 90, 2.0, 4, 2, "rocket")
    assert (missile.turn_rate_deg, missile.homing_seconds, missile.health) == (90, 2.0, 2)

    laser = EnemyLaserSpec(0.5, 1.5, 4, "beam")
    assert (laser.warning_seconds, laser.firing_seconds, laser.width) == (0.5, 1.5, 4)
    assert laser.sweeps is False


def test_gd43_a_bullet_bursts_into_a_ring_once_its_time_is_up() -> None:
    shots = _shots()
    burst = EnemyBurstSpec(1, 4, _bullet(speed=3))
    shots.fire_bullet(50, 50, 0, _bullet(speed=10, burst=burst))
    shots.step(0.5, 0, 0)
    assert len([b for b in shots.bullets if b.alive]) == 1
    shots.step(0.5, 0, 0)
    alive = [b for b in shots.bullets if b.alive]
    assert len(alive) == 4
    assert all(b.speed == 3 for b in alive)
    assert sorted(round(b.heading, 6) for b in alive) == pytest.approx(
        sorted([0, math.pi / 2, math.pi, 3 * math.pi / 2])
    )
    # The ring leaves from where the bullet was when it burst (after its last move, at y 60).
    assert all(b.y == pytest.approx(60) for b in alive)


def test_gd43_a_burst_at_once_fires_on_the_first_step() -> None:
    shots = _shots()
    shots.fire_bullet(50, 50, 0, _bullet(burst=EnemyBurstSpec(0, 2, _bullet())))
    shots.step(0.1, 0, 0)
    assert len([b for b in shots.bullets if b.alive]) == 2


def test_gd44_a_missile_that_leaves_the_playfield_is_removed() -> None:
    shots = _shots()
    # No homing: it flies straight up out of the playfield (105 + 10 > 100 + margin).
    shots.fire_missile(0, 105, 0, EnemyMissileSpec(10, 90, 0, 2, 5, "rocket"))
    shots.step(1, 0, 0)
    assert shots.missiles[0].alive is False


def test_gd43_a_burst_of_no_bullets_just_goes() -> None:
    shots = _shots()
    shots.fire_bullet(50, 50, 0, _bullet(speed=10, burst=EnemyBurstSpec(0, 0, _bullet())))
    shots.step(0.1, 0, 0)
    assert shots.count == 0


def test_p05_the_targets_are_the_living_enemies_and_missiles() -> None:
    world = _world()
    alive = WalkerEnemyWorld(10, 10)
    gone = WalkerEnemyWorld(20, 20)
    gone.gone = True
    world.add(alive, gone)
    assert world.targets == [alive]
    world.shots.fire_missile(50, 50, 0, EnemyMissileSpec(1, 1, 1, 1, 1, "m"))
    world.clear()
    assert world.targets == []


def test_p05_a_missile_with_no_health_leaves_a_missile_blast() -> None:
    world = _world()
    world.shots.fire_missile(30, 40, 0, EnemyMissileSpec(1, 1, 0, 3, 5, "m"))
    world.shots.missiles[0].health = 0
    world.step(0.1)
    assert _fields(world.blasts) == [("missile", 30, 40, 3)]


def test_gd43_an_enemy_fires_bullets_faster_by_the_difficulty_factor() -> None:
    def fire(e: WalkerEnemyWorld, ctx: object, dt: float) -> None:
        ctx.fire_bullet(1, 2, 0.5, EnemyBulletSpec(5, 2, "s", EnemyBurstSpec(1, 2, BULLET)))  # type: ignore[attr-defined]

    world = _world(EnemyDifficulty(2, 1))
    world.add(WalkerEnemyWorld(50, 50, action=fire))
    world.step(0.1)
    bullet = world.shots.bullets[0]
    assert bullet.speed == 10
    assert bullet.burst is not None
    assert bullet.burst.bullet.speed == 20


def test_p06_r08_faster_scales_a_bullet_and_the_bullets_it_bursts_into() -> None:
    spec = EnemyBulletSpec(5, 2, "s", EnemyBurstSpec(1, 3, EnemyBulletSpec(4, 1, "t")))
    faster = _faster(spec, 3)
    assert faster.speed == 15
    assert faster.burst is not None
    assert faster.burst.bullet.speed == 12
    assert faster.burst.count == 3
    plain = _faster(EnemyBulletSpec(5, 2, "s"), 2)
    assert plain.speed == 10
    assert plain.burst is None


def test_gd43_an_enemy_can_fire_missiles_and_lasers() -> None:
    laser = EnemyLaserSpec(0, 1, 4, "b")

    def fire(e: WalkerEnemyWorld, ctx: object, dt: float) -> None:
        ctx.fire_missile(1, 2, 0, EnemyMissileSpec(1, 1, 1, 1, 3, "m"))  # type: ignore[attr-defined]
        ctx.fire_laser(e, laser)  # type: ignore[attr-defined]

    world = _world()
    world.add(WalkerEnemyWorld(50, 50, action=fire))
    world.step(0.1)
    assert len(world.shots.missiles) == 1
    assert len(world.shots.lasers) == 1


def test_gd43_a_laser_fired_by_a_walker_is_in_the_shot_world() -> None:
    world = _world()
    world.shots.fire_laser(WalkerEnemyWorld(50, 50), EnemyLaserSpec(0, 1, 2, "b"))
    world.step(0.1)
    assert len(world.shots.lasers) == 1
    assert math.isfinite(world.shots.lasers[0].length)


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


def test_gd21_a_bullet_outside_the_hitbox_or_dead_is_no_hit() -> None:
    world = _world_hits()
    world.shots.fire_bullet(0, 6, 0, EnemyBulletSpec(0, 2, "s"))
    world.shots.fire_bullet(0, 0, 0, EnemyBulletSpec(0, 2, "s"))
    world.shots.bullets[1].alive = False
    assert find_player_hits(_Ship(), RULES, world, set()) == []


def test_gd21_a_missile_with_no_health_is_no_hit() -> None:
    world = _world_hits()
    world.shots.fire_missile(0, 0, 0, EnemyMissileSpec(0, 0, 0, 2, 0, "m"))
    assert find_player_hits(_Ship(), RULES, world, set()) == []


def test_gd21_a_laser_still_showing_its_warning_does_not_hit() -> None:
    world = _world_hits()
    world.shots.fire_laser(_Owner(PlanePoint(0, 10), math.pi), EnemyLaserSpec(1, 1, 4, "b"))
    world.shots.step(0.1, 0, 0)
    assert find_player_hits(_Ship(), RULES, world, set()) == []


def test_gd21_hits_come_most_damaging_first_and_equal_ones_keep_their_order() -> None:
    world = _world_hits()
    world.shots.fire_bullet(0, 0, 0, EnemyBulletSpec(0, 2, "a"))
    world.shots.fire_bullet(0, 1, 0, EnemyBulletSpec(0, 2, "b"))
    world.enemies = [_enemy(0, 2)]
    hits = find_player_hits(_Ship(), RULES, world, set())
    assert [h.kind for h in hits] == ["collision", "bullet", "bullet"]
    assert [h.y for h in hits[1:]] == [0, 1]
