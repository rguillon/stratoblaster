"""Helpers shared by the concrete enemies (P05), ported from `game/sim/enemies/enemy-helpers.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.enemy_motion import Path

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from core.entities.enemy import EnemyBulletSpec, EnemyContext, EnemySpawnArea  # noqa: E402
from core.math.rng import Random  # noqa: E402
from core.systems.enemy_motion import PathPoint  # noqa: E402

__pragma__("noskip")

# Degrees to radians.
DEG = math.pi / 180

# Straight down the screen, towards the player's side.
DOWN = math.pi

# A coin toss: a random number below one half.
HALF = 0.5

# Entries keep enemies this far (a fraction of the edge) from the corners.
ENTRY_INSET = 0.08


class Cadence:
    """A repeating timer: `tick` returns how many times it went off during `dt` (an attack every
    `interval` seconds, the first one after `first`, `interval` when None).
    """

    def __init__(self, interval: float, first: float | None = None) -> None:
        self.interval = interval
        self._left = interval if first is None else first

    @property
    def progress(self) -> float:
        """Fraction of the wait done before the next time, 0..1 (for charging lights)."""
        return min(1, max(0, 1 - self._left / self.interval))

    def tick(self, dt: float) -> int:
        self._left -= dt
        count = 0
        while self._left <= 0:
            self._left += self.interval
            count += 1
        return count


def on_playfield(enemy: Enemy, ctx: EnemyContext) -> bool:
    """Whether the enemy's centre is over the playfield (enemies only shoot from there)."""
    return enemy.x >= 0 and enemy.x <= ctx.width and enemy.y >= 0 and enemy.y <= ctx.height


def clamp_entry(position: float) -> float:
    """A wave's entry position, kept away from the corners of the playfield."""
    return min(1 - ENTRY_INSET, max(ENTRY_INSET, position))


def coin(random: Random) -> bool:
    """A coin toss, from a random number."""
    return random() < HALF


def top_bounds(area: EnemySpawnArea) -> tuple[float, float]:
    """The X range enemies coming in from the top keep to: `topRange`, or the whole width."""
    if area.top_range is None:
        return (0, area.width)
    return (area.top_range[0], area.top_range[1])


def top_x(area: EnemySpawnArea, fraction: float) -> float:
    """X at `fraction` (0..1) across the range enemies coming in from the top keep to."""
    low, high = top_bounds(area)
    return low + (high - low) * fraction


def range_in(random: Random, range_: tuple[float, float]) -> float:
    """A random number in `range_` (a [low, high) pair)."""
    return range_[0] + (range_[1] - range_[0]) * random()


def pick_x(random: Random, range_: tuple[float, float], area: EnemySpawnArea) -> float:
    """A random X at a fraction in `range_` across the range enemies coming in from the top keep
    to.
    """
    return top_x(area, range_in(random, range_))


def playfield_path(points: list[list[float]], area: EnemySpawnArea, mirror: bool) -> Path:
    """A path given in fractions of the playfield, mirrored left to right if `mirror`. It comes in
    from the top, so its X fractions are taken across the area's `top_range`.
    """
    controls: list[PathPoint] = []
    for point in points:
        fraction = 1 - point[0] if mirror else point[0]
        controls.append([top_x(area, fraction), point[1] * area.height])
    return Path(controls)


def bullet_shot(
    ctx: EnemyContext, bullet: EnemyBulletSpec
) -> Callable[[float, float, float], None]:
    """A shot callback for `fire_aimed`: each shot is a `bullet` of the enemy's own."""

    def fire(x: float, y: float, heading: float) -> None:
        ctx.fire_bullet(x, y, heading, bullet)

    return fire
