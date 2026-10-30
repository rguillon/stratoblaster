"""Unit tests of `src/core/systems/ship_journey.py`."""

from types import SimpleNamespace

import pytest

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip
from core.systems.player_flight import FlightInput
from core.systems.ship_journey import JourneyRules, ShipJourney, _ease_out, flight_of

SCREEN = SimpleNamespace(width=100, height=100)

SHIP = RunShip(PlanePoint(50, 10), 100, 0, 5)

STILL = FlightInput(0, 0)


class _Bounds:
    min_y = 0
    max_y = 100
    center_x = 50

    def half_width_at(self, y: float) -> float:
        return 50


class Still(Enemy):
    """An enemy that does nothing but stand where it is put."""

    def update(self, ctx: object, dt: float) -> None:  # type: ignore[override]
        pass


def _kind(health: float = 10, points: float = 100, y: float = 30) -> EnemyKindDefinition:
    return EnemyKindDefinition(
        "still",
        "Still",
        lambda area: [Still(50, y, EnemyStats("still", 4, health, points))],
    )


GUN = ProjectileWeaponDefinition(
    "gun", "Gun", "muzzle", 1, 50, 0, 50, 0, 0, 1, 5, 0, [[ShotStream(0, 0)], [ShotStream(0, 0)]]
)


def _level(
    waves: list | None = None,
    seconds: float = 10,
    bosses: list | None = None,
) -> GameLevel:
    scenery = SimpleNamespace(scroll_speed=10, sections=[SimpleNamespace(seconds=seconds)])
    return GameLevel("L1", scenery, waves or [], EnemyDifficulty(1, 1), bosses)  # type: ignore[arg-type]


def _run(**overrides: object) -> LevelRun:
    options: dict = dict(
        screen=SCREEN,
        level=_level(),
        kinds=[_kind()],
        weapon=GUN,
        weapon_level=1,
        ship=SHIP,
        bounds=_Bounds(),
        cull_margin=10,
        max_enemy_age=60,
        end_wait=1,
        seed=1,
    )
    options.update(overrides)
    return LevelRun(LevelRunOptions(**options))  # type: ignore[arg-type]


def _step(
    run: LevelRun,
    dt: float = 0.5,
    move: FlightInput = STILL,
    fire: bool = False,
    switch_weapon: bool | None = None,
    bomb: bool | None = None,
) -> None:
    run.step(dt, LevelControls(move, fire, switch_weapon, bomb))


class _Ship:
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0


class _BoundsShipJourney:
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


class _ShipOptions:
    start = PlanePoint(50, 100)
    max_speed = 300
    acceleration_seconds = 0.5


class _Screen:
    height = 200


class _Options:
    ship = _ShipOptions()
    bounds = _BoundsShipJourney()
    screen = _Screen()

    def __init__(self, journey: JourneyRules | None) -> None:
        self.journey = journey


def test_p06_r02_a_run_with_a_journey_leaves_once_the_level_is_cleared() -> None:
    run = _run(journey=JourneyRules(0.5, 5, 1, 50, 50, 10))
    assert run.journey is not None
    assert run.journey.stage == "arriving"
    _step(run)
    assert run.journey.stage == "flying"
    for _ in range(400):
        _step(run, dt=0.5)
        if run.phase == "complete":
            break
    assert run.phase == "complete"
    assert run.journey.stage == "gone"


def test_p06_r02_a_journey_ship_is_flown_by_the_journey_not_the_player() -> None:
    run = _run(journey=JourneyRules(2, 10, 3, 50, 50, 10))
    _step(run, dt=0.5, move=FlightInput(1, 0), fire=True)
    assert run.ship.x == pytest.approx(50)
    assert run.journey.stage == "arriving"
    assert run.enemies.kills == 0
    run.seek(0)
    assert run.journey.stage == "flying"
    assert (run.ship.x, run.ship.y) == (50, 10)


def test_gd01_a_new_journey_is_arriving_and_scripted() -> None:
    journey = _journey()
    assert journey.stage == "arriving"
    assert journey.scripted is True


def test_gd01_the_ship_rises_from_below_the_screen_to_its_start() -> None:
    journey = _journey()
    ship = _Ship()
    journey.step(0, ship, _BoundsShipJourney(), False)
    assert ship.y == pytest.approx(-10)
    assert ship.x == 50
    journey.step(1, ship, _BoundsShipJourney(), False)
    assert ship.y == pytest.approx(-10 + 110 * _ease_out(0.5))
    assert journey.stage == "arriving"
    journey.step(1, ship, _BoundsShipJourney(), False)
    assert ship.y == pytest.approx(100)
    assert journey.stage == "flying"
    assert journey.scripted is False


def test_gd01_with_no_arrival_time_the_ship_is_flying_after_one_step() -> None:
    journey = ShipJourney(JourneyRules(0, 10, 3, 50, 100, 20), START, TOP)
    ship = _Ship()
    journey.step(0.1, ship, _BoundsShipJourney(), False)
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
    journey.step(3, ship, _BoundsShipJourney(), False)
    assert journey.stage == "free"
    journey.step(0, ship, _BoundsShipJourney(), True)
    assert journey.stage == "leaving"


def test_gd01_the_ship_leaves_by_the_top_of_the_screen() -> None:
    journey = _journey()
    ship = _Ship()
    journey.skip_arrival(ship)
    journey.clear()
    for _ in range(6):
        journey.step(0.5, ship, _BoundsShipJourney(), True)
    assert journey.stage == "leaving"
    assert journey.scripted is True
    assert ship.y == pytest.approx(150)
    journey.step(0.5, ship, _BoundsShipJourney(), True)
    assert journey.stage == "gone"
    assert journey.scripted is True


def test_gd01_leaving_starts_at_the_ships_speed_when_it_is_faster() -> None:
    journey = _journey()
    ship = _Ship()
    journey.skip_arrival(ship)
    journey.clear()
    for _ in range(5):
        journey.step(0.5, ship, _BoundsShipJourney(), True)
    ship.vy = 80
    journey.step(0.5, ship, _BoundsShipJourney(), True)
    assert journey.stage == "leaving"
    # Starts at 80 (faster than the 50 rule), gains 100 a second for half a second.
    assert ship.vy == pytest.approx(130)


def test_gd01_the_ship_slows_its_sideways_drift_as_it_leaves() -> None:
    journey = _journey()
    journey.skip_arrival(_Ship())
    journey.clear()
    ship = _Ship()
    ship.vx = 10
    journey.step(3, ship, _BoundsShipJourney(), True)
    assert ship.vx == pytest.approx(10 * max(0, 1 - 4 * 3))
    assert ship.vx == 0


def test_gd01_a_free_ship_does_not_leave_while_not_ready() -> None:
    journey = _journey()
    journey.skip_arrival(_Ship())
    journey.clear()
    journey.step(10, _Ship(), _BoundsShipJourney(), False)
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
