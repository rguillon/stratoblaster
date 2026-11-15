# Copyright (c) 2026 Renaud Guillon
"""Neon trench geometry of the title screen (UI-TITLE-07, D-325).

A stretch of trench (a floor and two walls of panels of uneven depth, lit slots, a neon strip along
the foot of each wall, lit ribs across the floor, a dashed guide line) and speed streaks rushing
down it. Each stretch runs from z = 0 back to z = -length. Everything comes from `random`, so a
seeded generator gives the same trench every time.

A geometry is a dict of `positions`, `indices` and `colors` (RGBA), see `render.geometry`.
"""

import math

from core.math.rng import pick, random_in
from render.geometry.gradient_shapes import ColoredGeometry

# isort: split
# __pragma__ ("skip")
from typing import Any

from core.math.rng import Random

# __pragma__ ("noskip")


def _quad(geo: ColoredGeometry, corners: list[float], rgb: list[float]) -> None:
    """Add a quad (4 corners, 3 coordinates each) in the colour `rgb`."""
    base = len(geo.positions) // 3
    geo.positions.extend(corners)
    for _ in range(4):
        geo.colors.extend([rgb[0], rgb[1], rgb[2], 1])
    geo.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])


def _quad_x(
    geo: ColoredGeometry, x: float, ys: list[float], zs: list[float], rgb: list[float]
) -> None:
    """Add a rectangle in the plane X = `x` (a wall)."""
    _quad(geo, [x, ys[0], zs[0], x, ys[1], zs[0], x, ys[1], zs[1], x, ys[0], zs[1]], rgb)


def _quad_y(
    geo: ColoredGeometry, y: float, xs: list[float], zs: list[float], rgb: list[float]
) -> None:
    """Add a rectangle in the plane Y = `y` (the floor)."""
    _quad(geo, [xs[0], y, zs[0], xs[1], y, zs[0], xs[1], y, zs[1], xs[0], y, zs[1]], rgb)


def _quad_z(
    geo: ColoredGeometry, z: float, xs: list[float], ys: list[float], rgb: list[float]
) -> None:
    """Add a rectangle in the plane Z = `z` (the end of a panel)."""
    _quad(geo, [xs[0], ys[0], z, xs[1], ys[0], z, xs[1], ys[1], z, xs[0], ys[1], z], rgb)


def _scaled(rgb: list[float], k: float) -> list[float]:
    """Return the colour `rgb` times `k`."""
    return [rgb[0] * k, rgb[1] * k, rgb[2] * k]


def _range_in(random: Random, bounds: list[float]) -> float:
    """Return a number in the range `bounds`."""
    return random_in(random, bounds[0], bounds[1])


def _add_slot(
    lights: ColoredGeometry,
    random: Random,
    options: dict[str, Any],
    x: float,
    zs: list[float],
) -> None:
    """Add a lit slot on a panel's face at `x`, somewhere between the panel's ends `zs`."""
    slots = options["slots"]
    width = min(_range_in(random, slots["width"]), zs[1] - zs[0])
    z0 = random_in(random, zs[0], zs[1] - width)
    y = options["floorY"] + _range_in(random, slots["y"])
    height = _range_in(random, slots["height"])
    color = _scaled(pick(random, slots["colors"]), _range_in(random, slots["brightness"]))
    _quad_x(lights, x, [y, y + height], [z0, z0 + width], color)


def _add_wall(
    parts: dict[str, ColoredGeometry],
    options: dict[str, Any],
    random: Random,
    side: float,
) -> None:
    """Add the wall on `side` (-1 left, 1 right): panels of uneven depth, slots, the foot strip."""
    structure = parts["structure"]
    colors = options["colors"]
    half = options["halfWidth"]
    ys = [options["floorY"], options["floorY"] + options["wallHeight"]]
    strip = options["strip"]
    strip_ys = [ys[0] + strip["y"][0], ys[0] + strip["y"][1]]
    # The slots and the strip stand a hair in front of the panel, towards the trench's middle.
    inward = -side * 0.02
    z = 0.0
    end = -options["length"]
    while z > end:
        z1 = max(z - _range_in(random, options["panelLength"]), end)
        depth = _range_in(random, options["panelDepth"])
        x = side * (half - depth)
        face = colors["wall"] if random() < 0.5 else colors["wallAlt"]
        _quad_x(structure, x, ys, [z1, z], face)
        # The panel's two ends, back to the wall line.
        xs = [x, side * half] if side > 0 else [side * half, x]
        _quad_z(structure, z, xs, ys, colors["edge"])
        _quad_z(structure, z1, xs, ys, colors["edge"])
        if random() < options["slots"]["chance"]:
            _add_slot(parts["lights"], random, options, x + inward, [z1, z])
        _quad_x(parts["lights"], x + inward, strip_ys, [z1, z], strip["color"])
        z = z1


def _add_floor(parts: dict[str, ColoredGeometry], options: dict[str, Any]) -> None:
    """Add the floor, the lit ribs across it and the dashed guide line down its middle."""
    half = options["halfWidth"]
    length = options["length"]
    y = options["floorY"]
    _quad_y(parts["structure"], y, [-half, half], [-length, 0], options["colors"]["floor"])
    lit = y + 0.01
    ribs = options["ribs"]
    z = 0.0
    while z > -length:
        _quad_y(parts["lights"], lit, [-half, half], [z - ribs["width"], z], ribs["color"])
        z -= ribs["every"]
    guide = options["guide"]
    xs = [-guide["halfWidth"], guide["halfWidth"]]
    z = 0.0
    while z > -length:
        _quad_y(parts["lights"], lit, xs, [max(z - guide["dash"], -length), z], guide["color"])
        z -= guide["period"]


def build_trench_chunk(options: dict[str, Any], random: Random) -> dict[str, ColoredGeometry]:
    """Return one stretch of trench as two geometries: its dark `structure` and its `lights`.

    It runs from z = 0 back to z = -`length`; its walls stand at x = ±`halfWidth`, its floor at
    `floorY`. Panels' ends and the ribs line up with the stretch's ends, so stretches placed end to
    end join without a seam.
    """
    parts = {"structure": ColoredGeometry(), "lights": ColoredGeometry()}
    _add_floor(parts, options)
    for side in [-1.0, 1.0]:
        _add_wall(parts, options, random, side)
    return parts


def build_streaks(options: dict[str, Any], random: Random) -> ColoredGeometry:
    """Return the speed streaks of one stretch: thin quads along the trench, round its axis.

    Each streak lies along Z at a distance from the axis (x = 0, y = `axisY`) in `radius`, its width
    across the radius, so it faces the axis, where the camera looks from.
    """
    geo = ColoredGeometry()
    half_width = options["width"] / 2
    for _ in range(options["count"]):
        angle = random() * 2 * math.pi
        radius = _range_in(random, options["radius"])
        cx = math.cos(angle) * radius
        cy = options["axisY"] + math.sin(angle) * radius
        # Across the radius: the tangent of the circle round the axis.
        tx = -math.sin(angle) * half_width
        ty = math.cos(angle) * half_width
        size = _range_in(random, options["size"])
        z0 = random_in(random, -options["length"], -size)
        z1 = z0 + size
        color = _scaled(pick(random, options["colors"]), _range_in(random, options["brightness"]))
        _quad(
            geo,
            [
                cx - tx,
                cy - ty,
                z0,
                cx + tx,
                cy + ty,
                z0,
                cx + tx,
                cy + ty,
                z1,
                cx - tx,
                cy - ty,
                z1,
            ],
            color,
        )
    return geo
