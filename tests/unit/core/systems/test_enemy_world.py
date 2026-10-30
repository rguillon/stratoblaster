"""Tests of the enemies and their shots (P05), `core/systems/enemy_world.py`."""

import math
from collections.abc import Callable
from types import SimpleNamespace

import pytest

from core.entities.enemy import (
    Enemy,
    EnemyBulletSpec,
    EnemyBurstSpec,
    EnemyLaserSpec,
    EnemyMissileSpec,
    EnemyStats,
)
from core.entities.muzzle import PlanePoint, RaisedPoint
from core.math.rng import create_rng
from core.systems.enemy_world import (
    EnemyBlast,
    EnemyDifficulty,
    EnemyWorld,
    EnemyWorldOptions,
    _faster,
)

Action = Callable[["Walker", object, float], None]


class Walker(Enemy):
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


class _Part:
    """A piece of an enemy the player can break (DropSource)."""

    def __init__(self, x: float, y: float, points: float | None) -> None:
        self.id = 0
        self.x = x
        self.y = y
        self.radius = 3
        self.health = 0
        self.max_health = 5
        self.drop_chance = None
        self.points = points


def _fields(blasts: list[EnemyBlast]) -> list[tuple[str, float, float, float]]:
    return [(b.kind, b.x, b.y, b.radius) for b in blasts]


def _world(difficulty: EnemyDifficulty | None = None, eye: object = None) -> EnemyWorld:
    options = EnemyWorldOptions(100, 100, 10, 60, eye)  # type: ignore[arg-type]
    return EnemyWorld(options, create_rng(1), difficulty)


BULLET = EnemyBulletSpec(10, 2, "round")


def test_p05_enemies_added_get_ids_and_count_towards_the_spawned_totals() -> None:
    world = _world()
    world.add(Walker(10, 10, health=10), Walker(20, 20, health=5))
    assert [e.id for e in world.enemies] == [1, 2]
    assert world.spawned == 2
    assert world.spawned_health == 15


def test_p05_the_targets_are_the_living_enemies_and_missiles() -> None:
    world = _world()
    alive = Walker(10, 10)
    gone = Walker(20, 20)
    gone.gone = True
    world.add(alive, gone)
    assert world.targets == [alive]
    world.shots.fire_missile(50, 50, 0, EnemyMissileSpec(1, 1, 1, 1, 1, "m"))
    world.clear()
    assert world.targets == []


def test_p05_on_screen_counts_enemies_whose_centre_is_on_the_playfield() -> None:
    world = _world()
    world.add(Walker(50, 50), Walker(-5, 50), Walker(50, 105), Walker(100, 0))
    assert world.on_screen == 2


def test_p05_each_enemy_is_updated_every_step_and_ages() -> None:
    world = _world()
    enemy = Walker(50, 50)
    world.add(enemy)
    world.step(0.5)
    world.step(0.25)
    assert enemy.updates == [0.5, 0.25]
    assert enemy.age == pytest.approx(0.75)


def test_p05_a_destroyed_enemy_scores_once_and_leaves_a_blast() -> None:
    world = _world()
    enemy = Walker(50, 50, health=0, points=75)
    world.add(enemy)
    world.step(0.1)
    assert world.kills == 1
    assert world.score == 75
    assert world.destroyed == [enemy]
    assert enemy.gone is True
    assert _fields(world.blasts) == [("enemy", 50, 50, 2)]
    assert enemy not in world.enemies
    world.step(0.1)
    assert world.kills == 1
    assert world.destroyed == []


def test_p05_a_destroyed_enemy_runs_its_on_destroyed_hook_with_the_context() -> None:
    world = _world()
    calls: list[object] = []
    enemy = Walker(50, 50, health=0)
    enemy.on_destroyed = calls.append  # type: ignore[assignment]
    world.add(enemy)
    world.step(0.1)
    assert len(calls) == 1
    assert calls[0] is world._context  # type: ignore[attr-defined]


def test_gd45_an_enemy_that_flies_off_the_playfield_after_entering_is_removed() -> None:
    world = _world()
    enemy = Walker(50, 50, action=lambda e, ctx, dt: setattr(e, "y", e.y - 100 * dt))
    world.add(enemy)
    world.step(0.1)
    assert enemy in world.enemies
    world.step(1.0)
    assert enemy not in world.enemies
    assert enemy.gone is True
    assert world.kills == 0


def test_gd45_an_enemy_that_has_not_yet_entered_stays_while_off_screen() -> None:
    world = _world()
    enemy = Walker(50, 200)
    world.add(enemy)
    world.step(0.1)
    assert enemy in world.enemies


def test_gd45_an_enemy_too_old_is_removed_whatever_it_does() -> None:
    world = _world()
    enemy = Walker(50, 50)
    world.add(enemy)
    world.step(61)
    assert enemy not in world.enemies


def test_p05_an_enemy_that_does_not_expire_stays_until_destroyed() -> None:
    world = _world()
    boss_like = Walker(50, 50, action=lambda e, ctx, dt: setattr(e, "y", -500))
    boss_like.expires = False
    world.add(boss_like)
    world.step(1)
    assert boss_like in world.enemies
    boss_like.health = 0
    world.step(1)
    assert boss_like not in world.enemies
    assert world.kills == 1


