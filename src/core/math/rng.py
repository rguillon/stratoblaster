# Copyright (c) 2026 Renaud Guillon
"""Seeded pseudo-random numbers.

The generator is mulberry32 (ENG-18), written on unsigned 32-bit integers (see `bits.py`), so a
seed gives the same sequence, in the game and in the tests (ENG-46).
"""

from core.math.bits import imul, u32, ushr, xor

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence

Random = Callable[[], float]
# __pragma__ ("noskip")


U32 = 4294967296


def create_rng(seed: int) -> Random:
    """Return a generator whose values lie in [0, 1); the same seed gives the same sequence."""
    state = [u32(seed)]

    def next_value() -> float:
        state[0] = (state[0] + 0x6D2B79F5) % U32
        t = state[0]
        t = imul(xor(t, ushr(t, 15)), t | 1)
        t = xor(t, u32(t + imul(xor(t, ushr(t, 7)), t | 61)))
        return xor(t, ushr(t, 14)) / U32

    return next_value


def random_in(random: Random, low: float, high: float) -> float:
    """Return a number in [low, high)."""
    return low + (high - low) * random()


def pick[T](random: Random, items: Sequence[T]) -> T:
    """One of `items`, chosen uniformly."""
    if len(items) == 0:
        msg = "Cannot pick from an empty list"
        raise ValueError(msg)
    return items[int(random() * len(items))]
