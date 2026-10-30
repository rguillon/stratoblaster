"""A small debug tile with the frame rate and polygon count"""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class RenderStats:
    """Rendering numbers shown by a `StatsTile`."""

    def __init__(self, fps: float, polygons: float) -> None:
        self.fps = fps
        # Triangles drawn in the last frame.
        self.polygons = polygons


class StatsTile:
    """A small debug tile with the frame rate and the number of polygons drawn. The text changes
    at most every `refresh_seconds`, so the numbers stay readable.
    """

    def __init__(self, doc: Any, parent: Any, refresh_seconds: float) -> None:
        self.root = doc.createElement("div")
        self.root.className = "stats-tile"
        self._fps = doc.createElement("div")
        self._fps.className = "stats-fps"
        self._polygons = doc.createElement("div")
        self._polygons.className = "stats-polygons"
        self.root.append(self._fps, self._polygons)
        parent.append(self.root)
        self._refresh_seconds = refresh_seconds
        self._since_refresh = float("Infinity")

    def update(self, dt: float, stats: RenderStats) -> None:
        """Shows `stats` if `refresh_seconds` have passed since the last change (and the first
        time).
        """
        self._since_refresh += dt
        if self._since_refresh < self._refresh_seconds:
            return
        self._since_refresh = 0
        self._fps.textContent = "FPS: " + str(window.Math.round(stats.fps))
        self._polygons.textContent = "Polygons: " + window.Math.round(
            stats.polygons
        ).toLocaleString("en-US")
