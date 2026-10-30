"""Image-based lighting, tone mapping and glow for a scene (ported from
`render/environment/showcase-environment.visual.ts`).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    babylon_constant,
    image_processing_tone_mapping_aces,
    is_raw_cube_texture,
    new_glow_layer,
    new_raw_cube_texture,
    new_weak_map,
    update_raw_cube_texture,
    weak_map_get,
    weak_map_set,
)
from render.environment.gradient_cube import build_gradient_cube_faces

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from render.environment.gradient_cube import GradientStop  # noqa: E402

__pragma__("noskip")


class ShowcaseGlow:
    """Glow settings: `intensity`, `blur_kernel_size`, and optionally the resolution of the glow
    image as a share of the screen's (`ratio`, Babylon's 0.5 when None) and its samples per pixel
    (`samples`, Babylon's 1 when None)."""

    def __init__(
        self,
        intensity: float,
        blur_kernel_size: float,
        ratio: float | None = None,
        samples: int | None = None,
    ) -> None:
        self.intensity = intensity
        self.blur_kernel_size = blur_kernel_size
        self.ratio = ratio
        self.samples = samples


class ShowcaseEnvironmentOptions:
    """Look settings for `apply_showcase_environment`."""

    def __init__(
        self,
        cube_size: int,
        intensity: float,
        stops: list[GradientStop],
        glow: ShowcaseGlow,
    ) -> None:
        self.cube_size = cube_size
        self.intensity = intensity
        self.stops = stops
        self.glow = glow


def apply_showcase_environment(scene: Any, options: ShowcaseEnvironmentOptions) -> Any:
    """Gives `scene` image-based lighting from a procedural sky gradient (no asset download),
    ACES tone mapping and a glow layer for emissive parts (ENG-103). Returns the glow layer."""
    faces = build_gradient_cube_faces(options.cube_size, options.stops)
    scene.environmentTexture = new_raw_cube_texture(
        scene,
        faces,
        options.cube_size,
        babylon_constant("TEXTUREFORMAT_RGBA"),
        babylon_constant("TEXTURETYPE_UNSIGNED_BYTE"),
        True,
    )
    scene.environmentIntensity = options.intensity
    scene.imageProcessingConfiguration.toneMappingEnabled = True
    scene.imageProcessingConfiguration.toneMappingType = image_processing_tone_mapping_aces()
    glow = options.glow
    layer = new_glow_layer("glow", scene, glow.blur_kernel_size, glow.ratio, glow.samples)
    layer.intensity = glow.intensity
    return layer


# The sky key of each scene the last time its cube was built (P08-R04).
LAST_SKY = new_weak_map()


def _sky_key(stops: list[GradientStop]) -> str:
    parts: list[str] = []
    for stop in stops:
        channels = [str(math.floor(c * 255 + 0.5)) for c in stop.color]
        parts.append(",".join(channels))
    return ";".join(parts)


def update_sky_environment(
    scene: Any,
    cube_size: int,
    stops: list[GradientStop],
    intensity: float,
) -> None:
    """Gives the scene's sky lighting the gradient `stops` and `intensity` (P08-R04: they follow
    the time of day). The cube is only rebuilt when the gradient changed since the last call."""
    scene.environmentIntensity = intensity
    texture = scene.environmentTexture
    key = _sky_key(stops)
    if not is_raw_cube_texture(texture) or weak_map_get(LAST_SKY, scene) == key:
        return
    weak_map_set(LAST_SKY, scene, key)
    update_raw_cube_texture(
        texture,
        build_gradient_cube_faces(cube_size, stops),
        babylon_constant("TEXTUREFORMAT_RGBA"),
        babylon_constant("TEXTURETYPE_UNSIGNED_BYTE"),
        True,
    )
