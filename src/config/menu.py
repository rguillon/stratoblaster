# Copyright (c) 2026 Renaud Guillon
"""Tunables of the engine's menu screens (phase 01).

Game-specific values are in `src/game/config/`.
"""


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
        environment: Environment,
        glow: GlowSettings,
    ) -> None:
        # `menu_transition_duration`: screen fade, input ignored meanwhile (UI-FLOW-08).
        self.transition_seconds = transition_seconds
        # `cookie_max_age`: lifetime of the cookies the menus save (high score, volumes).
        self.cookie_max_age_days = cookie_max_age_days
        # Longest frame time fed to animations, so a stall does not make things jump.
        self.max_frame_seconds = max_frame_seconds
        self.environment = environment
        self.glow = glow


MENU_CONFIG = MenuConfig(
    0.25,
    365,
    0.1,
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
