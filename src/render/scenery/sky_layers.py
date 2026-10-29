"""The sky of a scenery stage (P04-R03, P08-R04, R05): the level's look along its length, the sun
and ambient light it sets, and the cloud layers, weather, aurora and lightning above the ground.
Ported from `render/scenery/sky-layers.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.lightning import flashed
from render.babylon import babylon_class
from render.scenery.atmosphere_of import atmosphere_track
from render.scenery.aurora_layer import AuroraLayer
from render.scenery.cloud_layers import (
    build_cloud_layer,
    update_cloud_layer,
)
from render.scenery.lightning_layer import LightningLayer
from render.scenery.scenery_lighting import apply_atmosphere, light_scenery
from render.scenery.weather_layer import WeatherLayer, WeatherView

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# The aurora's sheet flies this far above the highest cloud layer, under the ships.
AURORA_ABOVE_CLOUDS = 8


class SkyPlacement:
    """Where the sky's layers go: what the camera sees at a height, and the flight altitude.
    `window_at(altitude)` gives the ground window seen at an altitude; `altitude_of(look)` the
    altitude of a cloud layer."""

    def __init__(
        self, window_at: Any, altitude_of: Any, flight_altitude: float, margin: float
    ) -> None:
        self.window_at = window_at
        self.altitude_of = altitude_of
        self.flight_altitude = flight_altitude
        self.margin = margin


def _max_of(values: list[float], start: float) -> float:
    """`Math.max(start, ...values)`."""
    result = start
    for value in values:
        result = max(result, value)
    return result


def _min_of(values: list[float], start: float) -> float:
    """`Math.min(start, ...values)`."""
    result = start
    for value in values:
        result = min(result, value)
    return result


class SkyLayers:
    """The sky of a scenery stage (P04-R03, P08-R04, R05): the level's look along its length, the
    sun and ambient light it sets, and the cloud layers, the weather and the aurora above the
    ground. Built in two steps, as the scenery kit needs the sun first (`attach`).

    `setup` is `(scroll_speed, options, seed)`: `options` is the `AtmosphereOptions` (or None) and
    `seed` the level's seed (its lightning strikes are drawn from it, P09-R05)."""

    def __init__(self, scene: Any, look: Any, setup: tuple[float, Any, int]) -> None:
        scroll_speed, options, seed = setup
        self._scene = scene
        self._look = look
        self._seed = seed
        self._track = atmosphere_track(look, scroll_speed, options)
        self._atmosphere = self._track.at(0)
        self._lights = light_scenery(scene, self._atmosphere)
        # Whether the clouds' cover follows the look (a look with a time of day).
        self._follow = bool(look.atmosphere) or bool(options and options.time_of_day)
        self._clouds: list[Any] = []
        self._weather: WeatherLayer | None = None
        self._aurora: AuroraLayer | None = None
        self._lightning: LightningLayer | None = None
        self._flash = 0

    @property
    def sun(self) -> Any:
        return self._lights.sun

    @property
    def atmosphere(self) -> Any:
        return self._atmosphere

    @property
    def clouds(self) -> list[Any]:
        """The cloud layers' live settings."""
        return [layer.state for layer in self._clouds]

    @property
    def weather_particles(self) -> int:
        """Weather particles drawn on the last frame."""
        return self._weather.drawn if self._weather else 0

    @property
    def flash(self) -> float:
        """How bright the lightning was on the last frame (0..1, its strength included; P09-R05)."""
        return self._flash

    @property
    def lightning(self) -> Any:
        """The storm's lightning, once attached."""
        return self._lightning

    def attach(self, kit: Any, place: SkyPlacement) -> None:
        """Builds the cloud layers, the weather and the aurora with `kit`'s materials."""
        look = self._look
        clouds: list[Any] = []
        for i, cloud in enumerate(look.clouds):
            altitude = place.altitude_of(cloud)
            window = place.window_at(altitude)
            clouds.append(
                build_cloud_layer(
                    self._scene, cloud, kit.cloud(cloud), i, (window, altitude, place.margin)
                )
            )
        self._clouds = clouds
        self._weather = WeatherLayer(self._scene, kit.weather)
        altitudes = [place.altitude_of(cloud) for cloud in look.clouds]
        top = _max_of(altitudes, 0)
        altitude = min(place.flight_altitude - 4, top + AURORA_ABOVE_CLOUDS)
        window = place.window_at(altitude)
        self._aurora = AuroraLayer(self._scene, kit.aurora(), (window, altitude, place.margin))
        # P09-R05: bolts flash inside the lowest cloud layer.
        low = _min_of(altitudes, top)
        self._lightning = LightningLayer(self._scene, self._seed, (place.window_at(low), low))

    def update(self, distance: float, frame: tuple[float, Any, float]) -> Any:
        """The look at `distance` along the level, seen from `camera` at `time`: light, haze,
        clouds, weather (in the box of air from `z_min`), aurora and lightning (P09-R05: a flash
        lights the scene). `frame` is `(time, camera, z_min)`. Returns the atmosphere as lit on
        this frame."""
        time, camera, z_min = frame
        at = camera.position
        self._atmosphere = self._track.at(distance)
        flash = self._lightning.update(self._atmosphere, time, at.z) if self._lightning else 0
        self._flash = flash * self._atmosphere.lightning
        atmosphere = flashed(self._atmosphere, flash)
        apply_atmosphere(self._scene, self._lights, atmosphere)
        for i, layer in enumerate(self._clouds):
            update_cloud_layer(
                layer,
                (at.z, time),
                (atmosphere, atmosphere.clouds[i], self._follow),
            )
        if self._weather:
            right = camera.getDirection(babylon_class("Vector3").Right())
            up = camera.getDirection(babylon_class("Vector3").Up())
            self._weather.update(atmosphere, WeatherView(time, at, right, up, z_min))
        if self._aurora:
            self._aurora.update(atmosphere, time, at)
        return atmosphere
