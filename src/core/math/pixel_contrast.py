"""How well what is drawn stands out from what is behind it (phase 14, P14-R08). Pixels are RGBA
sRGB bytes, four per pixel, row by row."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

__pragma__("noskip")

from core.math.color import contrast_ratio, relative_luminance, srgb_byte_to_linear  # noqa: E402


class Pixels:
    """An RGBA image read back from the screen."""

    def __init__(self, width: int, height: int, data: Sequence[float]) -> None:
        self.width = width
        self.height = height
        self.data = data


class PixelBox:
    """A square of pixels: its centre and half its side, in pixels of the image."""

    def __init__(self, x: float, y: float, radius: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius


def _js_round(value: float) -> int:
    """JavaScript's Math.round: halves round up (Python's round() rounds them to even)."""
    return math.floor(value + 0.5)


def _byte_at(data: Sequence[float], index: int) -> float:
    return data[index] if index < len(data) else 0


def luminance_at(image: Pixels, x: int, y: int) -> float:
    """Relative luminance of the pixel at (`x`, `y`)."""
    i = (y * image.width + x) * 4

    def channel(k: int) -> float:
        return srgb_byte_to_linear(_byte_at(image.data, i + k))

    return relative_luminance([channel(0), channel(1), channel(2)])


def _box_luminances(image: Pixels, box: PixelBox) -> list[float]:
    """Luminances of the pixels of `box` inside the image."""
    out: list[float] = []
    x0 = max(0, _js_round(box.x - box.radius))
    x1 = min(image.width - 1, _js_round(box.x + box.radius))
    y0 = max(0, _js_round(box.y - box.radius))
    y1 = min(image.height - 1, _js_round(box.y + box.radius))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            out.append(luminance_at(image, x, y))
    return out


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    if len(ordered) == 0:
        return 0.0
    return ordered[len(ordered) // 2]


def box_contrast(frame: Pixels, background: Pixels, box: PixelBox) -> float:
    """How well what is drawn in `box` stands out: the contrast between its brightest pixel on
    `frame` and the median of the same pixels on `background`. 1 when the box is off the image."""
    drawn = _box_luminances(frame, box)
    if len(drawn) == 0:
        return 1.0
    return contrast_ratio(max(drawn), _median(_box_luminances(background, box)))


def brightest_but(image: Pixels, share: float) -> float:
    """The luminance only `share` (0..1) of the image's pixels are brighter than.

    The luminances are kept as 64-bit floats (a 32-bit store would round the result by about
    1e-7 relative at most).
    """
    n = image.width * image.height
    if n == 0:
        return 0.0
    values: list[float] = []
    for y in range(image.height):
        for x in range(image.width):
            values.append(luminance_at(image, x, y))
    values.sort()
    return values[math.floor((1 - share) * (n - 1))]


class ReadabilityReport:
    """How readable the frame is: the contrast of each kind of object with what is behind it
    (None when none is on screen), and the luminance of the background's brightest pixels."""

    def __init__(
        self,
        player: float | None,
        enemy: float | None,
        enemy_bullet: float | None,
        player_shot: float | None,
        background_luminance: float,
    ) -> None:
        self.player = player
        self.enemy = enemy
        self.enemy_bullet = enemy_bullet
        self.player_shot = player_shot
        self.background_luminance = background_luminance
