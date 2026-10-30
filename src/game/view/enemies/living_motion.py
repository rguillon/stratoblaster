"""The living motion of the enemy models (P16-R07), visual only"""

import math

from game.config.enemy_look import ENEMY_LOOK

# The breathing of a creature (P16-R07): every model of one creature (a boss's core, parts and
# limbs) shares one, so it breathes as one body.


class Breath:
    """A breath: its phase and period (P16-R07)."""

    def __init__(self, phase: float, period: float) -> None:
        self.phase = phase
        self.period = period


# Module state: the breaths made so far, and whether the living motion is on.
_BREATHS = [0]  # type: list[float]
_LIVING_MOTION = [True]


def new_breath() -> Breath:
    """A new breath, its period and phase spread from one creature to the next (P16-R07)."""
    breathing = ENEMY_LOOK.living.breathing
    period = breathing.period
    spread = breathing.spread
    # A golden-ratio sequence: deterministic, evenly spread.
    k = (_BREATHS[0] * 0.618034) % 1
    _BREATHS[0] += 1
    return Breath(2 * math.pi * k, period * (1 + spread * (2 * k - 1)))


def set_living_motion(on: bool) -> None:
    """Turns the living motion on or off (P16-R10, debug pages): off, bodies hold still at rest."""
    _LIVING_MOTION[0] = on


def is_living_motion() -> bool:
    return _LIVING_MOTION[0]


def breath_scale(breath: Breath, time: float) -> float:
    """The body's scale at `time` (P16-R07)."""
    a = ENEMY_LOOK.living.breathing.amplitude
    return float(1 + a * math.sin((2 * math.pi * time) / breath.period + breath.phase))


def glow_level(breath: Breath, time: float) -> float:
    """The veins' brightness at `time` (P16-R07), from `low` to 1."""
    glow = ENEMY_LOOK.living.glow
    period = glow.period
    low = glow.low
    wave = 0.5 + 0.5 * math.sin((2 * math.pi * time) / period + breath.phase)
    level: float = low + (1 - low) * wave
    return level


def flutter_angle(side: float, span: float, time: float, phase: float = 0) -> float:
    """A wing's roll at `time` (P16-R07): `side` up then down, slower for big wings."""
    flutter = ENEMY_LOOK.living.flutter
    f = flutter.bigHz if span > flutter.bigSpan else flutter.hz
    roll: float = -side * flutter.angle * math.sin(2 * math.pi * f * time + phase)
    return roll
