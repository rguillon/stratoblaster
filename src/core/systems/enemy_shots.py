"""The shots of all the enemies (GD-43, GD-44)

Bullets, homing missiles the player can shoot down, and lasers with a warning line. Pure and
deterministic, stepped with a fixed `dt`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.muzzle import RaisedPoint, seen_on_playfield
from core.systems.projectile_motion import heading_to, turn_towards

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol, TypeVar  # noqa: E402

from core.entities.enemy import (  # noqa: E402
    EnemyBulletSpec,
    EnemyBurstSpec,
    EnemyLaserSpec,
    EnemyMissileSpec,
    LaserOwner,
)
from core.entities.muzzle import PlayfieldEye  # noqa: E402


class _Pooled(Protocol):
    """An entry of a pool of shots: free for reuse once not `alive`."""

    alive: bool


P = TypeVar("P", bound=_Pooled)


class _Box(Protocol):
    """A playfield size."""

    @property
    def width(self) -> float: ...

    @property
    def height(self) -> float: ...


__pragma__("noskip")

DEG = math.pi / 180

INFINITY = float("Infinity")
# Directions this close to none do not move a shot across the edge.
EPSILON = 1e-9


class EnemyBullet:
    """An enemy bullet in flight (GD-43): straight, at constant speed. `age` is the seconds since
    it was fired; `burst` is what it bursts into (`EnemyBulletSpec.burst`).
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


class EnemyMissile:
    """An enemy missile in flight: it homes on the player for a while, and can be shot down. It is
    a shot target (the player's shots can hit it). `homing` is the seconds of homing left, `age`
    the seconds since launch.
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


class EnemyLaser:
    """A laser: a warning line first, then the beam, from its owner's emitter. The warning line
    follows its owner's heading (a turret turning towards the player); the beam keeps the heading
    its owner had when it started firing, straight (phase 8 review), unless its spec `sweeps`.
    `locked` is that heading, once the beam fires.
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
        self._length = value


class EnemyShotsOptions:
    """The playfield and what its shots are culled by.

    `cull_margin`: shots this far outside the playfield are removed. `eye`: the camera's eye, from
    which lasers are seen leaving their raised emitters; straight below them when None.
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
    """Length of a ray from (x, y) along `heading` to the edge of the playfield, grown by
    `margin`."""
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
    """The shots of all the enemies. Its `bullets` and `missiles` are pools: entries with `alive`
    false are free for reuse.
    """

    def __init__(self, options: EnemyShotsOptions) -> None:
        self.options = options
        self.bullets: list[EnemyBullet] = []
        self.missiles: list[EnemyMissile] = []
        self._lasers: list[EnemyLaser] = []
        self._next_missile_id = 1

    @property
    def lasers(self) -> list[EnemyLaser]:
        return self._lasers

    def fire_bullet(self, x: float, y: float, heading: float, spec: EnemyBulletSpec) -> None:
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
        bullet.age = 0

    def fire_missile(self, x: float, y: float, heading: float, spec: EnemyMissileSpec) -> None:
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
        missile.age = 0

    def fire_laser(self, owner: LaserOwner, spec: EnemyLaserSpec) -> None:
        self._lasers.append(EnemyLaser(owner, spec))
        self._aim(self._lasers[len(self._lasers) - 1])

    @property
    def count(self) -> int:
        """Number of bullets and missiles in flight, and lasers shown."""
        return _alive_count(self.bullets) + _alive_count(self.missiles) + len(self._lasers)

    def clear(self) -> None:
        """Removes every shot."""
        for bullet in self.bullets:
            bullet.alive = False
        for missile in self.missiles:
            missile.alive = False
        self._lasers.clear()

    def step(self, dt: float, player_x: float, player_y: float) -> None:
        """Moves the shots by `dt`; missiles home on (player_x, player_y)."""
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
        """Moves the bullets straight on; those due to burst do, once all have moved."""
        bursting: list[EnemyBullet] = []
        for b in self.bullets:
            if not b.alive:
                continue
            b.x += math.sin(b.heading) * b.speed * dt
            b.y += math.cos(b.heading) * b.speed * dt
            b.age += dt
            if self._is_out(b.x, b.y):
                b.alive = False
            elif b.burst and b.age >= b.burst.after:
                bursting.append(b)
        for b in bursting:
            self._burst(b)

    def _burst(self, b: EnemyBullet) -> None:
        """A bursting bullet is gone, and its ring of bullets leaves from where it was."""
        burst = b.burst
        b.alive = False
        if not burst:
            return
        for k in range(burst.count):
            self.fire_bullet(b.x, b.y, b.heading + (2 * math.pi * k) / burst.count, burst.bullet)

    def _move_missile(self, m: EnemyMissile, dt: float, player_x: float, player_y: float) -> None:
        if m.health <= 0:
            m.alive = False
            return
        if m.homing > 0:
            m.heading = turn_towards(
                m.heading, heading_to(m.x, m.y, player_x, player_y), m.turn_rate * dt
            )
            m.homing -= dt
        m.x += math.sin(m.heading) * m.speed * dt
        m.y += math.cos(m.heading) * m.speed * dt
        m.age += dt
        if self._is_out(m.x, m.y):
            m.alive = False

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


def _first_free(pool: list[P]) -> P | None:  # noqa: UP047 (Transcrypt has no PEP 695)
    """The first entry of a pool that is not alive, if any."""
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
