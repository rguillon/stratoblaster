"""Unit tests of `src/game/sim/sky_build.py`."""

from game.config.record import record
from game.sim.sky_build import sky_look, sky_script


def _look(**fields: object) -> object:
    base = {
        "timeOfDay": 0.5,
        "clouds": 0.3,
        "storm": None,
        "weather": None,
        "aurora": None,
        "lightning": None,
        "mist": None,
        "tint": None,
        "secondWeather": None,
        "cloudTint": None,
        "underglow": None,
        "groundLights": None,
        "brightness": None,
        "plainClouds": None,
    }
    base.update(fields)
    return record(base)


def test_p08_r04_a_sky_look_takes_the_time_of_day_and_cloud_cover() -> None:
    look = sky_look(_look())
    assert look.time_of_day == 0.5
    assert look.clouds == 0.3


def test_p08_r04_a_sky_look_maps_an_omitted_optional_field_to_none() -> None:
    look = sky_look(_look())
    assert look.weather is None
    assert look.mist is None
    assert look.underglow is None


def test_p08_r04_a_sky_look_maps_a_weather_and_a_mist_when_given() -> None:
    look = sky_look(
        _look(
            weather={"kind": "rain", "strength": 0.7},
            mist={"fog": 0.2, "white": 0.4},
        )
    )
    assert look.weather.kind == "rain"
    assert look.weather.strength == 0.7
    assert look.mist.fog == 0.2
    assert look.mist.white == 0.4


def test_p08_r04_a_sky_script_is_the_start_look_and_its_changes_in_order() -> None:
    config = record(
        {
            "start": _look(),
            "changes": [
                {"from": 0.0, "to": 0.5, "look": _look(timeOfDay=0.1)},
                {"from": 0.5, "to": 1.0, "look": _look(timeOfDay=0.9)},
            ],
        }
    )
    script = sky_script(config)
    assert script.start.time_of_day == 0.5
    assert len(script.changes) == 2
    assert script.changes[0].look.time_of_day == 0.1
    assert script.changes[1].look.time_of_day == 0.9


def test_p08_r04_a_sky_script_without_changes_has_none() -> None:
    script = sky_script(record({"start": _look()}))
    assert script.changes is None
