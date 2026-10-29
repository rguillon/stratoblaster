"""The atmosphere of a level along its length (P08-R04, P08-R12), ported from
`render/scenery/atmosphere-of.ts`: a level's fixed look or its sky script, as the atmosphere the
renderer applies.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.atmosphere import (
    Ambient,
    Atmosphere,
    AtmosphereChange,
    AtmosphereTrack,
    CloudCover,
    Fog,
    Sky,
    Sun,
)
from core.scenery.sky_look import (
    CLEAR,
    SkyBase,
    SkyLook,
    SkyScript,
    at_time_of_day,
    resolve_sky,
    without_weather,
)
from render.scenery.scenery_look import SceneryLook

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class AtmosphereOptions:
    """Debug choices on a level's look (P08-R12): `time_of_day` (`look=<time of day>`, every look
    at this time of day), `weather` (`weather=0`: False, no weather at all) and `tile_grid`
    (P15-R10, `tiles=1`: the grid of tiles drawn over the districts). None when not set."""

    def __init__(
        self,
        time_of_day: str | None = None,
        weather: bool | None = None,
        tile_grid: bool | None = None,
    ) -> None:
        self.time_of_day = time_of_day
        self.weather = weather
        self.tile_grid = tile_grid


def look_atmosphere(look: SceneryLook) -> Atmosphere:
    """The fixed atmosphere of a look without a sky script (World 1): its own sky, fog, sun,
    ambient light, clouds and lights, as they always were."""
    clouds: list[CloudCover] = []
    for c in look.clouds:
        clouds.append(CloudCover(c.coverage, c.opacity, c.color, c.shade))
    return Atmosphere(
        Sun(
            look.sun.elevationDeg,
            look.sun.azimuthDeg,
            look.sun.color,
            look.sun.intensity,
            look.sun.shadow.darkness,
        ),
        Sky(look.sky.haze, look.sky.stops, look.sky.environmentIntensity),
        Ambient(look.ambient.sky, look.ambient.ground, look.ambient.intensity),
        Fog(look.fog.start, look.fog.end),
        clouds,
        look.props.lightIntensity,
        CLEAR,
        0,
        0,
    )


def _script_of(look: SceneryLook, time_of_day: str | None) -> SkyScript | None:
    """The sky script of `look`, or one made from its own clouds when a time of day is forced."""
    if look.atmosphere != None:  # noqa: E711 (optional record field: undefined when absent)
        return look.atmosphere
    if time_of_day is None:
        return None
    low = look.clouds[0].coverage if len(look.clouds) > 0 else 0
    high = look.clouds[1].coverage if len(look.clouds) > 1 else 0
    return SkyScript(SkyLook(time_of_day, [low, high]))


def atmosphere_track(
    look: SceneryLook,
    scroll_speed: float,
    options: AtmosphereOptions | None = None,
) -> Any:
    """The atmosphere of a level along its length (P08-R04): its sky script's looks, their changes
    turned from seconds into distances at `scroll_speed`; or its fixed look. Returns an
    `AtmosphereTrack` (its `at(distance)`: the TypeScript `AtmosphereAlong`)."""
    if options is None:
        options = AtmosphereOptions()
    # The record's `changes` are plain objects (`from`, `to`, `look`), not AtmosphereChange.
    script: Any = _script_of(look, options.time_of_day)
    tone = 1 if look.tone == None else look.tone  # noqa: E711 (optional record field)
    # A fixed look has no weather to turn off.
    if script is None:
        return AtmosphereTrack(
            look,
            [],
            lambda lk: toned(look_atmosphere(lk), tone),
        )
    base = SkyBase(Fog(look.fog.start, look.fog.end), [c.opacity for c in look.clouds])

    def adjust(sky: SkyLook) -> SkyLook:
        timed = at_time_of_day(sky, options.time_of_day)
        return without_weather(timed) if options.weather is False else timed

    changes: list[AtmosphereChange] = []
    for c in script.changes if script.changes != None else []:  # noqa: E711 (optional record field)
        changes.append(
            AtmosphereChange(c["from"] * scroll_speed, c.to * scroll_speed, adjust(c.look))
        )
    return AtmosphereTrack(
        adjust(script.start),
        changes,
        lambda sky: toned(resolve_sky(sky, base), tone),
    )


def toned(atmosphere: Atmosphere, tone: float) -> Atmosphere:
    """`atmosphere` with its haze and clouds `tone` (0..1) as bright (`SceneryLook.tone`)."""
    if tone == 1:
        return atmosphere

    def dim(c: tuple[float, float, float]) -> tuple[float, float, float]:
        return (c[0] * tone, c[1] * tone, c[2] * tone)

    clouds: list[CloudCover] = []
    for c in atmosphere.clouds:
        clouds.append(CloudCover(c.coverage, c.opacity, dim(c.color), dim(c.shade)))
    return Atmosphere(
        atmosphere.sun,
        Sky(dim(atmosphere.sky.haze), atmosphere.sky.stops, atmosphere.sky.environment_intensity),
        atmosphere.ambient,
        atmosphere.fog,
        clouds,
        atmosphere.ground_lights,
        atmosphere.weather,
        atmosphere.aurora,
        atmosphere.lightning,
        atmosphere.second_weather,
    )
