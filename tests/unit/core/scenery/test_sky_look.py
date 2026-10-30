"""Unit tests of `src/core/scenery/sky_look.py`."""

import pytest

from config.time_of_day import OVERCAST, TIME_OF_DAY, UNDERGLOW
from config.weather import WEATHER_KINDS
from core.scenery.atmosphere import Fog, Weather
from core.scenery.sky_look import (
    MIST_COLOR,
    NO_UNDERGLOW,
    SkyBase,
    SkyGlow,
    SkyLook,
    SkyMist,
    SkyScript,
    at_time_of_day,
    copy_look,
    resolve_sky,
    weather_fog,
    weather_particles,
)

BASE = SkyBase(Fog(100, 1000), [0.8, 0.6])


def look(**overrides: object) -> SkyLook:
    """A midday look with clouds of 0.2 and 0.1 cover, as the level data gives it."""
    values: dict[str, object] = {"time_of_day": "midday", "clouds": [0.2, 0.1]}
    values.update(overrides)
    return SkyLook(**values)  # type: ignore[arg-type]


def test_p08_r04_clouds_keep_their_coverage_and_thin_when_heavy() -> None:
    clear = resolve_sky(look(clouds=[0.2, 0.1]), BASE).clouds
    assert [c.coverage for c in clear] == [0.2, 0.1]
    assert clear[0].opacity == pytest.approx(0.8)
    assert clear[1].opacity == pytest.approx(0.6)
    heavy = resolve_sky(look(clouds=[1.0, 1.0]), BASE).clouds
    assert heavy[0].opacity == pytest.approx(0.8 * (1 - OVERCAST.thinning))


def test_p08_r04_a_layer_without_a_base_opacity_takes_the_last_one_or_is_opaque() -> None:
    short = SkyBase(Fog(100, 1000), [0.5])
    layers = resolve_sky(look(clouds=[0.0, 0.0, 0.0]), short).clouds
    assert [c.opacity for c in layers] == pytest.approx([0.5, 0.5, 0.5])
    none = SkyBase(Fog(100, 1000), [])
    assert [c.opacity for c in resolve_sky(look(clouds=[0.0]), none).clouds] == [1]


def test_p08_r04_a_cloud_tint_and_a_glow_colour_the_clouds() -> None:
    tinted = resolve_sky(look(cloud_tint=(0.5, 0.5, 0.5)), BASE).clouds[0]
    base_color = TIME_OF_DAY["midday"].clouds.color
    assert tinted.color == pytest.approx(tuple(c * 0.5 for c in base_color))
    glow = SkyGlow((1, 0, 0), 1)
    lit = resolve_sky(look(underglow=glow), BASE).clouds[0]
    # The glow takes the cloud's body UNDERGLOW.cloud of the way to its colour (red here).
    assert lit.color[0] == pytest.approx(base_color[0] * (1 - UNDERGLOW.cloud) + UNDERGLOW.cloud)
    assert lit.color[1] == pytest.approx(base_color[1] * (1 - UNDERGLOW.cloud))
    plain = resolve_sky(look(underglow=glow, plain_clouds=True), BASE).clouds[0]
    assert plain.color == pytest.approx(base_color)


def test_p09_r04_a_mist_ends_the_fog_nearer_and_turns_the_haze_pale() -> None:
    mist = SkyMist(0.5, 1)
    atmosphere = resolve_sky(look(mist=mist), BASE)
    assert atmosphere.sky.haze == pytest.approx(MIST_COLOR)
    assert atmosphere.fog.end == pytest.approx(1000 * TIME_OF_DAY["midday"].fog * 0.5)


def test_p08_r05_rain_greys_the_haze_and_brings_the_fog_in() -> None:
    rain = Weather("rain", 1)
    clear = resolve_sky(look(), BASE)
    rainy = resolve_sky(look(weather=rain), BASE)
    assert rainy.sky.haze != pytest.approx(clear.sky.haze)
    assert rainy.fog.end == pytest.approx(
        1000 * TIME_OF_DAY["midday"].fog * WEATHER_KINDS["rain"].fog_at_1
    )
    assert rainy.weather is not None
    assert rainy.weather.kind == "rain"


def test_p08_r05_snow_does_not_grey_the_haze() -> None:
    clear = resolve_sky(look(), BASE)
    snowy = resolve_sky(look(weather=Weather("snow", 1)), BASE)
    assert snowy.sky.haze == pytest.approx(clear.sky.haze)


def test_p08_r05_weather_fog_is_one_in_clear_weather_and_its_kinds_otherwise() -> None:
    assert weather_fog(Weather("rain", 0)) == 1
    assert weather_fog(Weather("rain", 1)) == pytest.approx(WEATHER_KINDS["rain"].fog_at_1)
    assert weather_fog(Weather("rain", 5)) == pytest.approx(WEATHER_KINDS["rain"].fog_at_1)
    assert weather_fog(Weather("nothing", 1)) == 1


def test_p08_r05_weather_particles_grow_with_its_strength() -> None:
    snow_max = WEATHER_KINDS["snow"].max_particles
    assert weather_particles(Weather("snow", 0)) == 0
    assert weather_particles(Weather("snow", 1)) == snow_max
    assert weather_particles(Weather("snow", 0.5)) == int(snow_max * 0.5 + 0.5)
    assert weather_particles(Weather("nothing", 1)) == 0


def test_an_underglow_lights_the_haze_and_the_ground_ambient_light() -> None:
    glow = SkyGlow((1, 0.5, 0), 1)
    plain = resolve_sky(look(), BASE)
    lit = resolve_sky(look(underglow=glow), BASE)
    assert lit.sky.haze[1] != pytest.approx(plain.sky.haze[1])
    assert lit.ambient.ground[0] != pytest.approx(plain.ambient.ground[0])
    assert NO_UNDERGLOW.strength == 0


def test_copy_look_copies_every_field() -> None:
    original = look(
        storm=0.5,
        weather=Weather("rain", 0.2),
        aurora=0.1,
        lightning=0.2,
        mist=SkyMist(1, 0.5),
        tint=(1, 1, 1),
        second_weather=Weather("ash", 1),
        cloud_tint=(1, 1, 1),
        underglow=SkyGlow((1, 1, 1), 0.3),
        ground_lights=0.4,
        brightness=1.2,
        plain_clouds=False,
    )
    copied = copy_look(original)
    assert copied is not original
    assert copied.__dict__ == original.__dict__


def test_at_time_of_day_changes_only_the_time_of_day() -> None:
    original = look()
    assert at_time_of_day(original, None) is original
    assert at_time_of_day(original, "") is original
    dusk = at_time_of_day(original, "dusk")
    assert dusk.time_of_day == "dusk"
    assert original.time_of_day == "midday"


def test_a_sky_script_keeps_its_start_and_its_changes() -> None:
    start = look()
    assert SkyScript(start).start is start
    assert SkyScript(start).changes is None
