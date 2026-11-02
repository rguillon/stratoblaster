# Copyright (c) 2026 Renaud Guillon
"""How the ship comes into a level and leaves it (GAME-LEVEL-11, GAME-LEVEL-12).

It rises from below the screen to its start, the player flies it freely for a while once the level
is cleared, then it flies off the top of the screen. Logical pixels and seconds.
"""

from core.entities.muzzle import PlanePoint
from core.systems.player_flight import PlayerFlight

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Literal, Protocol

from core.systems.player_flight import FlightBounds

JourneyStage = Literal["arriving", "flying", "free", "leaving", "gone"]


class Moved(Protocol):
    """A ship's position and velocity, as the journey moves it."""

    x: float
    y: float
    vx: float
    vy: float


class ShipOptions(Protocol):
    """Where a run's ship starts and how it flies (`RunShip`)."""

    @property
    def start(self) -> PlanePoint:
        """Where the ship starts its journey."""
        ...

    @property
    def max_speed(self) -> float:
        """Top speed of the ship."""
        ...

    @property
    def acceleration_seconds(self) -> float:
        """Seconds the ship takes to reach its top speed."""
        ...


class ScreenSize(Protocol):
    """How tall the screen is, in logical pixels."""

    @property
    def height(self) -> float:
        """Height of the screen, in logical pixels."""
        ...


class FlightOptions(Protocol):
    """What `flight_of` needs of a run's options (a `LevelRunOptions`)."""

    @property
    def ship(self) -> ShipOptions:
        """The ship's options."""
        ...

    @property
    def bounds(self) -> FlightBounds:
        """Where the ship may fly."""
        ...

    @property
    def screen(self) -> ScreenSize:
        """The screen's size."""
        ...

    @property
    def journey(self) -> "JourneyRules | None":
        """The journey rules, when the run has a journey."""
        ...


# __pragma__ ("noskip")


class JourneyRules:
    """The ship's journey.

    `arrive_seconds` to rise from below the screen to the start, `below` how far below the bottom of
    the screen the ship starts, `free_seconds` the seconds the player keeps the ship once the level
    is cleared, and the fly-off: its starting speed `leave_speed`, its acceleration
    `leave_acceleration`, and how far past the top it goes (`above`).
    """

    def __init__(
        self,
        arrive_seconds: float,
        below: float,
        free_seconds: float,
        leave_speed: float,
        leave_acceleration: float,
        above: float,
    ) -> None:
        self.arrive_seconds = arrive_seconds
        self.below = below
        self.free_seconds = free_seconds
        self.leave_speed = leave_speed
        self.leave_acceleration = leave_acceleration
        self.above = above


def _ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


class ShipJourney:
    """The arrival and the departure of the ship (see `JourneyRules`).

    Pure. The player only flies the ship in the `flying` stage.
    """

    def __init__(self, rules: JourneyRules, start: PlanePoint, top: float) -> None:
        """`top`: height of the top of the screen."""
        self.rules = rules
        self.start = start
        self._top = top
        self._stage: JourneyStage = "arriving"
        self._time = 0.0
        self._speed = 0.0

    @property
    def stage(self) -> JourneyStage:
        """The journey's stage: 'arriving', 'flying', 'free', 'leaving' or 'gone'."""
        return self._stage

    @property
    def scripted(self) -> bool:
        """Whether the journey moves the ship, not the player (it cannot shoot or be hit then)."""
        return self._stage in ("arriving", "leaving", "gone")

    def skip_arrival(self, ship: Moved) -> None:
        """Put the ship at its start, as if it had arrived (a seek, a debug start)."""
        if self._stage != "arriving":
            return
        ship.x = self.start.x
        ship.y = self.start.y
        ship.vx = 0
        ship.vy = 0
        self._stage = "flying"

    def clear(self) -> None:
        """Mark the level cleared: the player keeps the ship for `free_seconds`."""
        if self._stage not in ("flying", "arriving"):
            return
        self._stage = "free"
        self._time = 0.0

    def step(self, dt: float, ship: Moved, bounds: FlightBounds, ready: bool) -> None:
        """Advances by `dt`, moving `ship` while it arrives or leaves. `ready`: it may leave now."""
        self._time += dt
        if self._stage == "arriving":
            self._arrive(ship, bounds)
        elif self._stage == "free" and ready and self._time >= self.rules.free_seconds:
            self._stage = "leaving"
            self._speed = max(self.rules.leave_speed, ship.vy)
        if self._stage == "leaving":
            self._leave(dt, ship)

    def _arrive(self, ship: Moved, bounds: FlightBounds) -> None:
        frm = bounds.min_y - self.rules.below
        t = min(1, self._time / max(1e-6, self.rules.arrive_seconds))
        y = frm + (self.start.y - frm) * _ease_out(t)
        ship.x = self.start.x
        ship.vx = 0
        ship.vy = 0
        ship.y = y
        if t >= 1:
            self._stage = "flying"

    def _leave(self, dt: float, ship: Moved) -> None:
        self._speed += self.rules.leave_acceleration * dt
        ship.vx *= max(0, 1 - 4 * dt)
        ship.x += ship.vx * dt
        ship.vy = self._speed
        ship.y += self._speed * dt
        if ship.y >= self._top + self.rules.above:
            self._stage = "gone"


class FlightOfResult:
    """The player's ship, and its journey if there is one."""

    def __init__(self, ship: PlayerFlight, journey: ShipJourney | None) -> None:
        self.ship = ship
        self.journey = journey


def flight_of(options: FlightOptions) -> FlightOfResult:
    """Return the player's ship, and its journey if `options.journey` is given.

    The ship then below the screen.
    """
    start = options.ship.start
    flight = PlayerFlight(start, options.ship.max_speed, options.ship.acceleration_seconds)
    if options.journey is None:
        return FlightOfResult(flight, None)
    journey = ShipJourney(options.journey, start, options.screen.height)
    journey.step(0, flight, options.bounds, False)
    return FlightOfResult(flight, journey)
