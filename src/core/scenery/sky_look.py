"""A level's look as its data describes it (P08-R04, R05): a time of day, a cloud cover and a
weather, turned into an `Atmosphere` with the engine's time-of-day presets. Ported from
`core/scenery/sky-look.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.scenery.atmosphere import AtmosphereChange  # noqa: E402

Rgb = tuple[float, float, float]
__pragma__("noskip")

from config.time_of_day import OVERCAST, SKY_STOPS, TIME_OF_DAY, UNDERGLOW  # noqa: E402
from config.weather import WEATHER_KINDS  # noqa: E402
from core.math.noise import smoothstep  # noqa: E402
from core.scenery.atmosphere import (  # noqa: E402
    Ambient,
    Atmosphere,
    CloudCover,
    Fog,
    Sky,
    SkyStop,
    Sun,
    Weather,
)


class SkyMist:
    """Phase 9: a mist (P09-R04, the 3-1 morning): the fog ends at `fog` of its distance (1 = as
    far as usual) and the haze turns `white` (0..1) of the way to the mist's pale colour."""

    def __init__(self, fog: float, white: float) -> None:
        self.fog = fog
        self.white = white


class SkyGlow:
    """Phase 10: a glow from below in `color` (fire, lava), `strength` 0..1."""

    def __init__(self, color: Rgb, strength: float) -> None:
        self.color = color
        self.strength = strength


