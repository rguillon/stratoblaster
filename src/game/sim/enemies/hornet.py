# Copyright (c) 2026 Renaud Guillon
"""The Hornet (`specs/enemies/hornet.md`)."""

import math

from core.entities.enemy import Enemy
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Literal, Protocol

from core.entities.enemy import EnemyContext, EnemyStats


class HornetConfig(Protocol):
    """The entry of the tunables a Hornet is built from (see `hornet_options`)."""

    @property
    def stats(self) -> EnemyStats:
        """The Hornet's stats block."""

    @property
    def entrySpeed(self) -> float | None:
        """The entry speed, when set."""

    @property
    def entryBrake(self) -> float | None:
        """The braking on entry, when set."""

    @property
    def pause(self) -> float:
        """The pause before the dive, in seconds."""

    @property
    def diveAcceleration(self) -> float:
        """The acceleration of the dive."""

    @property
    def diveMaxSpeed(self) -> float:
        """The top speed of the dive."""


HornetState = Literal["enter", "aim", "dive"]
# __pragma__ ("noskip")


# How fast the nose eases in on the player: turn rate per radian left to turn, per second.
TURN_EASE = 14

# A deceleration that never limits the entry.
NO_BRAKE = 1.7976931348623157e308


class HornetOptions:
    """How a `Hornet` moves.

    `stop_y` is the height where it stops before the dive; None means it starts with the pause.
    `stop_x` is where it stops across (None: straight below where it starts, as from the top); set,
    the Hornet flies in a straight line to (`stop_x`, `stop_y`), as from a side of the screen.
    `entry_brake` is the deceleration into the stop, so it slows down instead of halting at once.
    The dive starts from rest and gathers speed at `dive_acceleration` (phase 5 review: no jolt).
    """

    def __init__(
        self,
        stats: EnemyStats,
        stop_y: float | None,
        entry_speed: float,
        entry_brake: float,
        pause: float,
        dive_acceleration: float,
        dive_max_speed: float,
        stop_x: float | None = None,
    ) -> None:
        self.stats = stats
        self.stop_x = stop_x
        self.stop_y = stop_y
        self.entry_speed = entry_speed
        self.entry_brake = entry_brake
        self.pause = pause
        self.dive_acceleration = dive_acceleration
        self.dive_max_speed = dive_max_speed


def hornet_options(
    cfg: HornetConfig, stop_y: float | None, stop_x: float | None = None
) -> HornetOptions:
    """Return the options of a Hornet built from a config entry.

    Its `stats`, `pause`, dive and entry values, with `stop_y` (None: it starts with the pause, as a
    launched Hornet does, ENM-HORNET-08).
    """
    return HornetOptions(
        cfg.stats,
        stop_y,
        cfg.entrySpeed or 0,
        cfg.entryBrake or NO_BRAKE,
        cfg.pause,
        cfg.diveAcceleration,
        cfg.diveMaxSpeed,
        stop_x,
    )


class Hornet(Enemy):
    """A diver.

    It flies down to its stop height, braking into it (ENM-HORNET-04), stops for.

    `pause` seconds while turning its nose to the player (ENM-HORNET-05), then dives in a straight
    line towards where the player was at the end of the pause, accelerating from rest, until it
    leaves the screen (ENM-HORNET-06). It does not shoot (ENM-HORNET-07). Splitter pods
    (ENM-SPLITTER-08) are small Hornets that start with the pause.
    """

    def __init__(self, x: float, y: float, options: HornetOptions) -> None:
        super().__init__(x, y, options.stats)
        self._options = options
        self.state: HornetState = "aim" if options.stop_y is None else "enter"
        # Direction of the dive, fixed at the end of the pause; None before.
        self.dive_heading: float | None = None
        self._pause_left = options.pause
        self._speed = 0.0

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "enter":
            self._enter(ctx, dt)
        elif self.state == "aim":
            self._aim(ctx, dt)
        else:
            self._dive(dt)

    def _enter(self, ctx: EnemyContext, dt: float) -> None:
        options = self._options
        stop_y = self.y if options.stop_y is None else options.stop_y
        stop_x = self.x if options.stop_x is None else options.stop_x
        dx = stop_x - self.x
        dy = stop_y - self.y
        left = math.sqrt(dx * dx + dy * dy)
        # Full speed until the braking distance, then a constant deceleration down to 0 at the stop.
        speed = min(options.entry_speed, math.sqrt(2 * options.entry_brake * left))
        step = speed * dt
        arrived = step >= left
        if not arrived:
            self.x += dx / left * step
            self.y += dy / left * step
        # The nose starts coming round as it slows down.
        if speed < options.entry_speed:
            self._turn_to_player(ctx, dt)
        if arrived:
            self.x = stop_x
            self.y = stop_y
            self.state = "aim"

    def _turn_to_player(self, ctx: EnemyContext, dt: float) -> float:
        """Turn the nose to the player, easing in as it gets there; return its heading."""
        target = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
        left = abs(wrap_angle(target - self.heading))
        # Fast enough to turn all the way round during the pause, slowing down near the end.
        rate = min(math.pi / self._options.pause, TURN_EASE * left)
        self.heading = turn_towards(self.heading, target, rate * dt)
        return target

    def _aim(self, ctx: EnemyContext, dt: float) -> None:
        target = self._turn_to_player(ctx, dt)
        self._pause_left -= dt
        # A Wasp's charge light fills through the pause (ENM-WASP-04).
        self.charge = 1 - max(0, self._pause_left) / self._options.pause
        if self._pause_left > 0:
            return
        self.dive_heading = target
        self.heading = target
        self._speed = 0.0
        self.state = "dive"

    def _dive(self, dt: float) -> None:
        options = self._options
        self._speed = min(options.dive_max_speed, self._speed + options.dive_acceleration * dt)
        self.x += math.sin(self.heading) * self._speed * dt
        self.y += math.cos(self.heading) * self._speed * dt
