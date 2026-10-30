"""Unit tests of `src/game/view/reactor_flame.py`."""

import math

import pytest

from game.view import reactor_flame
from game.view.reactor_flame import (
    _around,
    _dimmed,
    flicker,
    puff_opacity,
    puff_progress,
    reactor_phase,
)


@pytest.fixture(autouse=True)
def python_bit_helpers(monkeypatch):
    """`Math.imul` and `charCodeAt` are JavaScript: their Python equivalents here."""

    def imul(a, b):
        value = (a * b) & 0xFFFFFFFF
        return value - 2**32 if value >= 2**31 else value

    monkeypatch.setattr(reactor_flame, "_imul", imul)
    monkeypatch.setattr(reactor_flame, "_char_code", lambda text, index: ord(text[index]))


def test_the_flicker_is_the_mean_of_its_sines_in_the_unit_range():
    value = flicker(0.37, 1.2, [1.0, 2.5, 4.0])
    assert -1 <= value <= 1
    expected = (
        sum(math.sin(2 * math.pi * f * 0.37 + 1.2 * (i + 1)) for i, f in enumerate([1.0, 2.5, 4.0]))
        / 3
    )
    assert value == pytest.approx(expected)


def test_a_flicker_without_frequencies_is_still():
    assert flicker(5.0, 1.0, []) == 0


def test_a_flicker_with_one_frequency_is_a_sine():
    assert flicker(0.25, 0.0, [1.0]) == pytest.approx(1.0)


def test_reactors_of_different_names_do_not_flicker_in_step():
    a = reactor_phase("player-engine-left")
    b = reactor_phase("player-engine-right")
    assert 0 <= a < 2 * math.pi
    assert a != b


def test_a_reactors_phase_is_stable_for_its_name():
    assert reactor_phase("flame") == reactor_phase("flame")


def test_a_puff_travels_down_the_exhaust_and_starts_again():
    assert puff_progress(0.0, 0, 4, 1.0) == 0
    assert puff_progress(0.5, 0, 4, 1.0) == pytest.approx(0.5)
    assert puff_progress(0.0, 1, 4, 1.0) == pytest.approx(0.25)
    assert 0 <= puff_progress(123.456, 3, 4, 2.0) < 1


def test_a_puff_fades_in_near_the_nozzle_and_out_at_the_tip():
    assert puff_opacity(0) == 0
    assert puff_opacity(1) == 0
    assert puff_opacity(0.5) > 0
    assert puff_opacity(0.5) > puff_opacity(0.95)


def test_a_puff_is_at_most_fully_opaque():
    assert max(puff_opacity(p / 100) for p in range(101)) <= 1


def test_the_flicker_maps_to_a_factor_around_one():
    assert _around(0, 0.2) == 1
    assert _around(1, 0.2) == pytest.approx(1.2)
    assert _around(-1, 0.2) == pytest.approx(0.8)


def test_the_flicker_maps_to_a_visibility_that_only_dims():
    assert _dimmed(1, 0.5) == pytest.approx(1)
    assert _dimmed(-1, 0.5) == pytest.approx(0.5)
    assert _dimmed(0, 0.5) == pytest.approx(0.75)
