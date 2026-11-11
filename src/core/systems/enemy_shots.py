# Copyright (c) 2026 Renaud Guillon
"""The shots of all the enemies (ENM-16 to ENM-19).

Bullets, homing missiles the player can shoot down, and lasers with a warning line. Pure and
deterministic, stepped with a fixed `dt`.
"""

import math

from core.entities.muzzle import RaisedPoint, seen_on_playfield
from core.systems.projectile_motion import heading_to, turn_towards

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Protocol

from core.entities.enemy import (
    EnemyBulletSpec,
    EnemyBurstSpec,
    EnemyLaserSpec,
    EnemyMissileSpec,
    LaserOwner,
)
from core.entities.muzzle import PlayfieldEye


class _Pooled(Protocol):
    """An entry of a pool of shots: free for reuse once not `alive`."""

    alive: bool


class _Box(Protocol):
    """A playfield size."""

    @property
    def width(self) -> float: ...

    @property
    def height(self) -> float: ...


# __pragma__ ("noskip")


DEG = math.pi / 180

INFINITY = float("Infinity")
# Directions this close to none do not move a shot across the edge.
EPSILON = 1e-9


def shot_damage(spec: object) -> float:
    """Return a shot spec's own damage, 0 (the hull's rule) when it has none (D-314).

    A kind may hand its config's record over as the spec: one without `damage` (or with `None`,
    as a record answers for a key it lacks) uses the rule.
    """
    if hasattr(spec, "damage"):
        damage: float | None = spec.damage
        if damage:
            return damage
    return 0


class EnemyBullet:
    """An enemy bullet in flight (ENM-16): straight, at constant speed.

    `age` is the seconds since it was fired; `burst` is what it bursts into
    (`EnemyBulletSpec.burst`); `damage` its own damage, 0 for the hull's rule (D-314).
    """

    def __init__(self) -> None:
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self.speed = 0.0
        self.radius = 0.0
        self.style = ""
        self.age = 0.0
        self.burst: EnemyBurstSpec | None = None
        self.damage = 0.0


class EnemyMissile:
    """An enemy missile in flight.

    It homes on the player for a while, and can be shot down (ENM-18). It is a shot target (the
    player's shots can hit it). `homing` is the seconds of homing left, `age` the seconds since
    launch; `burst` is what it bursts into once `burst.after` seconds old
    (`EnemyMissileSpec.burst`).
    """

    def __init__(self) -> None:
        self.alive = True
        self.id = 0
        self.x = 0.0
        self.y = 0.0
        self.radius = 0.0
        self.health = 0.0
        self.max_health = 0.0
        self.heading = 0.0
        self.speed = 0.0
        self.turn_rate = 0.0
        self.homing = 0.0
        self.style = ""
        self.age = 0.0
        self.burst: EnemyBurstSpec | None = None
        self.damage = 0.0
        # WPN-08: seconds left flying straight out of the port, before any turning.
        self.launch = 0.0
        # WPN-09: how high above the plane of play it is (0 on it), and how it gets there: "loft"
        # (up out of its silo and over, down to the plane) or "flat".
        self.height = 0.0
        self.stage = "flat"
        self.stage_age = 0.0
        # Its loft: how long it lasts, its height and upward speed (px/s) as it leaves the silo.
        self.loft_seconds = 0.0
        self.loft_from = 0.0
        self.loft_speed = 0.0
        # How far its nose points above the plane (radians: pi/2 straight up), for its model.
        self.pitch = 0.0
        # WPN-09: it drifts off to its side as it climbs (`side`, a heading, `drift` px/s at most),
        # and gathers speed towards the player (`aim`, a heading, None until it has one).
        self.side = 0.0
        self.drift = 0.0
        self.aim: float | None = None


# WPN-09: how fast (radians a second) a lofted missile's nose turns up or down along its way.
NOSE_RATE = 3.0


def loft_height(s: float, start: float, rise: float) -> float:
    """WPN-09: a loft's height at `s` (0 to 1 of it), from `start` up at `rise` (px per loft).

    Straight up out of the silo, slowing to its top, then down onto the plane, level as it lands.
    """
    left = 1 - s
    return left * left * left * (start + (rise + 3 * start) * s)


