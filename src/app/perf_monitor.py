"""Times the work of each frame and of each level start (P13-R01), ported from
`app/perf-monitor.ts`: how many frames are longer than `long_frame_ms`, the longest one, and the
last loading time. `now` is the clock, in milliseconds (`performance.now` in the browser).

`perf_overlay` shows the numbers on a debug overlay (dev and e2e builds only): with no
`perf_parent` it returns the ticker unchanged and does nothing.
"""

from org.transcrypt.stubs.browser import __pragma__

from app.page_audio import Ticker
from config.engine import ENGINE_CONFIG
from ui.perf_overlay import PerfNumbers, PerfOverlay

__pragma__("skip")
from typing import Any  # noqa: E402

from ui.screens.elements import MenuDocument  # noqa: E402

__pragma__("noskip")


class PerfMonitor:
    """Frame and level loading times (see the module doc)."""

    def __init__(self, long_frame_ms: float, now: Any) -> None:
        self._long_frame_ms = long_frame_ms
        self._now = now
        self._long_frames = 0
        self._longest_frame = 0.0
        self._frames = 0
        self._last_load: float | None = None
        self._longest_load_step: float | None = None
        self._loading_step = 0.0
        self._frame_start: float | None = None
        self._load_start: float | None = None
        # Frames left to skip before counting again (a level's first second, P13-R04).
        self._skip: float = 0

    @property
    def numbers(self) -> PerfNumbers:
        return PerfNumbers(
            self._long_frames,
            self._longest_frame,
            self._frames,
            self._last_load,
            self._longest_load_step,
        )

    @property
    def loading(self) -> bool:
        """Whether a level is loading (between `load_started` and `load_finished`)."""
        return self._load_start is not None

    def frame_started(self) -> None:
        """Starts timing a frame."""
        self._frame_start = self._now()

    def frame_ended(self) -> None:
        """Ends the frame started last; it counts unless skipped or part of a level loading."""
        if self._frame_start is None:
            return
        time = self._now() - self._frame_start
        self._frame_start = None
        if self.loading:
            self._loading_step = max(self._loading_step, time)
            return
        if self._skip > 0:
            self._skip = self._skip - 1
            return
        self._frames = self._frames + 1
        self._longest_frame = max(self._longest_frame, time)
        if time > self._long_frame_ms:
            self._long_frames = self._long_frames + 1

    def load_started(self) -> None:
        """A level was confirmed: its loading starts now."""
        # The frame the level was confirmed in is part of its loading.
        start = self._frame_start
        self._load_start = start if start is not None else self._now()
        self._loading_step = 0.0

    def load_finished(self, skip_frames: float = 0) -> None:
        """The level's first frame was drawn: records the loading time and resets the frame
        counts, which then skip the next `skip_frames` frames.
        """
        if self._load_start is None:
            return
        self._last_load = self._now() - self._load_start
        self._load_start = None
        # The frame drawing the level ends after this: it counts as a loading step if longer.
        self._longest_load_step = self._loading_step
        self.reset(skip_frames)

    def reset(self, skip_frames: float = 0) -> None:
        """Clears the frame counts (not the last loading time), skipping the next `skip_frames`."""
        self._long_frames = 0
        self._longest_frame = 0.0
        self._frames = 0
        self._skip = skip_frames


class PerfOverlayHandle:
    """What `perf_overlay` returns: `wrap(ticker)` and `dispose()`."""

    def __init__(self, wrap: Any, dispose: Any) -> None:
        self.wrap = wrap
        self.dispose = dispose


class PerfOverlayOptions:
    """What `perf_overlay` needs from the app's options."""

    def __init__(
        self, doc: MenuDocument, perf_parent: Any | None, keyboard_target: Any | None
    ) -> None:
        self.doc = doc
        # Where the overlay goes; None in production builds.
        self.perf_parent = perf_parent
        self.keyboard_target = keyboard_target


def perf_overlay(options: PerfOverlayOptions, perf: PerfMonitor) -> PerfOverlayHandle:
    """The perf overlay (P13-R01), toggled by its key, refreshed after each frame's simulation."""
    perf_parent = options.perf_parent
    keyboard_target = options.keyboard_target
    if perf_parent is None:
        return PerfOverlayHandle(_unchanged, _nothing)
    overlay = PerfOverlay(options.doc, perf_parent, ENGINE_CONFIG.perf_overlay.refresh)

    def on_key(event: Any) -> None:
        if event.code != ENGINE_CONFIG.perf_overlay.key:
            return
        event.preventDefault()
        overlay.toggle()

    if keyboard_target is not None:
        keyboard_target.addEventListener("keydown", on_key)
    return PerfOverlayHandle(
        _wrapper(overlay, perf),
        _disposer(keyboard_target, on_key, overlay),
    )


def _unchanged(ticker: Ticker) -> Ticker:
    return ticker


def _nothing() -> None:
    return None


def _wrapper(overlay: PerfOverlay, perf: PerfMonitor) -> Any:
    def wrap(ticker: Ticker) -> Ticker:
        def simulate(dt: float) -> None:
            ticker.simulate(dt)
            overlay.update(dt, perf.numbers)

        return Ticker(simulate, ticker.render)

    return wrap


def _disposer(keyboard_target: Any | None, on_key: Any, overlay: PerfOverlay) -> Any:
    def dispose() -> None:
        if keyboard_target is not None:
            keyboard_target.removeEventListener("keydown", on_key)
        overlay.dispose()

    return dispose
