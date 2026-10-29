"""Seeded pseudo-random numbers, ported from `core/math/rng.ts`.

The generator is mulberry32, written on unsigned 32-bit integers, so a seed gives the same
sequence as the TypeScript version. JavaScript bit operators work on signed 32-bit values,
so their results are wrapped back into [0, 2**32) by `_u32`.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import TypeVar  # noqa: E402

Random = Callable[[], float]
T = TypeVar("T")
__pragma__("noskip")

U32 = 4294967296


def _u32(value: int) -> int:
    """`value` as an unsigned 32-bit integer (`value >>> 0`)."""
    return (value % U32 + U32) % U32


def _xor(a: int, b: int) -> int:
    return _u32(a ^ b)


def _ushr(value: int, shift: int) -> int:
    """`value >>> shift` for an unsigned 32-bit `value`."""
    return value // (1 << shift)


def _imul(a: int, b: int) -> int:
    """`Math.imul(a, b)` as an unsigned 32-bit integer.

    The product is built from 16-bit halves so every intermediate stays below 2**53 and
    is exact in a JavaScript number.
    """
    a = _u32(a)
    b = _u32(b)
    a_low = a % 65536
    a_high = a // 65536
    b_low = b % 65536
    b_high = b // 65536
    cross = (a_high * b_low + a_low * b_high) % 65536
    return (a_low * b_low + cross * 65536) % U32


def create_rng(seed: int) -> Random:
    """A generator whose values lie in [0, 1); the same seed gives the same sequence."""
    state = [_u32(seed)]

    def next_value() -> float:
        state[0] = (state[0] + 0x6D2B79F5) % U32
        t = state[0]
        t = _imul(_xor(t, _ushr(t, 15)), t | 1)
        t = _xor(t, _u32(t + _imul(_xor(t, _ushr(t, 7)), t | 61)))
        return _xor(t, _ushr(t, 14)) / U32

    return next_value


def random_in(random: Random, low: float, high: float) -> float:
    """A number in [low, high)."""
    return low + (high - low) * random()


def pick(random: Random, items: Sequence[T]) -> T:  # noqa: UP047 (Transcrypt has no PEP 695)
    """One of `items`, chosen uniformly."""
    if len(items) == 0:
        raise ValueError("Cannot pick from an empty list")
    return items[int(random() * len(items))]
