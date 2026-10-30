"""Unit tests of `src/render/scenery/sky_layers.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeScene
from helpers.render_looks import make_look
from helpers.sample_level import sample_atmosphere

from core.scenery.atmosphere import CloudCover, Weather
from render.scenery import sky_layers
from render.scenery.sky_layers import AURORA_ABOVE_CLOUDS, SkyLayers, SkyPlacement, _max_of, _min_of
from render.scenery.weather_layer import WeatherView


class _Track:
    """An atmosphere track that gives the same atmosphere at every distance."""

    def __init__(self, atmosphere: Any) -> None:
        self.atmosphere = atmosphere
        self.distances: list[float] = []

    def at(self, distance: float) -> Any:
        self.distances.append(distance)
        return self.atmosphere


class _Layer:
    """A stand-in for a layer class: it records its constructor arguments and its updates."""

    def __init__(self, *args: Any) -> None:
        self.args = args
        self.updates: list[tuple[Any, ...]] = []
        self.drawn = 3
        self.flash = 0.0

    def update(self, *args: Any) -> float:
        self.updates.append(args)
        return self.flash


class _Material:
    def __init__(self, label: str) -> None:
        self.material = label


class _Kit:
    """The parts of a scenery kit the sky asks for."""

    weather = "weather-factory"

    def cloud(self, look: Any) -> _Material:
        return _Material("cloud-" + str(look.altitude))

    def aurora(self) -> _Material:
        return _Material("aurora")


# The track the patched `atmosphere_track` hands out next (set by `_sky`).
_NEXT_TRACK: list[_Track] = []
# What the patched `apply_atmosphere` and `update_cloud_layer` were called with.
_APPLIED: list[Any] = []
_CLOUD_UPDATES: list[tuple[Any, Any, Any]] = []


@pytest.fixture(autouse=True)
def _fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    _APPLIED.clear()
    _CLOUD_UPDATES.clear()
    monkeypatch.setattr(
        sky_layers, "atmosphere_track", lambda look, speed, options: _NEXT_TRACK[-1]
    )
    monkeypatch.setattr(
        sky_layers,
        "light_scenery",
        lambda scene, atmosphere: SimpleNamespace(sun="sun-light", ambient="ambient-light"),
    )
    monkeypatch.setattr(
        sky_layers, "apply_atmosphere", lambda scene, lights, atmo: _APPLIED.append(atmo)
    )
    monkeypatch.setattr(sky_layers, "build_cloud_layer", _build_cloud)
    monkeypatch.setattr(
        sky_layers,
        "update_cloud_layer",
        lambda layer, camera_time, frame: _CLOUD_UPDATES.append((layer, camera_time, frame)),
    )
    monkeypatch.setattr(sky_layers, "WeatherLayer", _Layer)
    monkeypatch.setattr(sky_layers, "AuroraLayer", _Layer)
    monkeypatch.setattr(sky_layers, "LightningLayer", _Layer)
    monkeypatch.setattr(
        sky_layers,
        "babylon_class",
        lambda name: SimpleNamespace(Right=lambda: "right", Up=lambda: "up"),
    )


def _build_cloud(
    scene: Any, look: Any, material: Any, index: int, placement: tuple[Any, ...]
) -> Any:
    return SimpleNamespace(
        state=("state", index), look=look, material=material, placement=placement
    )


def _cloud(altitude: float) -> Any:
    return SimpleNamespace(altitude=altitude, coverage=0.5, opacity=0.5)


def _sky(
    clouds: list[Any] | None = None, look: Any = None, options: Any = None
) -> tuple[SkyLayers, _Track]:
    """A sky over a track that gives one atmosphere (a fresh sample) at every distance."""
    track = _Track(sample_atmosphere())
    _NEXT_TRACK.append(track)
    if look is None:
        look = make_look(clouds=clouds or [])
    return SkyLayers(FakeScene(), look, (1.5, options, 7)), track


def _camera(z: float = 40) -> SimpleNamespace:
    return SimpleNamespace(
        position=SimpleNamespace(z=z), getDirection=lambda direction: ("dir", direction)
    )


def _window(altitude: float) -> str:
    return f"window@{altitude}"


def _placement(flight: float = 200, margin: float = 3) -> SkyPlacement:
    return SkyPlacement(_window, lambda look: look.altitude, flight, margin)


def test_the_largest_and_the_smallest_of_a_list_start_from_the_given_value() -> None:
    assert _max_of([1, 5, 3], 0) == 5
    assert _max_of([], 4) == 4
    assert _min_of([7, 2, 9], 10) == 2
    assert _min_of([], 10) == 10


def test_a_sky_starts_with_the_atmosphere_of_its_track_at_distance_zero() -> None:
    sky, track = _sky()
    assert sky.atmosphere is track.atmosphere
    assert sky.flash == 0
    assert sky.weather_particles == 0
    assert sky.clouds == []


def test_the_sun_of_a_sky_is_the_sun_of_its_lights() -> None:
    sky, _ = _sky()
    assert sky.sun == "sun-light"


def test_attaching_builds_one_cloud_layer_per_cloud_at_its_altitude_and_window() -> None:
    sky, _ = _sky(clouds=[_cloud(100), _cloud(160)])
    sky.attach(_Kit(), _placement(flight=200, margin=3))
    assert [layer.placement for layer in sky._clouds] == [
        (_window(100), 100, 3),
        (_window(160), 160, 3),
    ]
    assert [layer.material.material for layer in sky._clouds] == ["cloud-100", "cloud-160"]
    assert [layer.state for layer in sky._clouds] == [("state", 0), ("state", 1)]


def test_the_clouds_state_is_the_state_of_each_cloud_layer() -> None:
    sky, _ = _sky(clouds=[_cloud(100)])
    sky.attach(_Kit(), _placement())
    assert sky.clouds == [("state", 0)]


def test_the_aurora_flies_eight_above_the_highest_cloud_when_that_is_below_the_ships() -> None:
    sky, _ = _sky(clouds=[_cloud(100), _cloud(160)])
    sky.attach(_Kit(), _placement(flight=200))
    assert sky._aurora.args[2][1] == 160 + AURORA_ABOVE_CLOUDS


def test_the_aurora_stays_four_below_the_flight_altitude_when_the_clouds_are_high() -> None:
    sky, _ = _sky(clouds=[_cloud(190)])
    sky.attach(_Kit(), _placement(flight=200))
    assert sky._aurora.args[2][1] == 196


def test_the_lightning_flashes_inside_the_lowest_cloud_layer() -> None:
    sky, _ = _sky(clouds=[_cloud(160), _cloud(100)])
    sky.attach(_Kit(), _placement(flight=200))
    _scene, seed, placement = sky._lightning.args
    assert seed == 7
    assert placement == (_window(100), 100)


def test_a_sky_without_clouds_has_its_aurora_and_lightning_at_the_ground() -> None:
    sky, _ = _sky(clouds=[])
    sky.attach(_Kit(), _placement(flight=200))
    assert sky._aurora.args[2][1] == AURORA_ABOVE_CLOUDS
    assert sky._lightning.args[2][1] == 0


def test_a_look_with_a_sky_script_or_a_time_of_day_makes_its_clouds_follow_it() -> None:
    plain, _ = _sky(clouds=[_cloud(100)])
    assert plain._follow is False
    scripted_look = make_look(clouds=[], atmosphere="script")
    scripted, _ = _sky(look=scripted_look)
    assert scripted._follow is True
    timed, _ = _sky(options=SimpleNamespace(time_of_day="dusk"))
    assert timed._follow is True


def test_updating_follows_the_camera_and_the_time_with_each_cloud_layer() -> None:
    sky, track = _sky(clouds=[_cloud(100)])
    sky.attach(_Kit(), _placement())
    track.atmosphere.clouds = [CloudCover(0.5, 0.5, (1, 1, 1), (0, 0, 0))]
    sky.update(10, (2.5, _camera(z=40), 0))
    layer, camera_time, frame = _CLOUD_UPDATES[0]
    assert layer is sky._clouds[0]
    assert camera_time == (40, 2.5)
    atmosphere, cover, follow = frame
    assert cover is track.atmosphere.clouds[0]
    assert follow is False


def test_the_track_is_asked_for_the_atmosphere_at_the_distance_along_the_level() -> None:
    sky, track = _sky()
    sky.update(123.0, (0, _camera(), 0))
    assert track.distances[-1] == 123.0


def test_without_lightning_a_frame_is_lit_as_its_atmosphere_says() -> None:
    sky, track = _sky()
    lit = sky.update(0, (0, _camera(), 0))
    assert [track.atmosphere] == _APPLIED
    assert lit is track.atmosphere
    assert sky.flash == 0


def test_a_flash_of_a_storm_brightens_the_atmosphere_and_is_reported_on_the_sky() -> None:
    storm = sample_atmosphere(lightning=1.0)
    sky, track = _sky()
    track.atmosphere = storm
    sky.attach(_Kit(), _placement())
    sky._lightning.flash = 1.0
    lit = sky.update(0, (0, _camera(), 0))
    assert lit.ambient.intensity > storm.ambient.intensity
    assert sky.flash == pytest.approx(1.0)
    assert [lit] == _APPLIED


def test_a_flash_does_not_light_a_sky_without_lightning() -> None:
    sky, track = _sky()
    sky.attach(_Kit(), _placement())
    sky._lightning.flash = 1.0
    lit = sky.update(0, (0, _camera(), 0))
    assert sky.flash == 0
    assert lit is track.atmosphere


def test_the_weather_is_shown_in_the_box_of_air_from_the_given_start() -> None:
    sky, track = _sky()
    sky.attach(_Kit(), _placement())
    track.atmosphere.weather = Weather("snow", 1)
    sky.update(0, (7.0, _camera(z=12), -50))
    _atmosphere, view = sky._weather.updates[-1]
    assert isinstance(view, WeatherView)
    assert (view.time, view.start) == (7.0, -50)
    assert view.right == ("dir", "right")
    assert view.up == ("dir", "up")


def test_the_weather_particles_drawn_are_those_of_the_weather_layer() -> None:
    sky, _ = _sky()
    sky.attach(_Kit(), _placement())
    assert sky.weather_particles == 3


def test_the_aurora_is_updated_with_the_atmosphere_time_and_camera() -> None:
    sky, _ = _sky()
    sky.attach(_Kit(), _placement())
    camera = _camera(z=9)
    sky.update(0, (4.0, camera, 0))
    _atmosphere, time, position = sky._aurora.updates[-1]
    assert time == 4.0
    assert position is camera.position


def test_a_sky_without_clouds_weather_or_aurora_still_updates_a_frame() -> None:
    sky, track = _sky()
    lit = sky.update(5, (0, _camera(), 0))
    assert lit is track.atmosphere
    assert sky.weather_particles == 0