def loft_rise(s: float, start: float, rise: float) -> float:
    """WPN-09: how fast a loft's height grows at `s` (px per loft, `loft_height`'s slope)."""
    left = 1 - s
    b = rise + 3 * start
    return left * left * (b * left - 3 * (start + b * s))


def loft_side(s: float) -> float:
    """WPN-09: how much of its sideways drift a lofted missile has at `s`: none, all at a third."""
    left = 1 - s
    return 6.75 * s * left * left


def loft_gather(s: float) -> float:
    """WPN-09: how much of its speed towards the player a lofted missile has at `s`.

    Gathering from the start, so it is already on its way as it tips over its top, eased into its
    full speed as it lands.
    """
    return s * (2 - s)


class EnemyLaser:
    """A laser (ENM-19): a warning line first, then the beam, from its owner's emitter.

    The warning line follows its owner's heading (a turret turning towards the player); the beam
    keeps the heading its owner had when it started firing, straight (BOSS-30), unless its spec
    `sweeps`. `locked` is that heading, once the beam fires.
    """

    def __init__(self, owner: LaserOwner, spec: EnemyLaserSpec) -> None:
        self.owner = owner
        self.spec = spec
        self.age = 0.0
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self._length = 0.0  # `length` is a property: Transcrypt forbids this attribute name
        self.phase = "warning"
        self.locked: float | None = None

    @property
    def length(self) -> float:
        """Length to the edge of the playfield."""
        return self._length

    @length.setter
    def length(self, value: float) -> None:
        """Set the length to the edge of the playfield."""
        self._length = value


