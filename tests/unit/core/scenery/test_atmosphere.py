"""Unit tests of `src/core/scenery/atmosphere.py`."""

import pytest
from helpers.sample_level import sample_atmosphere

from core.scenery.atmosphere import (
    NO_WEATHER,
    Ambient,
    Atmosphere,
    AtmosphereChange,
    AtmosphereTrack,
    CloudCover,
    Fog,
    Sky,
    SkyStop,
    Sun,
    Weather,
    _blend_weather,
    _lerp_angle,
    _smooth,
    blend_atmosphere,
    is_time_of_day,
    sorted_by_from,
)
from core.scenery.sky_look import SkyLook, without_weather


def cloud(coverage: float, opacity: float = 0.5) -> CloudCover:
    return CloudCover(coverage, opacity, (1, 1, 1), (0.5, 0.5, 0.5))


def with_clouds(clouds: list[CloudCover]) -> Atmosphere:
    base = sample_atmosphere()
    return Atmosphere(
        base.sun,
        base.sky,
        base.ambient,
        base.fog,
        clouds,
        base.ground_lights,
        base.weather,
        base.aurora,
        base.lightning,
    )


def look(**overrides: object) -> SkyLook:
    """A midday look with clouds of 0.2 and 0.1 cover, as the level data gives it."""
    values: dict[str, object] = {"time_of_day": "midday", "clouds": [0.2, 0.1]}
    values.update(overrides)
    return SkyLook(**values)  # type: ignore[arg-type]


def test_p08_r04_the_six_times_of_day_are_names() -> None:
    assert is_time_of_day("dawn")
    assert is_time_of_day("night")
    assert not is_time_of_day("noon")


def test_p08_r04_blending_at_the_ends_gives_the_looks_themselves() -> None:
    a = sample_atmosphere()
    b = sample_atmosphere(lightning=1.0)
    assert blend_atmosphere(a, b, 0) is a
    assert blend_atmosphere(a, b, -1) is a
    assert blend_atmosphere(a, b, 1) is b
    assert blend_atmosphere(a, b, 2) is b


def test_p08_r04_halfway_blends_every_number_halfway() -> None:
    a = sample_atmosphere()
    b = sample_atmosphere(lightning=1.0, haze=(1.0, 0.5, 0.0))
    b.fog = Fog(300, 2000)
    b.sun = Sun(90, 10, (0, 0, 0), 3, 1)
    half = blend_atmosphere(a, b, 0.5)
    assert half.fog.start == pytest.approx(200)
    assert half.fog.end == pytest.approx(1500)
    assert half.sun.elevation_deg == pytest.approx(67.5)
    assert half.sun.intensity == pytest.approx(2)
    assert half.sun.shadow_darkness == pytest.approx(0.75)
    assert half.sky.haze == pytest.approx((0.75, 0.5, 0.3))
    assert half.lightning == pytest.approx(0.5)


def test_p08_r04_the_sun_turns_the_short_way_round() -> None:
    a = sample_atmosphere()
    b = sample_atmosphere()
    a.sun = Sun(0, 350, (1, 1, 1), 1, 1)
    b.sun = Sun(0, 10, (1, 1, 1), 1, 1)
    assert blend_atmosphere(a, b, 0.5).sun.azimuth_deg == pytest.approx(360)
    assert _lerp_angle(10, 350, 0.5) == pytest.approx(0)


def test_p08_r04_stops_and_clouds_of_unequal_lists_keep_the_extra_ones() -> None:
    a = sample_atmosphere()
    b = sample_atmosphere()
    a.sky = Sky(a.sky.haze, [SkyStop(-1, (0, 0, 0)), SkyStop(0, (1, 1, 1))], 1)
    b.sky = Sky(b.sky.haze, [SkyStop(-1, (1, 1, 1))], 1)
    stops = blend_atmosphere(a, b, 0.5).sky.stops
    assert stops[0].color == pytest.approx((0.5, 0.5, 0.5))
    assert stops[1].color == pytest.approx((1, 1, 1))
    two = with_clouds([cloud(0.2), cloud(0.8)])
    one = with_clouds([cloud(0.6, 0.0)])
    blended = blend_atmosphere(two, one, 0.5).clouds
    assert len(blended) == 2
    assert blended[0].coverage == pytest.approx(0.4)
    assert blended[1].coverage == pytest.approx(0.8)
    assert len(blend_atmosphere(one, two, 0.5).clouds) == 1


