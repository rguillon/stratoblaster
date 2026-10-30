"""Weather kinds and lightning tunables (phase 8-10, P08-R05, P09-R05, P10-R06), ported from
`config/weather.ts`.

The classes are defined here (not imported from `core/`), so `config/` never imports `core/` at
runtime: `core/scenery/lightning.py` imports this module.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

Rgb = tuple[float, float, float]
__pragma__("noskip")


class WeatherHaze:
    """Phase 9: at strength 1 the haze turns `share` of the way to `color` (rain greys it)."""

    def __init__(self, color: Rgb, share: float) -> None:
        self.color = color
        self.share = share


class WeatherRings:
    """Phase 9: faint rings spreading on the water where drops land (rain): about `per_cell` in
    each square of `cell` world units at strength 1, each growing to `radius` over `period`
    seconds, as opaque as `alpha` at most, in `color`."""

    def __init__(
        self,
        color: Rgb,
        cell: float,
        per_cell: float,
        radius: float,
        period: float,
        alpha: float,
    ) -> None:
        self.color = color
        self.cell = cell
        self.per_cell = per_cell
        self.radius = radius
        self.period = period
        self.alpha = alpha


class WeatherFlicker:
    """Phase 10: each particle's brightness flickers by up to `amount` (0..1), `hz` times a
    second."""

    def __init__(self, amount: float, hz: float) -> None:
        self.amount = amount
        self.hz = hz


class WeatherVolume:
    """The box of air a weather fills around the view: half its width across the level, its
    length along it, and its bottom and top heights."""

    def __init__(self, half_width: float, length: float, bottom: float, top: float) -> None:
        self.half_width = half_width
        self.length_ = length
        self.bottom = bottom
        self.top = top


class WeatherKind:
    """A kind of weather (P08-R05): particles falling through the air between the ground and the
    flight altitude, drawn behind everything on the playfield. Kinds are data."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        max_particles: int,
        fog_at_1: float,
        fall: Sequence[float],
        wind: Sequence[float],
        size: Sequence[float],
        streak: float,
        sway: Sequence[float],
        color: Rgb,
        alpha: float,
        volume: WeatherVolume,
        align: str | None = None,
        haze: WeatherHaze | None = None,
        rings: WeatherRings | None = None,
        blend: str | None = None,
        flicker: WeatherFlicker | None = None,
        fade_high: float | None = None,
    ) -> None:
        """`max_particles`: particles drawn at strength 1. `fog_at_1`: how far the fog ends at
        strength
        1, as a share of its clear-weather distance. `fall`: speed they fall at, [min, max]. `wind`:
        the sideways wind at strength 0 and 1 (world units / s). `size`: size of a particle, [min,
        max]. `streak`: how much longer it streaks along the wind at 1. `sway`: [amplitude,
        frequency]
        of the slow sway of each particle. `alpha`: opacity of a particle. `align` (phase 9): `fall`
        stretches each particle along the way it falls (rain), `wind` (the default) sideways at
        strength 1 only. `blend` (phase 10): `add` draws them added onto what is behind (embers).
        `fade_high` (phase 10): particles fade out over the top share of the box of air they
        fill."""
        self.max_particles = max_particles
        self.fog_at_1 = fog_at_1
        self.fall = fall
        self.wind = wind
        self.size = size
        self.streak = streak
        self.sway = sway
        self.color = color
        self.alpha = alpha
        self.volume = volume
        self.align = align
        self.haze = haze
        self.rings = rings
        self.blend = blend
        self.flicker = flicker
        self.fade_high = fade_high


class LightningRules:
    """How lightning comes and how bright it gets (see `LIGHTNING`)."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        gap: Sequence[float],
        flash: float,
        rise: float,
        double_chance: float,
        double_after: float,
        brightness: float,
        max_haze: float,
        bolt_chance: float,
        max_per_second: int,
    ) -> None:
        """`gap`: seconds between two strikes, [min, max]. `flash` and `rise`: seconds a flash
        lasts,
        and how long it takes to rise to full brightness. `double_chance` and `double_after`: chance
        that a strike flashes twice, and the seconds between its two flashes. `brightness`: ambient
        light and sky at most this many times as bright as the storm's. `max_haze`: a flash
        brightens
        no channel of the haze past this (0..1). `bolt_chance`: chance that a strike draws a bolt in
        the clouds. `max_per_second`: never more flashes than this in any second."""
        self.gap = gap
        self.flash = flash
        self.rise = rise
        self.double_chance = double_chance
        self.double_after = double_after
        self.brightness = brightness
        self.max_haze = max_haze
        self.bolt_chance = bolt_chance
        self.max_per_second = max_per_second


_VOLUME = WeatherVolume(420, 1100, 0, 300)

# The weather kinds of the engine (P08-R05, P09-R05, P10-R06).
WEATHER_KINDS = {
    "snow": WeatherKind(
        1500,
        0.55,
        [26, 48],
        [6, 120],
        [1.4, 2.6],
        4,
        [6, 0.35],
        (0.96, 0.97, 1),
        0.5,
        _VOLUME,
    ),
    # P09-R05: thin, light streaks falling fast at a slight slant (`rain_streaks_max`).
    "rain": WeatherKind(
        2000,
        0.6,
        [380, 520],
        [30, 70],
        [0.35, 0.55],
        16,
        [0, 0],
        (0.76, 0.81, 0.9),
        0.32,
        _VOLUME,
        "fall",
        WeatherHaze((0.52, 0.56, 0.6), 0.45),
        WeatherRings((0.86, 0.9, 0.95), 9, 1, 2.2, 0.8, 0.32),
        None,
        None,
        None,
    ),
    # P10-R06: grey flakes falling slowly and drifting, a dull snow (`ash_flakes_max`).
    "ash": WeatherKind(
        1500,
        0.5,
        [12, 26],
        [4, 36],
        [1, 1.9],
        1.5,
        [5, 0.22],
        (0.56, 0.54, 0.5),
        0.42,
        _VOLUME,
        None,
        WeatherHaze((0.46, 0.41, 0.34), 0.6),
        None,
        None,
        None,
        None,
    ),
    # P10-R06: small glowing orange sparks rising from the ground (`embers_max`).
    "embers": WeatherKind(
        800,
        0.92,
        [-58, -28],
        [6, 26],
        [0.45, 0.85],
        0,
        [4, 0.6],
        (1, 0.42, 0.06),
        0.9,
        WeatherVolume(420, 1100, 0, 280),
        None,
        None,
        None,
        "add",
        WeatherFlicker(0.65, 4.5),
        0.45,
    ),
}

# Lightning (P09-R05), a storm option on top of rain.
LIGHTNING = LightningRules(
    [4, 10],
    0.15,
    0.03,
    0.35,
    0.25,
    1.8,
    0.85,
    0.6,
    3,
)
