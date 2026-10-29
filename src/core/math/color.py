"""Colour helpers for readability (phase 14): luminance, contrast ratio, hue families.

Colours are linear RGB, 0..1, unless noted. Ported from `core/math/color.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

Rgb = Sequence[float]
__pragma__("noskip")

import math  # noqa: E402


def relative_luminance(color: Rgb) -> float:
    """Relative luminance of a linear RGB colour (WCAG 2), 0..1."""
    r, g, b = color[0], color[1], color[2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


SRGB_LINEAR_THRESHOLD = 0.04045


def srgb_byte_to_linear(byte: float) -> float:
    """A gamma-encoded (sRGB) channel byte, 0..255, as linear 0..1."""
    c = byte / 255
    if c <= SRGB_LINEAR_THRESHOLD:
        return c / 12.92
    return math.pow((c + 0.055) / 1.055, 2.4)


def contrast_ratio(a: float, b: float) -> float:
    """Contrast ratio between two relative luminances (WCAG 2): 1 (none) to 21."""
    hi, lo = (a, b) if a > b else (b, a)
    return (hi + 0.05) / (lo + 0.05)


def hue_saturation(color: Rgb) -> tuple[float, float]:
    """Hue in degrees [0, 360) and saturation (HSV, 0..1) of a colour; grey has hue 0."""
    r, g, b = color[0], color[1], color[2]
    high = max(r, g, b)
    low = min(r, g, b)
    chroma = high - low
    if chroma <= 0:
        return 0.0, 0.0
    if high == r:
        sector = ((g - b) / chroma + 6) % 6
    elif high == g:
        sector = (b - r) / chroma + 2
    else:
        sector = (r - g) / chroma + 4
    return sector * 60, chroma / high


class ColorFamily:
    """Colours whose hue lies in `[start, end]` degrees (`start` > `end` wraps past 0),
    saturated at least `min_saturation`. Greys and whites belong to no family."""

    def __init__(self, start: float, end: float, min_saturation: float) -> None:
        self.start = start
        self.end = end
        self.min_saturation = min_saturation


def _span(family: ColorFamily) -> float:
    """Width of `family`'s hue range, in degrees."""
    return (family.end - family.start + 360) % 360


def in_family(color: Rgb, family: ColorFamily) -> bool:
    """Whether `color` is in `family`."""
    hue, saturation = hue_saturation(color)
    return saturation >= family.min_saturation and (hue - family.start + 360) % 360 <= _span(family)


def _with_hue(color: Rgb, hue: float) -> Rgb:
    """`color` with its hue set to `hue`, keeping its HSV value and saturation."""
    high = max(color[0], color[1], color[2])
    low = min(color[0], color[1], color[2])

    def channel(n: float) -> float:
        k = (n + hue / 60) % 6
        return high - (high - low) * max(0, min(k, 4 - k, 1))

    return [channel(5), channel(3), channel(1)]


def fold_into_family(color: Rgb, family: ColorFamily) -> Rgb:
    """`color` moved into `family` (phase 14, P14-R02): its hue squeezed from the whole wheel
    into the family's range, in the same order, keeping brightness and saturation. Greys stay."""
    hue, saturation = hue_saturation(color)
    if saturation == 0:
        return color
    return _with_hue(color, (family.start + (hue / 360) * _span(family)) % 360)
