"""The Hornet (P05-R02)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import Enemy
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Literal, Protocol  # noqa: E402

from core.entities.enemy import EnemyContext, EnemyStats  # noqa: E402


class HornetConfig(Protocol):
    """The entry of the tunables a Hornet is built from (see `hornet_options`)."""

    @property
    def stats(self) -> EnemyStats: ...

    @property
    def entrySpeed(self) -> float | None: ...  # noqa: N802 (config field, as in TS)

    @property
    def entryBrake(self) -> float | None: ...  # noqa: N802 (config field, as in TS)

    @property
    def pause(self) -> float: ...

    @property
    def diveAcceleration(self) -> float: ...  # noqa: N802 (config field, as in TS)

    @property
    def diveMaxSpeed(self) -> float: ...  # noqa: N802 (config field, as in TS)


HornetState = Literal["enter", "aim", "dive"]
__pragma__("noskip")

# How fast the nose eases in on the player: turn rate per radian left to turn, per second.
TURN_EASE = 14

# A deceleration that never limits the entry.
NO_BRAKE = 1.7976931348623157e308


class HornetOptions:
    """How a `Hornet` moves. `stop_y` is the height where it stops before the dive; None means it
    starts with the pause. `entry_brake` is the deceleration into the stop, so it slows down
    instead of halting at once. The dive starts from rest and gathers speed at
    `dive_acceleration` (phase 5 review: no jolt).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        stats: EnemyStats,
        stop_y: float | None,
        entry_speed: float,
        entry_brake: float,
        pause: float,
        dive_acceleration: float,
        dive_max_speed: float,
    ) -> None:
        self.stats = stats
        self.stop_y = stop_y
        self.entry_speed = entry_speed
        self.entry_brake = entry_brake
        self.pause = pause
        self.dive_acceleration = dive_acceleration
        self.dive_max_speed = dive_max_speed


def hornet_options(cfg: HornetConfig, stop_y: float | None) -> HornetOptions:
    """The options of a Hornet built from a config entry (its `stats`, `pause`, dive and entry
    values), with `stop_y` (None: it starts with the pause).
    """
    return HornetOptions(
        cfg.stats,
        stop_y,
        cfg.entrySpeed or 0,
        cfg.entryBrake or NO_BRAKE,
        cfg.pause,
        cfg.diveAcceleration,
        cfg.diveMaxSpeed,
    )


class Hornet(Enemy):
    """A diver. It flies down to its stop height, braking into it, stops for `pause` seconds while
    turning its nose to the player, then dives in a straight line towards where the player was at
    the end of the pause, accelerating from rest, until it leaves the screen. It does not shoot.
    Splitter pods (P05-R10) are small Hornets that start with the pause.
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
        if self.state == "enter":
            self._enter(ctx, dt)
        elif self.state == "aim":
            self._aim(ctx, dt)
        else:
            self._dive(dt)

    def _enter(self, ctx: EnemyContext, dt: float) -> None:
        options = self._options
        stop_y = self.y if options.stop_y is None else options.stop_y
        # Full speed until the braking distance, then a constant deceleration down to 0 at the stop.
        speed = min(options.entry_speed, math.sqrt(2 * options.entry_brake * (self.y - stop_y)))
        self.y -= speed * dt
        # The nose starts coming round as it slows down.
        if speed < options.entry_speed:
            self._turn_to_player(ctx, dt)
        if self.y <= stop_y:
            self.y = stop_y
            self.state = "aim"

    def _turn_to_player(self, ctx: EnemyContext, dt: float) -> float:
        """Turns the nose to the player, easing in as it gets there; returns its heading."""
        target = heading_to(self.x, self.y, ctx.player_x, ctx.player_y)
        left = abs(wrap_angle(target - self.heading))
        # Fast enough to turn all the way round during the pause, slowing down near the end.
        rate = min(math.pi / self._options.pause, TURN_EASE * left)
        self.heading = turn_towards(self.heading, target, rate * dt)
        return target

    def _aim(self, ctx: EnemyContext, dt: float) -> None:
        target = self._turn_to_player(ctx, dt)
        self._pause_left -= dt
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
