"""Projectiles in flight (P03), ported from `core/systems/projectile-motion.ts`.

A shot's heading is in radians from forward (+Y), positive to the right.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.shot_target import closest_target

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.entities.shot_target import ShotTarget  # noqa: E402
from core.entities.weapon import ProjectileWeaponDefinition  # noqa: E402

__pragma__("noskip")

DEG = math.pi / 180


class Projectile:
    """A shot in flight. `age` is the seconds since launch."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        alive: bool,
        weapon: ProjectileWeaponDefinition,
        x: float,
        y: float,
        heading: float,
        speed: float,
        age: float,
    ) -> None:
        self.alive = alive
        self.weapon = weapon
        self.x = x
        self.y = y
        self.heading = heading
        self.speed = speed
        self.age = age


def wrap_angle(angle: float) -> float:
    """Wraps an angle into (-π, π]."""
    wrapped = angle - 2 * math.pi * math.floor((angle + math.pi) / (2 * math.pi))
    return math.pi if wrapped == -math.pi else wrapped


def heading_to(x: float, y: float, tx: float, ty: float) -> float:
    """Heading (from +Y, positive to the right) of the direction from (x, y) to (tx, ty)."""
    return math.atan2(tx - x, ty - y)


def _sign(value: float) -> float:
    """`Math.sign`."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def turn_towards(heading: float, desired: float, max_turn: float) -> float:
    """Turns `heading` towards `desired` by at most `max_turn` radians."""
    delta = wrap_angle(desired - heading)
    if abs(delta) <= max_turn:
        return desired
    return wrap_angle(heading + _sign(delta) * max_turn)


def advance_projectile(shot: Projectile, targets: Sequence[ShotTarget], dt: float) -> None:
    """Advances a projectile by `dt` (P03-R01, P03-R03): homes on the living target closest to it,
    within its weapon's homing range (re-chosen every step) if its weapon homes, accelerates up to
    the speed cap, then moves along its heading.
    """
    weapon = shot.weapon
    if weapon.homing_turn_rate_deg > 0:
        target = closest_target(targets, shot.x, shot.y, weapon.homing_range)
        if target:
            desired = heading_to(shot.x, shot.y, target.x, target.y)
            shot.heading = turn_towards(
                shot.heading, desired, weapon.homing_turn_rate_deg * DEG * dt
            )
    if weapon.acceleration > 0:
        shot.speed = min(weapon.max_speed, shot.speed + weapon.acceleration * dt)
    shot.x += math.sin(shot.heading) * shot.speed * dt
    shot.y += math.cos(shot.heading) * shot.speed * dt
    shot.age += dt
