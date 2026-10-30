"""Tunables of the engine's menu screens (phase 01), ported from `config/menu.ts`.

Game-specific values are in `src/game/config/`.
"""

import math


class ShipSelectCamera:
    """The camera of the ship select screen."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        alpha: float,
        beta: float,
        horizontal_fov: float,
        framing_margin: float,
        target_y: float,
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.horizontal_fov = horizontal_fov
        # Extra room around the row of ships (1 = ships touch the screen edges).
        self.framing_margin = framing_margin
        # Camera target height: positive values move the ships down the screen.
        self.target_y = target_y


class ShipSelectLights:
    """The lights of the ship select screen."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        ambient_intensity: float,
        spot_intensity: float,
        spot_direction: tuple[float, float, float],
        rim_intensity: float,
        rim_direction: tuple[float, float, float],
    ) -> None:
        self.ambient_intensity = ambient_intensity
        # Key light on the highlighted ship only, so the others look dimmed.
        self.spot_intensity = spot_intensity
        self.spot_direction = spot_direction
        self.rim_intensity = rim_intensity
        self.rim_direction = rim_direction


class ShipSelectRing:
    """Neon ring under the highlighted ship."""

    def __init__(
        self,
        diameter: float,
        thickness: float,
        y: float,
        color: tuple[float, float, float],
    ) -> None:
        self.diameter = diameter
        self.thickness = thickness
        self.y = y
        self.color = color


class ShipSelect:
    """The ship select screen's tunables."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        spacing: float,
        rotation_speed_rad_per_sec: float,
        highlight_scale: float,
        dim_scale: float,
        scale_ease_per_sec: float,
        camera: ShipSelectCamera,
        lights: ShipSelectLights,
        ring: ShipSelectRing,
    ) -> None:
        # Distance between two ship centres, in world units.
        self.spacing = spacing
        # `ship_select_rotation_speed`.
        self.rotation_speed_rad_per_sec = rotation_speed_rad_per_sec
        # Scale of the highlighted ship and of the others (P01-R06).
        self.highlight_scale = highlight_scale
        self.dim_scale = dim_scale
        # How fast the scales ease towards their target (1/s).
        self.scale_ease_per_sec = scale_ease_per_sec
        self.camera = camera
        self.lights = lights
        self.ring = ring


class EnvironmentStop:
    """One stop of the image-based lighting: a colour at a height (-1 down, 1 up)."""

    def __init__(self, at: float, color: tuple[float, float, float]) -> None:
        self.at = at
        self.color = color


class Environment:
    """Image-based lighting of the menu scenes (procedural, no download)."""

    def __init__(self, cube_size: float, intensity: float, stops: list[EnvironmentStop]) -> None:
        self.cube_size = cube_size
        self.intensity = intensity
        self.stops = stops


class GlowSettings:
    """The glow post-process."""

    def __init__(self, intensity: float, blur_kernel_size: float) -> None:
        self.intensity = intensity
        self.blur_kernel_size = blur_kernel_size


class MenuConfig:
    """The menu screens' tunables, in the order of `MENU_CONFIG`."""

    def __init__(
        self,
        transition_seconds: float,
        cookie_max_age_days: float,
        max_frame_seconds: float,
        ship_select: ShipSelect,
        environment: Environment,
        glow: GlowSettings,
    ) -> None:
        # `menu_transition_duration`: screen fade, input ignored meanwhile (P01-R15).
        self.transition_seconds = transition_seconds
        # `cookie_max_age`: lifetime of the high score and last ship cookies.
        self.cookie_max_age_days = cookie_max_age_days
        # Longest frame time fed to animations, so a stall does not make things jump.
        self.max_frame_seconds = max_frame_seconds
        self.ship_select = ship_select
        self.environment = environment
        self.glow = glow


MENU_CONFIG = MenuConfig(
    0.25,
    365,
    0.1,
    ShipSelect(
        7,
        0.5,
        1.2,
        0.7,
        10,
        ShipSelectCamera(-math.pi / 2, 1.2, 1.0, 1.05, -1.2),
        ShipSelectLights(0.25, 2.6, (-0.4, -1, 0.6), 0.8, (0.6, -0.3, -1)),
        ShipSelectRing(6.4, 0.12, -1.3, (1, 0.92, 0.05)),
    ),
    Environment(
        64,
        1.0,
        [
            EnvironmentStop(-1, (0.1, 0.06, 0.2)),
            EnvironmentStop(-0.1, (0.3, 0.2, 0.45)),
            EnvironmentStop(0, (1, 0.65, 0.85)),
            EnvironmentStop(0.15, (0.6, 0.65, 1)),
            EnvironmentStop(1, (0.9, 0.9, 1)),
        ],
    ),
    GlowSettings(0.8, 48),
)
