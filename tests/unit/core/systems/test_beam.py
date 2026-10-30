"""Unit tests of `src/core/systems/beam.py`."""

import pytest

from core.entities.weapon import BeamLevel
from core.systems.beam import BeamHit, BeamSegment, trace_beam


class _Target:
    def __init__(self, x: float, y: float, radius: float = 5, health: float = 10) -> None:
        self.id = 0
        self.x = x
        self.y = y
        self.radius = radius
        self.health = health
        self.max_health = health


LEVELS = [BeamLevel(10, 4), BeamLevel(20, 8)]


def test_p03_r02_no_target_runs_to_the_top_at_level_width() -> None:
    trace = trace_beam(LEVELS, 1, 0, 0, 100, [])
    assert len(trace.segments) == 1
    seg = trace.segments[0]
    assert (seg.x, seg.y0, seg.y1, seg.level, seg.width, seg.hit) == (0, 0, 100, 1, 4, False)
    assert trace.hits == []


def test_p03_r02_level_1_stops_at_the_first_target() -> None:
    trace = trace_beam(LEVELS, 1, 0, 0, 100, [_Target(0, 50)])
    assert [s.hit for s in trace.segments] == [True]
    assert trace.segments[0].y1 == pytest.approx(45)
    assert len(trace.hits) == 1
    assert trace.hits[0].level == 1
    assert trace.hits[0].y == pytest.approx(45)


def test_p03_r02_horizontal_reach_is_radius_plus_half_width() -> None:
    # Width 4 gives a half width of 2, the target radius 5: reach 7.
    assert trace_beam(LEVELS, 1, 0, 0, 100, [_Target(7, 50)]).hits != []
    assert trace_beam(LEVELS, 1, 0, 0, 100, [_Target(7.01, 50)]).hits == []


def test_p03_r02_dead_target_is_ignored() -> None:
    trace = trace_beam(LEVELS, 1, 0, 0, 100, [_Target(0, 50, health=0)])
    assert trace.hits == []


def test_p03_r02_targets_at_or_below_the_start_are_ignored() -> None:
    trace = trace_beam(LEVELS, 1, 0, 10, 100, [_Target(0, 10), _Target(0, 5)])
    assert trace.hits == []


def test_p03_r02_level_1_hits_the_lowest_target_above() -> None:
    trace = trace_beam(LEVELS, 1, 0, 0, 100, [_Target(0, 60), _Target(0, 30)])
    assert trace.hits[0].target.y == 30


def test_p03_r02_level_2_goes_through_a_target_and_continues_one_level_lower() -> None:
    near = _Target(0, 30)
    far = _Target(0, 80)
    trace = trace_beam(LEVELS, 2, 0, 0, 100, [near, far])
    assert [h.target for h in trace.hits] == [near, far]
    assert [h.level for h in trace.hits] == [2, 1]
    assert trace.hits[0].y == pytest.approx(25)
    assert trace.hits[1].y == pytest.approx(75)
    assert [(s.level, s.width, s.hit) for s in trace.segments] == [(2, 8, True), (1, 4, True)]


def test_p03_r02_a_target_is_hit_once_even_when_the_beam_continues() -> None:
    trace = trace_beam(LEVELS, 2, 0, 0, 100, [_Target(0, 30)])
    assert len(trace.hits) == 1
    assert [s.hit for s in trace.segments] == [True, False]
    assert trace.segments[1].y1 == 100


def test_p03_r02_contact_is_never_below_the_start_of_a_segment() -> None:
    # The target's edge (42 - 5 = 37) is below the start (40): the beam touches it at 40.
    trace = trace_beam(LEVELS, 1, 0, 40, 100, [_Target(0, 42)])
    assert trace.hits[0].y == 40
    assert trace.segments[0].y1 == 40


def test_p03_r02_a_level_past_the_list_has_no_width() -> None:
    trace = trace_beam(LEVELS, 3, 0, 0, 100, [])
    assert trace.segments[0].level == 3
    assert trace.segments[0].width == 0


def test_p03_r02_a_zero_width_beam_only_touches_within_the_radius() -> None:
    trace = trace_beam(LEVELS, 3, 0, 0, 100, [_Target(5.01, 50)])
    assert trace.hits == []
    assert trace_beam(LEVELS, 3, 0, 0, 100, [_Target(0, 50)]).hits != []


def test_p03_r02_level_0_traces_nothing() -> None:
    trace = trace_beam(LEVELS, 0, 0, 0, 100, [_Target(0, 50)])
    assert trace.segments == []
    assert trace.hits == []


def test_p03_r02_segment_and_hit_records_keep_their_fields() -> None:
    target = _Target(0, 50)
    seg = BeamSegment(1, 2, 3, 4, 5, True)
    hit = BeamHit(target, 2, 9)
    assert (seg.x, seg.y0, seg.y1, seg.level, seg.width, seg.hit) == (1, 2, 3, 4, 5, True)
    assert (hit.target, hit.level, hit.y) == (target, 2, 9)
