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
QUARTER = 1.5707963267948966

# A port's barrel: its outer radius, the hole's, its length.
PORT_RADIUS = 2.3
PORT_HOLE = 1.6
PORT_LENGTH = 2.4
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


def hex_port(parts: Any, at: Vec3, direction: str = "up", radius: float = PORT_RADIUS) -> None:
    """WPN-07: add a hexagonal missile port at `at`: a hex barrel, a dark hole, a glowing rim.

    The barrel is `radius` wide: the launcher it ends is never thinner than it.
    """
    k = radius / PORT_RADIUS
    length = PORT_LENGTH * k
    hole = PORT_HOLE * k
    place = axis_of(at, direction, length)
    parts.hull.lathe([[radius, 0], [radius, length]], 6, H.dark, place)
    parts.hull.lathe([[hole, length + 0.04], [0, length + 0.04]], 6, HOLE, place)
    # The glowing rim of the hole, and the nose of the missile waiting in it.
    parts.charge.lathe(
        [[hole + 0.5 * k, length + 0.06], [hole, length + 0.06]], 6, WHITE, place, False
    )
    parts.charge.lathe(
        [[0.9 * k, length - 0.5], [0.45 * k, length + 0.1], [0, length + 0.3]], 6, WHITE, place
    )


def laser_lens(parts: Any, at: Vec3, direction: str = "forward") -> None:
    """WPN-06: add a laser's emitter at `at`: a hex barrel, two coils and a white-hot lens."""
    place = axis_of(at, direction, LENS_LENGTH)
    length = LENS_LENGTH
    parts.hull.lathe([[LENS_RADIUS, 0], [LENS_RADIUS, length]], 6, H.dark, place)
    for y in [0.7, 1.9]:
        parts.charge.ring(LENS_RADIUS * 1.2, 0.5, 6, WHITE, axis_of_shift(place, y))
    parts.charge.lathe(shift_profile(LENS_PROFILE, length), 6, WHITE, place)


def axis_of_shift(place: Placement, along: float) -> Placement:
    """Return `place` moved `along` its own axis (up, or forward when it is pitched)."""
    at = place.at or [0, 0, 0]
    if place.pitch != 0:
        return Placement([at[0], at[1], at[2] + along], place.yaw, place.pitch, place.roll)
    return Placement([at[0], at[1] + along, at[2]], place.yaw, place.pitch, place.roll)


def shift_profile(profile: list[list[float]], by: float) -> list[list[float]]:
    """Return a lathe profile moved up its axis by `by`."""
    return [[p[0], p[1] + by] for p in profile]
