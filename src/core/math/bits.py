"""32-bit integer helpers: JavaScript's `>>>`, `Math.imul` and `^` in pure arithmetic.

JavaScript bit operators work on signed 32-bit values. The helpers below take any integer
and return the unsigned 32-bit result, so the port matches the TypeScript bit by bit.
"""

U32 = 4294967296


def u32(value: int) -> int:
    """`value >>> 0`: the 32-bit pattern of `value` as an unsigned integer."""
    return (value % U32 + U32) % U32


def xor(a: int, b: int) -> int:
    """`a ^ b` as an unsigned 32-bit integer."""
    return u32(a ^ b)


def ushr(value: int, shift: int) -> int:
    """`value >>> shift` for a 32-bit `value` (`shift` below 31)."""
    return u32(value) // (1 << shift)


def imul(a: int, b: int) -> int:
    """`Math.imul(a, b)` as an unsigned 32-bit integer.

    The product is built from 16-bit halves so every intermediate stays below 2**53 and is
    exact in a JavaScript number.
    """
    a = u32(a)
    b = u32(b)
    a_low = a % 65536
    a_high = a // 65536
    b_low = b % 65536
    b_high = b // 65536
    cross = (a_high * b_low + a_low * b_high) % 65536
    return (a_low * b_low + cross * 65536) % U32
