"""Tunables of the game screen (P06-R02, R03, R09), ported from `config/game-play.ts`.

Logical pixels, Y up, origin at the bottom left of the playfield; times in seconds.
"""

from config.scenery_stage import SCENERY_STAGE_CONFIG, SceneryStageConfig


class ShipMargin:
    """How close to the edges of what the camera shows the ship may fly (and its bottom margin,
    which keeps it above the HUD's bar, 48 px high: reviewer, 2026-10-28)."""

    def __init__(self, side: float, bottom: float, top: float) -> None:
        self.side = side
        self.bottom = bottom
        self.top = top


class ShipRoll:
    """The ship banks as it moves sideways (phase 6 review): up to `max_deg` at full sideways
    speed, easing to its target at `ease_per_sec` (share of the gap closed per second)."""

    def __init__(self, max_deg: float, ease_per_sec: float) -> None:
        self.max_deg = max_deg
        self.ease_per_sec = ease_per_sec


class ShipDamage:
    """Hits on the player (phase 6 review): the ship blinks `blink_hz` times a second while
    invincible (GD-22); a hit makes a spark of radius `hit_spark`, a lost life a blast of radius
    `ship_blast`; the "Game over" overlay shows `game_over_delay` after the last life is lost."""

    def __init__(
        self, blink_hz: float, hit_spark: float, ship_blast: float, game_over_delay: float
    ) -> None:
        self.blink_hz = blink_hz
        self.hit_spark = hit_spark
        self.ship_blast = ship_blast
        self.game_over_delay = game_over_delay


class ShipJourney:
    """The ship's arrival and departure (reviewer, 2026-10-28): it rises from `below` under the
    bottom edge to its start in `arrive_seconds`; once the final boss is destroyed the player keeps
    it `free_seconds`, then it flies off the top, from `leave_speed` px/s, accelerating."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        arrive_seconds: float,
        below: float,
        free_seconds: float,
        leave_speed: float,
        leave_acceleration: float,
        above: float,
    ) -> None:
        self.arrive_seconds = arrive_seconds
        self.below = below
        self.free_seconds = free_seconds
        self.leave_speed = leave_speed
        self.leave_acceleration = leave_acceleration
        self.above = above


class DebugOptions:
    """Debug options (P06-R09): F fast-forwards x4, the arrows jump `seek_step` s."""

    def __init__(self, fast_forward: float, seek_step: float) -> None:
        self.fast_forward = fast_forward
        self.seek_step = seek_step


class DebugStats:
    """Debug tile: FPS averaged over `fps_window` s, text refreshed every `refresh` s."""

    def __init__(self, fps_window: float, refresh: float) -> None:
        self.fps_window = fps_window
        self.refresh = refresh


class ReadabilityProbe:
    """Phase 14 (P14-R08): the readability probe measures round the ship and round a player shot
    `ship_radius` / `shot_radius` (logical pixels; enemies and bullets use their hit radius), only
    objects `margin` inside the view, and only player shots `shot_ahead` ahead of the ship."""

    def __init__(
        self, ship_radius: float, shot_radius: float, margin: float, shot_ahead: float
    ) -> None:
        self.ship_radius = ship_radius
        self.shot_radius = shot_radius
        self.margin = margin
        self.shot_ahead = shot_ahead


class GamePlayConfig:
    """The game screen's tunables, in the order of `GAME_PLAY_CONFIG`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        step_hz: float,
        max_steps_per_frame: float,
        max_frame_seconds: float,
        environment_cube_size: float,
        stage: SceneryStageConfig,
        ship_start_y: float,
        ship_margin: ShipMargin,
        roll: ShipRoll,
        damage: ShipDamage,
        muzzle_inset: float,
        cull_margin: float,
        max_enemy_age: float,
        end_wait: float,
        journey: ShipJourney,
        complete_delay: float,
        seed: float,
        debug: DebugOptions,
        stats: DebugStats,
        readability_probe: ReadabilityProbe,
    ) -> None:
        # Fixed simulation rate (ENG-100) and the most steps run in one frame: enough for the
        # longest frame (`max_frame_seconds`) fast-forwarded x4.
        self.step_hz = step_hz
        self.max_steps_per_frame = max_steps_per_frame
        # Longest frame time used, so a stall does not jump the game.
        self.max_frame_seconds = max_frame_seconds
        self.environment_cube_size = environment_cube_size
        # The generated ground under the playfield.
        self.stage = stage
        # Where the ship starts (from the middle of the bottom edge).
        self.ship_start_y = ship_start_y
        self.ship_margin = ship_margin
        self.roll = roll
        self.damage = damage
        # Player shots leave this far below the tip of the ship's nose.
        self.muzzle_inset = muzzle_inset
        # Shots and enemies this far outside the playfield are removed.
        self.cull_margin = cull_margin
        # Enemies older than this are removed, whatever they do.
        self.max_enemy_age = max_enemy_age
        # `level_end_wait`: the longest wait for the last enemies after the scroll ends (P06-R03).
        self.end_wait = end_wait
        self.journey = journey
        # Input is ignored this long after the "Level complete" overlay shows, so a held fire key
        # does not skip it.
        self.complete_delay = complete_delay
        # Seed of the enemies' random choices: a level plays the same every time (P06-R07).
        self.seed = seed
        self.debug = debug
        # Debug tile: FPS averaged over `fps_window` s, text refreshed every `refresh` s.
        self.stats = stats
        self.readability_probe = readability_probe


GAME_PLAY_CONFIG = GamePlayConfig(
    60,
    25,
    0.1,
    64,
    SCENERY_STAGE_CONFIG,
    90,
    ShipMargin(18, 78, 200),
    ShipRoll(35, 8),
    ShipDamage(10, 6, 16, 2),
    3,
    80,
    40,
    10,
    ShipJourney(1.6, 160, 3, 120, 900, 120),
    1,
    606,
    DebugOptions(4, 10),
    DebugStats(0.5, 0.25),
    ReadabilityProbe(14, 5, 12, 60),
)
