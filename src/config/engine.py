# Copyright (c) 2026 Renaud Guillon
"""Engine-wide tunables (ENG-17).

Game-specific values go in `src/game/config/`.
"""


class E2eConfig:
    """e2e builds only (ENG-52, ENG-58, DEV-API-10): pixels drawn per screen pixel, across.

    And whether to antialias.

    The e2e tests check the game's state, not its pixels, and software WebGL (CI) pays per pixel:
    a quarter of the pixels, without multisampling, makes their frames several times cheaper.
    """

    def __init__(self, render_scale: float, antialias: bool) -> None:
        self.render_scale = render_scale
        self.antialias = antialias


class PerfOverlay:
    """Debug perf overlay (DEV-PERF-03, ENG-111): refreshed every `refresh` s, toggled by `key`."""

    def __init__(self, refresh: float, key: str) -> None:
        self.refresh = refresh
        self.key = key


class QualityLevel:
    """A graphics quality level (D-410): what it draws, from the full look down.

    `render_scale`: the share of the pixels drawn across (1: all; 0.5: a quarter of them), on top of
    the fit's (ENG-110). `shadow_filter`: the sun's shadows' filtering, `"medium"` or `"low"`
    (Babylon's PCF qualities).
    """

    def __init__(self, render_scale: float, shadow_filter: str) -> None:
        self.render_scale = render_scale
        self.shadow_filter = shadow_filter


class QualityConfig:
    """Automatic graphics quality (D-410): levels, and when to change level.

    `levels`: from the full look (0) down. While a level plays, frames are judged by windows of
    `window_ms` of frames: a window is slow when its mean frame interval is above `slow_ms` and
    more than `late_share` of its frames are late (longer than `late_factor` times the display's
    frame, the shortest interval seen lately), so a display slower than 60 Hz is not taken for a
    slow machine. A slow window lowers the level by one; then `settle_ms` of frames are not judged.
    After `clean_ms` of windows that are not slow, with frames within `fast_ms` (and, where the GPU
    can be timed, the GPU's and the main thread's work within `headroom_ms`), the level goes up by
    one to try; if the next window is slow, it goes back down and stays there.
    `medium` and `low`: the levels the Graphics quality setting's Medium and Low choices hold.
    A slow window whose main thread's work takes more than `cpu_share` of its frames is the
    processor's, which fewer pixels do not help: the level stays.
    """

    def __init__(
        self,
        levels: list[QualityLevel],
        window_ms: float,
        slow_ms: float,
        late_share: float,
        late_factor: float,
        settle_ms: float,
        clean_ms: float,
        fast_ms: float,
        headroom_ms: float,
        medium: int,
        low: int,
        cpu_share: float,
    ) -> None:
        self.levels = levels
        self.window_ms = window_ms
        self.slow_ms = slow_ms
        self.late_share = late_share
        self.late_factor = late_factor
        self.settle_ms = settle_ms
        self.clean_ms = clean_ms
        self.fast_ms = fast_ms
        self.headroom_ms = headroom_ms
        self.medium = medium
        self.low = low
        self.cpu_share = cpu_share


class EngineConfig:
    """The engine-wide tunables, in the order of `ENGINE_CONFIG`."""

    def __init__(
        self,
        simulation_hz: float,
        max_steps_per_frame: float,
        max_device_pixel_ratio: float,
        max_render_scale: float,
        e2e: E2eConfig,
        long_frame_ms: float,
        perf_overlay: PerfOverlay,
        quality: QualityConfig,
    ) -> None:
        # Fixed simulation rate in Hz (ENG-100).
        self.simulation_hz = simulation_hz
        # Maximum simulation steps per rendered frame, to avoid a spiral of death after a stall.
        self.max_steps_per_frame = max_steps_per_frame
        # Device pixel ratio cap (ENG-110).
        self.max_device_pixel_ratio = max_device_pixel_ratio
        # D-250, ENG-110: the most pixels drawn per logical pixel, across (the canvas never
        # renders bigger than the logical screen times this, whatever the window and the
        # device pixel ratio: a 4K panel is not drawn at 4K).
        self.max_render_scale = max_render_scale
        self.e2e = e2e
        # PERF-01 `long_frame_ms`: a frame whose work takes longer counts as a long frame.
        self.long_frame_ms = long_frame_ms
        self.perf_overlay = perf_overlay
        # D-410: the graphics quality levels, and when the game changes level by itself.
        self.quality = quality


ENGINE_CONFIG = EngineConfig(
    60,
    5,
    2,
    1.5,
    E2eConfig(0.5, False),
    50,
    PerfOverlay(0.25, "F3"),
    QualityConfig(
        [
            QualityLevel(1.0, "medium"),
            QualityLevel(0.8, "medium"),
            QualityLevel(0.67, "low"),
            QualityLevel(0.57, "low"),
            QualityLevel(0.5, "low"),
        ],
        2000,
        1000 / 55,
        0.1,
        1.5,
        1500,
        10000,
        17.5,
        9,
        2,
        4,
        0.8,
    ),
)
