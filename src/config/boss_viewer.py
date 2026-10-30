"""Tunables of the bosses debug page (`bosses/`, P07-R09), ported from `config/boss-viewer.ts`.

Logical pixels, Y up, origin at the bottom left of the playfield; times in seconds.
"""

from config.game_play import GAME_PLAY_CONFIG, ShipMargin
from config.scenery_stage import SceneryStageConfig


class ShipStart:
    """Where the player ship starts."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class BossCircles:
    """Wireframe view: colours of the core's circle, of the parts that shield it, of the others."""

    def __init__(
        self,
        core: tuple[float, float, float],
        shield: tuple[float, float, float],
        part: tuple[float, float, float],
    ) -> None:
        self.core = core
        self.shield = shield
        self.part = part


class BossViewerStats:
    """Debug tile: FPS averaged over `fps_window` s, text refreshed every `refresh` s."""

    def __init__(self, fps_window: float, refresh: float) -> None:
        self.fps_window = fps_window
        self.refresh = refresh


class BossViewerConfig:
    """The bosses page's tunables, in the order of `BOSS_VIEWER_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        step_hz: float,
        max_steps_per_frame: float,
        max_frame_seconds: float,
        environment_cube_size: float,
        stage: SceneryStageConfig,
        ship_start: ShipStart,
        ship_margin: ShipMargin,
        muzzle_inset: float,
        cull_margin: float,
        max_enemy_age: float,
        respawn_delay: float,
        seed: float,
        circles: BossCircles,
        stats: BossViewerStats,
    ) -> None:
        # Fixed simulation rate (ENG-100) and the most steps run in one frame.
        self.step_hz = step_hz
        self.max_steps_per_frame = max_steps_per_frame
        # Longest frame time used, so a stall does not jump the animations.
        self.max_frame_seconds = max_frame_seconds
        self.environment_cube_size = environment_cube_size
        # The levels' scenery, as on the game screen.
        self.stage = stage
        # Where the player ship starts, and how close to the visible edges it may fly.
        self.ship_start = ship_start
        self.ship_margin = ship_margin
        # Player shots leave this far below the tip of the ship's nose (as on `enemies/`).
        self.muzzle_inset = muzzle_inset
        # Shots and enemies this far outside the playfield are removed.
        self.cull_margin = cull_margin
        # Enemies the bosses launch are removed this old, whatever they do.
        self.max_enemy_age = max_enemy_age
        # A boss comes again this long after the last one blew up.
        self.respawn_delay = respawn_delay
        self.seed = seed
        self.circles = circles
        # Debug tile: FPS averaged over `fps_window` s, text refreshed every `refresh` s.
        self.stats = stats


BOSS_VIEWER_CONFIG = BossViewerConfig(
    60,
    5,
    0.1,
    64,
    GAME_PLAY_CONFIG.stage,
    ShipStart(240, 90),
    GAME_PLAY_CONFIG.ship_margin,
    3,
    80,
    40,
    1.5,
    707,
    BossCircles((1, 0.2, 0.2), (1, 0.9, 0.1), (0.1, 0.9, 1)),
    BossViewerStats(0.5, 0.25),
)
