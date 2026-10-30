"""Sky gradient as cube-map faces (no asset download), ported from
`render/environment/gradient-cube.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import uint8_array

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class GradientStop:
    """A colour (linear RGB, 0..1) at a given height of the sky (-1 = straight down, 1 = up)."""

    def __init__(self, at: float, color: list[float]) -> None:
        self.at = at
        self.color = color


def _lerp_rgb(a: list[float], b: list[float], t: float) -> list[float]:
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]


def sample_gradient(stops: list[GradientStop], y: float) -> list[float]:
    """Colour of the gradient at height `y`, linearly interpolated between stops sorted by `at`."""
    previous: GradientStop | None = None
    for stop in stops:
        if y <= stop.at:
            if previous is not None:
                return _lerp_rgb(
                    previous.color,
                    stop.color,
                    (y - previous.at) / (stop.at - previous.at),
                )
            return list(stop.color)
        previous = stop
    if previous is None:
        raise ValueError("A gradient needs at least one stop")
    return list(previous.color)


def _hypot3(a: float, b: float, c: float) -> float:
    """`Math.hypot(a, b, c)`: JavaScript's rounding, not `math.hypot`."""
    __pragma__("js", "{}", "return Math.hypot(a, b, c);")
    return 0


# Vertical component of the direction through pixel row `v` (-1 top .. 1 bottom) of each face,
# in the +X, -X, +Y, -Y, +Z, -Z order used by cube textures.
def _side_height(u: float, v: float) -> float:
    return -v / _hypot3(1, u, v)


def _top_height(u: float, v: float) -> float:
    return 1


def _bottom_height(u: float, v: float) -> float:
    return -1


FACE_HEIGHT = [
    _side_height,
    _side_height,
    _top_height,
    _bottom_height,
    _side_height,
    _side_height,
]


def _channel_byte(c: float) -> int:
    return math.floor(min(1, max(0, c)) * 255 + 0.5)


def build_gradient_cube_faces(size: int, stops: list[GradientStop]) -> list[Any]:
    """Builds the 6 RGBA8 faces (`Uint8Array`s) of a cube map whose colour depends only on
    height."""
    faces: list[Any] = []
    for height in FACE_HEIGHT:
        face = uint8_array(size * size * 4)
        for row in range(size):
            for col in range(size):
                u = ((col + 0.5) / size) * 2 - 1
                v = ((row + 0.5) / size) * 2 - 1
                rgb = sample_gradient(stops, height(u, v))
                base = (row * size + col) * 4
                face[base] = _channel_byte(rgb[0])
                face[base + 1] = _channel_byte(rgb[1])
                face[base + 2] = _channel_byte(rgb[2])
                face[base + 3] = 255
        faces.append(face)
    return faces
