"""Unit tests of `src/core/systems/projectile_motion.py`."""

import math

import pytest

from core.entities.boss_turret import BossTurret
from core.entities.enemy import EnemyBulletSpec, EnemyLaserSpec, EnemyMissileSpec
from core.entities.muzzle import PlanePoint, RaisedPoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.boss_pattern import BossPattern, BossRingShape, BossVolley
from core.systems.projectile_motion import DEG as DEG_MOTION
from core.systems.projectile_motion import (
    Projectile,
    advance_projectile,
    heading_to,
    turn_towards,
    wrap_angle,
)

DEG = math.pi / 180

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


class _Target:
    def __init__(self, x: float, y: float, health: float = 10) -> None:
        self.id = 0
        self.x = x
        self.y = y
        self.radius = 1
        self.health = health
        self.max_health = health


def _weapon(
    homing_turn_rate_deg: float = 0,
    homing_range: float = 1000,
    acceleration: float = 0,
    max_speed: float = 100,
) -> ProjectileWeaponDefinition:
    return ProjectileWeaponDefinition(
        "w",
        "W",
        "muzzle",
        5,
        10,
        acceleration,
        max_speed,
        homing_turn_rate_deg,
        homing_range,
        1,
        1,
        0,
        [[ShotStream(0, 0)]],
    )


def _shot(weapon: ProjectileWeaponDefinition, heading: float = 0, speed: float = 10) -> Projectile:
    return Projectile(True, weapon, 0, 0, heading, speed, 0)


def test_p07_r04_a_ring_fires_all_around_and_turns_on_each_volley() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(BossRingShape(4, 30, BULLET), first=0)])
    sources = _sources({"core": _Src()})
    pattern.step(ctx, 0.1, sources)
    first = sorted(wrap_angle(h) for _, _, h, _ in ctx.bullets)
    assert first == pytest.approx(sorted(wrap_angle(DOWN + k * math.pi / 2) for k in range(4)))
    ctx.bullets.clear()
    pattern._states[0].left = 0
    pattern.step(ctx, 0.1, sources)
    second = sorted(wrap_angle(h) for _, _, h, _ in ctx.bullets)
    expected = sorted(wrap_angle(DOWN + 30 * DEG + k * math.pi / 2) for k in range(4))
    assert second == pytest.approx(expected)
    assert pattern._states[0].turns == 2


def test_p03_r01_wrap_angle_maps_into_minus_pi_to_pi() -> None:
    assert wrap_angle(0) == 0
    assert wrap_angle(math.pi) == pytest.approx(math.pi)
    assert wrap_angle(-math.pi) == pytest.approx(math.pi)
    assert wrap_angle(3 * math.pi) == pytest.approx(math.pi)
    assert wrap_angle(-3 * math.pi / 2) == pytest.approx(math.pi / 2)


def test_p03_r01_heading_points_from_the_first_point_to_the_second() -> None:
    assert heading_to(0, 0, 0, 1) == pytest.approx(0)
    assert heading_to(0, 0, 1, 0) == pytest.approx(math.pi / 2)
    assert heading_to(0, 0, 0, -1) == pytest.approx(math.pi)
    assert heading_to(2, 2, 2, 3) == pytest.approx(0)


def test_p03_r01_turn_within_the_limit_reaches_the_desired_heading() -> None:
    assert turn_towards(0, 0.1, 0.5) == 0.1


def test_p03_r01_turn_beyond_the_limit_moves_by_the_limit() -> None:
    assert turn_towards(0, 1.0, 0.25) == pytest.approx(0.25)
    assert turn_towards(0, -1.0, 0.25) == pytest.approx(-0.25)


def test_p03_r01_turn_takes_the_shorter_way_round() -> None:
    # From 3.0 to -3.0 the short way goes through pi: heading grows.
    assert turn_towards(3.0, -3.0, 0.1) == pytest.approx(3.1)


def test_p03_r01_turn_with_no_difference_and_a_negative_limit_stays() -> None:
    assert turn_towards(0, 0, -0.5) == 0


def test_p03_r01_a_straight_shot_moves_along_its_heading() -> None:
    shot = _shot(_weapon(), heading=0, speed=10)
    advance_projectile(shot, [], 0.5)
    assert shot.x == pytest.approx(0)
    assert shot.y == pytest.approx(5)
    assert shot.age == pytest.approx(0.5)
    assert shot.speed == 10


def test_p03_r01_a_sideways_shot_moves_along_x() -> None:
    shot = _shot(_weapon(), heading=math.pi / 2, speed=10)
    advance_projectile(shot, [], 0.5)
    assert shot.x == pytest.approx(5)
    assert shot.y == pytest.approx(0, abs=1e-9)


def test_p03_r01_acceleration_speeds_up_to_the_cap() -> None:
    shot = _shot(_weapon(acceleration=20, max_speed=100), speed=10)
    advance_projectile(shot, [], 0.5)
    assert shot.speed == pytest.approx(20)
    advance_projectile(shot, [], 1000)
    assert shot.speed == 100


def test_p03_r01_homing_turns_towards_the_closest_target_in_range() -> None:
    # Target straight to the right; 90 deg/s over 0.5 s turns at most 45 deg.
    shot = _shot(_weapon(homing_turn_rate_deg=90), heading=0, speed=0)
    advance_projectile(shot, [_Target(100, 0)], 0.5)
    assert shot.heading == pytest.approx(math.pi / 4)


def test_p03_r01_homing_reaches_a_target_within_the_turn_limit() -> None:
    shot = _shot(_weapon(homing_turn_rate_deg=360), heading=math.pi / 2, speed=0)
    advance_projectile(shot, [_Target(0, 100)], 0.5)
    assert shot.heading == pytest.approx(0)


def test_p03_r01_homing_ignores_targets_out_of_range_and_dead_ones() -> None:
    shot = _shot(_weapon(homing_turn_rate_deg=90, homing_range=50), heading=0, speed=0)
    advance_projectile(shot, [_Target(500, 0), _Target(1, 0, health=0)], 0.5)
    assert shot.heading == 0


def test_p03_r01_a_shot_without_homing_ignores_targets() -> None:
    shot = _shot(_weapon(homing_turn_rate_deg=0), heading=0, speed=0)
    advance_projectile(shot, [_Target(100, 0)], 0.5)
    assert shot.heading == 0


def test_p03_r01_degrees_to_radians_constant() -> None:
    assert pytest.approx(math.pi / 180) == DEG_MOTION
