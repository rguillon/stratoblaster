"""32-bit helpers (`core.math.bits`): the JavaScript operators in Python arithmetic."""

from core.math.bits import imul, u32, ushr, xor


def test_u32_is_the_unsigned_pattern_of_a_signed_value() -> None:
    assert u32(-1) == 0xFFFFFFFF
    assert u32(5) == 5
    assert u32(0x1_0000_0005) == 5


def test_xor_is_unsigned_and_matches_javascript() -> None:
    assert xor(-1, 5) == 0xFFFFFFFA
    assert xor(6, 3) == 5


def test_ushr_shifts_the_unsigned_pattern() -> None:
    assert ushr(-1, 3) == 0x1FFFFFFF
    assert ushr(16, 2) == 4


def test_imul_wraps_like_math_imul() -> None:
    assert imul(0x7FFFFFFF, 3) == 2147483645
    assert imul(-5, 7) == (-35) & 0xFFFFFFFF
    assert imul(1 << 20, 1 << 20) == 0
