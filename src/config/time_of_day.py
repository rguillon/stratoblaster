"""The six times of day (P08-R04) and the light tunables of the sky (P08-R04, P10-R04), ported
from `config/time-of-day.ts`.

Colours are gamma-space RGB, 0..1, as the scenery looks.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

Rgb = tuple[float, float, float]
__pragma__("noskip")


class PresetSun:
    """The sun (or, at night, a dim cold moon) of a time of day."""

    def __init__(
        self, elevation_deg: float, azimuth_deg: float, color: Rgb, intensity: float
    ) -> None:
        self.elevation_deg = elevation_deg
        self.azimuth_deg = azimuth_deg
        self.color = color
        self.intensity = intensity


class PresetSky:
    """The sky of a time of day: the haze, and the gradient used for reflections only (the camera
    never sees the sky): under the horizon, at it, a little above, and straight up."""

    def __init__(
        self,
        haze: Rgb,
        gradient: Sequence[Rgb],
        environment_intensity: float,
    ) -> None:
        self.haze = haze
        self.gradient = gradient
        self.environment_intensity = environment_intensity


class PresetAmbient:
    """The ambient light of a time of day."""

    def __init__(self, sky: Rgb, ground: Rgb, intensity: float) -> None:
        self.sky = sky
        self.ground = ground
        self.intensity = intensity


class CloudColors:
    """A colour and the colour of the thin edges (clouds, or a storm's clouds)."""

    def __init__(self, color: Rgb, shade: Rgb) -> None:
        self.color = color
        self.shade = shade


class TimeOfDayPreset:
    """How a time of day lights a level (P08-R04), before its clouds and weather."""

    def __init__(
        self,
        sun: PresetSun,
        sky: PresetSky,
        ambient: PresetAmbient,
        clouds: CloudColors,
        ground_lights: float,
        fog: float,
    ) -> None:
        """`clouds`: colour of the clouds and of their thin edges (P08-R04). `ground_lights`:
        brightness of the ground's window, street, neon and car lights. `fog`: factor on the level's
        fog distances (the haze comes closer at night)."""
        self.sun = sun
        self.sky = sky
        self.ambient = ambient
        self.clouds = clouds
        self.ground_lights = ground_lights
        self.fog = fog


# Heights of the sky gradient's stops (see `PresetSky.gradient`).
SKY_STOPS = [-1, 0, 0.35, 1]

# The six times of day (P08-R04). At night the sun is a dim, cold moon.
TIME_OF_DAY = {
    "dawn": TimeOfDayPreset(
        PresetSun(9, -62, (1, 0.66, 0.46), 1.45),
        PresetSky(
            (0.86, 0.7, 0.68),
            [(0.22, 0.2, 0.24), (1, 0.7, 0.54), (0.8, 0.66, 0.74), (0.38, 0.46, 0.7)],
            0.6,
        ),
        PresetAmbient((0.66, 0.6, 0.72), (0.32, 0.28, 0.32), 0.7),
        CloudColors((1, 0.76, 0.66), (0.8, 0.54, 0.58)),
        0.7,
        1,
    ),
    "morning": TimeOfDayPreset(
        PresetSun(30, 48, (1, 0.95, 0.86), 1.75),
        PresetSky(
            (0.78, 0.86, 0.95),
            [(0.24, 0.26, 0.3), (0.88, 0.92, 0.98), (0.62, 0.76, 0.93), (0.2, 0.42, 0.82)],
            0.7,
        ),
        PresetAmbient((0.64, 0.74, 0.92), (0.32, 0.34, 0.4), 0.6),
        CloudColors((1, 1, 1), (0.78, 0.81, 0.88)),
        0.15,
        1,
    ),
    "midday": TimeOfDayPreset(
        PresetSun(62, 20, (1, 0.97, 0.92), 1.7),
        PresetSky(
            (0.8, 0.85, 0.9),
            [(0.25, 0.25, 0.27), (0.86, 0.9, 0.95), (0.66, 0.76, 0.9), (0.25, 0.48, 0.82)],
            0.7,
        ),
        PresetAmbient((0.68, 0.76, 0.88), (0.34, 0.35, 0.37), 0.62),
        CloudColors((0.98, 0.98, 0.98), (0.76, 0.78, 0.82)),
        0.1,
        1,
    ),
    "afternoon": TimeOfDayPreset(
        PresetSun(34, 42, (1, 0.88, 0.72), 1.6),
        PresetSky(
            (0.82, 0.78, 0.74),
            [(0.26, 0.24, 0.22), (0.96, 0.84, 0.66), (0.66, 0.7, 0.82), (0.3, 0.44, 0.74)],
            0.65,
        ),
        PresetAmbient((0.68, 0.68, 0.76), (0.38, 0.33, 0.3), 0.6),
        CloudColors((0.98, 0.95, 0.9), (0.74, 0.72, 0.74)),
        0.2,
        1,
    ),
    "dusk": TimeOfDayPreset(
        PresetSun(7, 66, (1, 0.52, 0.34), 1.15),
        PresetSky(
            (0.6, 0.46, 0.52),
            [(0.16, 0.14, 0.18), (0.98, 0.54, 0.38), (0.62, 0.44, 0.6), (0.18, 0.2, 0.44)],
            0.55,
        ),
        PresetAmbient((0.54, 0.46, 0.64), (0.24, 0.2, 0.26), 0.65),
        CloudColors((1, 0.62, 0.52), (0.6, 0.36, 0.46)),
        1.2,
        0.95,
    ),
    # A dim, cold moon instead of the sun.
    "night": TimeOfDayPreset(
        PresetSun(42, -28, (0.62, 0.74, 1), 0.6),
        PresetSky(
            (0.07, 0.09, 0.17),
            # Moonlit: the ships' metal still catches some light (readability, P08-R04).
            [(0.08, 0.09, 0.14), (0.34, 0.4, 0.56), (0.26, 0.32, 0.5), (0.14, 0.18, 0.34)],
            0.6,
        ),
        PresetAmbient((0.34, 0.42, 0.64), (0.12, 0.13, 0.2), 0.6),
        CloudColors((0.42, 0.48, 0.64), (0.22, 0.26, 0.4)),
        1.5,
        0.85,
    ),
}


class Overcast:
    """How clouds and storms change the light (P08-R04): a heavy low cover (from `overcast[0]` to
    full at `overcast[1]`) dims the sun by up to `sun_dim`, softens the shadows towards
    `soft_shadows`, brightens the ambient light by up to `ambient_gain` and greys the haze by up to
    `haze_grey`; heavy layers turn see-through by up to `thinning` so the ground still shows. A
    storm turns the clouds towards `storm`."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        overcast: Sequence[float],
        sun_dim: float,
        shadow_darkness: float,
        soft_shadows: float,
        ambient_gain: float,
        haze_grey: float,
        thinning: float,
        storm: CloudColors,
    ) -> None:
        self.overcast = overcast
        self.sun_dim = sun_dim
        self.shadow_darkness = shadow_darkness
        self.soft_shadows = soft_shadows
        self.ambient_gain = ambient_gain
        self.haze_grey = haze_grey
        self.thinning = thinning
        self.storm = storm


class Underglow:
    """Phase 10: a glow from below (P10-R04: fire and lava lighting the clouds, the haze and the
    ambient light from the ground): at strength 1 the clouds' edges turn `shade` of the way to its
    colour, their body `cloud` of the way (dark smoke stays dark), the haze `haze` and the ambient
    light from the ground `ground` of the way."""

    def __init__(self, shade: float, cloud: float, haze: float, ground: float) -> None:
        self.shade = shade
        self.cloud = cloud
        self.haze = haze
        self.ground = ground


OVERCAST = Overcast(
    [0.45, 1],
    0.6,
    0.35,
    0.85,
    0.45,
    0.35,
    0.65,
    CloudColors((0.36, 0.38, 0.42), (0.22, 0.23, 0.26)),
)

UNDERGLOW = Underglow(0.75, 0.2, 0.35, 0.6)
