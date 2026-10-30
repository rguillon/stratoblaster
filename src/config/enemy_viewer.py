"""Tunables of the enemies debug page (`enemies/`, P05-R11), ported from `config/enemy-viewer.ts`.

Logical pixels, Y up, origin at the bottom left of the playfield; times in seconds.
"""

import math

from config.scenery_stage import SCENERY_STAGE_CONFIG, SceneryStageConfig


class ShipStart:
    """Where the player ship starts."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class ViewerShipMargin:
    """How close to the visible edges the player ship may fly."""

    def __init__(self, side: float, bottom: float, top: float) -> None:
        self.side = side
        self.bottom = bottom
        self.top = top


class CloseUpView:
    """Model and wireframe views (phase 5 review: like `player_ship/`, close up): the dark grey
    background (lighter than `player_ship/`'s, for the dark hulls to stand out), turns per second,
    share of the screen width the model fills, how far the wheel zooms in and out, and the camera
    angles: from -Z (behind the model), 45 degrees above it, as the enemies are flat ships mostly
    seen from above."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        clear_color: tuple[float, float, float, float],
        wire_color: tuple[float, float, float],
        hitbox_color: tuple[float, float, float],
        hitbox_segments: float,
        body_materials: list[str],
        spin_rad_per_sec: float,
        fill: float,
        zoom: tuple[float, float],
        alpha: float,
        beta: float,
    ) -> None:
        self.clear_color = clear_color
        # Wireframe view: the hull's line colour, and the hit circle's colour and segments.
        self.wire_color = wire_color
        self.hitbox_color = hitbox_color
        self.hitbox_segments = hitbox_segments
        # The materials of the meshes drawn as wires: the body's metal and flesh (P16-R01).
        self.body_materials = body_materials
        self.spin_rad_per_sec = spin_rad_per_sec
        self.fill = fill
        self.zoom = zoom
        self.alpha = alpha
        self.beta = beta


class EnemyViewerStats:
    """Debug tile: FPS averaged over `fps_window` s, text refreshed every `refresh` s."""

    def __init__(self, fps_window: float, refresh: float) -> None:
        self.fps_window = fps_window
        self.refresh = refresh


class EnemyViewerConfig:
    """The enemies page's tunables, in the order of `ENEMY_VIEWER_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        step_hz: float,
        max_steps_per_frame: float,
        max_frame_seconds: float,
        environment_cube_size: float,
        stage: SceneryStageConfig,
        ship_start: ShipStart,
        ship_margin: ViewerShipMargin,
        muzzle_inset: float,
        cull_margin: float,
        max_enemy_age: float,
        respawn_delay: float,
        seed: float,
        close_up: CloseUpView,
        stats: EnemyViewerStats,
    ) -> None:
        # Fixed simulation rate (ENG-100) and the most steps run in one frame.
        self.step_hz = step_hz
        self.max_steps_per_frame = max_steps_per_frame
        # Longest frame time used, so a stall does not jump the animations.
        self.max_frame_seconds = max_frame_seconds
        self.environment_cube_size = environment_cube_size
        # The generated ground under the playfield.
        self.stage = stage
        # Where the player ship starts, and how close to the visible edges it may fly.
        self.ship_start = ship_start
        self.ship_margin = ship_margin
        # Player shots leave this far below the tip of the ship's nose (as on `player_shots/`).
        self.muzzle_inset = muzzle_inset
        # Shots and enemies this far outside the playfield are removed.
        self.cull_margin = cull_margin
        # Enemies older than this are removed, whatever they do.
        self.max_enemy_age = max_enemy_age
        # A new group appears this long after the last one has gone.
        self.respawn_delay = respawn_delay
        self.seed = seed
        self.close_up = close_up
        # Debug tile: FPS averaged over `fps_window` s, text refreshed every `refresh` s.
        self.stats = stats


ENEMY_VIEWER_CONFIG = EnemyViewerConfig(
    60,
    5,
    0.1,
    64,
    SCENERY_STAGE_CONFIG,
    ShipStart(240, 90),
    ViewerShipMargin(18, 30, 200),
    3,
    80,
    40,
    1,
    505,
    CloseUpView(
        (0.2, 0.2, 0.21, 1),
        (0.75, 0.8, 0.85),
        (1, 0.2, 0.2),
        48,
        ["enemy-hull", "enemy-flesh"],
        0.6,
        0.6,
        (0.4, 3),
        -math.pi / 2,
        math.pi / 4,
    ),
    EnemyViewerStats(0.5, 0.25),
)
