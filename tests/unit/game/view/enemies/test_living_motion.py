"""Unit tests of `src/game/view/enemies/living_motion.py`."""

import math

import pytest

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import living_motion
from game.view.enemies.living_motion import (
    Breath,
    breath_scale,
    flutter_angle,
    glow_level,
    is_living_motion,
    new_breath,
    set_living_motion,
)


@pytest.fixture(autouse=True)
def fresh_state(monkeypatch):
    """Each test starts with no breaths made and the living motion on."""
    monkeypatch.setattr(living_motion, "_BREATHS", [0])
    monkeypatch.setattr(living_motion, "_LIVING_MOTION", [True])


def test_p16_r07_first_breath_takes_the_bottom_of_the_period_spread():
    breathing = ENEMY_LOOK.living.breathing
    first = new_breath()
    # k = 0 for the first creature: phase 0, period cut by the full spread.
    assert first.phase == pytest.approx(0)
    assert first.period == pytest.approx(breathing.period * (1 - breathing.spread))


def test_p16_r07_breaths_are_deterministic_and_evenly_spread():
    breathing = ENEMY_LOOK.living.breathing
    breaths = [new_breath() for _ in range(5)]
    phases = [b.phase for b in breaths]
    # Each phase is a fraction of a turn, and no two creatures share one.
    assert all(0 <= p < 2 * math.pi for p in phases)
    assert len({round(p, 9) for p in phases}) == 5
    for b in breaths:
        assert breathing.period * (1 - breathing.spread) <= b.period
        assert b.period <= breathing.period * (1 + breathing.spread) + 1e-9


def test_p16_r07_the_breath_sequence_restarts_when_its_state_is_reset(monkeypatch):
    first = [new_breath().phase for _ in range(3)]
    monkeypatch.setattr(living_motion, "_BREATHS", [0])
    again = [new_breath().phase for _ in range(3)]
    assert first == pytest.approx(again)


def test_p16_r07_breath_scale_swells_by_the_amplitude_at_a_quarter_period():
    amplitude = ENEMY_LOOK.living.breathing.amplitude
    breath = Breath(phase=0, period=4.0)
    assert breath_scale(breath, 0) == pytest.approx(1)
    assert breath_scale(breath, 1.0) == pytest.approx(1 + amplitude)
    assert breath_scale(breath, 3.0) == pytest.approx(1 - amplitude)


def test_p16_r07_breath_scale_follows_the_phase():
    amplitude = ENEMY_LOOK.living.breathing.amplitude
    # A half turn of phase is a half turn of the swell: at time 0 the scale is at its peak.
    breath = Breath(phase=math.pi / 2, period=2.0)
    assert breath_scale(breath, 0) == pytest.approx(1 + amplitude)


def test_p16_r07_glow_stays_between_low_and_full_brightness():
    glow = ENEMY_LOOK.living.glow
    breath = Breath(phase=0, period=glow.period)
    samples = [glow_level(breath, glow.period * i / 50) for i in range(50)]
    assert min(samples) == pytest.approx(glow.low, abs=0.02)
    assert max(samples) == pytest.approx(1, abs=0.02)
    assert all(glow.low - 1e-9 <= s <= 1 + 1e-9 for s in samples)


def test_p16_r07_glow_is_at_full_brightness_at_the_peak_of_the_wave():
    glow = ENEMY_LOOK.living.glow
    # At time 0 with no phase the wave is at its midpoint, so the level is halfway.
    assert glow_level(Breath(0, glow.period), 0) == pytest.approx((glow.low + 1) / 2)


@pytest.mark.parametrize("span_big", [True, False])
def test_p16_r07_flutter_rolls_by_side_and_uses_the_slower_beat_for_big_wings(span_big):
    flutter = ENEMY_LOOK.living.flutter
    span = flutter.bigSpan + 1 if span_big else flutter.bigSpan - 1
    hz = flutter.bigHz if span_big else flutter.hz
    t = 0.1
    # A left wing (side -1) rolls up first: the sign is -side.
    expected = flutter.angle * math.sin(2 * math.pi * hz * t)
    assert flutter_angle(-1, span, t) == pytest.approx(expected)
    # The right wing flaps the other way.
    assert flutter_angle(1, span, t) == pytest.approx(-expected)


def test_p16_r07_flutter_angle_is_zero_at_rest_and_honours_a_phase():
    assert flutter_angle(1, 0, 0) == pytest.approx(0)
    flutter = ENEMY_LOOK.living.flutter
    assert flutter_angle(1, 0, 0, phase=math.pi / 2) == pytest.approx(-flutter.angle)


def test_p16_r10_living_motion_switch_can_be_turned_off_and_on_again():
    assert is_living_motion() is True
    set_living_motion(False)
    assert is_living_motion() is False
    set_living_motion(True)
    assert is_living_motion() is True
