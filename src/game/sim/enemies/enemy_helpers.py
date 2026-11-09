# Copyright (c) 2026 Renaud Guillon
"""Helpers shared by the concrete enemies, each kind with its preset movement (ENM-24)."""

import math

from core.entities.enemy import Enemy, EnemyMissileSpec, MissileFlight
from core.systems.enemy_motion import Path
from core.systems.enemy_shots import shot_damage
from core.systems.projectile_motion import turn_towards
from game.config.weapons import WEAPONS

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

from core.entities.enemy import EnemyBulletSpec, EnemyContext, EnemySpawnArea
from core.math.rng import Random
from core.systems.enemy_motion import PathPoint

# __pragma__ ("noskip")


# Degrees to radians.
DEG = math.pi / 180

# Straight down the screen, towards the player's side.
DOWN = math.pi

# Straight up the screen, away from the player's side.
UP = 0.0

# How fast an enemy turns its nose to the way it leaves, rad/s.
LEAVE_TURN = 4.0

# Enemies coming in from a side keep above this fraction of the playfield height, so none appears
# laterally in the bottom third, next to the player's ship.
SIDE_MIN_HEIGHT = 1 / 3

# A coin toss: a random number below one half.
HALF = 0.5

# Entries keep enemies this far (a fraction of the edge) from the corners.
ENTRY_INSET = 0.08


def leave_upward(enemy: Enemy, speed: float, dt: float) -> None:
    """Fly `enemy` up the screen at `speed`, its nose turning round to point the way it goes."""
    enemy.heading = turn_towards(enemy.heading, UP, LEAVE_TURN * dt)
    enemy.y += speed * dt


def missile_flight(up: bool) -> MissileFlight:
    """Return how a missile leaves its launcher (WPN-08, WPN-09): from an upward silo, or not."""
    if up:
        return MissileFlight(
            0, WEAPONS.missileLoftSeconds, WEAPONS.missileLoftSpeed, WEAPONS.missileLoftDrift
        )
    return MissileFlight(WEAPONS.missileLaunchSeconds)


def missile_spec(missile: Any, up: bool = False) -> EnemyMissileSpec:
    """Return the engine's missile spec of a config's `missile` record.

    The core reads `turn_rate_deg` and `homing_seconds`, which the config writes in camel case, so
    a config record cannot be handed over as it is.
    """
    return EnemyMissileSpec(
        missile.speed,
        missile.turnRateDeg,
        missile.homingSeconds,
        missile.radius,
        missile.health,
        missile.style,
        None,
        missile_flight(up),
        shot_damage(missile),
    )


class Cadence:
    """A repeating timer: an attack every `interval` seconds.

    `tick` returns how many times it went off during `dt` (an attack every `interval` seconds, the
    first one after `first`, `interval` when None).
    """

    def __init__(self, interval: float, first: float | None = None) -> None:
        self.interval = interval
        self._left = interval if first is None else first

    @property
    def progress(self) -> float:
        """Fraction of the wait done before the next time, 0..1 (for charging lights, ENM-23)."""
        return min(1, max(0, 1 - self._left / self.interval))

    def tick(self, dt: float) -> int:
        """Count down `dt` seconds and return how many times the interval came due."""
        self._left -= dt
        count = 0
        while self._left <= 0:
            self._left += self.interval
            count += 1
        return count


def on_playfield(enemy: Enemy, ctx: EnemyContext) -> bool:
    """Whether the enemy's centre is over the playfield (enemies only shoot from there, ENM-15)."""
    return enemy.x >= 0 and enemy.x <= ctx.width and enemy.y >= 0 and enemy.y <= ctx.height


def clamp_entry(position: float) -> float:
    """Return a wave's entry position (ENM-08), kept away from the corners of the playfield."""
    return min(1 - ENTRY_INSET, max(ENTRY_INSET, position))


def side_height(position: float) -> float:
    """Return the height fraction (0..1 from the bottom) a side entry at `position` comes in at.

    Kept away from the corners and out of the bottom third of the playfield.
    """
    return max(SIDE_MIN_HEIGHT, clamp_entry(position))


def side_dive_stop_x(area: EnemySpawnArea, left: bool) -> float:
    """X where a diver coming in from a side stops, in that side's half of the range (ENM-08).

    A little random, so the divers of one wave do not stop on top of each other.
    """
    fraction = 0.2 + 0.3 * area.random()
    return top_x(area, fraction if left else 1 - fraction)


def coin(random: Random) -> bool:
    """Return a coin toss, from a random number."""
    return random() < HALF


def top_bounds(area: EnemySpawnArea) -> tuple[float, float]:
    """Return the X range enemies from the top keep to (ENM-09).

    It is `topRange`, or the whole width.
    """
    if area.top_range is None:
        return (0, area.width)
    return (area.top_range[0], area.top_range[1])


def top_x(area: EnemySpawnArea, fraction: float) -> float:
    """X at `fraction` (0..1) across the range enemies coming in from the top keep to."""
    low, high = top_bounds(area)
    return low + (high - low) * fraction


def range_in(random: Random, range_: tuple[float, float]) -> float:
    """Return a random number in `range_` (a [low, high) pair)."""
    return range_[0] + (range_[1] - range_[0]) * random()


def stop_height(area: EnemySpawnArea, range_: tuple[float, float]) -> float:
    """Return a height at a random fraction in `range_` of the area's height (D-313).

    Each enemy of a kind stops at its own height, so a crowd spreads down the playfield instead of
    lining up along the top.
    """
    return range_in(area.random, range_) * area.height


def pick_x(random: Random, range_: tuple[float, float], area: EnemySpawnArea) -> float:
    """Return a random X at a fraction in `range_` across the top enemies' range.

    That is the range that enemies from the top keep to.
    """
    return top_x(area, range_in(random, range_))


def playfield_path(points: list[list[float]], area: EnemySpawnArea, mirror: bool) -> Path:
    """Return a path given in fractions of the playfield, mirrored if `mirror` (ENM-25).

    It is mirrored left to right. It comes in from the top, so its X fractions are taken across the
    area's `top_range`.
    """
    controls: list[PathPoint] = []
    for point in points:
        fraction = 1 - point[0] if mirror else point[0]
        controls.append([top_x(area, fraction), point[1] * area.height])
    return Path(controls)


def bullet_shot(
    ctx: EnemyContext, bullet: EnemyBulletSpec
) -> Callable[[float, float, float], None]:
    """Return a shot callback for `fire_aimed`: each shot is a `bullet` of the enemy's own."""

    def fire(x: float, y: float, heading: float) -> None:
        ctx.fire_bullet(x, y, heading, bullet)

    return fire
