"""Small vector maths on plain lists of 3 numbers (the vectors of `render/geometry`, see
`solids.py`)."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
Vec3 = list[float]

__pragma__("noskip")


def norm(v: Vec3) -> Vec3:
    """`v` scaled to length 1 (straight up, for a zero vector)."""
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length == 0:
        return [0, 1, 0]
    return [v[0] / length, v[1] / length, v[2] / length]


def cross(a: Vec3, b: Vec3) -> Vec3:
    """`a × b`."""
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def plus(a: Vec3, b: Vec3, k: float) -> Vec3:
    """`a + k b`."""
    return [a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k]
