"""Branches (D-214): tapered limbs between two points, and limbs forking into smaller ones, as bare
wood does. Seeded: the same seed gives the same branches.

Game-agnostic: they draw into a `SolidBuilder` and know nothing of what they are used for.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.noise import hash_2d
from render.geometry.solids import SolidBuilder, shaded
from render.geometry.vec3 import cross, norm, plus

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
Rgb = list[float]
Vec3 = list[float]
__pragma__("noskip")

# Draws of a fork (its turn round the limb, its angle, its length, where it starts) and of a limb
# (its shade): each has its own stream.
_TURN = 1
_ANGLE = 2
_LENGTH = 3
_START = 4
_SHADE = 5
# A direction this close to straight up or down is crossed with X, not Y, to find its square.
_STEEP = 0.9


def across(direction: Vec3) -> list[Vec3]:
    """Two unit vectors `u`, `v` square to `direction` and to each other, `u × v` along it."""
    d = norm(direction)
    helper: Vec3 = [0, 1, 0] if abs(d[1]) < _STEEP else [1, 0, 0]
    u = norm(cross(d, helper))
    return [u, cross(d, u)]


def limb(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    start: Vec3,
    end: Vec3,
    radii: list[float],
    sides: int,
    color: Rgb,
) -> None:
    """A limb from `start` to `end`, `radii` = [radius at the start, at the end], of `sides` flat
    facets. An end radius of 0 closes it to a point; otherwise its end is capped. Its start is left
    open: it stands in the trunk or limb it grows from."""
    uv = across([end[0] - start[0], end[1] - start[1], end[2] - start[2]])
    u = uv[0]
    v = uv[1]

    def ring(centre: Vec3, r: float) -> list[Vec3]:
        out: list[Vec3] = []
        for i in range(sides):
            a = (i / sides) * math.pi * 2
            out.append(plus(plus(centre, u, r * math.cos(a)), v, r * math.sin(a)))
        return out

    low = ring(start, radii[0])
    if radii[1] <= 0:
        for i in range(sides):
            n = (i + 1) % sides
            s.face([low[i], low[n], end], color)
        return
    high = ring(end, radii[1])
    for i in range(sides):
        n = (i + 1) % sides
        s.face([low[i], low[n], high[n], high[i]], color)
    s.face(high, color)


class Branching:
    """How a limb forks: into `forks` limbs, each turned `spread` radians off it (give or take a
    third), `shrink` times as long (give or take a fifth) and `thin` times as thick at its base as
    the limb is at its end, starting in the outer `reach` (0..1) of it and bent `rise` up (or down,
    below 0) by unit of its length. A limb's end is `taper` times as thick as its start, a limb
    that forks no more ends in a point. Each limb is shaded up to `shade` lighter or darker."""

    def __init__(  # noqa: PLR0913, PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        forks: int,
        spread: float,
        shrink: float,
        thin: float,
        reach: float,
        rise: float,
        taper: float,
        shade: float,
    ) -> None:
        self.forks = forks
        self.spread = spread
        self.shrink = shrink
        self.thin = thin
        self.reach = reach
        self.rise = rise
        self.taper = taper
        self.shade = shade


def branch(  # noqa: PLR0913, PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    start: Vec3,
    direction: Vec3,
    size: list[float],
    depth: int,
    shape: Branching,
    color: Rgb,
    seed: int,
) -> None:
    """A limb from `start` along `direction`, `size` = [length, radius at its start], that forks
    `depth` times more as `shape` says. Its facets go from 6 down to 3 as its limbs get thinner;
    the same seed gives the same limbs whatever the `depth`, so a shallower one is its outline."""
    length = size[0]
    radius = size[1]
    d = norm(direction)
    end = plus(start, d, length)
    tint = shaded(color, 1 + (hash_2d(seed, depth, _SHADE) - 0.5) * 2 * shape.shade)
    sides = max(3, min(6, math.floor(radius * 14)))
    limb(s, start, end, [radius, radius * shape.taper if depth > 0 else 0], sides, tint)
    if depth <= 0:
        return
    uv = across(d)
    for k in range(shape.forks):
        turn = (k / shape.forks + hash_2d(seed, k, _TURN) * 0.3) * math.pi * 2
        angle = shape.spread * (1 + (hash_2d(seed, k, _ANGLE) - 0.5) * 0.66)
        side = plus(plus([0, 0, 0], uv[0], math.cos(turn)), uv[1], math.sin(turn))
        out = plus(plus(d, d, math.cos(angle) - 1), side, math.sin(angle))
        out = norm([out[0], out[1] + shape.rise, out[2]])
        at = 1 - shape.reach * hash_2d(seed, k, _START)
        child = [
            length * shape.shrink * (1 + (hash_2d(seed, k, _LENGTH) - 0.5) * 0.4),
            radius * shape.taper * shape.thin,
        ]
        branch(
            s, plus(start, d, length * at), out, child, depth - 1, shape, color, seed * 5 + k + 1
        )
