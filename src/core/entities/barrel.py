# Copyright (c) 2026 Renaud Guillon
"""A gun's barrel: where it points, and how far it is thrown back by a shot (WPN-01, WPN-03)."""

import math

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from core.entities.muzzle import Muzzle  # noqa: TC001

# __pragma__ ("noskip")

DEG = math.pi / 180
INFINITY = float("Infinity")

# How long a barrel takes to slide back out after a shot (WPN-03), seconds.
RECOIL_SECONDS = 0.18


class Barrel:
    """One barrel of a gun: its muzzle, the way it points on its body and its recoil.

    `muzzle` is the barrel's tip (see `muzzle.py`). `angle` is the way it points, radians from the
    body's nose, positive to the right as headings are: a fixed barrel fires only that way, and its
    shots leave along it (WPN-01). None for a gun that still aims its shots at will (not converted
    to barrels yet).
    """

    def __init__(self, entry: list[float], recoil_seconds: float = RECOIL_SECONDS) -> None:
        """`entry` is `[x, y, height]`, then optionally the barrel's angle in degrees."""
        self.muzzle: Muzzle = (entry[0], entry[1], entry[2])
        self.angle: float | None = entry[3] * DEG if len(entry) > 3 else None
        self.recoil_seconds = recoil_seconds
        # The `age` of the body when it last fired, None before.
        self.fired_at: float | None = None

    def kick(self, now: float) -> None:
        """Record a shot fired at `now`: the barrel is thrown back (recoil 1) and slides out."""
        self.fired_at = now

    def since_fired(self, now: float) -> float:
        """Return the seconds since it last fired at `now`, Infinity before its first shot."""
        if self.fired_at is None:
            return INFINITY
        return now - self.fired_at

    def recoil_at(self, now: float) -> float:
        """Return the recoil at `now`: 1 as it fires, easing down to 0 after `recoil_seconds`."""
        if self.fired_at is None:
            return 0
        t = (now - self.fired_at) / self.recoil_seconds
        if t >= 1 or t < 0:
            return 0
        return (1 - t) * (1 - t)
