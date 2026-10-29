"""The bosses' angry patterns (phase 7 review), ported from `config/bosses/boss-rage.ts`.

The bullet hell a boss fires from its core for `BOSS_TIMING.rageSeconds` after the pause that
follows each destroyed part. `heat` goes from 0 (1-1's mini boss) to 4.5 (1-5's final boss): about
20 → 56 bullets a second, a little faster each level, but slower than the stages' bullets
(120 → 156 px/s) and with lanes between them, so a kid in 1-1 can still weave through. `share` is
the part of that rate a pattern fires, for a boss firing two of them.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, volley
from game.config.record import concat, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def rate(heat: float, share: float) -> float:
    """Bullets a second at `heat`."""
    return (20 + 8 * heat) * share


def arms(heat: float) -> int:
    """Bullets in a ring at `heat`."""
    return 5 + math.floor(heat * 0.7 + 0.5)


def angry(style: str, heat: float) -> Any:
    """A slow bullet of `style` for the angry patterns, at `heat`."""
    return bullet(style, 120 + 8 * heat, 4)


def _spirals(heat: float, a: str, b: str, share: float = 1) -> Any:
    """Two spirals turning opposite ways from the core, crossing as they go."""
    every = (2 * arms(heat)) / rate(heat, share)
    return [
        volley.ring("core", every, arms(heat), 13, angry(a, heat), 0.05),
        volley.ring("core", every, arms(heat), -17, angry(b, heat), 0.05 + every / 2),
    ]


def _flower(heat: float, a: str, b: str, share: float = 1) -> Any:
    """A dense, slowly turning ring blooming from the core, and small fans at the player."""
    petals = arms(heat) * 2 + 2
    every = (petals + 1.5) / rate(heat, share)
    return [
        volley.ring("core", every, petals, 9, angry(a, heat), 0.05),
        volley.aimed("core", every * 2, 3, 14, angry(b, heat), 0.3),
    ]


def _curtain(heat: float, a: str, b: str, share: float = 1) -> Any:
    """Fans sweeping across the screen and back, a ring under them."""
    ring = arms(heat) + 3
    sweep = (24 + 2 * ring) / rate(heat, share)
    fans = [
        volley.fan("core", sweep, 3, 7, angry(a, heat), 0.05 + (sweep * i) / 8, heading)
        for i, heading in enumerate([-40, -20, 0, 20, 40, 20, 0, -20])
    ]
    return concat(fans, [volley.ring("core", sweep / 2, ring, 11, angry(b, heat), 0.2)])


def _vortex(heat: float, a: str, b: str, share: float = 1) -> Any:
    """One fast-turning spiral, and bursts at the player."""
    spiral = max(3, arms(heat) - 2)
    every = (spiral + 0.5) / rate(heat, share)
    return [
        volley.ring("core", every, spiral, 23, angry(a, heat), 0.05),
        volley.burst("core", every * 6, 3, 0.12, angry(b, heat), 0.5),
    ]


rage = record(
    {
        "spirals": _spirals,
        "flower": _flower,
        "curtain": _curtain,
        "vortex": _vortex,
    }
)
