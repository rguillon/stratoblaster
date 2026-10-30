"""32-bit integer helpers: JavaScript's `>>>`, `Math.imul` and `^` in pure arithmetic.

JavaScript bit operators work on signed 32-bit values. The helpers below take any integer
and return the unsigned 32-bit result, so the results match JavaScript bit by bit.
"""

from org.transcrypt.stubs.browser import __pragma__  # noqa: E402

U32 = 4294967296


# Each helper has its Python twin in a `skip` block: Transcrypt compiles the JavaScript only, and
# CPython (the unit tests) runs the twin. The two agree on 32-bit values (tests/unit).


def u32(value: int) -> int:
    """`value >>> 0`: the 32-bit pattern of `value` as an unsigned integer."""
    r = 0
    __pragma__("skip")
    r = value & 0xFFFFFFFF
    __pragma__("noskip")
    __pragma__("js", "{}", "r = value >>> 0;")
    return r


def xor(a: int, b: int) -> int:
    """`a ^ b` as an unsigned 32-bit integer."""
    r = 0
    __pragma__("skip")
    r = (a ^ b) & 0xFFFFFFFF
    __pragma__("noskip")
    __pragma__("js", "{}", "r = (a ^ b) >>> 0;")
    return r


def ushr(value: int, shift: int) -> int:
    """`value >>> shift` for a 32-bit `value` (`shift` below 31)."""
    r = 0
    __pragma__("skip")
    r = (value & 0xFFFFFFFF) >> shift
    __pragma__("noskip")
    __pragma__("js", "{}", "r = value >>> shift;")
    return r


def _signed(value: int) -> int:
    """The signed 32-bit value of the pattern `value` (as JavaScript's `|0` reads it)."""
    v = value & 0xFFFFFFFF
    return v - U32 if v >= U32 // 2 else v


def imul(a: int, b: int) -> int:
    """`Math.imul(a, b)` as an unsigned 32-bit integer: JavaScript's own, exact on whole numbers
    (the hash runs for every random number, so Transcrypt's arithmetic is too slow here)."""
    r = 0
    __pragma__("skip")
    r = (_signed(a) * _signed(b)) & 0xFFFFFFFF
    __pragma__("noskip")
    __pragma__("js", "{}", "r = Math.imul(a, b) >>> 0;")
    return r
