"""A turret on a boss's piece, ported from `core/entities/boss-turret.ts` (phase 7 review).

Its guns' muzzles turn with it around its pivot, so that the barrels the player sees point the
way it aims.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.entities.muzzle import Muzzle  # noqa: E402

__pragma__("noskip")


class BossTurretSpec:
    """A turret's pivot and how fast it turns."""

    def __init__(
        self,
        x: float,
        y: float,
        turn_rate_deg: float,
        laser_turn_rate_deg: float | None = None,
    ) -> None:
        """`x` and `y` are its pivot, from the boss's centre (X right, Y up), as the boss is drawn.
        `turn_rate_deg` is how many degrees a second it turns at, at most. `laser_turn_rate_deg`
        is how many degrees a second it follows the player at while a laser's warning line shows
        (phase 8 review: slow enough to outrun); `turn_rate_deg` when None.
        """
        self.x = x
        self.y = y
        self.turn_rate_deg = turn_rate_deg
        self.laser_turn_rate_deg = laser_turn_rate_deg


class BossTurret:
    """A turret of a boss's piece, and how far it has turned (see `BossTurretSpec`)."""

    def __init__(self, spec: BossTurretSpec) -> None:
        self.spec = spec
        # How far it has turned from its rest (barrels straight down): radians, clockwise on
        # screen.
        self.aim = 0

    def turned(self, muzzle: Muzzle) -> Muzzle:
        """`muzzle` (from the boss's centre, as drawn at rest) turned with it around its pivot."""
        mx, my, mh = muzzle
        c, s = math.cos(self.aim), math.sin(self.aim)
        dx, dy = mx - self.spec.x, my - self.spec.y
        return (self.spec.x + dx * c + dy * s, self.spec.y - dx * s + dy * c, mh)
