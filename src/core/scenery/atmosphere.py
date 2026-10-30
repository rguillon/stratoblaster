"""The changing part of a level's look (phase 8, P08-R04, P08-R05): the time of day, the clouds,
the haze, the ground lights and the weather, as plain numbers that blend smoothly from one look to
another along the level. Pure; the renderer applies it to the scene every frame.

Ported from `core/scenery/atmosphere.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any, Literal  # noqa: E402

Rgb = tuple[float, float, float]
TimeOfDay = Literal["dawn", "morning", "midday", "afternoon", "dusk", "night"]
Look = Any  # The TypeScript class is generic in its look; Transcrypt has no generic classes.
__pragma__("noskip")

# `%` keeps JavaScript's sign rule (the result takes the sign of the dividend), as in the
# TypeScript.
__pragma__("jsmod")

# Blend point at which the kind of weather switches (halfway).
HALF = 0.5

TIMES_OF_DAY = ["dawn", "morning", "midday", "afternoon", "dusk", "night"]


def is_time_of_day(value: str) -> bool:
    """Whether `value` names a time of day."""
    return value in TIMES_OF_DAY


class SkyStop:
    """A colour of the sky gradient at a height (-1 straight down … 1 straight up)."""

    def __init__(self, at: float, color: Rgb) -> None:
        self.at = at
        self.color = color


class CloudCover:
    """One cloud layer as the atmosphere shows it."""

    def __init__(self, coverage: float, opacity: float, color: Rgb, shade: Rgb) -> None:
        """`coverage`: share (0..1) of the sky the layer covers. `opacity`: 0 = invisible,
        1 = opaque. `shade`: colour of the thin edges."""
        self.coverage = coverage
        self.opacity = opacity
        self.color = color
        self.shade = shade


class Weather:
    """Weather (P08-R05): a kind (e.g. `snow`, a key of the engine's weather kinds) and its
    strength (0 = none, 1 = the heaviest)."""

    def __init__(self, kind: str, strength: float) -> None:
        self.kind = kind
        self.strength = strength


class Sun:
    """Where and how the sun (or the moon) lights the level."""

    def __init__(
        self,
        elevation_deg: float,
        azimuth_deg: float,
        color: Rgb,
        intensity: float,
        shadow_darkness: float,
    ) -> None:
        """`azimuth_deg`: 0 = straight ahead (+Z), positive towards +X. `shadow_darkness`: 0 =
        black shadows, 1 = no shadows."""
        self.elevation_deg = elevation_deg
        self.azimuth_deg = azimuth_deg
        self.color = color
        self.intensity = intensity
        self.shadow_darkness = shadow_darkness


class Sky:
    """The sky's haze and the gradient used for reflections."""

    def __init__(
        self,
        haze: Rgb,
        stops: Sequence[SkyStop],
        environment_intensity: float,
    ) -> None:
        """`haze`: clear and fog colour. `stops`: sky gradient for reflections (sea, metal);
        every atmosphere of a level has as many stops."""
        self.haze = haze
        self.stops = stops
        self.environment_intensity = environment_intensity


class Ambient:
    """The ambient light: from the sky, and from the ground."""

    def __init__(self, sky: Rgb, ground: Rgb, intensity: float) -> None:
        self.sky = sky
        self.ground = ground
        self.intensity = intensity


class Fog:
    """Linear fog, in world units from the camera."""

    def __init__(self, start: float, end: float) -> None:
        self.start = start
        self.end = end


class Atmosphere:
    """Everything about a level's look that changes with the time of day and the weather."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        sun: Sun,
        sky: Sky,
        ambient: Ambient,
        fog: Fog,
        clouds: Sequence[CloudCover],
        ground_lights: float,
        weather: Weather,
        aurora: float,
        lightning: float,
        second_weather: Weather | None = None,
    ) -> None:
        """`aurora`: strength (0..1) of the aurora's curtains in the haze. `lightning`: strength
        (0..1) of a storm's lightning flashes (P09-R05). `second_weather`: phase 10, a second
        weather at the same time (ash and embers together)."""
        self.sun = sun
        self.sky = sky
        self.ambient = ambient
        self.fog = fog
        self.clouds = clouds
        """Cloud layers."""
        self.ground_lights = ground_lights
        """Brightness of the window, street, neon and car lights of the ground (0 = off)."""
        self.weather = weather
        self.second_weather = second_weather
        self.aurora = aurora
        self.lightning = lightning


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_rgb(a: Rgb, b: Rgb, t: float) -> Rgb:
    return (_lerp(a[0], b[0], t), _lerp(a[1], b[1], t), _lerp(a[2], b[2], t))


def _lerp_angle(a: float, b: float, t: float) -> float:
    """Turns `a` towards `b` the short way round, by `t` (degrees)."""
    turn = ((((b - a) % 360) + 540) % 360) - 180
    return a + turn * t


def _blend_clouds(a: Sequence[CloudCover], b: Sequence[CloudCover], t: float) -> list[CloudCover]:
    result: list[CloudCover] = []
    for i, ca in enumerate(a):
        cb = b[i] if i < len(b) else ca
        result.append(
            CloudCover(
                _lerp(ca.coverage, cb.coverage, t),
                _lerp(ca.opacity, cb.opacity, t),
                _lerp_rgb(ca.color, cb.color, t),
                _lerp_rgb(ca.shade, cb.shade, t),
            )
        )
    return result


def _blend_weather(a: Weather, b: Weather, t: float) -> Weather:
    """Weather between `a` and `b`: the strength blends; the kind is the one that is there."""
    if a.strength <= 0:
        kind = b.kind
    elif b.strength <= 0 or t < HALF:
        kind = a.kind
    else:
        kind = b.kind
    return Weather(kind, _lerp(a.strength, b.strength, t))


# No weather (a second weather missing on one side blends from or to it).
NO_WEATHER = Weather("snow", 0)


def _blend_second_weather(a: Atmosphere, b: Atmosphere, t: float) -> Weather | None:
    """The second weathers of `a` and `b` blended, if either has one (phase 10)."""
    if a.second_weather is None and b.second_weather is None:
        return None
    wa = a.second_weather if a.second_weather is not None else NO_WEATHER
    wb = b.second_weather if b.second_weather is not None else NO_WEATHER
    return _blend_weather(wa, wb, t)


def blend_atmosphere(a: Atmosphere, b: Atmosphere, t: float) -> Atmosphere:
    """The atmosphere `t` of the way from `a` to `b` (0 = `a`, 1 = `b`): every number halfway at
    0.5."""
    if t <= 0:
        return a
    if t >= 1:
        return b
    stops: list[SkyStop] = []
    for i, s in enumerate(a.sky.stops):
        other = b.sky.stops[i].color if i < len(b.sky.stops) else s.color
        stops.append(SkyStop(s.at, _lerp_rgb(s.color, other, t)))
    return Atmosphere(
        Sun(
            _lerp(a.sun.elevation_deg, b.sun.elevation_deg, t),
            _lerp_angle(a.sun.azimuth_deg, b.sun.azimuth_deg, t),
            _lerp_rgb(a.sun.color, b.sun.color, t),
            _lerp(a.sun.intensity, b.sun.intensity, t),
            _lerp(a.sun.shadow_darkness, b.sun.shadow_darkness, t),
        ),
        Sky(
            _lerp_rgb(a.sky.haze, b.sky.haze, t),
            stops,
            _lerp(a.sky.environment_intensity, b.sky.environment_intensity, t),
        ),
        Ambient(
            _lerp_rgb(a.ambient.sky, b.ambient.sky, t),
            _lerp_rgb(a.ambient.ground, b.ambient.ground, t),
            _lerp(a.ambient.intensity, b.ambient.intensity, t),
        ),
        Fog(_lerp(a.fog.start, b.fog.start, t), _lerp(a.fog.end, b.fog.end, t)),
        _blend_clouds(a.clouds, b.clouds, t),
        _lerp(a.ground_lights, b.ground_lights, t),
        _blend_weather(a.weather, b.weather, t),
        _lerp(a.aurora, b.aurora, t),
        _lerp(a.lightning, b.lightning, t),
        _blend_second_weather(a, b, t),
    )


class AtmosphereChange:
    """A change of look over a stretch of the level: from distance `from_` to `to` it becomes
    `look`."""

    def __init__(self, from_: float, to: float, look: Look) -> None:
        self.from_ = from_
        self.to = to
        self.look = look


class _Stretch:
    """A look change once resolved into an atmosphere."""

    def __init__(self, from_: float, to: float, end: Atmosphere) -> None:
        self.from_ = from_
        self.to = to
        self.end = end


def _smooth(t: float) -> float:
    """An eased 0..1 ramp that stays at one half halfway (smoothstep)."""
    return t * t * (3 - 2 * t)


class AtmosphereTrack:
    """A level's look along its length (P08-R04): `start`, then each change in turn, blending
    every number smoothly over its stretch. It follows the distance, so a jump along the level
    shows the look of where it lands. `resolve` turns a look description into an atmosphere.
    """

    def __init__(
        self,
        start: Look,
        changes: Sequence[AtmosphereChange],
        resolve: Callable[[Look], Atmosphere],
    ) -> None:
        self._start = resolve(start)
        ordered = sorted_by_from(changes)
        self._changes: list[_Stretch] = []
        for c in ordered:
            if not (c.to >= c.from_):
                raise ValueError("A look change must end after it starts")
            self._changes.append(_Stretch(c.from_, c.to, resolve(c.look)))

    def at(self, distance: float) -> Atmosphere:
        """The atmosphere at `distance` along the level."""
        now = self._start
        for stretch in self._changes:
            if distance <= stretch.from_:
                break
            t = 1.0
            if stretch.to > stretch.from_:
                t = min(1, (distance - stretch.from_) / (stretch.to - stretch.from_))
            now = blend_atmosphere(now, stretch.end, _smooth(t))
        return now


def sorted_by_from(changes: Sequence[AtmosphereChange]) -> list[AtmosphereChange]:
    """The changes in order of their `from_` (a stable sort, as JavaScript's)."""
    result = list(changes)
    # Insertion sort: stable, and the lists are short (one entry per look change of a level).
    for i in range(1, len(result)):
        item = result[i]
        j = i - 1
        while j >= 0 and result[j].from_ > item.from_:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = item
    return result