def test_p05_a_missile_with_no_health_leaves_a_missile_blast() -> None:
    world = _world()
    world.shots.fire_missile(30, 40, 0, EnemyMissileSpec(1, 1, 0, 3, 5, "m"))
    world.shots.missiles[0].health = 0
    world.step(0.1)
    assert _fields(world.blasts) == [("missile", 30, 40, 3)]


def test_gd43_an_enemy_fires_bullets_faster_by_the_difficulty_factor() -> None:
    def fire(e: Walker, ctx: object, dt: float) -> None:
        ctx.fire_bullet(1, 2, 0.5, EnemyBulletSpec(5, 2, "s", EnemyBurstSpec(1, 2, BULLET)))  # type: ignore[attr-defined]

    world = _world(EnemyDifficulty(2, 1))
    world.add(Walker(50, 50, action=fire))
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

    def fire(e: Walker, ctx: object, dt: float) -> None:
        ctx.fire_missile(1, 2, 0, EnemyMissileSpec(1, 1, 1, 1, 3, "m"))  # type: ignore[attr-defined]
        ctx.fire_laser(e, laser)  # type: ignore[attr-defined]

    world = _world()
    world.add(Walker(50, 50, action=fire))
    world.step(0.1)
    assert len(world.shots.missiles) == 1
    assert len(world.shots.lasers) == 1


def test_gd45_the_context_gives_enemies_the_playfield_the_player_and_the_random_source() -> None:
    seen: dict[str, object] = {}

    def look(e: Walker, ctx: object, dt: float) -> None:
        seen["width"] = ctx.width  # type: ignore[attr-defined]
        seen["height"] = ctx.height  # type: ignore[attr-defined]
        seen["player"] = (ctx.player_x, ctx.player_y)  # type: ignore[attr-defined]
        seen["fire_rate"] = ctx.fire_rate  # type: ignore[attr-defined]
        seen["random"] = ctx.random()  # type: ignore[attr-defined]
        seen["seen"] = ctx.seen(_point())  # type: ignore[attr-defined]

    world = _world(EnemyDifficulty(1, 3))
    world.player_x = 30
    world.player_y = 40
    world.add(Walker(50, 50, action=look))
    world.step(0.1)
    assert seen["width"] == 100
    assert seen["height"] == 100
    assert seen["player"] == (30, 40)
    assert seen["fire_rate"] == 3
    assert 0 <= seen["random"] < 1  # type: ignore[operator]
    seen_point = seen["seen"]
    assert isinstance(seen_point, PlanePoint)
    assert (seen_point.x, seen_point.y) == (5, 6)


def _point() -> RaisedPoint:
    return RaisedPoint(5, 6, 0)


def test_gd45_a_seen_point_is_moved_by_the_eye_when_raised() -> None:
    eye = SimpleNamespace(x=0, y=0, height=100)
    world = _world(eye=eye)
    from core.entities.muzzle import RaisedPoint  # noqa: PLC0415

    point = world._context.seen(RaisedPoint(0, 50, 50))  # type: ignore[attr-defined]
    assert isinstance(point, PlanePoint)
    assert (point.x, point.y) == pytest.approx((0, 100))


def test_p05_an_enemy_can_spawn_new_enemies_that_join_from_the_next_step() -> None:
    def spawn(e: Walker, ctx: object, dt: float) -> None:
        ctx.spawn(Walker(10, 10))  # type: ignore[attr-defined]

    world = _world()
    world.add(Walker(50, 50, action=spawn))
    world.step(0.1)
    assert len(world.enemies) == 2
    assert world.spawned == 2
    assert world.spawned_enemies == []


def test_p05_an_enemy_can_explode_and_break_its_parts() -> None:
    part_points = _Part(20, 20, points=30)
    free_part = _Part(40, 40, points=None)

    def wreck(e: Walker, ctx: object, dt: float) -> None:
        ctx.explode(1, 1, 5)  # type: ignore[attr-defined]
        ctx.break_part(part_points)  # type: ignore[attr-defined]
        ctx.break_part(free_part)  # type: ignore[attr-defined]

    world = _world()
    world.add(Walker(50, 50, action=wreck))
    world.step(0.1)
    assert ("enemy", 1, 1, 5) in _fields(world.blasts)
    assert world.broken_parts == [part_points, free_part]
    assert world.score == 30
    assert ("enemy", 20, 20, 3) in _fields(world.blasts)


def test_p05_clearing_the_world_removes_enemies_shots_and_blasts() -> None:
    world = _world()
    world.add(Walker(50, 50, health=0))
    world.shots.fire_bullet(1, 1, 0, BULLET)
    world.step(0.1)
    world.add(Walker(10, 10))
    world.clear()
    assert world.enemies == []
    assert world.shots.count == 0
    assert world.blasts == []
    assert world.destroyed == []
    assert world.broken_parts == []
    assert world.targets == []


def test_gd43_a_laser_fired_by_a_walker_is_in_the_shot_world() -> None:
    world = _world()
    world.shots.fire_laser(Walker(50, 50), EnemyLaserSpec(0, 1, 2, "b"))
    world.step(0.1)
    assert len(world.shots.lasers) == 1
    assert math.isfinite(world.shots.lasers[0].length)
