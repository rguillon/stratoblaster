"""Unit tests of `src/render/scenery/atmosphere_of.py`."""

import pytest
from helpers.render_looks import GREY, cloud, make_look

from core.scenery.atmosphere import AtmosphereChange, Fog, Weather
from core.scenery.sky_look import CLEAR, SkyBase, SkyLook, SkyScript, resolve_sky
from render.scenery.atmosphere_of import (
    AtmosphereOptions,
    atmosphere_track,
    look_atmosphere,
    toned,
)


def _resolved(sky: SkyLook, opacities: list[float], fog_start: float, fog_end: float) -> object:
    return resolve_sky(sky, SkyBase(Fog(fog_start, fog_end), opacities))


def test_a_fixed_look_gives_its_own_sun_sky_fog_and_clouds() -> None:
    look = make_look(clouds=[cloud(coverage=0.4, opacity=0.6)])
    atmosphere = look_atmosphere(look)

    assert atmosphere.sun.elevation_deg == 45
    assert atmosphere.sun.shadow_darkness == 0.5
    assert atmosphere.sky.haze == GREY
    assert (atmosphere.fog.start, atmosphere.fog.end) == (100, 400)
    assert len(atmosphere.clouds) == 1
    assert atmosphere.clouds[0].coverage == 0.4
    assert atmosphere.ground_lights == 1
    assert atmosphere.weather is CLEAR
    assert (atmosphere.aurora, atmosphere.lightning) == (0, 0)


def test_a_look_without_a_script_is_a_track_that_stays_put() -> None:
    look = make_look(clouds=[cloud()])
    track = atmosphere_track(look, scroll_speed=10)
    for distance in (0, 50, 5000):
        assert track.at(distance).sun.elevation_deg == 45
        assert track.at(distance).fog.end == 400


def test_a_tone_below_one_dims_the_haze_and_the_clouds() -> None:
    look = make_look(clouds=[cloud()], tone=0.5)
    atmosphere = atmosphere_track(look, scroll_speed=1).at(0)
    assert atmosphere.sky.haze == pytest.approx((0.25, 0.25, 0.25))
    assert atmosphere.clouds[0].color == pytest.approx((0.5, 0.5, 0.5))
    assert atmosphere.clouds[0].shade == pytest.approx((0.25, 0.25, 0.25))


def test_toned_at_full_brightness_is_the_same_atmosphere() -> None:
    atmosphere = look_atmosphere(make_look())
    assert toned(atmosphere, 1) is atmosphere


def test_a_scripted_look_blends_into_its_change_along_the_scroll() -> None:
    dusk = SkyLook("dusk", [0.2, 0.2])
    night = SkyLook("night", [0.9, 0.9])
    script = SkyScript(dusk, [AtmosphereChange(10, 20, night)])
    look = make_look(atmosphere=script, clouds=[cloud(), cloud()])

    track = atmosphere_track(look, scroll_speed=2)
    base_opacity = [c.opacity for c in look.clouds]

    before = track.at(0)
    after = track.at(100)
    dusk_expected = _resolved(dusk, base_opacity, 100, 400)
    night_expected = _resolved(night, base_opacity, 100, 400)
    assert before.sun.elevation_deg == pytest.approx(dusk_expected.sun.elevation_deg)
    assert after.sun.elevation_deg == pytest.approx(night_expected.sun.elevation_deg)


def test_a_time_of_day_option_replaces_the_scripted_time_of_day() -> None:
    script = SkyScript(SkyLook("dusk", [0.2, 0.2]))
    look = make_look(atmosphere=script)
    options = AtmosphereOptions(time_of_day="midday")
    track = atmosphere_track(look, scroll_speed=1, options=options)
    expected = _resolved(SkyLook("midday", [0.2, 0.2]), [c.opacity for c in look.clouds], 100, 400)
    assert track.at(0).sun.elevation_deg == pytest.approx(expected.sun.elevation_deg)


def test_weather_off_takes_the_weather_out_of_the_script() -> None:
    stormy = SkyLook("dusk", [0.2, 0.2], weather=Weather("rain", 1))
    look = make_look(atmosphere=SkyScript(stormy))
    atmosphere = atmosphere_track(look, 1, AtmosphereOptions(weather=False)).at(0)
    assert atmosphere.weather is CLEAR


def test_a_look_without_a_script_takes_its_time_of_day_from_the_clouds() -> None:
    look = make_look(clouds=[cloud(coverage=0.2), cloud(coverage=0.9)])
    track = atmosphere_track(look, 1, AtmosphereOptions(time_of_day="midday"))
    expected = _resolved(SkyLook("midday", [0.2, 0.9]), [c.opacity for c in look.clouds], 100, 400)
    assert track.at(0).sun.elevation_deg == pytest.approx(expected.sun.elevation_deg)


def test_the_options_default_to_no_choice() -> None:
    options = AtmosphereOptions()
    assert (options.time_of_day, options.weather, options.tile_grid) == (None, None, None)
