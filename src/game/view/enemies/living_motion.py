"""The living motion of the enemy models (ENM-42), visual only (ENM-45)"""

import math

from game.config.enemy_look import ENEMY_LOOK

# The breathing of a creature (ENM-44): every model of one creature (a boss's core, parts and
# limbs, BOSS-51) shares one, so it breathes as one body.


class Breath:
    """A breath: its phase and period. It only sets the phase of the veins' pulse: the body never
    swells (ENM-43)."""

    def __init__(self, phase: float, period: float) -> None:
        self.phase = phase
        self.period = period


# Module state: the breaths made so far, and whether the living motion is on.
_BREATHS = [0]  # type: list[float]
_LIVING_MOTION = [True]


def new_breath() -> Breath:
    """A new breath, its period and phase spread from one creature to the next (ENM-44)."""
    breathing = ENEMY_LOOK.living.breathing
    period = breathing.period
    spread = breathing.spread
    # A golden-ratio sequence: deterministic, evenly spread.
    k = (_BREATHS[0] * 0.618034) % 1
    _BREATHS[0] += 1
    return Breath(2 * math.pi * k, period * (1 + spread * (2 * k - 1)))


def set_living_motion(on: bool) -> None:
    """Turns the living motion on or off (a debug toggle): off, bodies hold still at rest."""
    _LIVING_MOTION[0] = on


def is_living_motion() -> bool:
    return _LIVING_MOTION[0]


def glow_level(breath: Breath, time: float) -> float:
    """The veins' brightness at `time` (ENM-42; the eyes and glands lit as veins, GFX-ART-14),
    from `low` to 1."""
    glow = ENEMY_LOOK.living.glow
    period = glow.period
    low = glow.low
    wave = 0.5 + 0.5 * math.sin((2 * math.pi * time) / period + breath.phase)
    level: float = low + (1 - low) * wave
    return level


def flutter_angle(side: float, span: float, time: float, phase: float = 0) -> float:
    """A wing's roll at `time` (ENM-42): `side` up then down, slower for big wings."""
    flutter = ENEMY_LOOK.living.flutter
    f = flutter.bigHz if span > flutter.bigSpan else flutter.hz
    roll: float = -side * flutter.angle * math.sin(2 * math.pi * f * time + phase)
    return roll
