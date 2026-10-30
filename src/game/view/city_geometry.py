"""Night city geometry of the title screen, ported from `city-geometry.ts`: stretches of city along
a street (buildings, lit windows, neon trims and blade signs, lane lines), a distant skyline,
and rain. Everything comes from `random`, so a seeded generator gives the same city every time.

A geometry is a dict of `positions`, `indices` and `colors` (RGBA), see `render.geometry`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

from core.math.rng import Random  # noqa: E402

__pragma__("noskip")

from core.math.rng import pick, random_in  # noqa: E402
from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402


def _empty_geometry() -> ColoredGeometry:
    """A geometry with no vertices yet."""
    return ColoredGeometry()


def _quad(geo: ColoredGeometry, corners: list[float], rgb: list[float]) -> None:
    """Adds a quad (4 corners, 3 coordinates each) in the colour `rgb`."""
    base = len(geo.positions) // 3
    geo.positions.extend(corners)
    for _ in range(4):
        geo.colors.extend([rgb[0], rgb[1], rgb[2], 1])
    geo.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])


def _quad_x(
    geo: ColoredGeometry,
    x: float,
    y_range: list[float],
    z_range: list[float],
    rgb: list[float],
) -> None:
    """A rectangle in the plane X = `x`."""
    _quad(
        geo,
        [
            x,
            y_range[0],
            z_range[0],
            x,
            y_range[1],
            z_range[0],
            x,
            y_range[1],
            z_range[1],
            x,
            y_range[0],
            z_range[1],
        ],
        rgb,
    )


def _quad_y(
    geo: ColoredGeometry,
    y: float,
    x_range: list[float],
    z_range: list[float],
    rgb: list[float],
) -> None:
    """A rectangle in the plane Y = `y`."""
    _quad(
        geo,
        [
            x_range[0],
            y,
            z_range[0],
            x_range[1],
            y,
            z_range[0],
            x_range[1],
            y,
            z_range[1],
            x_range[0],
            y,
            z_range[1],
        ],
        rgb,
    )


def _quad_z(
    geo: ColoredGeometry,
    z: float,
    x_range: list[float],
    y_range: list[float],
    rgb: list[float],
) -> None:
    """A rectangle in the plane Z = `z`, facing the camera (which looks towards +Z)."""
    _quad(
        geo,
        [
            x_range[0],
            y_range[0],
            z,
            x_range[1],
            y_range[0],
            z,
            x_range[1],
            y_range[1],
            z,
            x_range[0],
            y_range[1],
            z,
        ],
        rgb,
    )


def _scaled(rgb: list[float], k: float) -> list[float]:
    """The colour `rgb` times `k`."""
    return [rgb[0] * k, rgb[1] * k, rgb[2] * k]


def _range_in(random: Random, bounds: list[float]) -> float:
    """A number in the range `bounds` (`randomIn`)."""
    return random_in(random, bounds[0], bounds[1])


def _lit_window_color(random: Random, windows: dict[str, Any]) -> list[float]:
    """The colour of a lit window: one of the window colours, brightened at random."""
    return _scaled(pick(random, windows["colors"]), _range_in(random, windows["brightness"]))


def _for_each_lit_window(
    random: Random,
    windows: dict[str, Any],
    width: float,
    height: float,
    cell: Callable[[float, float], None],
) -> None:
    """Calls `cell(u0, v0)` for each lit cell of a `width × height` window grid."""
    cols = math.floor(width / windows["cellWidth"])
    rows = math.floor((height - windows["groundFloor"]) / windows["cellHeight"])
    margin_u = (width - cols * windows["cellWidth"]) / 2 + (
        windows["cellWidth"] - windows["width"]
    ) / 2
    margin_v = windows["groundFloor"] + (windows["cellHeight"] - windows["height"]) / 2
    for row in range(rows):
        for col in range(cols):
            if random() < windows["litChance"]:
                cell(margin_u + col * windows["cellWidth"], margin_v + row * windows["cellHeight"])


def _add_sign(
    lights: ColoredGeometry,
    random: Random,
    options: dict[str, Any],
    facade_x: float,
    side: float,
    z: float,
) -> None:
    """A blade sign hanging from a facade into the street, facing the camera."""
    signs = options["signs"]
    width = _range_in(random, signs["width"])
    height = _range_in(random, signs["height"])
    y0 = _range_in(random, signs["baseHeight"])
    color = pick(random, options["neonColors"])
    x_in = side * (facade_x - 0.1)
    x_out = side * (facade_x - 0.1 - width)
    border = 0.18
    _quad_z(lights, z, [x_in, x_out], [y0, y0 + height], color)
    inner_in = x_in - side * border
    inner_out = x_out + side * border
    _quad_z(
        lights, z - 0.02, [inner_in, inner_out], [y0 + border, y0 + height - border], signs["panel"]
    )
    # Bars of random length suggest lines of text.
    step = (height - 2 * border) / (2 * signs["lines"] + 1)
    for line in range(signs["lines"]):
        y = y0 + border + (2 * line + 1) * step
        length = (width - 2 * border) * _range_in(random, [0.45, 0.9])
        start = inner_in - side * ((width - 2 * border - length) / 2)
        _quad_z(lights, z - 0.04, [start, start - side * length], [y, y + step], color)


def _window_cell(
    lights: ColoredGeometry,
    windows: dict[str, Any],
    random: Random,
    window_x: float,
    z0: float,
) -> Callable[[float, float], None]:
    """The callback that draws one lit window of a facade (a factory: it is made in a loop)."""

    def cell(u: float, v: float) -> None:
        color = _lit_window_color(random, windows)
        _quad_x(
            lights,
            window_x,
            [v, v + windows["height"]],
            [z0 + u, z0 + u + windows["width"]],
            color,
        )

    return cell


def _add_building(
    city: dict[str, ColoredGeometry],
    random: Random,
    options: dict[str, Any],
    row: dict[str, Any],
    side: float,
    z_range: list[float],
) -> None:
    """One building on one side of the street: its walls, lit windows, trim and sign."""
    structure = city["structure"]
    lights = city["lights"]
    z0 = z_range[0]
    z1 = z_range[1]
    facade_x = options["streetHalfWidth"] + row["facadeOffset"]
    depth = _range_in(random, row["depth"])
    height = _range_in(random, row["height"])
    x0 = side * facade_x
    x1 = side * (facade_x + depth)
    _quad_x(structure, x0, [0, height], [z0, z1], options["colors"]["facade"])
    _quad_z(structure, z0, [x0, x1], [0, height], options["colors"]["wall"])
    _quad_y(structure, height, [x0, x1], [z0, z1], options["colors"]["roof"])

    window_x = x0 - side * 0.05
    _for_each_lit_window(
        random,
        options["windows"],
        z1 - z0,
        height,
        _window_cell(lights, options["windows"], random, window_x, z0),
    )
    if random() < options["trim"]["chance"]:
        color = pick(random, options["neonColors"])
        _quad_x(
            lights, x0 - side * 0.08, [height - options["trim"]["height"], height], [z0, z1], color
        )
    if row["signs"] and random() < options["signs"]["chance"]:
        _add_sign(lights, random, options, facade_x, side, z0 + 0.6)


def _add_street(city: dict[str, ColoredGeometry], options: dict[str, Any]) -> None:
    """The street's ground and its dashed lane lines."""
    street = options["street"]
    length = options["length"]
    _quad_y(
        city["structure"],
        0,
        [-street["halfWidth"], street["halfWidth"]],
        [0, length],
        street["color"],
    )
    half = street["lineWidth"] / 2
    z = 0
    while z + street["dash"] <= length:
        for x in street["laneX"]:
            _quad_y(
                city["lights"],
                0.02,
                [x - half, x + half],
                [z, z + street["dash"]],
                street["lineColor"],
            )
        z += street["dashPeriod"]