class EnemyShotsOptions:
    """The playfield and what its shots are culled by.

    `cull_margin`: shots this far outside the playfield are removed (GAME-SCREEN-07). `eye`: the
    camera's eye, from which lasers are seen leaving their raised emitters; straight below them when
    None.
    """

    def __init__(
        self,
        width: float,
        height: float,
        cull_margin: float,
        eye: PlayfieldEye | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.cull_margin = cull_margin
        self.eye = eye


def ray_to_edge(x: float, y: float, heading: float, box: _Box, margin: float) -> float:
    """Length of a ray from (x, y) along `heading` to the edge of the playfield.

    Grown by `margin`.
    """
    dx = math.sin(heading)
    dy = math.cos(heading)

    def along(p: float, d: float, size: float) -> float:
        if d > EPSILON:
            return (size + margin - p) / d
        if d < -EPSILON:
            return (-margin - p) / d
        return INFINITY

    return max(0, min(along(x, dx, box.width), along(y, dy, box.height)))


class EnemyShots:
    """The shots of all the enemies.

    Its `bullets` and `missiles` are pools: entries with `alive` false are free for reuse.
    """

    def __init__(self, options: EnemyShotsOptions) -> None:
        self.options = options
        self.bullets: list[EnemyBullet] = []
        self.missiles: list[EnemyMissile] = []
        self._lasers: list[EnemyLaser] = []
        self._next_missile_id = 1

    @property
    def lasers(self) -> list[EnemyLaser]:
        """The lasers in the world."""
        return self._lasers

    def fire_bullet(self, x: float, y: float, heading: float, spec: EnemyBulletSpec) -> None:
        """Fire a bullet of `spec` from (x, y) along `heading`.

        Reusing a free one from the pool.
        """
        bullet = _first_free(self.bullets)
        if bullet is None:
            bullet = EnemyBullet()
            self.bullets.append(bullet)
        bullet.alive = True
        bullet.x = x
        bullet.y = y
        bullet.heading = heading
        bullet.speed = spec.speed
        bullet.radius = spec.radius
        bullet.style = spec.style
        bullet.burst = spec.burst
        bullet.damage = shot_damage(spec)
        bullet.age = 0

    def fire_missile(
        self, x: float, y: float, heading: float, spec: EnemyMissileSpec, height: float = 0
    ) -> None:
        """Launch a missile of `spec` from (x, y), `height` above the plane, along `heading`.

        Reusing a free one from the pool, with a fresh id.
        """
        missile = _first_free(self.missiles)
        if missile is None:
            missile = EnemyMissile()
            self.missiles.append(missile)
        missile.alive = True
        missile.id = self._next_missile_id
        self._next_missile_id += 1
        missile.x = x
        missile.y = y
        missile.heading = heading
        missile.radius = spec.radius
        missile.health = spec.health
        missile.max_health = spec.health
        missile.speed = spec.speed
        missile.turn_rate = spec.turn_rate_deg * DEG
        missile.homing = spec.homing_seconds
        missile.style = spec.style
        missile.burst = spec.burst
        missile.damage = shot_damage(spec)
        missile.age = 0
        flight = spec.flight
        lofts = flight.loft_seconds > 0
        missile.launch = 0 if lofts else flight.launch_seconds
        missile.loft_seconds = flight.loft_seconds
        missile.loft_speed = flight.loft_speed
        missile.height = height if lofts else 0
        missile.loft_from = missile.height
        missile.side = heading
        missile.drift = flight.loft_drift if lofts else 0
        missile.aim = None
        missile.pitch = math.pi / 2 if lofts else 0
        missile.stage_age = 0
        missile.stage = "loft" if lofts else "flat"

    def fire_laser(self, owner: LaserOwner, spec: EnemyLaserSpec) -> None:
        """Start a laser of `spec` from `owner`, aimed at once."""
        self._lasers.append(EnemyLaser(owner, spec))
        self._aim(self._lasers[len(self._lasers) - 1])

    @property
    def count(self) -> int:
        """Number of bullets and missiles in flight, and lasers shown."""
        return _alive_count(self.bullets) + _alive_count(self.missiles) + len(self._lasers)

    def clear(self) -> None:
        """Remove every shot (as a bomb does, GAME-BOMB-05)."""
        for bullet in self.bullets:
            bullet.alive = False
        for missile in self.missiles:
            missile.alive = False
        self._lasers.clear()

    def step(self, dt: float, player_x: float, player_y: float) -> None:
        """Move the shots by `dt`; missiles home on (player_x, player_y)."""
        self._move_bullets(dt)
        for missile in self.missiles:
            if missile.alive:
                self._move_missile(missile, dt, player_x, player_y)
        i = len(self._lasers) - 1
        while i >= 0:
            if not self._step_laser(self._lasers[i], dt):
                self._lasers.pop(i)
            i -= 1

    def _move_bullets(self, dt: float) -> None:
        """Move the bullets straight on; those due to burst do, once all have moved."""
        bursting: list[tuple[EnemyBullet, EnemyBurstSpec]] = []
        for b in self.bullets:
            if not b.alive:
                continue
            b.x += math.sin(b.heading) * b.speed * dt
            b.y += math.cos(b.heading) * b.speed * dt
            b.age += dt
            if self._is_out(b.x, b.y):
                b.alive = False
            elif b.burst and b.age >= b.burst.after:
                bursting.append((b, b.burst))
        for b, burst in bursting:
            self._burst(b, burst)

    def _burst(self, b: EnemyBullet, burst: EnemyBurstSpec) -> None:
        """Remove a bursting bullet and fire its ring of bullets (`burst`) from where it was."""
        b.alive = False
        for k in range(burst.count):
            self.fire_bullet(b.x, b.y, b.heading + (2 * math.pi * k) / burst.count, burst.bullet)

    def _move_missile(self, m: EnemyMissile, dt: float, player_x: float, player_y: float) -> None:
        if m.health <= 0:
            m.alive = False
            return
        if m.stage == "loft":
            self._loft(m, dt, player_x, player_y)
            return
        if m.launch > 0:
            # WPN-08: straight out of the port first, the homing time not yet running.
            m.launch -= dt
        elif m.homing > 0:
            m.heading = turn_towards(
                m.heading, heading_to(m.x, m.y, player_x, player_y), m.turn_rate * dt
            )
            m.homing -= dt
        m.x += math.sin(m.heading) * m.speed * dt
        m.y += math.cos(m.heading) * m.speed * dt
        m.age += dt
        if self._is_out(m.x, m.y):
            m.alive = False
        elif m.burst and m.age >= m.burst.after:
            self._burst_missile(m, m.burst)

    def _loft(self, m: EnemyMissile, dt: float, player_x: float, player_y: float) -> None:
        """WPN-09: up out of the silo, over and down onto the plane, then it homes.

        One smooth curve over `loft_seconds`: it leaves straight up at `loft_speed`, drifting off to
        its side (so the missiles of a block part), slows to its top, and comes down gathering its
        speed towards the player, landing level and at full speed along its way.
        """
        to_player = heading_to(m.x, m.y, player_x, player_y)
        if m.aim is None:
            m.aim = to_player
        aim = turn_towards(m.aim, to_player, m.turn_rate * dt)
        m.aim = aim
        m.age += dt
        seconds = m.loft_seconds
        before = m.stage_age / seconds
        m.stage_age = min(seconds, m.stage_age + dt)
        s = m.stage_age / seconds
        # Along the plane, by its velocity halfway through the step.
        mid = self._loft_velocity(m, aim, (before + s) / 2)
        m.x += mid[0] * dt
        m.y += mid[1] * dt
        rise = m.loft_speed * seconds
        m.height = loft_height(s, m.loft_from, rise)
        v = self._loft_velocity(m, aim, s)
        flat = math.hypot(v[0], v[1])
        if flat > 1e-6:
            m.heading = math.atan2(v[0], v[1])
        # Its nose follows its way, turning no faster than `NOSE_RATE` (no flip over its top).
        way = math.atan2(loft_rise(s, m.loft_from, rise) / seconds, flat)
        m.pitch = turn_towards(m.pitch, way, NOSE_RATE * dt)
        if s >= 1:
            m.height = 0
            m.pitch = 0
            m.heading = aim
            m.stage = "flat"
        if self._is_out(m.x, m.y):
            m.alive = False

    @staticmethod
    def _loft_velocity(m: EnemyMissile, aim: float, s: float) -> tuple[float, float]:
        """WPN-09: a lofted missile's velocity along the plane at `s` (0 to 1 of its loft)."""
        drift = m.drift * loft_side(s)
        travel = m.speed * loft_gather(s)
        return (
            math.sin(m.side) * drift + math.sin(aim) * travel,
            math.cos(m.side) * drift + math.cos(aim) * travel,
        )

    def _burst_missile(self, m: EnemyMissile, burst: EnemyBurstSpec) -> None:
        """Remove a missile whose fuse is out and fire its ring of bullets from where it was."""
        m.alive = False
        for k in range(burst.count):
            self.fire_bullet(m.x, m.y, m.heading + (2 * math.pi * k) / burst.count, burst.bullet)

    def _step_laser(self, laser: EnemyLaser, dt: float) -> bool:
        """Advances a laser; returns false once it is over (or its owner is gone)."""
        laser.age += dt
        warning = laser.spec.warning_seconds
        firing = laser.spec.firing_seconds
        owner = laser.owner
        if owner.gone or owner.health <= 0 or laser.age >= warning + firing:
            return False
        laser.phase = "warning" if laser.age < warning else "firing"
        if laser.phase == "firing" and laser.spec.sweeps is not True and laser.locked is None:
            laser.locked = owner.heading
        self._aim(laser)
        return True

    def _aim(self, laser: EnemyLaser) -> None:
        emitter = laser.owner.emitter
        height = emitter.height if hasattr(emitter, "height") else 0
        point = seen_on_playfield(self.options.eye, RaisedPoint(emitter.x, emitter.y, height))
        laser.x = point.x
        laser.y = point.y
        laser.heading = laser.locked if laser.locked is not None else laser.owner.heading
        laser.length = ray_to_edge(
            point.x, point.y, laser.heading, self.options, self.options.cull_margin
        )

    def _is_out(self, x: float, y: float) -> bool:
        m = self.options.cull_margin
        return x < -m or x > self.options.width + m or y < -m or y > self.options.height + m


def _first_free[P: _Pooled](pool: list[P]) -> P | None:
    """Return the first entry of a pool that is not alive, if any."""
    for entry in pool:
        if not entry.alive:
            return entry
    return None


def _alive_count(pool: Sequence[_Pooled]) -> int:
    count = 0
    for entry in pool:
        if entry.alive:
            count += 1
    return count
