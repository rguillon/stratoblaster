"""Unit tests of `src/app/rate_meter.py`."""

import pytest

from app.rate_meter import RateMeter


def test_p13_r01_no_samples_means_no_rate() -> None:
    assert RateMeter(1.0).rate == 0


def test_p13_r01_a_single_sample_has_no_span_to_measure() -> None:
    meter = RateMeter(1.0)
    meter.add(0.5, 10)
    assert meter.rate == 0


def test_p13_r01_the_rate_is_the_growth_per_second_over_the_samples() -> None:
    meter = RateMeter(10.0)
    meter.add(1.0, 0)
    meter.add(1.0, 30)
    meter.add(2.0, 90)
    # Samples at 1 s, 2 s and 4 s: (90 - 0) over 3 s.
    assert meter.rate == pytest.approx(30.0)


def test_p13_r01_old_samples_fall_out_of_the_window() -> None:
    meter = RateMeter(1.0)
    for step in range(10):
        meter.add(0.5, step * 10.0)
    # The window now covers the last second: 10 per half second, so 20 per second.
    assert meter.rate == pytest.approx(20.0)


def test_p13_r01_a_zero_time_span_reads_as_zero() -> None:
    meter = RateMeter(1.0)
    meter.add(0.0, 5)
    meter.add(0.0, 9)
    assert meter.rate == 0
