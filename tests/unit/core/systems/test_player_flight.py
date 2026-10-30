"""Unit tests of `src/core/systems/player_flight.py`."""

import math
from types import SimpleNamespace

import pytest

from core.content.game_level import GameLevel
from core.entities.enemy import Enemy, EnemyKindDefinition, EnemyStats
from core.entities.muzzle import PlanePoint
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip
from core.systems.player_flight import FlightInput, PlayerFlight

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


class _BoundsPlayerFlight:
    def __init__(
        self,
        min_y: float = -1000,
        max_y: float = 1000,
        center_x: float = 0,
        half: float = 1000,
    ) -> None:
        self.min_y = min_y
        self.max_y = max_y
        self.center_x = center_x
        self.half = half

    def half_width_at(self, y: float) -> float:
        return self.half


WIDE = _BoundsPlayerFlight()


def _ship(acceleration_seconds: float = 1.0, max_speed: float = 100) -> PlayerFlight:
    return PlayerFlight(PlanePoint(0, 0), max_speed, acceleration_seconds)


def test_p06_r02_the_ship_flies_with_the_controls() -> None:
    run = _run()
    _step(run, dt=0.1, move=FlightInput(1, 0))
    assert run.ship.x == pytest.approx(60)
    assert run.ship.y == pytest.approx(10)


def test_p06_r02_a_ship_needs_a_positive_speed_and_a_non_negative_acceleration() -> None:
    with pytest.raises(ValueError):
        PlayerFlight(PlanePoint(0, 0), 0, 1)
    with pytest.raises(ValueError):
        PlayerFlight(PlanePoint(0, 0), -5, 1)
    with pytest.raises(ValueError):
        PlayerFlight(PlanePoint(0, 0), 100, -1)
    with pytest.raises(ValueError):
        PlayerFlight(PlanePoint(0, 0), float("nan"), 1)
    assert PlayerFlight(PlanePoint(0, 0), 100, 0).acceleration_seconds == 0


def test_p06_r02_the_velocity_eases_towards_the_input() -> None:
    ship = _ship(acceleration_seconds=1.0)
    ship.step(0.1, FlightInput(1, 0), WIDE)
    assert ship.vx == pytest.approx(10)
    assert ship.x == pytest.approx(1)


def test_p06_r02_the_ship_reaches_full_speed_after_the_acceleration_time() -> None:
    ship = _ship(acceleration_seconds=1.0)
    for _ in range(100):
        ship.step(0.01, FlightInput(1, 0), WIDE)
    assert ship.vx == pytest.approx(100)


def test_p06_r02_with_no_acceleration_time_the_speed_is_reached_at_once() -> None:
    ship = _ship(acceleration_seconds=0)
    ship.step(0.1, FlightInput(0, 1), WIDE)
    assert ship.vy == pytest.approx(100)
    assert ship.y == pytest.approx(10)


def test_p06_r02_an_input_longer_than_one_is_normalised() -> None:
    ship = _ship(acceleration_seconds=0)
    ship.step(0.1, FlightInput(3, 4), WIDE)
    assert ship.vx == pytest.approx(60)
    assert ship.vy == pytest.approx(80)


def test_p06_r02_an_input_inside_the_unit_circle_keeps_its_length() -> None:
    ship = _ship(acceleration_seconds=0)
    ship.step(0.1, FlightInput(0.5, 0), WIDE)
    assert ship.vx == pytest.approx(50)
    assert ship.vy == 0


def test_p06_r02_letting_go_slows_the_ship_down() -> None:
    ship = _ship(acceleration_seconds=0)
    ship.step(0.1, FlightInput(1, 0), WIDE)
    ship = _ship(acceleration_seconds=1.0)
    ship.vx = 100
    ship.step(0.1, FlightInput(0, 0), WIDE)
    assert ship.vx == pytest.approx(90)


def test_p06_r02_the_ship_stops_at_the_top_and_bottom_of_its_bounds() -> None:
    ship = PlayerFlight(PlanePoint(0, 99), 100, 0)
    ship.step(1, FlightInput(0, 1), _BoundsPlayerFlight(max_y=100))
    assert ship.y == 100
    assert ship.vy == 0
    ship = PlayerFlight(PlanePoint(0, 1), 100, 0)
    ship.step(1, FlightInput(0, -1), _BoundsPlayerFlight(min_y=0))
    assert ship.y == 0
    assert ship.vy == 0


def test_p06_r02_the_ship_stops_at_the_sides_of_its_bounds() -> None:
    bounds = _BoundsPlayerFlight(center_x=50, half=50)
    ship = PlayerFlight(PlanePoint(90, 0), 100, 0)
    ship.step(1, FlightInput(1, 0), bounds)
    assert ship.x == 100
    assert ship.vx == 0
    ship = PlayerFlight(PlanePoint(10, 0), 100, 0)
    ship.step(1, FlightInput(-1, 0), bounds)
    assert ship.x == 0
    assert ship.vx == 0


def test_p06_r02_a_negative_width_pins_the_ship_to_the_centre() -> None:
    bounds = _BoundsPlayerFlight(center_x=50, half=-10)
    ship = PlayerFlight(PlanePoint(20, 0), 100, 0)
    ship.step(0.01, FlightInput(0, 0), bounds)
    assert ship.x == 50


def test_p06_r02_a_ship_inside_its_bounds_keeps_its_velocity() -> None:
    ship = PlayerFlight(PlanePoint(0, 0), 100, 0)
    ship.step(1, FlightInput(0, 1), _BoundsPlayerFlight(min_y=-10, max_y=500))
    assert ship.vy == 100
    assert ship.y == pytest.approx(100)
    assert math.isfinite(ship.x)