class SkyLook:
    """How a level looks at one place along it (P08-R04). The optional fields default to None,
    which means the defaults of the TypeScript (see the comments)."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        time_of_day: str,
        clouds: Sequence[float],
        storm: float | None = None,
        weather: Weather | None = None,
        aurora: float | None = None,
        lightning: float | None = None,
        mist: SkyMist | None = None,
        tint: Rgb | None = None,
        second_weather: Weather | None = None,
        cloud_tint: Rgb | None = None,
        underglow: SkyGlow | None = None,
        ground_lights: float | None = None,
        brightness: float | None = None,
        plain_clouds: bool | None = None,
    ) -> None:
        """`time_of_day`: a time of day. `clouds`: cover (0 = clear, 1 = overcast) of the low and
        the high cloud layers. `storm`: how stormy the clouds look (0 = the time of day's colour,
        1 = dark storm grey). `weather`: weather (P08-R05), none when None. `aurora`: strength
        (0..1) of an aurora in the night haze. `lightning`: strength (0..1) of the lightning of a
        storm (P09-R05). `mist` (P09-R04). `tint`: a tint (RGB factors) on the ambient light.
        `second_weather` (phase 10): a second weather at the same time. `cloud_tint` (phase 10): a
        tint on the clouds' colours. `underglow` (phase 10): a glow from below. `ground_lights`:
        strength of the lights on the ground; the time of day's when None. `brightness`: a factor on
        the sun and the ambient light (1 = the time of day's). `plain_clouds`: the clouds keep the
        time of day's colours: no storm grey, tint or glow from below."""
        self.time_of_day = time_of_day
        self.clouds = clouds
        self.storm = storm
        self.weather = weather
        self.aurora = aurora
        self.lightning = lightning
        self.mist = mist
        self.tint = tint
        self.second_weather = second_weather
        self.cloud_tint = cloud_tint
        self.underglow = underglow
        self.ground_lights = ground_lights
        self.brightness = brightness
        self.plain_clouds = plain_clouds


class SkyScript:
    """The look of a level along its length: `start`, and changes over stretches given in seconds
    of scrolling from the level's start (the stage turns them into distances at its speed)."""

    def __init__(self, start: SkyLook, changes: Sequence[AtmosphereChange] | None = None) -> None:
        self.start = start
        self.changes = changes


class SkyBase:
    """What a level's own look gives the atmosphere: its fog and its cloud layers' opacity."""

    def __init__(self, fog: Fog, cloud_opacity: Sequence[float]) -> None:
        self.fog = fog
        self.cloud_opacity = cloud_opacity


# No weather.
CLEAR = Weather("snow", 0)

# The colour a mist turns the haze to (phase 9).
MIST_COLOR = (0.9, 0.92, 0.9)

# No glow from below.
NO_UNDERGLOW = SkyGlow((0, 0, 0), 0)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _mix(a: Rgb, b: Rgb, t: float) -> Rgb:
    return (_lerp(a[0], b[0], t), _lerp(a[1], b[1], t), _lerp(a[2], b[2], t))


def _scale(c: Rgb, k: float) -> Rgb:
    return (c[0] * k, c[1] * k, c[2] * k)


def _times(c: Rgb, k: Rgb) -> Rgb:
    return (c[0] * k[0], c[1] * k[1], c[2] * k[2])


def _clamp01(v: float) -> float:
    return min(1, max(0, v))


def _weather_haze(haze: Rgb, weather: Weather) -> Rgb:
    """The haze of `weather` (phase 9: rain greys it), over `haze`."""
    kind = WEATHER_KINDS.get(weather.kind)
    tint = kind.haze if kind is not None else None
    if tint is None:
        return haze
    return _mix(haze, tint.color, tint.share * _clamp01(weather.strength))


def weather_fog(weather: Weather) -> float:
    """How far the fog comes in for `weather`: 1 in clear weather, down to its kind's `fog_at_1`."""
    kind = WEATHER_KINDS.get(weather.kind)
    strength = _clamp01(weather.strength)
    return _lerp(1, kind.fog_at_1, strength) if kind is not None else 1


def _clouds_of(look: SkyLook, base: SkyBase, color: Rgb, shade: Rgb) -> list[CloudCover]:
    """The cloud layers of `look`: the time of day's colours, greyed by a storm, tinted, lit from
    below (phase 10), thinned when heavy."""
    plain = look.plain_clouds is True
    storm = 0 if plain else (look.storm if look.storm is not None else 0)
    tint: Rgb = (
        (1, 1, 1) if plain else (look.cloud_tint if look.cloud_tint is not None else (1, 1, 1))
    )
    glow = (
        NO_UNDERGLOW if plain else (look.underglow if look.underglow is not None else NO_UNDERGLOW)
    )
    lit = UNDERGLOW.cloud * glow.strength
    edge = UNDERGLOW.shade * glow.strength
    cloud_color = _mix(_times(_mix(color, OVERCAST.storm.color, storm), tint), glow.color, lit)
    cloud_shade = _mix(_times(_mix(shade, OVERCAST.storm.shade, storm), tint), glow.color, edge)
    clouds: list[CloudCover] = []
    for i, coverage in enumerate(look.clouds):
        if i < len(base.cloud_opacity):
            opacity_base = base.cloud_opacity[i]
        elif len(base.cloud_opacity) > 0:
            opacity_base = base.cloud_opacity[len(base.cloud_opacity) - 1]
        else:
            opacity_base = 1
        opacity = opacity_base * (1 - OVERCAST.thinning * smoothstep(0.5, 1, coverage))
        clouds.append(CloudCover(coverage, opacity, cloud_color, cloud_shade))
    return clouds


def resolve_sky(look: SkyLook, base: SkyBase) -> Atmosphere:
    """The atmosphere of `look` (P08-R04): its time of day's light, dimmed and softened under a
    heavy cloud cover, its clouds, and the fog of `base` brought in by the time of day and the
    weather."""
    preset = TIME_OF_DAY[look.time_of_day]
    o = smoothstep(OVERCAST.overcast[0], OVERCAST.overcast[1], look.clouds[0])
    clouds = _clouds_of(look, base, preset.clouds.color, preset.clouds.shade)
    weather = look.weather if look.weather is not None else CLEAR
    second = look.second_weather if look.second_weather is not None else CLEAR
    mist = look.mist if look.mist is not None else SkyMist(1, 0)
    glow = look.underglow if look.underglow is not None else NO_UNDERGLOW
    tint: Rgb = look.tint if look.tint is not None else (1, 1, 1)
    brightness = look.brightness if look.brightness is not None else 1
    # The weathers and the mist bring the end of the haze in, its start only half as much.
    near = weather_fog(weather) * weather_fog(second) * mist.fog
    fog_end = preset.fog * near
    fog_start = (preset.fog * (1 + near)) / 2
    cloud_color = clouds[0].color if len(clouds) > 0 else preset.clouds.color
    haze = _mix(preset.sky.haze, _scale(cloud_color, 0.9), OVERCAST.haze_grey * o)
    sun = preset.sun
    stops: list[SkyStop] = []
    for i, color in enumerate(preset.sky.gradient):
        at = SKY_STOPS[i] if i < len(SKY_STOPS) else 0
        stops.append(SkyStop(at, color))
    sky_haze = _mix(
        _mix(_weather_haze(_weather_haze(haze, weather), second), MIST_COLOR, mist.white),
        glow.color,
        UNDERGLOW.haze * glow.strength,
    )
    ambient = preset.ambient
    look_ground_lights = (
        look.ground_lights if look.ground_lights is not None else preset.ground_lights
    )
    return Atmosphere(
        Sun(
            sun.elevation_deg,
            sun.azimuth_deg,
            sun.color,
            sun.intensity * brightness * (1 - OVERCAST.sun_dim * o),
            _lerp(OVERCAST.shadow_darkness, OVERCAST.soft_shadows, o),
        ),
        Sky(sky_haze, stops, preset.sky.environment_intensity),
        Ambient(
            _times(ambient.sky, tint),
            _mix(_times(ambient.ground, tint), glow.color, UNDERGLOW.ground * glow.strength),
            ambient.intensity * brightness * (1 + OVERCAST.ambient_gain * o),
        ),
        Fog(base.fog.start * fog_start, base.fog.end * fog_end),
        clouds,
        look_ground_lights,
        weather,
        look.aurora if look.aurora is not None else 0,
        look.lightning if look.lightning is not None else 0,
        second if look.second_weather is not None else None,
    )


def copy_look(look: SkyLook) -> SkyLook:
    """A copy of `look`, field by field."""
    return SkyLook(
        look.time_of_day,
        look.clouds,
        look.storm,
        look.weather,
        look.aurora,
        look.lightning,
        look.mist,
        look.tint,
        look.second_weather,
        look.cloud_tint,
        look.underglow,
        look.ground_lights,
        look.brightness,
        look.plain_clouds,
    )


def at_time_of_day(look: SkyLook, time_of_day: str | None) -> SkyLook:
    """`look` at another time of day (the `look=` debug option, P08-R12)."""
    if not time_of_day:
        return look
    result = copy_look(look)
    result.time_of_day = time_of_day
    return result


def without_weather(look: SkyLook) -> SkyLook:
    """`look` without its weather, lightning and second weather included (the `weather=0` debug
    option, P08-R12)."""
    result = copy_look(look)
    result.weather = CLEAR
    result.lightning = 0
    if look.second_weather is not None:
        result.second_weather = CLEAR
    return result


def weather_particles(weather: Weather) -> int:
    """How many particles `weather` draws (P08-R05): none at strength 0, its kind's most at 1, in
    proportion between."""
    kind = WEATHER_KINDS.get(weather.kind)
    strength = _clamp01(weather.strength)
    if kind is None:
        return 0
    return math.floor(kind.max_particles * strength + 0.5)
