"""Unit tests of `src/core/entities/muzzle.py`."""

import math
from collections.abc import Callable
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.enemy import (
    Enemy,
    EnemyBulletSpec,
    EnemyBurstSpec,
    EnemyLaserSpec,
    EnemyMissileSpec,
    EnemyStats,
)
from core.entities.muzzle import PlanePoint, RaisedPoint, muzzle_point, seen_on_playfield
from core.math.rng import create_rng
from core.systems.boss_pattern import BossAimedShape, BossPattern, BossVolley
from core.systems.enemy_shots import EnemyShots, EnemyShotsOptions
from core.systems.enemy_world import EnemyDifficulty, EnemyWorld, EnemyWorldOptions


@dataclass
class Eye:
    x: float
    y: float
    height: float


@dataclass
class Body:
    x: float
    y: float
    heading: float


@dataclass
class RolledBody(Body):
    roll: float = 0.0


DOWN = math.pi

BULLET = EnemyBulletSpec(10, 1, "round")


class _Ctx:
    """What a volley fires with: records every shot."""

    def __init__(self, fire_rate: float = 1.0, player: tuple[float, float] = (100, 0)) -> None:
        self.fire_rate = fire_rate
        self.player_x, self.player_y = player
        self.bullets: list[tuple[float, float, float, EnemyBulletSpec]] = []
        self.missiles: list[tuple[float, float, float, EnemyMissileSpec]] = []
        self.lasers: list[tuple[object, EnemyLaserSpec]] = []
        self.spawned: list[object] = []

    def seen(self, point: RaisedPoint) -> PlanePoint:
        return PlanePoint(point.x, point.y)

    def fire_bullet(self, x: float, y: float, heading: float, spec: EnemyBulletSpec) -> None:
        self.bullets.append((x, y, heading, spec))

    def fire_missile(self, x: float, y: float, heading: float, spec: EnemyMissileSpec) -> None:
        self.missiles.append((x, y, heading, spec))

    def fire_laser(self, owner: object, spec: EnemyLaserSpec) -> None:
        self.lasers.append((owner, spec))

    def spawn(self, enemy: object) -> None:
        self.spawned.append(enemy)


class _Src:
    """A piece of a boss: where it is, its turret if any; it places its muzzles (`MuzzleSource`)."""

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        heading: float = DOWN,
        turret: BossTurret | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.heading = heading
        self.gone = False
        self.health = 10
        self.turret = turret

    @property
    def emitter(self) -> PlanePoint:
        return PlanePoint(self.x, self.y)

    def place(self, muzzle, on_turret=False):  # type: ignore[no-untyped-def]
        mx, my, mh = muzzle
        return RaisedPoint(self.x + mx, self.y + my, mh)


def _sources(parts: dict[str, _Src]):  # type: ignore[no-untyped-def]
    return parts.get


def _volley(shape: object, from_: str = "core", every: float = 10, **kwargs: object) -> BossVolley:
    return BossVolley(from_, every, shape, **kwargs)  # type: ignore[arg-type]


def _aimed(count: int = 1, spacing: float = 0) -> BossAimedShape:
    return BossAimedShape(count, spacing, BULLET)


def _turret(turn_rate: float, laser_rate: float | None = None, x: float = 0) -> BossTurret:
    return BossTurret(BossTurretSpec(x, 0, turn_rate, laser_rate))


class _Owner:
    """A laser owner: an emitter, a heading, and whether it still stands."""

    def __init__(self, emitter: PlanePoint | RaisedPoint, heading: float = math.pi) -> None:
        self.emitter = emitter
        self.heading = heading
        self.gone = False
        self.health = 10


def _bullet(speed: float = 10, burst: EnemyBurstSpec | None = None) -> EnemyBulletSpec:
    return EnemyBulletSpec(speed, 2, "round", burst)


def _missile(health: float = 5) -> EnemyMissileSpec:
    return EnemyMissileSpec(
        speed=10, turn_rate_deg=90, homing_seconds=1, radius=2, health=health, style="rocket"
    )


def _laser(warning: float = 1, firing: float = 1, sweeps: bool = False) -> EnemyLaserSpec:
    return EnemyLaserSpec(warning, firing, 4, "beam", sweeps)


def _shots(eye: object = None) -> EnemyShots:
    return EnemyShots(EnemyShotsOptions(100, 100, 10, eye))  # type: ignore[arg-type]


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


def _world(difficulty: EnemyDifficulty | None = None, eye: object = None) -> EnemyWorld:
    options = EnemyWorldOptions(100, 100, 10, 60, eye)  # type: ignore[arg-type]
    return EnemyWorld(options, create_rng(1), difficulty)


def _point() -> RaisedPoint:
    return RaisedPoint(5, 6, 0)


def test_a_point_on_the_playfield_is_seen_where_it_is() -> None:
    no_eye = seen_on_playfield(None, RaisedPoint(3, 4, 50))
    assert (no_eye.x, no_eye.y) == (3, 4)
    on_playfield = seen_on_playfield(Eye(0, 0, 100), RaisedPoint(3, 4, 0))
    assert (on_playfield.x, on_playfield.y) == (3, 4)


def test_a_raised_point_is_seen_further_out_from_the_eye() -> None:
    seen = seen_on_playfield(Eye(0, 0, 100), RaisedPoint(10, 10, 50))
    assert (seen.x, seen.y) == pytest.approx((20, 20))


