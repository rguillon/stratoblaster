"""Unit tests of `src/core/loop/fixed_step_clock.py`."""

import pytest

from core.loop.fixed_step_clock import FixedStepClock


def test_step_seconds_is_the_inverse_of_the_rate() -> None:
    assert FixedStepClock(hz=10, max_steps_per_frame=5).step_seconds == pytest.approx(0.1)


@pytest.mark.parametrize(("hz", "max_steps"), [(0, 5), (-1, 5), (10, 0), (10, -2)])
def test_bad_settings_raise(hz: float, max_steps: int) -> None:
    with pytest.raises(ValueError):
        FixedStepClock(hz=hz, max_steps_per_frame=max_steps)


def test_a_frame_gives_whole_steps_and_the_remainder_as_alpha() -> None:
    clock = FixedStepClock(hz=10, max_steps_per_frame=5)
    advance = clock.advance(0.25)
    assert advance.steps == 2
    assert advance.alpha == pytest.approx(0.5)


def test_short_frames_accumulate_until_a_step_is_due() -> None:
    clock = FixedStepClock(hz=10, max_steps_per_frame=5)
    first = clock.advance(0.06)
    assert first.steps == 0
    assert first.alpha == pytest.approx(0.6)
    second = clock.advance(0.06)
    assert second.steps == 1
    assert second.alpha == pytest.approx(0.2)


def test_negative_frame_time_counts_as_no_time() -> None:
    clock = FixedStepClock(hz=10, max_steps_per_frame=5)
    advance = clock.advance(-1.0)
    assert advance.steps == 0
    assert advance.alpha == pytest.approx(0.0)


def test_exactly_the_cap_is_not_dropped() -> None:
    clock = FixedStepClock(hz=10, max_steps_per_frame=2)
    advance = clock.advance(0.25)
    assert advance.steps == 2
    assert advance.alpha == pytest.approx(0.5)


def test_p_eng100_time_beyond_the_cap_is_dropped() -> None:
    clock = FixedStepClock(hz=10, max_steps_per_frame=2)
    capped = clock.advance(0.55)
    assert capped.steps == 2
    assert capped.alpha == 0.0
    # The dropped time does not come back on the next frame.
    assert clock.advance(0.0).steps == 0
