"""How a boss rolls into its sideways moves

See `BossStats.roll` (phase 7 review).
"""

import math


class BossRoll:
    """How far a boss rolls, how fast, and how quickly it eases into the roll."""

    def __init__(self, max_deg: float, full_speed: float, ease_per_sec: float) -> None:
        self.max_deg = max_deg
        self.full_speed = full_speed
        self.ease_per_sec = ease_per_sec


def roll_towards(rule: BossRoll, roll: float, vx: float, dt: float) -> float:
    """Its roll after `dt` seconds moving across at `vx` px/s: easing from `roll` towards
    `rule.max_deg` at `rule.full_speed`, in proportion below it.
    """
    limit = (rule.max_deg * math.pi) / 180
    target = max(-limit, min(limit, (vx / rule.full_speed) * limit))
    return roll + (target - roll) * min(1, rule.ease_per_sec * dt)
