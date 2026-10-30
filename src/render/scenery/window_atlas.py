"""The building windows painted once into one texture, an atlas (D-210): a grid of window cells in a
few styles, some lit (each its own colour and brightness, a soft halo round it), some dark. Each
wall of a building is one quad mapped on a block of cells, picked at random, so the buildings all
look different. Pure: the atlas is RGBA pixels; the scenery kit uploads them.

The RGB is the light (black where nothing is lit), the alpha the shape (the windows, their halos;
0 on the wall between them, which shows through).

The look (`WindowAtlasLook`, a config record) has:
- `size`: pixels across the (square) atlas; `cell`: pixels across a window cell;
- `styles`: the styles, each painted in its own band of columns, as many bands as styles. A style
  has `window`, the window's `[x0, y0, x1, y1]` pixels in its cell, and `lit`, the chance a window
  is lit on a floor of average activity;
- `colors`: the colours of the lit windows; `brightness`: their `[low, high]` brightness;
- `blinds`: the chance a lit window has its blind half down (its top half dimmer);
- `dark`: the colour of a dark window; `halo`: the opacity of the halo round a lit one;
- `glass`: how much the sun lights the atlas (for the material, not the atlas);
- `seed`: the seed of the lit pattern.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.rng import create_rng, pick, random_in

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# How bright the half of a lit window under its blind is.
BLIND_DIM = 0.35
# How bright a halo is, next to its window.
HALO_LIGHT = 0.6


def _uint8_array(length: int) -> Any:
    """A zero-filled `Uint8Array` of `length` bytes (the atlas is pure: no Babylon here)."""
    __pragma__("js", "{}", "return new Uint8Array(length);")
    return None


def _byte(v: float) -> int:
    """`v` (0..1) as a byte."""
    if v <= 0:
        return 0
    if v >= 1:
        return 255
    return math.floor(v * 255 + 0.5)


def atlas_cells(look: Any) -> int:  # noqa: ANN401 (a config record)
    """Window cells across the atlas (and down it)."""
    size: int = look.size
    cell: int = look.cell
    return math.floor(size / cell)


def style_columns(look: Any) -> int:  # noqa: ANN401 (a config record)
    """Window cells across the band of columns of one style."""
    return math.floor(atlas_cells(look) / len(look.styles))


def _put(pixels: Any, i: int, rgb: list[float], alpha: float) -> None:  # noqa: ANN401
    """Sets pixel `i`, unless it already shows something more opaque (halos meet, windows win)."""
    a = _byte(alpha)
    if pixels[i * 4 + 3] > a:
        return
    pixels[i * 4] = _byte(rgb[0])
    pixels[i * 4 + 1] = _byte(rgb[1])
    pixels[i * 4 + 2] = _byte(rgb[2])
    pixels[i * 4 + 3] = a


def _scaled(rgb: list[float], k: float) -> list[float]:
    return [rgb[0] * k, rgb[1] * k, rgb[2] * k]


def _paint_window(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    pixels: Any,  # noqa: ANN401
    look: Any,  # noqa: ANN401
    at: list[int],
    window: list[int],
    light: list[float] | None,
    blind: bool,  # noqa: FBT001
) -> None:
    """One window whose cell's corner is pixel `at`: lit in `light` (None: dark), with its halo
    when lit."""
    size = look.size
    x0 = at[0] + window[0]
    y0 = at[1] + window[1]
    x1 = at[0] + window[2]
    y1 = at[1] + window[3]
    if light is not None:
        halo = _scaled(light, HALO_LIGHT)
        for y in range(y0 - 1, y1 + 1):
            for x in range(x0 - 1, x1 + 1):
                # The atlas wraps: a halo past its edge shows on the other side.
                i = ((y + size) % size) * size + (x + size) % size
                _put(pixels, i, halo, look.halo)
    half = y0 + math.floor((y1 - y0) / 2)
    for y in range(y0, y1):
        for x in range(x0, x1):
            rgb = look.dark
            if light is not None:
                rgb = _scaled(light, BLIND_DIM) if blind and y >= half else light
            _put(pixels, (y % size) * size + x % size, rgb, 1)


def window_atlas_pixels(look: Any) -> Any:  # noqa: ANN401 (a config record)
    """RGBA8 pixels of the atlas of `look` (see the module doc). Its rows go up the walls: row 0
    is V = 0, the bottom of a window cell."""
    size = look.size
    cell = look.cell
    cells = atlas_cells(look)
    band = style_columns(look)
    random = create_rng(look.seed)
    pixels = _uint8_array(size * size * 4)
    for s in range(len(look.styles)):
        style = look.styles[s]
        for row in range(cells):
            # Some floors busier than others, so the lit windows bunch as in real buildings.
            activity = random_in(random, 0.2, 1.8)
            for col in range(band):
                light = None
                blind = False
                if random() < style.lit * activity:
                    light = _scaled(
                        pick(random, look.colors),
                        random_in(random, look.brightness[0], look.brightness[1]),
                    )
                    blind = random() < look.blinds
                at = [(s * band + col) * cell, row * cell]
                _paint_window(pixels, look, at, style.window, light, blind)
    return pixels


# The atlases made, by look (the look is the same for every level: made once, kept).
_kept: dict[str, Any] = {}


def _json_of(value: Any) -> str:  # noqa: ANN401
    __pragma__("js", "{}", "return JSON.stringify(value);")
    return repr(value)


def kept_window_atlas(look: Any) -> Any:  # noqa: ANN401 (a config record)
    """The pixels of `window_atlas_pixels(look)`, made on first use and kept. Callers must not
    change them."""
    key = _json_of(look)
    pixels = _kept.get(key)
    if pixels is None:
        pixels = window_atlas_pixels(look)
        _kept[key] = pixels
    return pixels
