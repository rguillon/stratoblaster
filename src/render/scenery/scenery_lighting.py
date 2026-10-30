"""The lights of a scenery scene (P08-R04): the
sun (or the moon) and the sky's ambient light, lit as an atmosphere says.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    color3,
    color3_black,
    color4,
    fog_mode_linear,
    new_directional_light,
    new_hemispheric_light,
    vector3,
    vector3_cross,
    vector3_dot,
    vector3_down,
    vector3_up,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.scenery.atmosphere import Atmosphere  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

__pragma__("noskip")

DEG = math.pi / 180


def sun_direction(elevation_deg: float, azimuth_deg: float) -> Any:
    """Direction the sunlight travels, from its elevation and azimuth (0 = from straight ahead)."""
    el = elevation_deg * DEG
    az = azimuth_deg * DEG
    return vector3(
        -math.cos(el) * math.sin(az),
        -math.sin(el),
        -math.cos(el) * math.cos(az),
    )


class SceneryLights:
    """The lights of a scenery scene: the sun (or the moon) and the sky's ambient light."""

    def __init__(self, sun: Any, ambient: Any) -> None:
        self.sun = sun
        self.ambient = ambient


def light_scenery(scene: Any, atmosphere: Atmosphere) -> SceneryLights:
    """Creates the sun and the ambient light, then lights the scene as `atmosphere` says."""
    scene.fogMode = fog_mode_linear()
    scene.clearColor = color4(0, 0, 0, 1)
    scene.fogColor = color3(0, 0, 0)
    ambient = new_hemispheric_light("scenery-ambient", vector3_up(), scene)
    ambient.specular = color3_black()
    sun = new_directional_light("scenery-sun", vector3_down(), scene)
    lights = SceneryLights(sun, ambient)
    apply_atmosphere(scene, lights, atmosphere)
    return lights


def apply_atmosphere(scene: Any, lights: SceneryLights, atmosphere: Atmosphere) -> None:
    """Lights the scene as `atmosphere` says (P08-R04): haze (clear colour and linear fog), sky and
    ground ambient light, and the sun's direction, colour and strength. Called every frame."""
    haze = atmosphere.sky.haze
    scene.clearColor.set(haze[0], haze[1], haze[2], 1)
    scene.fogColor.set(haze[0], haze[1], haze[2])
    scene.fogStart = atmosphere.fog.start
    scene.fogEnd = atmosphere.fog.end
    ambient = lights.ambient
    sun = lights.sun
    sky = atmosphere.ambient.sky
    ground = atmosphere.ambient.ground
    ambient.diffuse.set(sky[0], sky[1], sky[2])
    ambient.groundColor.set(ground[0], ground[1], ground[2])
    ambient.intensity = atmosphere.ambient.intensity
    s = atmosphere.sun
    sun.direction = sun_direction(s.elevation_deg, s.azimuth_deg)
    sun.diffuse.set(s.color[0], s.color[1], s.color[2])
    sun.specular.set(s.color[0], s.color[1], s.color[2])
    sun.intensity = s.intensity


def snapped_light_position(direction: Any, target: Any, distance: float, texel: float) -> Any:
    """Where to put a directional light of direction `direction` that looks at `target` from
    `distance` away, with `target` moved to the nearest whole shadow texel (`texel` world units)
    across the light: the shadow map then slides by whole texels as the view scrolls, and the
    shadows stay still instead of shimmering (phase 4 review)."""
    forward = direction.normalizeToNew()
    right = vector3_cross(vector3_up(), forward).normalize()
    up = vector3_cross(forward, right)

    def snap(axis: Any) -> Any:
        along = vector3_dot(target, axis)
        return axis.scale(math.floor(along / texel + 0.5) * texel - along)

    snapped = target.add(snap(right)).add(snap(up))
    return snapped.subtract(forward.scale(distance))
