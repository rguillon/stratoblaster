"""Builds the core sky of a level (P08-R04, P09-R04, P10) from its config record: the sky script
(`atmosphere`) of a scenery look, as `core/scenery/sky_look.py` reads it. The config keeps the
camelCase keys; `core/` takes snake_case attributes, and an omitted optional field is
None. Mapping rules are in `config_build.py`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.atmosphere import AtmosphereChange, Weather
from core.scenery.sky_look import SkyGlow, SkyLook, SkyMist, SkyScript
from game.sim.config_build import mapped, maybe, opt

__pragma__("skip")
from typing import Any  # noqa: E402

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
__pragma__("noskip")


def _weather(weather: ConfigRecord) -> Weather:
    return Weather(weather.kind, weather.strength)


def _mist(mist: ConfigRecord) -> SkyMist:
    return SkyMist(mist.fog, mist.white)


def _glow(glow: ConfigRecord) -> SkyGlow:
    return SkyGlow(glow.color, glow.strength)


def sky_look(config: ConfigRecord) -> SkyLook:
    """A level's look at one place along it (P08-R04, R05)."""
    return SkyLook(
        config.timeOfDay,
        config.clouds,
        opt(config.storm),
        maybe(config.weather, _weather),
        opt(config.aurora),
        opt(config.lightning),
        maybe(config.mist, _mist),
        opt(config.tint),
        maybe(config.secondWeather, _weather),
        opt(config.cloudTint),
        maybe(config.underglow, _glow),
        opt(config.groundLights),
        opt(config.brightness),
        opt(config.plainClouds),
    )


def _change(change: ConfigRecord) -> AtmosphereChange:
    return AtmosphereChange(change["from"], change.to, sky_look(change.look))


def sky_script(config: ConfigRecord) -> SkyScript:
    """The sky script of a scenery look: its start, and its changes over stretches of the level."""
    return SkyScript(sky_look(config.start), maybe(config.changes, _changes))


def _changes(changes: ConfigRecord) -> list[AtmosphereChange]:
    return mapped(changes, _change)
