"""Unit tests of `src/core/scenery/street_runs.py`."""

import pytest

from core.scenery.street_runs import Point, _resample


def test_resample_is_points_every_step_from_first_to_last() -> None:
    run = [Point(0.0, 0.0), Point(10.0, 0.0)]
    points = _resample(run, 2.5)
    assert [p.x for p in points] == pytest.approx([0.0, 2.5, 5.0, 7.5, 10.0])
    assert _resample([], 4.0) == []


def test_resample_of_a_zero_length_run_keeps_two_points() -> None:
    points = _resample([Point(3.0, 3.0), Point(3.0, 3.0)], 4.0)
    assert len(points) == 2
    assert all((p.x, p.z) == (3.0, 3.0) for p in points)
