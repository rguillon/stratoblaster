"""Tunables of the props viewer page (`props/`, reviewer 2026-10-28), ported from
`config/prop-viewer.ts`. World units.
"""

import math


class PropCamera:
    """The camera of the props viewer."""

    def __init__(self, alpha: float, beta: float, fov: float, framing_margin: float) -> None:
        self.alpha = alpha
        self.beta = beta
        self.fov = fov
        self.framing_margin = framing_margin


class PropLights:
    """The lights of the props viewer."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        ambient_intensity: float,
        key_intensity: float,
        key_direction: tuple[float, float, float],
        fill_intensity: float,
        fill_direction: tuple[float, float, float],
    ) -> None:
        self.ambient_intensity = ambient_intensity
        self.key_intensity = key_intensity
        self.key_direction = key_direction
        # From the other side, so the faces away from the key light are not black.
        self.fill_intensity = fill_intensity
        self.fill_direction = fill_direction


class EnvironmentStop:
    """One stop of the image-based lighting: a colour at a height (-1 down, 1 up)."""

    def __init__(self, at: float, color: tuple[float, float, float]) -> None:
        self.at = at
        self.color = color


class Environment:
    """Image-based lighting of the viewer (procedural, no download)."""

    def __init__(self, cube_size: float, intensity: float, stops: list[EnvironmentStop]) -> None:
        self.cube_size = cube_size
        self.intensity = intensity
        self.stops = stops


class GlowSettings:
    """The glow post-process."""

    def __init__(self, intensity: float, blur_kernel_size: float) -> None:
        self.intensity = intensity
        self.blur_kernel_size = blur_kernel_size


class Ground:
    """Ground under the grid; `margin` is its margin beyond the props, in tiles."""

    def __init__(self, color: tuple[float, float, float], margin: float) -> None:
        self.color = color
        self.margin = margin


class TileGrid:
    """Lines of the grid of tiles on the ground (phase 15), above the road tiles."""

    def __init__(self, color: tuple[float, float, float], height: float) -> None:
        self.color = color
        self.height = height


class TileDefaults:
    """Grid of tiles when the game names none."""

    def __init__(self, size: float, sidewalk: float) -> None:
        self.size = size
        self.sidewalk = sidewalk


class PropViewerConfig:
    """The props page's tunables, in the order of `PROP_VIEWER_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        gap: float,
        clear_color: tuple[float, float, float, float],
        camera: PropCamera,
        lights: PropLights,
        light_intensity: float,
        environment: Environment,
        glow: GlowSettings,
        ground: Ground,
        grid: TileGrid,
        tile: TileDefaults,
    ) -> None:
        # Room between two props of the grid, beyond the largest footprint of the group.
        self.gap = gap
        self.clear_color = clear_color
        self.camera = camera
        self.lights = lights
        # Strength of the self-lit parts (windows, lamps, headlights).
        self.light_intensity = light_intensity
        self.environment = environment
        self.glow = glow
        self.ground = ground
        self.grid = grid
        self.tile = tile


PROP_VIEWER_CONFIG = PropViewerConfig(
    6,
    (0.12, 0.1, 0.18, 1),
    PropCamera(-math.pi / 2, 1, 0.8, 1.15),
    PropLights(1, 1.9, (-0.4, -1, 0.6), 0.9, (0.5, -0.6, -0.7)),
    1.2,
    Environment(
        64,
        1.2,
        [
            EnvironmentStop(-1, (0.06, 0.05, 0.08)),
            EnvironmentStop(0, (0.5, 0.5, 0.6)),
            EnvironmentStop(1, (0.85, 0.9, 1)),
        ],
    ),
    GlowSettings(0.6, 32),
    Ground((0.26, 0.26, 0.31), 1),
    TileGrid((0.45, 0.5, 0.65), 0.3),
    TileDefaults(10, 2),
)
