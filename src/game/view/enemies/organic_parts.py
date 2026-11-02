# Copyright (c) 2026 Renaud Guillon
"""GFX-ART-12: the Cyber-Organic pieces every enemy and boss model shares.

They are built from the engine's organic shape kit (GFX-ART-17). Logical pixels, nose +Z, Y up.
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from render.geometry.organic import curve, organ, vein
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[float]
type Rgb = list[float]
# __pragma__ ("noskip")


F = ENEMY_LOOK.flesh


def opt(options: Any, key: str, default: Any) -> Any:
    """`options.key ?? default` for an options object that may leave the key out."""
    if key in options:
        return options[key]
    return default


def reactor_sac(
    parts: Any, at: Vec3, radius: float, glow: Rgb, flesh: Any = None, vein_length: Any = None
) -> None:
    """Add a reactor set in a glowing organ (ENM-40).

    A flesh sac swells around its nozzle at `at` (thrusting towards -Z), a gland is lit on its back,
    and a vein runs from it `vein` forward.
    """
    if flesh is None:
        flesh = F.slate
    if vein_length is None:
        vein_length = radius * 3
    x = at[0]
    y = at[1]
    z = at[2]
    # A sac lying along Z around the nozzle, its mouth at `at`.
    organ(
        parts.flesh,
        radius * 1.35,
        6,
        flesh,
        Placement([x, y, z + radius * 0.2], 0, math.pi / 2),
        0.9,
    )
    parts.reactor(at, radius)
    back = [x, y + radius * 1.2, z + radius * 1.2]
    vein(
        parts.vein,
        curve(
            back,
            [x, y + radius * 0.9, z + radius * 1.2 + vein_length],
            [0, radius * 0.4, 0],
            2,
        ),
        radius * 0.35,
        glow,
    )


def eyes(parts: Any, at: Vec3, options: Any, glow: Rgb) -> None:
    """Add a cluster of `count` eyes across `at` (GFX-ART-14), `size` each, `spacing` apart.

    They are lit as veins.
    """
    count = opt(options, "count", 2)
    size = opt(options, "size", 0.6)
    spacing = opt(options, "spacing", 1.4)
    for i in range(count):
        x = at[0] + (i - (count - 1) / 2) * spacing
        organ(parts.vein, size, 5, glow, Placement([x, at[1], at[2]]), 0.7)