def build_city_chunk(options: dict[str, Any], random: Random) -> dict[str, ColoredGeometry]:
    """A stretch of night city along a street running towards +Z: rows of dark buildings on both
    sides, lit windows on the facades facing the street, neon roof trims and blade signs, and
    dashed lane lines. The chunk spans Z in [0, length]; two chunks end to end tile seamlessly."""
    city = {"structure": _empty_geometry(), "lights": _empty_geometry()}
    _add_street(city, options)
    for row in options["rows"]:
        for side in [-1, 1]:
            z = _range_in(random, row["gap"])
            while True:
                width = _range_in(random, row["width"])
                if z + width > options["length"]:
                    break
                _add_building(city, random, options, row, side, [z, z + width])
                z += width + _range_in(random, row["gap"])
    return city


def _skyline_cell(
    city: dict[str, ColoredGeometry],
    windows: dict[str, Any],
    random: Random,
    left: float,
) -> Callable[[float, float], None]:
    """The callback that draws one lit window of a skyline tower (a factory: made in a loop)."""

    def cell(u: float, v: float) -> None:
        color = _lit_window_color(random, windows)
        x0 = left + u
        _quad_z(
            city["lights"], -0.05, [x0, x0 + windows["width"]], [v, v + windows["height"]], color
        )

    return cell


def build_skyline(options: dict[str, Any], random: Random) -> dict[str, ColoredGeometry]:
    """Flat silhouettes of distant towers in the XY plane (bottom at Y = 0), with a few lit windows
    slightly in front of them. The skyline spans X in [-halfWidth, halfWidth]."""
    city = {"structure": _empty_geometry(), "lights": _empty_geometry()}
    x = -options["halfWidth"]
    while x < options["halfWidth"]:
        width = _range_in(random, options["width"])
        height = _range_in(random, options["height"])
        _quad_z(city["structure"], 0, [x, x + width], [0, height], options["color"])
        _for_each_lit_window(
            random,
            options["windows"],
            width,
            height,
            _skyline_cell(city, options["windows"], random, x),
        )
        x += width
    return city


def build_rain(options: dict[str, Any], random: Random) -> ColoredGeometry:
    """Thin vertical rain streaks facing the camera. The pattern is drawn twice, stacked, so moving
    the mesh down by up to `height` and wrapping loops without a gap."""
    geo = _empty_geometry()
    for _ in range(options["count"]):
        x = random_in(random, -options["halfWidth"], options["halfWidth"])
        y = random() * options["height"]
        z = _range_in(random, options["z"])
        length = _range_in(random, options["length"])
        for offset in [0, options["height"]]:
            _quad_z(
                geo,
                z,
                [x, x + options["width"]],
                [y + offset, y + offset + length],
                options["color"],
            )
    return geo
