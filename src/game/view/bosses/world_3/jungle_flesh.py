# Copyright (c) 2026 Renaud Guillon
"""BOSS-47, GFX-ART-12: the Cyber-Organic pieces of the World 3 bosses (the jungle and its river).

Living bodies grown over by the jungle, metal grafted on. Logical pixels, nose +Z, Y up.
"""

from game.config.enemy_look import ENEMY_LOOK

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from game.config.record import record
from render.geometry.organic import RibSpec, curve, organ, ribs, tendril, vein
from render.geometry.solids import Placement

# isort: split
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Rgb = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The flesh shades (GFX-ART-15).
F = ENEMY_LOOK.flesh

# A jungle-green flesh, dark enough for the ground (GFX-ART-06): moss-skinned bodies.
JUNGLE_FLESH = [0.05, 0.1, 0.045]


def table(rows: Any) -> Any:
    """Return a constant table of numbers, or a list handed to an enemy helper.

    Identity at run time: mypy would join its int and float rows to `list[object]`, and the enemy
    helpers type their points as tuples where the render helpers use lists (both are JavaScript
    arrays).
    """
    return rows


def sign_of(x: float) -> int:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def spine(p: EnemyParts, path: list[Vec3], arches: Any, glow: Rgb) -> None:
    """Add a spine down a back (GFX-ART-12): a pulsing vein along `path`, and rib arches.

    At each of `arches.at` (z), a rib arch `arches.halfWidth` out over it from `arches.y`, in bone.
    """
    arches = record(arches)
    vein(p.vein, path, 1.2, glow)
    ribs(
        p.flesh,
        arches.at,
        RibSpec(arches.halfWidth, arches.y, arches.height, 0.7),
        F.bone,
    )


def gland(p: EnemyParts, at: Vec3, radius: float, glow: Rgb) -> None:
    """Add a glowing gland (GFX-ART-14) of `radius` sitting at `at`, pulsing with the veins."""
    organ(p.vein, radius, 5, glow, Placement(at), 0.6)


def sac(p: EnemyParts, at: Vec3, radius: float, color: Rgb, stretch: float = 0.7) -> None:
    """Add a swollen flesh sac (GFX-ART-12) of `radius` at `at`, `stretch` times as tall."""
    organ(
        p.flesh,
        radius,
        6,
        color,
        Placement([at[0], at[1] - radius * stretch, at[2]]),
        stretch,
    )


def sinew(
    p: EnemyParts,
    ends: list[Vec3],
    bow: Vec3,
    radius: float,
    color: Rgb = F.sinew,
) -> None:
    """Add a sinew from `ends[0]` to `ends[1]` bowed by `bow`.

    A tapering flesh tendril, `radius` thick.
    """
    tendril(p.flesh, curve(ends[0], ends[1], bow, 3), [radius, radius * 0.4], 4, color)


def vein_to(
    p: EnemyParts,
    ends: list[Vec3],
    bow: Vec3,
    glow: Rgb,
    width: float = 0.9,
) -> None:
    """Add a vein from `ends[0]` to `ends[1]` bowed by `bow`, `width` across, pulsing (BOSS-51)."""
    vein(p.vein, curve(ends[0], ends[1], bow, 3), width, glow)
