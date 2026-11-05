# Copyright (c) 2026 Renaud Guillon
"""WPN-06, WPN-07: the two weapons that are not guns, drawn the same on every owner.

A missile leaves a hexagonal port bored in the end of a short thick barrel (a dark hole with a
glowing rim, a missile's nose seen in it). A laser leaves a lens at the end of a hexagonal barrel,
as the Overlord's cannons (a collar, two coils, a white-hot lens). Neither recoils. Logical pixels,
nose +Z, Y up.
"""

from game.config.enemy_look import ENEMY_LOOK
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[float]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]  # type: list[float]
HOLE = [0.01, 0.01, 0.015]  # type: list[float]
ROCKET_BODY = ENEMY_LOOK.hull.panel
QUARTER = 1.5707963267948966

# A missile's drawn radius and length per unit of hit radius (`ENEMY_LOOK.missile`).
ROCKET = ENEMY_LOOK.missile
# The boss missiles' hit radius, the default port's rocket (BOSS-23).
DEFAULT_MISSILE = 5
# The bore's clearance around its rocket, and the wall around the bore.
BORE_CLEARANCE = 1.15
PORT_WALL = 0.6
# cos 30°: a hexagon's inner radius per unit of its corner radius.
HEX_INNER = 0.8660254037844386


# A laser lens's barrel and lens.
LENS_RADIUS = 2.0
LENS_LENGTH = 3.0
LENS_PROFILE = [[0, 0], [1.6, 0.5], [1.1, 1.4], [0, 1.7]]  # type: list[list[float]]


def axis_of(at: Vec3, direction: str, back: float) -> Placement:
    """Return the placement of a part standing along `direction` ("up" or "forward") from `at`.

    Its base is `back` behind `at` for a forward part (it ends at `at`), and at `at` for an upward
    one (it stands on the deck).
    """
    if direction == "up":
        return Placement([at[0], at[1], at[2]])
    return Placement([at[0], at[1], at[2] - back], 0, QUARTER)


def rocket_radius(missile: float) -> float:
    """Return the drawn radius of a missile of hit radius `missile` (the shot renderer's scale)."""
    radius: float = ROCKET.radius
    base: float = ROCKET.baseRadius
    return radius * missile / base


def port_bore(missile: float) -> float:
    """Return the corner radius of the hexagonal bore a missile of hit radius `missile` fits in."""
    return rocket_radius(missile) / HEX_INNER * BORE_CLEARANCE


def port_radius(missile: float) -> float:
    """Return the outer radius of the port of a missile of hit radius `missile`.

    The tube a port ends is at least this wide (WPN-07: the launcher is wider than its rocket).
    """
    return port_bore(missile) + PORT_WALL


def port_depth(missile: float) -> float:
    """Return the depth of the port of a missile of hit radius `missile`.

    A launcher tube behind it stops there, so that nothing closes its well.
    """
    return max(2.4, port_bore(missile) * 1.8)


def hex_port(
    parts: Any,
    at: Vec3,
    direction: str = "up",
    missile: float = DEFAULT_MISSILE,
    index: int = 0,
    rim: bool = True,
    well: float | None = None,
) -> None:
    """WPN-07: add a hexagonal missile port at `at` for missiles of hit radius `missile`.

    `well` is how deep it is (`port_depth` when None): a launcher can be its port all along.

    A hex barrel with a hollow hexagonal bore wider than the rocket, a dark floor down the well and
    a glowing rim; the rocket of launcher number `index` waits in it, and is gone from the moment
    it is launched until the next one has risen into the well (`Enemy.launchers`).
    """
    bore = port_bore(missile)
    outer = bore + PORT_WALL
    depth = port_depth(missile) if well is None else well
    place = axis_of(at, direction, depth)
    # One revolved profile: the outer wall up, the rim in, the inner wall down the well. A port
    # with no rim is lit along its launcher's sides: nothing glows at its mouth, not even the
    # edge trim (it is drawn bare).
    metal = parts.hull if rim or not hasattr(parts, "bare") else parts.bare
    metal.lathe([[outer, 0], [outer, depth], [bore, depth], [bore, 0.3]], 6, H.dark, place, False)
    metal.lathe([[bore, 0.3], [0, 0.3]], 6, HOLE, place)
    # Its glowing rim, unless the launcher is lit along its sides instead.
    if rim:
        parts.charge.lathe(
            [[outer - 0.05, depth + 0.03], [bore + 0.05, depth + 0.03]], 6, WHITE, place, False
        )
    _rocket(parts, at, direction, missile, depth, index)


def _rocket(parts: Any, at: Vec3, direction: str, missile: float, depth: float, index: int) -> None:
    """Add the rocket loaded in a port: a piece sliding out of sight down the well (WPN-07)."""
    radius = rocket_radius(missile)
    length = ROCKET.length * missile / ROCKET.baseRadius
    nose = 1.6 * missile / ROCKET.baseRadius
    # Its nose just under the mouth, its body down the well and the tube behind.
    tip = depth - 0.1
    place = axis_of(at, direction, depth)

    def draw(piece: Any) -> None:
        piece.hull.cylinder(
            radius, length - nose, 6, ROCKET_BODY, axis_of_shift(place, tip - length)
        )
        piece.neon.cylinder(radius, nose, 6, ROCKET.tip, axis_of_shift(place, tip - nose), 0)

    base = axis_of_shift(place, 0).at or [0, 0, 0]
    if direction == "up":
        parts.slide(base, [0, 0], depth + nose, index, draw, False, None, "rocket", -1)
    else:
        parts.slide(base, [0, -1], depth + nose, index, draw, False, None, "rocket", 0)


def laser_lens(
    parts: Any,
    at: Vec3,
    direction: str = "forward",
    length: float = LENS_LENGTH,
    radius: float = LENS_RADIUS,
) -> None:
    """WPN-06: add a laser's emitter at `at`: a hex barrel, two coils and a white-hot lens.

    The barrel is `length` long behind `at` and `radius` wide; its coils and lens scale with its
    radius and stay at its mouth, so a long barrel is a gun the length of a whole nose.
    """
    place = axis_of(at, direction, length)
    k = radius / LENS_RADIUS
    parts.hull.lathe([[radius, 0], [radius, length]], 6, H.dark, place)
    for y in [0.7, 1.9]:
        coil = length - (LENS_LENGTH - y) * k
        parts.charge.ring(radius * 1.2, 0.5 * k, 6, WHITE, axis_of_shift(place, coil))
    lens = [[p[0] * k, p[1] * k] for p in LENS_PROFILE]
    parts.charge.lathe(shift_profile(lens, length), 6, WHITE, place)


def axis_of_shift(place: Placement, along: float) -> Placement:
    """Return `place` moved `along` its own axis (up, or forward when it is pitched)."""
    at = place.at or [0, 0, 0]
    if place.pitch != 0:
        return Placement([at[0], at[1], at[2] + along], place.yaw, place.pitch, place.roll)
    return Placement([at[0], at[1] + along, at[2]], place.yaw, place.pitch, place.roll)


def shift_profile(profile: list[list[float]], by: float) -> list[list[float]]:
    """Return a lathe profile moved up its axis by `by`."""
    return [[p[0], p[1] + by] for p in profile]
