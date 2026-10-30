"""Tests of the ship's arrival and departure (reviewer, 2026-10-28),
`core/systems/ship_journey.py`."""

import pytest

from core.entities.muzzle import PlanePoint
from core.systems.ship_journey import JourneyRules, ShipJourney, _ease_out, flight_of


class _Ship:
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0


class _Bounds:
    min_y = 0.0
    max_y = 500.0
    center_x = 50.0

    def half_width_at(self, y: float) -> float:
        return 50.0


RULES = JourneyRules(
    arrive_seconds=2,
    below=10,
    free_seconds=3,
    leave_speed=50,
    leave_acceleration=100,
    above=20,
)
START = PlanePoint(50, 100)
TOP = 200


def _journey() -> ShipJourney:
    return ShipJourney(RULES, START, TOP)


def test_gd01_a_new_journey_is_arriving_and_scripted() -> None:
    journey = _journey()
    assert journey.stage == "arriving"
    assert journey.scripted is True


def test_gd01_the_ship_rises_from_below_the_screen_to_its_start() -> None:
    journey = _journey()
    ship = _Ship()
    journey.step(0, ship, _Bounds(), False)
    assert ship.y == pytest.approx(-10)
    assert ship.x == 50
    journey.step(1, ship, _Bounds(), False)
    assert ship.y == pytest.approx(-10 + 110 * _ease_out(0.5))
    assert journey.stage == "arriving"
    journey.step(1, ship, _Bounds(), False)
    assert ship.y == pytest.approx(100)
    assert journey.stage == "flying"
    assert journey.scripted is False


def test_gd01_with_no_arrival_time_the_ship_is_flying_after_one_step() -> None:
    journey = ShipJourney(JourneyRules(0, 10, 3, 50, 100, 20), START, TOP)
    ship = _Ship()
    journey.step(0.1, ship, _Bounds(), False)
    assert journey.stage == "flying"
    assert ship.y == 100


def test_gd01_the_ease_out_curve_starts_fast_and_ends_at_one() -> None:
    assert _ease_out(0) == 0
    assert _ease_out(1) == 1
    assert _ease_out(0.5) == pytest.approx(0.875)


def test_gd01_skipping_the_arrival_puts_the_ship_at_its_start() -> None:
    journey = _journey()
    ship = _Ship()
    ship.vx = 5
    ship.vy = 6
    journey.skip_arrival(ship)
    assert (ship.x, ship.y, ship.vx, ship.vy) == (50, 100, 0, 0)
    assert journey.stage == "flying"
    journey.skip_arrival(_Ship())
    assert journey.stage == "flying"


def test_gd01_clearing_the_level_keeps_the_ship_free_from_arriving_or_flying() -> None:
    journey = _journey()
    journey.clear()
    assert journey.stage == "free"
    assert journey.scripted is False
    flying = _journey()
    flying.skip_arrival(_Ship())
    flying.clear()
    assert flying.stage == "free"
    # Once free, clearing again changes nothing.
    flying.clear()
    assert flying.stage == "free"


def test_gd01_a_free_ship_waits_for_its_seconds_and_for_ready() -> None:
    journey = _journey()
    journey.skip_arrival(_Ship())
    journey.clear()
    ship = _Ship()
    journey.step(3, ship, _Bounds(), False)
    assert journey.stage == "free"
    journey.step(0, ship, _Bounds(), True)
    assert journey.stage == "leaving"


def test_gd01_the_ship_leaves_by_the_top_of_the_screen() -> None:
    journey = _journey()
    ship = _Ship()
    journey.skip_arrival(ship)
    journey.clear()
    for _ in range(6):
        journey.step(0.5, ship, _Bounds(), True)
    assert journey.stage == "leaving"
    assert journey.scripted is True
    assert ship.y == pytest.approx(150)
    journey.step(0.5, ship, _Bounds(), True)
    assert journey.stage == "gone"
    assert journey.scripted is True


def test_gd01_leaving_starts_at_the_ships_speed_when_it_is_faster() -> None:
    journey = _journey()
    ship = _Ship()
    journey.skip_arrival(ship)
    journey.clear()
    for _ in range(5):
        journey.step(0.5, ship, _Bounds(), True)
    ship.vy = 80
    journey.step(0.5, ship, _Bounds(), True)
    assert journey.stage == "leaving"
    # Starts at 80 (faster than the 50 rule), gains 100 a second for half a second.
    assert ship.vy == pytest.approx(130)


def test_gd01_the_ship_slows_its_sideways_drift_as_it_leaves() -> None:
    journey = _journey()
    journey.skip_arrival(_Ship())
    journey.clear()
    ship = _Ship()
    ship.vx = 10
    journey.step(3, ship, _Bounds(), True)
    assert ship.vx == pytest.approx(10 * max(0, 1 - 4 * 3))
    assert ship.vx == 0


def test_gd01_a_free_ship_does_not_leave_while_not_ready() -> None:
    journey = _journey()
    journey.skip_arrival(_Ship())
    journey.clear()
    journey.step(10, _Ship(), _Bounds(), False)
    assert journey.stage == "free"


def test_gd01_flight_of_without_a_journey_puts_the_ship_at_its_start() -> None:
    options = _Options(journey=None)
    result = flight_of(options)
    assert result.journey is None
    assert (result.ship.x, result.ship.y) == (50, 100)
    assert result.ship.max_speed == 300


def test_gd01_flight_of_with_a_journey_puts_the_ship_below_the_screen() -> None:
    options = _Options(journey=RULES)
    result = flight_of(options)
    assert isinstance(result.journey, ShipJourney)
    assert result.journey.stage == "arriving"
    assert result.ship.y == pytest.approx(-10)
    assert result.ship.x == 50


class _ShipOptions:
    start = PlanePoint(50, 100)
    max_speed = 300
    acceleration_seconds = 0.5


class _Screen:
    height = 200


class _Options:
    ship = _ShipOptions()
    bounds = _Bounds()
    screen = _Screen()

    def __init__(self, journey: JourneyRules | None) -> None:
        self.journey = journey
