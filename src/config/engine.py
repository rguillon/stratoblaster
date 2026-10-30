"""Engine-wide tunables (ENG-17), ported from `config/engine.ts`.

Game-specific values go in `src/game/config/`.
"""


class E2eConfig:
    """e2e builds only (ENG-52): pixels drawn per screen pixel, across, and whether to antialias.

    The e2e tests check the game's state, not its pixels, and software WebGL (CI) pays per pixel:
    a quarter of the pixels, without multisampling, makes their frames several times cheaper.
    """

    def __init__(self, render_scale: float, antialias: bool) -> None:
        self.render_scale = render_scale
        self.antialias = antialias


class PerfOverlay:
    """Debug perf overlay (P13-R01, ENG-111): refreshed every `refresh` s, toggled with `key`."""

    def __init__(self, refresh: float, key: str) -> None:
        self.refresh = refresh
        self.key = key


class EngineConfig:
    """The engine-wide tunables, in the order of `ENGINE_CONFIG`."""

    def __init__(
        self,
        simulation_hz: float,
        max_steps_per_frame: float,
        max_device_pixel_ratio: float,
        e2e: E2eConfig,
        long_frame_ms: float,
        perf_overlay: PerfOverlay,
    ) -> None:
        # Fixed simulation rate in Hz (ENG-100).
        self.simulation_hz = simulation_hz
        # Maximum simulation steps per rendered frame, to avoid a spiral of death after a stall.
        self.max_steps_per_frame = max_steps_per_frame
        # Device pixel ratio cap (ENG-110).
        self.max_device_pixel_ratio = max_device_pixel_ratio
        self.e2e = e2e
        # P13-R01 `long_frame_ms`: a frame whose work takes longer counts as a long frame.
        self.long_frame_ms = long_frame_ms
        self.perf_overlay = perf_overlay


ENGINE_CONFIG = EngineConfig(
    60,
    5,
    2,
    E2eConfig(0.5, False),
    50,
    PerfOverlay(0.25, "F3"),
)
