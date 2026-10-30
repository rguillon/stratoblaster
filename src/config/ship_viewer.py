"""Tunables of the player ship viewer page (`player_ship/`), ported from `config/ship-viewer.ts`."""

import math


class ShipCamera:
    """The camera of the ship viewer."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        alpha: float,
        beta: float,
        horizontal_fov: float,
        framing_margin: float,
        min_zoom_factor: float,
        max_zoom_factor: float,
    ) -> None:
        # Horizontal angle: -pi/2 looks from -Z towards +Z.
        self.alpha = alpha
        # Angle from the vertical axis.
        self.beta = beta
        # Fixed horizontal field of view, so the 3 ships always fit the width.
        self.horizontal_fov = horizontal_fov
        # Extra room around the row of ships (1 = ships touch the screen edges).
        self.framing_margin = framing_margin
        self.min_zoom_factor = min_zoom_factor
        self.max_zoom_factor = max_zoom_factor


class ShipLights:
    """The lights of the ship viewer."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        ambient_intensity: float,
        key_intensity: float,
        key_direction: tuple[float, float, float],
        rim_intensity: float,
        rim_direction: tuple[float, float, float],
    ) -> None:
        self.ambient_intensity = ambient_intensity
        self.key_intensity = key_intensity
        self.key_direction = key_direction
        self.rim_intensity = rim_intensity
        self.rim_direction = rim_direction


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


class ShipViewerConfig:
    """The ship viewer's tunables, in the order of `SHIP_VIEWER_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        spacing: float,
        rotation_speed_rad_per_sec: float,
        clear_color: tuple[float, float, float, float],
        camera: ShipCamera,
        lights: ShipLights,
        environment: Environment,
        glow: GlowSettings,
    ) -> None:
        # Distance between two ship centres, in world units. Must exceed the largest wingspan.
        self.spacing = spacing
        self.rotation_speed_rad_per_sec = rotation_speed_rad_per_sec
        self.clear_color = clear_color
        self.camera = camera
        self.lights = lights
        self.environment = environment
        self.glow = glow


SHIP_VIEWER_CONFIG = ShipViewerConfig(
    8,
    0.6,
    (0.05, 0.02, 0.1, 1),
    ShipCamera(-math.pi / 2, 1.15, 1.0, 1.1, 0.3, 2.5),
    ShipLights(0.35, 2.2, (-0.4, -1, 0.6), 1.2, (0.6, -0.3, -1)),
    Environment(
        64,
        1.1,
        [
            EnvironmentStop(-1, (0.03, 0.02, 0.06)),
            EnvironmentStop(-0.1, (0.12, 0.08, 0.2)),
            EnvironmentStop(0, (0.95, 0.55, 0.85)),
            EnvironmentStop(0.12, (0.45, 0.6, 1)),
            EnvironmentStop(1, (0.85, 0.9, 1)),
        ],
    ),
    GlowSettings(0.9, 48),
)
