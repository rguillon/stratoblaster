# Copyright (c) 2026 Renaud Guillon
"""Debug perf overlay (DEV-PERF-03, ENG-111)."""

from org.transcrypt.stubs.browser import window

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


class PerfNumbers:
    """What the perf monitor has measured (DEV-PERF-01). Times in milliseconds."""

    def __init__(
        self,
        long_frames: int,
        longest_frame: float,
        frames: int,
        last_load: float | None,
        longest_load_step: float | None,
        draw_calls: float,
    ) -> None:
        # Frames longer than the long-frame limit since the counts were last reset.
        self.long_frames = long_frames
        # Longest frame since the counts were last reset.
        self.longest_frame = longest_frame
        # Frames measured since the counts were last reset.
        self.frames = frames
        # How long the last level took from its confirmation to its first drawn frame, if any.
        self.last_load = last_load
        # Longest frame of the last level loading (PERF-10: the longest frozen step), if any.
        self.longest_load_step = longest_load_step
        # Draw calls of the last frame drawn (ENG-106, budget under 200 in play).
        self.draw_calls = draw_calls


def _ms(value: float | None) -> str:
    """Format milliseconds for the overlay."""
    if value is None:
        return "\u2013"
    return str(window.Number(value).toFixed(0)) + " ms"


class PerfOverlay:
    """The debug perf overlay (DEV-PERF-03, ENG-111; dev and e2e builds only): long frames.

    The longest frame and the last level loading time. Hidden until toggled (F3); the text changes
    at most every `refresh_seconds`, so the numbers stay readable.
    """

    def __init__(self, doc: Any, parent: Any, refresh_seconds: float) -> None:
        self.root = doc.createElement("div")
        self.root.className = "perf-overlay"
        self.root.hidden = True
        parent.append(self.root)
        self._refresh_seconds = refresh_seconds
        self._since_refresh = float("Infinity")

    @property
    def shown(self) -> bool:
        """The shown."""
        return not self.root.hidden

    def toggle(self) -> None:
        """Toggle."""
        self.root.hidden = not self.root.hidden
        self._since_refresh = float("Infinity")

    def update(self, dt: float, numbers: PerfNumbers) -> None:
        """Show `numbers` if shown and `refresh_seconds` have passed since the last change."""
        self._since_refresh += dt
        if not self.shown or self._since_refresh < self._refresh_seconds:
            return
        self._since_refresh = 0
        self.root.textContent = "\n".join([
            "Long frames: " + str(numbers.long_frames),
            "Longest frame: " + _ms(numbers.longest_frame),
            "Draw calls: " + str(window.Math.round(numbers.draw_calls)),
            "Level load: " + _ms(numbers.last_load),
        ])

    def dispose(self) -> None:
        """Dispose."""
        self.root.remove()
