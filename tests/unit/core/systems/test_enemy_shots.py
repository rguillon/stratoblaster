"""Unit tests of `src/core/systems/enemy_shots.py`."""

import math
from types import SimpleNamespace

import pytest

from core.entities.enemy import EnemyBulletSpec, EnemyBurstSpec, EnemyLaserSpec, EnemyMissileSpec
from core.entities.muzzle import PlanePoint, RaisedPoint
from core.systems.enemy_shots import (
    EnemyBullet,
    EnemyLaser,
    EnemyMissile,
    EnemyShots,
    EnemyShotsOptions,
    ray_to_edge,
)

BOX = SimpleNamespace(width=100, height=100)


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


def test_gd43_a_ray_reaches_the_edge_in_its_direction() -> None:
    assert ray_to_edge(50, 50, 0, BOX, 0) == pytest.approx(50)
    assert ray_to_edge(50, 50, math.pi / 2, BOX, 0) == pytest.approx(50)
    assert ray_to_edge(50, 50, math.pi, BOX, 0) == pytest.approx(50)
    assert ray_to_edge(50, 50, -math.pi / 2, BOX, 0) == pytest.approx(50)
    assert ray_to_edge(50, 50, math.pi / 4, BOX, 0) == pytest.approx(50 / math.sin(math.pi / 4))


def test_gd43_the_margin_grows_the_edge_and_a_ray_outside_has_no_length() -> None:
    assert ray_to_edge(50, 50, 0, BOX, 10) == pytest.approx(60)
    assert ray_to_edge(150, 50, math.pi / 2, BOX, 0) == 0


def test_gd43_fire_bullet_sets_its_fields() -> None:
    shots = _shots()
    shots.fire_bullet(1, 2, 0.5, _bullet(speed=7, burst=EnemyBurstSpec(1, 3, _bullet())))
    bullet = shots.bullets[0]
    assert isinstance(bullet, EnemyBullet)
    assert (bullet.x, bullet.y, bullet.heading, bullet.speed) == (1, 2, 0.5, 7)
    assert (bullet.radius, bullet.style, bullet.age) == (2, "round", 0)
    assert bullet.burst is not None
    assert bullet.burst.count == 3


def test_gd43_a_free_bullet_is_reused() -> None:
    shots = _shots()
    shots.fire_bullet(0, 0, 0, _bullet())
    shots.bullets[0].alive = False
    shots.fire_bullet(5, 5, 0, _bullet())
    assert len(shots.bullets) == 1
    assert (shots.bullets[0].x, shots.bullets[0].alive) == (5, True)


def test_gd43_bullets_fly_straight_and_leave_the_playfield_behind() -> None:
    shots = _shots()
    shots.fire_bullet(50, 50, 0, _bullet(speed=10))
    shots.step(0.5, 0, 0)
    assert shots.bullets[0].y == pytest.approx(55)
    assert shots.bullets[0].age == pytest.approx(0.5)
    shots.fire_bullet(0, 0, math.pi, _bullet(speed=100))
    shots.step(1, 0, 0)
    assert shots.bullets[1].alive is False


def test_gd44_a_missile_homes_on_the_player_for_its_homing_time() -> None:
    shots = _shots()
    shots.fire_missile(0, 0, math.pi / 2, _missile())
    missile = shots.missiles[0]
    assert isinstance(missile, EnemyMissile)
    assert missile.id == 1
    assert missile.turn_rate == pytest.approx(math.pi / 2)
    # Player straight up: a 90 deg/s turn for half a second turns 45 degrees towards it.
    shots.step(0.5, 0, 100)
    assert missile.heading == pytest.approx(math.pi / 4)
    assert missile.homing == pytest.approx(0.5)
    shots.step(0.5, 0, 100)
    assert missile.heading == pytest.approx(0)
    assert missile.homing == pytest.approx(0)
    shots.step(0.5, 0, 0)
    assert missile.heading == pytest.approx(0)


def test_gd44_a_missile_with_no_health_dies_without_moving() -> None:
    shots = _shots()
    shots.fire_missile(0, 0, 0, _missile())
    shots.missiles[0].health = 0
    shots.step(1, 0, 0)
    assert shots.missiles[0].alive is False
    assert shots.missiles[0].y == 0


def test_gd44_free_missiles_are_reused_and_keep_counting_ids() -> None:
    shots = _shots()
    shots.fire_missile(0, 0, 0, _missile())
    shots.missiles[0].alive = False
    shots.fire_missile(0, 0, 0, _missile())
    assert len(shots.missiles) == 1
    assert shots.missiles[0].id == 2
    assert shots.missiles[0].max_health == 5


def test_gd43_a_laser_warns_then_fires_along_its_locked_heading() -> None:
    shots = _shots()
    owner = _Owner(PlanePoint(10, 10), heading=0)
    shots.fire_laser(owner, _laser(warning=1, firing=1))
    laser = shots.lasers[0]
    assert isinstance(laser, EnemyLaser)
    assert (laser.x, laser.y, laser.heading, laser.phase) == (10, 10, 0, "warning")
    assert laser.length == pytest.approx(100)
    shots.step(0.5, 0, 0)
    assert laser.phase == "warning"
    owner.heading = 1.0
    shots.step(0.5, 0, 0)
    # It locks onto the heading its owner has as it starts firing (1.0), then stays on it.
    assert laser.phase == "firing"
    assert laser.locked == pytest.approx(1.0)
    assert laser.heading == pytest.approx(1.0)
    owner.heading = 2.0
    shots.step(0.1, 0, 0)
    assert laser.heading == pytest.approx(1.0)
