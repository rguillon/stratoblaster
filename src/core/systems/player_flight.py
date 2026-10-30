"""The player ship's movement (P06-R02, GD-10), ported from `core/systems/player-flight.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.muzzle import PlanePoint

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Protocol  # noqa: E402


class FlightBounds(Protocol):
    """Where the player ship may fly, in playfield logical pixels (X right, Y up)."""

    @property
    def min_y(self) -> float: ...

    @property
    def max_y(self) -> float: ...

    @property
    def center_x(self) -> float:
        """X of the middle of the area the ship may fly in."""
        ...

    def half_width_at(self, y: float) -> float:
        """Half the width the ship may use at height `y` (with a tilted camera the screen shows
        less of the playfield at the bottom than at the top).
        """
        ...


__pragma__("noskip")

INFINITY = float("Infinity")


class FlightInput:
    """A direction to fly in, X right, Y up, of length 0..1 (0 = let go, 1 = full speed)."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class PlayerFlight:
    """The player ship's movement: its velocity eases towards the stick or keys at a high
    acceleration, so it reaches its top speed after `acceleration_seconds`, and it stays inside
    its `FlightBounds`. Pure and deterministic.
    """

    def __init__(self, start: PlanePoint, max_speed: float, acceleration_seconds: float) -> None:
        """`acceleration_seconds`: seconds from rest to full speed (and from full speed to rest)."""
        if not (max_speed > 0) or not (acceleration_seconds >= 0):
            raise ValueError("A ship needs a positive speed and a non-negative acceleration time")
        self.x = start.x
        self.y = start.y
        self.vx = 0.0
        self.vy = 0.0
        self.max_speed = max_speed
        self.acceleration_seconds = acceleration_seconds

    def step(self, dt: float, input: FlightInput, bounds: FlightBounds) -> None:
        """Moves for `dt` seconds towards `input`, then keeps the ship inside `bounds`."""
        length = math.hypot(input.x, input.y)
        scale = 1 / length if length > 1 else 1
        tx = input.x * scale * self.max_speed
        ty = input.y * scale * self.max_speed
        change = (
            (self.max_speed / self.acceleration_seconds) * dt
            if self.acceleration_seconds > 0
            else INFINITY
        )
        dx = tx - self.vx
        dy = ty - self.vy
        gap = math.hypot(dx, dy)
        k = change / gap if gap > change else 1
        self.vx += dx * k
        self.vy += dy * k
        self.x += self.vx * dt
        self.y += self.vy * dt
        self._keep_inside(bounds)

    def _keep_inside(self, bounds: FlightBounds) -> None:
        """Puts the ship back inside `bounds`, stopping it against the edge it hit."""
        y = min(bounds.max_y, max(bounds.min_y, self.y))
        if y != self.y:
            self.vy = 0
        self.y = y
        half = max(0, bounds.half_width_at(y))
        x = min(bounds.center_x + half, max(bounds.center_x - half, self.x))
        if x != self.x:
            self.vx = 0
        self.x = x