def test_p08_r05_weather_changes_kind_halfway() -> None:
    snow = Weather("snow", 1)
    rain = Weather("rain", 0.5)
    assert _blend_weather(snow, rain, 0.25).kind == "snow"
    assert _blend_weather(snow, rain, 0.75).kind == "rain"
    assert _blend_weather(snow, rain, 0.5).strength == pytest.approx(0.75)


def test_p08_r05_weather_with_no_strength_takes_the_other_kind() -> None:
    rain = Weather("rain", 0.5)
    assert _blend_weather(NO_WEATHER, rain, 0.2).kind == "rain"
    assert _blend_weather(rain, NO_WEATHER, 0.8).kind == "rain"
    assert _blend_weather(Weather("ash", 1), NO_WEATHER, 0.9).kind == "ash"


def test_second_weather_blends_only_when_either_look_has_one() -> None:
    plain = sample_atmosphere()
    assert blend_atmosphere(plain, plain, 0.5).second_weather is None
    with_second = sample_atmosphere()
    with_second.second_weather = Weather("ash", 1)
    blended = blend_atmosphere(plain, with_second, 0.5).second_weather
    assert blended is not None
    assert blended.kind == "ash"
    assert blended.strength == pytest.approx(0.5)
    both = blend_atmosphere(with_second, with_second, 0.5).second_weather
    assert both is not None
    assert both.kind == "ash"


def test_p08_r04_the_track_blends_along_the_level() -> None:
    a = sample_atmosphere()
    b = sample_atmosphere(lightning=1.0)
    track = AtmosphereTrack(
        a,
        [AtmosphereChange(100, 200, b)],
        lambda look: look,
    )
    assert track.at(0) is a
    assert track.at(100) is a
    assert track.at(300).lightning == pytest.approx(1)
    middle = track.at(150).lightning
    assert middle == pytest.approx(_smooth(0.5))
    assert 0 < middle < 1


def test_p08_r04_an_instant_change_jumps_to_its_look() -> None:
    a = sample_atmosphere()
    b = sample_atmosphere(lightning=1.0)
    track = AtmosphereTrack(a, [AtmosphereChange(50, 50, b)], lambda look: look)
    assert track.at(49).lightning == 0
    # The change starts just past its distance: at it, the look is still the start's.
    assert track.at(50).lightning == 0
    assert track.at(50.5).lightning == pytest.approx(1)


def test_p08_r04_the_track_takes_the_changes_in_order_of_their_start() -> None:
    a = sample_atmosphere()
    b = sample_atmosphere(lightning=1.0)
    late = AtmosphereChange(200, 220, a)
    early = AtmosphereChange(100, 120, b)
    track = AtmosphereTrack(a, [late, early], lambda look: look)
    assert track.at(130).lightning == pytest.approx(1)


def test_p08_r04_a_change_that_ends_before_it_starts_is_refused() -> None:
    with pytest.raises(ValueError):
        AtmosphereTrack(
            sample_atmosphere(),
            [AtmosphereChange(200, 100, sample_atmosphere())],
            lambda look: look,
        )


def test_the_changes_are_sorted_stably_by_their_start() -> None:
    first = AtmosphereChange(10, 20, "a")
    second = AtmosphereChange(10, 30, "b")
    early = AtmosphereChange(5, 6, "c")
    assert [c.look for c in sorted_by_from([first, second, early])] == ["c", "a", "b"]
    assert sorted_by_from([]) == []


def test_smooth_is_an_eased_ramp_halfway_at_one_half() -> None:
    assert _smooth(0) == 0
    assert _smooth(1) == 1
    assert _smooth(0.5) == pytest.approx(0.5)
    assert _smooth(0.25) < 0.25


def test_the_atmosphere_objects_hold_their_fields() -> None:
    weather = Weather("rain", 0.3)
    assert weather.kind == "rain"
    assert CloudCover(0.1, 0.2, (1, 1, 1), (0, 0, 0)).opacity == 0.2
    ambient = Ambient((1, 1, 1), (0, 0, 0), 2)
    assert ambient.intensity == 2


def test_without_weather_clears_the_weather_lightning_and_second_weather() -> None:
    stormy = look(weather=Weather("rain", 1), lightning=1, second_weather=Weather("ash", 1))
    calm = without_weather(stormy)
    assert calm.weather is not None
    assert calm.weather.strength == 0
    assert calm.lightning == 0
    assert calm.second_weather is not None
    assert calm.second_weather.strength == 0
    assert stormy.weather is not None and stormy.weather.kind == "rain"
    no_second = without_weather(look(weather=Weather("rain", 1)))
    assert no_second.second_weather is None
