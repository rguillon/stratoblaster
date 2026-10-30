"""Seeded pseudo-random numbers (`core.math.rng`)."""

import pytest

from core.math.rng import create_rng, pick, random_in


def _mulberry32(seed: int) -> list[float]:
    """An independent reference of mulberry32, on plain Python integers, for the first values."""
    state = seed & 0xFFFFFFFF
    out: list[float] = []
    for _ in range(5):
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = state
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t = (t ^ ((t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        out.append(((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296)
    return out


def test_same_seed_gives_the_same_sequence() -> None:
    a = create_rng(12345)
    b = create_rng(12345)
    assert [a() for _ in range(20)] == [b() for _ in range(20)]


def test_different_seeds_give_different_sequences() -> None:
    a = create_rng(1)
    b = create_rng(2)
    assert [a() for _ in range(5)] != [b() for _ in range(5)]


def test_values_lie_in_zero_one() -> None:
    random = create_rng(7)
    values = [random() for _ in range(1000)]
    assert all(0 <= v < 1 for v in values)


def test_sequence_matches_the_mulberry32_reference() -> None:
    random = create_rng(42)
    assert [random() for _ in range(5)] == pytest.approx(_mulberry32(42), abs=0)


def test_negative_seed_is_read_as_its_unsigned_pattern() -> None:
    a = create_rng(-1)
    b = create_rng(0xFFFFFFFF)
    assert [a() for _ in range(3)] == [b() for _ in range(3)]


def test_random_in_maps_the_unit_interval_onto_the_range() -> None:
    assert random_in(lambda: 0.0, 10, 20) == pytest.approx(10)
    assert random_in(lambda: 0.5, 10, 20) == pytest.approx(15)


def test_pick_chooses_by_the_unit_value() -> None:
    items = ["a", "b", "c"]
    assert pick(lambda: 0.0, items) == "a"
    assert pick(lambda: 0.5, items) == "b"
    assert pick(lambda: 0.999, items) == "c"


def test_pick_from_an_empty_list_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        pick(lambda: 0.5, [])
