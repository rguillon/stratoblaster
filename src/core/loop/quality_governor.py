# Copyright (c) 2026 Renaud Guillon
"""Choose the graphics quality level from the frames' times (D-410).

Pure: it is told each frame's interval, the main thread's work on it and, where the browser can
time it, the GPU's; it says when the level changes. See `config.engine.QualityConfig` for the
rules: lower the level when frames are late, try a higher one after a long run of quick frames,
and stay down if that try is slow.
"""

from config.engine import QualityConfig


class QualityGovernor:
    """The graphics quality level of a session, moved by the frames' times (D-410).

    `level` is an index into the config's levels (0: the full look). `floor` is the best level it
    may go up to, `ceiling` the lowest it may go down to.
    """

    def __init__(self, config: QualityConfig, level: int) -> None:
        self._config = config
        self.floor = 0
        self.ceiling = len(config.levels) - 1
        self.level = max(self.floor, min(self.ceiling, level))
        # The display's frame, as the shortest interval seen lately (ms); 0 before any frame.
        self._display_ms = 0.0
        self._settle_ms = 0.0
        self._clean_ms = 0.0
        # Whether the last change went up and is still on trial, and whether a try has failed.
        self._trying = False
        self._stay_down = False
        self._reset_window()

    def _reset_window(self) -> None:
        self._sum_ms = 0.0
        self._frames = 0
        self._late = 0
        self._sum_work = 0.0
        self._sum_gpu = 0.0
        self._gpu_frames = 0

    def restart(self) -> None:
        """Forget the frames seen so far (a level starts, or play goes on after a pause)."""
        self._reset_window()
        self._settle_ms = self._config.settle_ms
        self._clean_ms = 0.0

    def sample(self, interval_ms: float, work_ms: float, gpu_ms: float | None) -> bool:
        """Count a frame `interval_ms` after the last one; return whether the level changed."""
        if interval_ms <= 0:
            return False
        if self._display_ms == 0 or interval_ms < self._display_ms:
            self._display_ms = interval_ms
        else:
            # Lets the display's frame grow back slowly (a window moved to a slower display).
            self._display_ms = self._display_ms + (interval_ms - self._display_ms) * 0.001
        if self._settle_ms > 0:
            self._settle_ms -= interval_ms
            return False
        self._sum_ms += interval_ms
        self._frames += 1
        if interval_ms > self._display_ms * self._config.late_factor:
            self._late += 1
        self._sum_work += work_ms
        if gpu_ms is not None:
            self._sum_gpu += gpu_ms
            self._gpu_frames += 1
        if self._sum_ms < self._config.window_ms:
            return False
        changed = self._judge()
        self._reset_window()
        return changed

    def _judge(self) -> bool:
        """Judge the window of frames just ended; return whether the level changed."""
        config = self._config
        mean = self._sum_ms / self._frames
        late = self._late / self._frames
        cpu_bound = self._sum_work / self._frames > mean * config.cpu_share
        if mean > config.slow_ms and late > config.late_share and not cpu_bound:
            return self._step_down()
        quick = mean <= config.fast_ms
        self._clean_ms = self._clean_ms + self._sum_ms if quick else 0.0
        if self._trying:
            # A try holds once it has run as long as it took to earn it, all quick.
            if self._clean_ms >= config.clean_ms:
                self._trying = False
                self._clean_ms = 0.0
            return False
        if self._stay_down or self.level <= self.floor or self._clean_ms < config.clean_ms:
            return False
        if not self._has_headroom():
            return False
        self.level -= 1
        self._trying = True
        self._clean_ms = 0.0
        self._settle_ms = config.settle_ms
        return True

    def _step_down(self) -> bool:
        """Step down a level after a slow window (a slow try stops the tries); whether it moved."""
        if self._trying:
            self._stay_down = True
        self._trying = False
        self._clean_ms = 0.0
        if self.level >= self.ceiling:
            return False
        self.level += 1
        self._settle_ms = self._config.settle_ms
        return True

    def _has_headroom(self) -> bool:
        """Whether the window's main-thread work and GPU time (when timed) leave room to try."""
        headroom = self._config.headroom_ms
        if self._sum_work / self._frames > headroom:
            return False
        return self._gpu_frames == 0 or self._sum_gpu / self._gpu_frames <= headroom
