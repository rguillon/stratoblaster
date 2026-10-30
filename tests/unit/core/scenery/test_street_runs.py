"""The straight runs of the built links of a street grid (`core/scenery/street_runs.py`)."""

import pytest

from core.scenery.street_links import Link, Nodes
from core.scenery.street_runs import Point, _resample, straight_runs


def _link(
    nodes: Nodes, a: tuple[float, float], b: tuple[float, float], across: bool = True
) -> Link:
    na = nodes.use(nodes.at(*a))
    nb = nodes.use(nodes.at(*b))
    return Link(na, nb, across, False, False, True, True, False)


def test_p04_r08_built_links_in_a_line_make_one_straight_run() -> None:
    nodes = Nodes(lambda x, z: True)
    links = [
        _link(nodes, (20.0, 0.0), (30.0, 0.0)),
        _link(nodes, (0.0, 0.0), (10.0, 0.0)),
        _link(nodes, (10.0, 0.0), (20.0, 0.0)),
    ]
    runs = straight_runs(links, 5.0)
    assert len(runs) == 1
    assert [p.x for p in runs[0]] == pytest.approx([0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])
    assert all(p.z == 0.0 for p in runs[0])


def test_a_gap_in_the_line_starts_another_run() -> None:
    nodes = Nodes(lambda x, z: True)
    links = [
        _link(nodes, (0.0, 0.0), (10.0, 0.0)),
        _link(nodes, (30.0, 0.0), (40.0, 0.0)),
    ]
    runs = straight_runs(links, 5.0)
    assert [len(run) for run in runs] == [3, 3]


def test_runs_across_and_along_are_separate_lines() -> None:
    nodes = Nodes(lambda x, z: True)
    runs = straight_runs(
        [
            _link(nodes, (0.0, 0.0), (10.0, 0.0), across=True),
            _link(nodes, (0.0, 0.0), (0.0, 10.0), across=False),
        ],
        5.0,
    )
    assert len(runs) == 2


def test_resample_is_points_every_step_from_first_to_last() -> None:
    run = [Point(0.0, 0.0), Point(10.0, 0.0)]
    points = _resample(run, 2.5)
    assert [p.x for p in points] == pytest.approx([0.0, 2.5, 5.0, 7.5, 10.0])
    assert _resample([], 4.0) == []


def test_resample_of_a_zero_length_run_keeps_two_points() -> None:
    points = _resample([Point(3.0, 3.0), Point(3.0, 3.0)], 4.0)
    assert len(points) == 2
    assert all((p.x, p.z) == (3.0, 3.0) for p in points)
