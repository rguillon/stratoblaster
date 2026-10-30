"""Lightning (phase 9, P09-R05): when the flashes of a storm come, drawn from the level's seed,
and how a flash lights the scene. Pure: the renderer asks for the flash at its own clock, so the
same level always flashes at the same times, and nothing in the simulation reads it. Ported from
`core/scenery/lightning.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from config.weather import LightningRules  # noqa: E402

Rgb = tuple[float, float, float]
__pragma__("noskip")

from config.weather import LIGHTNING  # noqa: E402
from core.math.rng import create_rng, random_in  # noqa: E402
from core.scenery.atmosphere import Ambient, Atmosphere, Sky  # noqa: E402

INFINITY = float("Infinity")


class Bolt:
    """The bolt of a strike, drawn in the clouds: its place (0..1 across and along) and seed."""

    def __init__(self, x: float, z: float, seed: float) -> None:
        self.x = x
        self.z = z
        self.seed = seed


class Strike:
    """One strike: when its flashes start, and where its bolt is drawn."""

    def __init__(self, flashes: Sequence[float], bolt: Bolt | None) -> None:
        self.flashes = flashes
        self.bolt = bolt


def _max_of(values: Sequence[float]) -> float:
    """`Math.max(...values)`: -Infinity for no values."""
    high = -INFINITY
    for v in values:
        high = max(high, v)
    return high


class LightningSchedule:
    """The strikes of a storm along a level's clock (P09-R05): every `gap` seconds, drawn from
    `seed`, so the same level always flashes at the same times. Strikes are drawn as far as they
    are asked for."""

    def __init__(self, seed: int, rules: LightningRules = LIGHTNING) -> None:
        self._random = create_rng(seed * 7 + 17)
        self._strikes: list[Strike] = []
        self._rules = rules
        self._next = random_in(self._random, rules.gap[0], rules.gap[1])

    def strikes_before(self, time: float) -> list[Strike]:
        """The strikes whose first flash comes before `time`."""
        while self._next < time:
            self._strike()
        return self._strikes

    def flashes_between(self, from_: float, to: float) -> list[float]:
        """Every flash start in [`from_`, `to`)."""
        result: list[float] = []
        for strike in self.strikes_before(to):
            for t in strike.flashes:
                if t >= from_ and t < to:
                    result.append(t)
        return result

    def strike_at(self, time: float) -> Strike | None:
        """The strike lit at `time`, if any."""
        strikes = self.strikes_before(time)
        for i in range(len(strikes) - 1, -1, -1):
            strike = strikes[i]
            if len(strike.flashes) == 0:
                continue
            last = strike.flashes[len(strike.flashes) - 1]
            if time >= strike.flashes[0] and time < last + self._rules.flash:
                return strike
            if last + self._rules.flash < time:
                break
        return None

    def flash_at(self, time: float) -> float:
        """How bright the lightning is at `time`: 0 between flashes, 1 at a flash's height."""
        strike = self.strike_at(time)
        if strike is None:
            return 0
        rules = self._rules
        return _max_of(
            [_envelope(time - start, rules.rise, rules.flash) for start in strike.flashes]
        )

    def _strike(self) -> None:
        r = self._random
        rules = self._rules
        start = self._next
        flashes = [start, start + rules.double_after] if r() < rules.double_chance else [start]
        bolt: Bolt | None = None
        if r() < rules.bolt_chance:
            x = r()
            z = r()
            bolt = Bolt(x, z, math.floor(r() * 1000000))
        self._strikes.append(Strike(flashes, bolt))
        self._next = start + random_in(r, rules.gap[0], rules.gap[1])


def _envelope(age: float, rise: float, length: float) -> float:
    """A flash `age` seconds after it starts: a quick rise, then a fade out over `length`."""
    if age < 0 or age >= length:
        return 0
    if age < rise:
        return age / rise
    t = (age - rise) / (length - rise)
    return (1 - t) * (1 - t)


def _brighter(c: Rgb, k: float, cap: float) -> Rgb:
    """`c` brightened `k` times, no channel past `cap` (or past itself, if it already is)."""
    return (
        min(c[0] * k, max(c[0], cap)),
        min(c[1] * k, max(c[1], cap)),
        min(c[2] * k, max(c[2], cap)),
    )


def flashed(atmosphere: Atmosphere, flash: float, rules: LightningRules = LIGHTNING) -> Atmosphere:
    """`atmosphere` lit by a flash of `flash` (0..1) of a storm's lightning of strength
    `atmosphere.lightning` (P09-R05): the ambient light, the sky and the haze up to `brightness`
    times as bright, never more, the haze never past `max_haze`, so the playfield never turns
    white."""
    f = min(1, max(0, flash)) * min(1, max(0, atmosphere.lightning))
    if f <= 0:
        return atmosphere
    k = 1 + (rules.brightness - 1) * f
    ambient = atmosphere.ambient
    sky = atmosphere.sky
    return Atmosphere(
        atmosphere.sun,
        Sky(
            _brighter(sky.haze, k, rules.max_haze),
            sky.stops,
            sky.environment_intensity * k,
        ),
        Ambient(ambient.sky, ambient.ground, ambient.intensity * k),
        atmosphere.fog,
        atmosphere.clouds,
        atmosphere.ground_lights,
        atmosphere.weather,
        atmosphere.aurora,
        atmosphere.lightning,
        atmosphere.second_weather,
    )
