# Copyright (c) 2026 Renaud Guillon
"""Shapes shared by the elite models (the five elite kinds, specs/enemies/*.md).

Logical pixels, nose +Z, Y up; a design point (x, y) facing down the screen is model (-x, height,
-y) (`boss_point`).
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[float]
type Rgb = list[float]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]  # type: Rgb
QUARTER = math.pi / 2


def ahead(at: Vec3, yaw: float, d: float) -> list[float]:
    """Return the point `d` from `at` along `yaw`, at the same height.

    `yaw` is in radians from +Z towards +X.
    """
    return [at[0] + math.sin(yaw) * d, at[1], at[2] + math.cos(yaw) * d]


def barrel(p: Any, tip: Vec3, yaw: float, size: Any, kind: str = "gun") -> None:
    """Add a gun barrel pointing `yaw`, ending at `tip`, `radius` thick and `length` long.

    Dark steel, with a charge light at its mouth (the drones' and the cannons' charge lights,
    ENM-ORBITER-04, ENM-JUGGERNAUT-04), and the muzzle (`kind`) marked at the tip.
    """
    radius = size[0]
    length = size[1]

    def place(back: float) -> Placement:
        return Placement(ahead(tip, yaw, -back), yaw, QUARTER)

    p.hull.cylinder(radius, length, 6, H.dark, place(length + 0.5))
    p.charge.cylinder(radius * 1.08, 0.5, 6, WHITE, place(0.5))
    p.muzzle(tip, kind)


def strip(neon: Any, at: Vec3, yaw: float, span: Any, color: Rgb) -> None:
    """Add a neon strip `length` long, centred `d` from `at` along `yaw`, `width` wide."""
    d = span[0]
    length = span[1]
    width = span[2]
    xyz = ahead(at, yaw, d)
    neon.box([width, 0.5, length], color, Placement(xyz, yaw))
