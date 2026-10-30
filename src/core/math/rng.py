"""Seeded pseudo-random numbers, ported from `core/math/rng.ts`.

The generator is mulberry32, written on unsigned 32-bit integers (see `bits.py`), so a seed
gives the same sequence as the TypeScript version.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import TypeVar  # noqa: E402

Random = Callable[[], float]
T = TypeVar("T")
__pragma__("noskip")

from core.math.bits import imul, u32, ushr, xor  # noqa: E402

U32 = 4294967296


def create_rng(seed: int) -> Random:
    """A generator whose values lie in [0, 1); the same seed gives the same sequence."""
    state = [u32(seed)]

    def next_value() -> float:
        state[0] = (state[0] + 0x6D2B79F5) % U32
        t = state[0]
        t = imul(xor(t, ushr(t, 15)), t | 1)
        t = xor(t, u32(t + imul(xor(t, ushr(t, 7)), t | 61)))
        return xor(t, ushr(t, 14)) / U32

    return next_value


def random_in(random: Random, low: float, high: float) -> float:
    """A number in [low, high)."""
    return low + (high - low) * random()


def pick(random: Random, items: Sequence[T]) -> T:  # noqa: UP047 (Transcrypt has no PEP 695)
    """One of `items`, chosen uniformly."""
    if len(items) == 0:
        raise ValueError("Cannot pick from an empty list")
    return items[int(random() * len(items))]
