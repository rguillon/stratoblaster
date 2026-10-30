"""Where enemy shots leave from, ported from `core/entities/muzzle.ts` (phase 7 review).

A gun's muzzle is a point of the enemy as it is drawn, above the playfield; the tilted camera
sees it in front of another point of the playfield, where its shots (flying on the playfield)
start.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Protocol  # noqa: E402

# A muzzle: its offset from the enemy's centre as seen when the enemy faces down the screen (X
# right, Y up, logical pixels), and its height above the playfield (towards the camera).
Muzzle = tuple[float, float, float]


class PlayfieldEye(Protocol):
    """Where the camera's eye is: the playfield point under it, and its height above it."""

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...

    @property
    def height(self) -> float: ...


class MuzzleBody(Protocol):
    """How a body is placed: its centre and the way its nose points (`roll` is optional)."""

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...

    @property
    def heading(self) -> float: ...


__pragma__("noskip")


class RaisedPoint:
    """A point of the playfield (X right, Y up), and its height above it."""

    def __init__(self, x: float, y: float, height: float) -> None:
        self.x = x
        self.y = y
        self.height = height


class PlanePoint:
    """A point of the playfield (X right, Y up), without a height."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def seen_on_playfield(eye: PlayfieldEye | None, point: RaisedPoint) -> PlanePoint:
    """The point of the playfield the eye sees behind `point`: along the line from the eye through
    it, down to the playfield. Straight below it without an eye (or when it is on the playfield).
    """
    if eye is None or point.height == 0:
        return PlanePoint(point.x, point.y)
    k = eye.height / max(1, eye.height - point.height)
    return PlanePoint(eye.x + (point.x - eye.x) * k, eye.y + (point.y - eye.y) * k)


def muzzle_point(body: MuzzleBody, muzzle: Muzzle, spin: float = 0) -> RaisedPoint:
    """Where `muzzle` is on the playfield, and how high, on `body`. `spin` (radians, clockwise on
    screen) first turns it around the body's centre, as for a boss's orbiting parts. The body's
    optional `roll` (radians about its nose; positive dips its right side) is 0 when absent.
    """
    mx, my, mh = muzzle
    sc, ss = math.cos(spin), math.sin(spin)
    x0, y0 = mx * sc + my * ss, -mx * ss + my * sc
    # (Transcrypt returns null, not the default, from getattr with a default: hasattr instead.)
    roll = body.roll if hasattr(body, "roll") else 0
    rc, rs = math.cos(roll), math.sin(roll)
    x1, height = x0 * rc + mh * rs, mh * rc - x0 * rs
    # Facing down (heading pi) the offset is as given; otherwise it turns with the nose.
    hc, hs = math.cos(body.heading), math.sin(body.heading)
    return RaisedPoint(body.x - x1 * hc - y0 * hs, body.y + x1 * hs - y0 * hc, height)
