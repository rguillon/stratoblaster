"""P16-R01: the Cyber-Organic pieces every enemy and boss model shares, ported from
`enemies/organic-parts.ts`. Logical pixels, nose +Z, Y up."""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from render.geometry.organic import curve, organ, vein  # noqa: E402

F = ENEMY_LOOK.flesh


def opt(options: Any, key: str, default: Any) -> Any:
    """`options.key ?? default` for an options object that may leave the key out."""
    if key in options:
        return options[key]
    return default


def reactor_sac(
    parts: Any, at: Vec3, radius: float, glow: Rgb, flesh: Any = None, vein_length: Any = None
) -> None:
    """A reactor set in a glowing organ (P16-R01): a flesh sac swelling around its nozzle at `at`
    (thrusting towards -Z), a gland lit on its back and a vein running from it `vein` forward."""
    if flesh is None:
        flesh = F.crimson
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
    """A cluster of `count` eyes across `at` (P16-R01), `size` each, `spacing` apart,
    lit as veins."""
    count = opt(options, "count", 2)
    size = opt(options, "size", 0.6)
    spacing = opt(options, "spacing", 1.4)
    for i in range(count):
        x = at[0] + (i - (count - 1) / 2) * spacing
        organ(parts.vein, size, 5, glow, Placement([x, at[1], at[2]]), 0.7)