def test_the_eye_clamps_its_distance_when_it_is_level_with_the_point() -> None:
    seen = seen_on_playfield(Eye(0, 0, 10), RaisedPoint(10, 10, 10))
    assert (seen.x, seen.y) == pytest.approx((100, 100))


def test_a_muzzle_facing_down_keeps_its_offset() -> None:
    body = Body(100, 200, math.pi)
    point = muzzle_point(body, (3, 4, 2))
    assert (point.x, point.y, point.height) == pytest.approx((103, 204, 2))


def test_a_muzzle_turns_with_the_nose() -> None:
    body = Body(100, 200, 0)
    point = muzzle_point(body, (3, 4, 2))
    assert (point.x, point.y) == pytest.approx((97, 196))


def test_a_muzzle_turns_with_the_spin_first() -> None:
    body = Body(0, 0, math.pi)
    point = muzzle_point(body, (3, 4, 2), spin=math.pi / 2)
    assert (point.x, point.y) == pytest.approx((4, -3))


def test_a_rolled_body_dips_its_muzzles_out_of_the_height() -> None:
    body = RolledBody(0, 0, math.pi, roll=math.pi / 2)
    point = muzzle_point(body, (0, 0, 10))
    assert (point.x, point.y, point.height) == pytest.approx((10, 0, 0))


def test_a_body_without_a_roll_is_not_rolled() -> None:
    point = muzzle_point(Body(0, 0, math.pi), (0, 0, 10))
    assert point.height == pytest.approx(10)


def test_p07_r04_a_piece_without_muzzle_placing_is_aimed_from_its_centre() -> None:
    class _Plain:
        def __init__(self, turret: BossTurret) -> None:
            self.x = 0
            self.y = 0
            self.heading = DOWN
            self.gone = False
            self.health = 10
            self.turret = turret

        @property
        def emitter(self) -> PlanePoint:
            return PlanePoint(self.x, self.y)

    turret = _turret(100000, x=10)
    pattern = BossPattern([_volley(_aimed(), turret=True, first=10)])
    pattern.turn_turrets(_Ctx(player=(100, 0)), 1, _sources({"core": _Plain(turret)}))  # type: ignore[dict-item]
    assert turret.aim == pytest.approx(-math.pi / 2)


def test_gd43_a_sweeping_laser_keeps_turning_with_its_owner() -> None:
    shots = _shots()
    owner = _Owner(PlanePoint(10, 10), heading=0)
    shots.fire_laser(owner, _laser(warning=0, firing=5, sweeps=True))
    shots.step(0.1, 0, 0)
    owner.heading = 1.0
    shots.step(0.1, 0, 0)
    assert shots.lasers[0].locked is None
    assert shots.lasers[0].heading == pytest.approx(1.0)


def test_gd43_a_laser_ends_after_its_warning_and_firing_time() -> None:
    shots = _shots()
    shots.fire_laser(_Owner(PlanePoint(0, 0)), _laser(warning=1, firing=1))
    shots.step(1.5, 0, 0)
    assert len(shots.lasers) == 1
    shots.step(1, 0, 0)
    assert shots.lasers == []


def test_gd43_a_laser_ends_when_its_owner_is_gone_or_has_no_health() -> None:
    shots = _shots()
    gone = _Owner(PlanePoint(0, 0))
    shots.fire_laser(gone, _laser())
    gone.gone = True
    shots.step(0.1, 0, 0)
    assert shots.lasers == []
    dead = _Owner(PlanePoint(0, 0))
    shots.fire_laser(dead, _laser())
    dead.health = 0
    shots.step(0.1, 0, 0)
    assert shots.lasers == []


def test_gd43_a_laser_is_seen_leaving_its_raised_emitter_through_the_eye() -> None:
    eye = SimpleNamespace(x=0, y=0, height=100)
    shots = _shots(eye)
    shots.fire_laser(_Owner(RaisedPoint(0, 50, 50), heading=0), _laser())
    laser = shots.lasers[0]
    # The eye sees the point at height 50 of a raised emitter twice as far out on the playfield.
    assert (laser.x, laser.y) == pytest.approx((0, 100))


def test_gd43_a_laser_on_the_playfield_is_seen_where_it_is() -> None:
    shots = _shots(SimpleNamespace(x=0, y=0, height=100))
    shots.fire_laser(_Owner(PlanePoint(20, 30), heading=0), _laser())
    assert (shots.lasers[0].x, shots.lasers[0].y) == (20, 30)


def test_gd43_counts_and_clear_cover_bullets_missiles_and_lasers() -> None:
    shots = _shots()
    shots.fire_bullet(50, 50, 0, _bullet())
    shots.fire_missile(50, 50, 0, _missile())
    shots.fire_laser(_Owner(PlanePoint(0, 0)), _laser())
    assert shots.count == 3
    shots.clear()
    assert shots.count == 0
    assert shots.lasers == []
    assert all(not b.alive for b in shots.bullets)


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


def test_gd45_a_seen_point_is_moved_by_the_eye_when_raised() -> None:
    eye = SimpleNamespace(x=0, y=0, height=100)
    world = _world(eye=eye)
    from core.entities.muzzle import RaisedPoint  # noqa: PLC0415

    point = world._context.seen(RaisedPoint(0, 50, 50))  # type: ignore[attr-defined]
    assert isinstance(point, PlanePoint)
    assert (point.x, point.y) == pytest.approx((0, 100))
