"""Tunables of the player shots viewer page (`player_shots/`, P03-R10), ported from
`config/shot-viewer.ts`.

Positions in logical pixels, Y up, origin at the bottom left of the playfield.
"""


class ShotGrid:
    """Faint reference grid, to judge angles and speeds; `depth` puts it behind everything."""

    def __init__(self, cell: float, depth: float, color: tuple[float, float, float]) -> None:
        self.cell = cell
        self.depth = depth
        self.color = color


class ShotGuides:
    """Lines along each stream of the selected level (toggled with G)."""

    def __init__(self, length: float, color: tuple[float, float, float]) -> None:
        # `length`: an attribute named `length` cannot be assigned under Transcrypt, so it is
        # `length_` (see ENG-150..154).
        self.length_ = length
        self.color = color


class TargetAnchor:
    """Where a dummy target hangs, in logical pixels."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class TargetRing:
    """The ring of a dummy target: its thickness, and its colour alive and destroyed."""

    def __init__(
        self,
        thickness: float,
        color: tuple[float, float, float],
        dead_color: tuple[float, float, float],
    ) -> None:
        self.thickness = thickness
        self.color = color
        self.dead_color = dead_color


class TargetHealthBar:
    """The health bar above a dummy target."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        width: float,
        height: float,
        gap: float,
        color: tuple[float, float, float],
        back_color: tuple[float, float, float],
    ) -> None:
        self.width = width
        self.height = height
        self.gap = gap
        self.color = color
        self.back_color = back_color


class ShotTargets:
    """Dummy targets. A column above the ship shows the laser going through ships; the side
    targets pull the homing missiles sideways. They sway together and come back after
    `respawn_seconds` once destroyed."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        radius: float,
        max_health: float,
        anchors: list[TargetAnchor],
        sway_amplitude: float,
        sway_hz: float,
        respawn_seconds: float,
        ring: TargetRing,
        health_bar: TargetHealthBar,
    ) -> None:
        self.radius = radius
        self.max_health = max_health
        self.anchors = anchors
        self.sway_amplitude = sway_amplitude
        self.sway_hz = sway_hz
        self.respawn_seconds = respawn_seconds
        self.ring = ring
        self.health_bar = health_bar


class ShotLights:
    """The lights of the shot viewer."""

    def __init__(
        self,
        ambient_intensity: float,
        key_intensity: float,
        key_direction: tuple[float, float, float],
    ) -> None:
        self.ambient_intensity = ambient_intensity
        self.key_intensity = key_intensity
        self.key_direction = key_direction


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


class ShotViewerStats:
    """Debug tile (phase 3 review): FPS averaged over `fps_window` s, text refreshed every
    `refresh` s."""

    def __init__(self, fps_window: float, refresh: float) -> None:
        self.fps_window = fps_window
        self.refresh = refresh


class ShotViewerConfig:
    """The shots page's tunables, in the order of `SHOT_VIEWER_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        step_hz: float,
        max_steps_per_frame: float,
        ship_y: float,
        muzzle_inset: float,
        cull_margin: float,
        clear_color: tuple[float, float, float, float],
        grid: ShotGrid,
        guides: ShotGuides,
        targets: ShotTargets,
        damage_rate_window: float,
        stats: ShotViewerStats,
        lights: ShotLights,
        environment: Environment,
        glow: GlowSettings,
    ) -> None:
        # Fixed simulation rate (ENG-100) and the most steps run in one frame.
        self.step_hz = step_hz
        self.max_steps_per_frame = max_steps_per_frame
        # Ship centre height.
        self.ship_y = ship_y
        # Shots from the muzzle start this far below the tip of the ship's nose, measured on each
        # ship's model (phase 3 review: bullets started ahead of the ship).
        self.muzzle_inset = muzzle_inset
        # Shots this far outside the playfield are removed.
        self.cull_margin = cull_margin
        self.clear_color = clear_color
        self.grid = grid
        self.guides = guides
        self.targets = targets
        # Window over which the damage rate is measured, in seconds.
        self.damage_rate_window = damage_rate_window
        self.stats = stats
        self.lights = lights
        self.environment = environment
        self.glow = glow


SHOT_VIEWER_CONFIG = ShotViewerConfig(
    60,
    5,
    80,
    3,
    40,
    (0.02, 0.02, 0.05, 1),
    ShotGrid(40, 200, (0.1, 0.12, 0.2)),
    ShotGuides(900, (0.55, 0.45, 0.1)),
    ShotTargets(
        20,
        300,
        [
            TargetAnchor(240, 300),
            TargetAnchor(240, 380),
            TargetAnchor(240, 460),
            TargetAnchor(240, 540),
            TargetAnchor(90, 470),
            TargetAnchor(390, 470),
        ],
        40,
        0.12,
        1,
        TargetRing(3, (0.85, 0.2, 0.3), (0.25, 0.25, 0.3)),
        TargetHealthBar(36, 4, 8, (0.3, 1, 0.5), (0.15, 0.15, 0.2)),
    ),
    1,
    ShotViewerStats(0.5, 0.25),
    ShotLights(0.6, 2, (0.3, 0.5, 1)),
    Environment(
        64,
        1,
        [
            EnvironmentStop(-1, (0.03, 0.02, 0.06)),
            EnvironmentStop(0, (0.4, 0.45, 0.6)),
            EnvironmentStop(1, (0.85, 0.9, 1)),
        ],
    ),
    GlowSettings(0.35, 24),
)
