"""Movement helpers for enemies (GD-45), ported from `core/systems/enemy-motion.ts`.

Playfield logical pixels, Y up; headings in radians from +Y, positive to the right.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

PathPoint = Sequence[float]

__pragma__("noskip")

# A path needs at least this many control points.
MIN_CONTROLS = 2


class PathPose:
    """A point along a `Path`, with the direction of travel there."""

    def __init__(self, x: float, y: float, heading: float) -> None:
        self.x = x
        self.y = y
        self.heading = heading


def _catmull_rom(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
    t2 = t * t
    return 0.5 * (
        2 * p1
        + (p2 - p0) * t
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
        + (3 * p1 - p0 - 3 * p2 + p3) * t2 * t
    )


def _at_or(values: list[float], index: int, default: float) -> float:
    """`values[index] ?? default`: Transcrypt returns undefined past the end, not an error."""
    return values[index] if 0 <= index < len(values) else default


class Path:
    """A smooth predefined path through control points (a Catmull-Rom curve), followed by distance
    travelled, so an enemy moving along it at a constant speed keeps that speed on the curves.
    """

    def __init__(self, controls: Sequence[PathPoint], samples_per_span: int = 16) -> None:
        if len(controls) < MIN_CONTROLS:
            raise ValueError("A path needs at least 2 points")
        self._points: list[list[float]] = []
        # Distance travelled from the start at each sampled point.
        self._lengths: list[float] = []
        last_control = len(controls) - 1
        for span in range(last_control):
            p0 = controls[min(max(span - 1, 0), last_control)]
            p1 = controls[min(max(span, 0), last_control)]
            p2 = controls[min(max(span + 1, 0), last_control)]
            p3 = controls[min(max(span + 2, 0), last_control)]
            first = 0 if span == 0 else 1
            for s in range(first, samples_per_span + 1):
                t = s / samples_per_span
                self._add(
                    [
                        _catmull_rom(p0[0], p1[0], p2[0], p3[0], t),
                        _catmull_rom(p0[1], p1[1], p2[1], p3[1], t),
                    ]
                )

    def _add(self, point: list[float]) -> None:
        count = len(self._points)
        step = 0.0
        if count > 0:
            last = self._points[count - 1]
            step = math.hypot(point[0] - last[0], point[1] - last[1])
        previous = _at_or(self._lengths, len(self._lengths) - 1, 0)
        self._lengths.append(previous + step)
        self._points.append(point)

    @property
    def length(self) -> float:
        """Total length."""
        return _at_or(self._lengths, len(self._lengths) - 1, 0)

    def at(self, distance: float) -> PathPose:
        """The pose `distance` along the path, clamped to its ends."""
        d = min(max(distance, 0), self.length)
        i = 1
        while i < len(self._lengths) - 1 and _at_or(self._lengths, i, 0) < d:
            i += 1
        a = _at_or_point(self._points, i - 1)
        b = _at_or_point(self._points, i)
        la = _at_or(self._lengths, i - 1, 0)
        lb = _at_or(self._lengths, i, 0)
        t = (d - la) / (lb - la) if lb > la else 0
        return PathPose(
            a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            math.atan2(b[0] - a[0], b[1] - a[1]),
        )


def _at_or_point(points: list[list[float]], index: int) -> list[float]:
    """`points[index] ?? [0, 0]`."""
    return points[index] if 0 <= index < len(points) else [0, 0]


def fan_headings(center: float, count: int, spacing: float) -> list[float]:
    """`count` headings spread `spacing` radians apart, centred on `center` (e.g. a fan of 3
    bullets at -15°, 0° and +15° from straight down).
    """
    return [center + (i - (count - 1) / 2) * spacing for i in range(count)]


def _sign(value: float) -> float:
    """`Math.sign`."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def approach(value: float, target: float, max_step: float) -> float:
    """Moves `value` towards `target` by at most `max_step`."""
    if abs(target - value) <= max_step:
        return target
    return value + _sign(target - value) * max_step
