"""Unit tests of `src/config/time_of_day.py`."""

import pytest

from config.time_of_day import OVERCAST, SKY_STOPS, TIME_OF_DAY
from core.scenery.atmosphere import Fog, Weather
from core.scenery.sky_look import CLEAR, SkyBase, SkyLook, resolve_sky

BASE = SkyBase(Fog(100, 1000), [0.8, 0.6])


def look(**overrides: object) -> SkyLook:
    """A midday look with clouds of 0.2 and 0.1 cover, as the level data gives it."""
    values: dict[str, object] = {"time_of_day": "midday", "clouds": [0.2, 0.1]}
    values.update(overrides)
    return SkyLook(**values)  # type: ignore[arg-type]


def test_p08_r04_a_clear_sky_keeps_the_time_of_days_light_and_fog() -> None:
    preset = TIME_OF_DAY["midday"]
    atmosphere = resolve_sky(look(), BASE)
    assert atmosphere.sun.elevation_deg == preset.sun.elevation_deg
    assert atmosphere.sun.intensity == pytest.approx(preset.sun.intensity)
    assert atmosphere.sun.shadow_darkness == pytest.approx(OVERCAST.shadow_darkness)
    assert atmosphere.ambient.intensity == pytest.approx(preset.ambient.intensity)
    assert atmosphere.fog.start == pytest.approx(100 * preset.fog)
    assert atmosphere.fog.end == pytest.approx(1000 * preset.fog)
    assert atmosphere.ground_lights == preset.ground_lights
    assert [s.at for s in atmosphere.sky.stops] == SKY_STOPS
    assert atmosphere.aurora == 0
    assert atmosphere.lightning == 0
    assert atmosphere.second_weather is None
    assert atmosphere.weather.kind == CLEAR.kind


def test_p08_r04_a_heavy_cover_dims_the_sun_and_adds_to_the_ambient_light() -> None:
    preset = TIME_OF_DAY["midday"]
    overcast = resolve_sky(look(clouds=[1.0, 1.0]), BASE)
    assert overcast.sun.intensity == pytest.approx(preset.sun.intensity * (1 - OVERCAST.sun_dim))
    assert overcast.sun.shadow_darkness == pytest.approx(OVERCAST.soft_shadows)
    assert overcast.ambient.intensity == pytest.approx(
        preset.ambient.intensity * (1 + OVERCAST.ambient_gain)
    )


def test_p08_r04_a_storm_greys_the_clouds_and_a_plain_sky_does_not() -> None:
    stormy = resolve_sky(look(storm=1), BASE).clouds[0]
    assert stormy.color == pytest.approx(OVERCAST.storm.color)
    assert stormy.shade == pytest.approx(OVERCAST.storm.shade)
    plain = resolve_sky(look(storm=1, plain_clouds=True), BASE).clouds[0]
    assert plain.color == pytest.approx(TIME_OF_DAY["midday"].clouds.color)


def test_second_weather_and_ground_lights_and_brightness_and_tint_follow_the_look() -> None:
    second = Weather("ash", 0.5)
    atmosphere = resolve_sky(
        look(
            second_weather=second,
            ground_lights=0.9,
            brightness=2,
            tint=(0.5, 1, 1),
            aurora=0.3,
            lightning=0.4,
        ),
        BASE,
    )
    assert atmosphere.second_weather is second
    assert atmosphere.ground_lights == 0.9
    assert atmosphere.sun.intensity == pytest.approx(TIME_OF_DAY["midday"].sun.intensity * 2)
    # The tint multiplies the ambient light from the sky; the brightness does not touch its colour.
    assert atmosphere.ambient.sky[0] == pytest.approx(TIME_OF_DAY["midday"].ambient.sky[0] * 0.5)
    assert atmosphere.ambient.sky[1] == pytest.approx(TIME_OF_DAY["midday"].ambient.sky[1])
    assert atmosphere.aurora == 0.3
    assert atmosphere.lightning == 0.4
