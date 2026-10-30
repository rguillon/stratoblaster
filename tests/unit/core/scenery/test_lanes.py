"""Lanes and widths of the roads (`core/scenery/lanes.py`, phase 4 review)."""

from types import SimpleNamespace

from level_builders import road_rules

from core.scenery.lanes import (
    is_boulevard,
    lanes_of,
    main_road_width,
    run_width,
    street_width,
    with_width,
)
from core.scenery.scenery_level import Boulevard, Dual


def _point(x: float, z: float) -> SimpleNamespace:
    return SimpleNamespace(x=x, z=z)


def test_p04_r07_roads_are_one_lane_each_way_unless_they_are_dual() -> None:
    rules = road_rules()
    assert lanes_of(rules, rules.main_width) == 1
    assert lanes_of(rules, rules.dual.width) == 2
    assert is_boulevard(rules, rules.main_width) is False


def test_boulevards_have_their_own_lanes() -> None:
    rules = road_rules(boulevards=[Boulevard(3, 36.0, 0.3)])
    assert lanes_of(rules, 36.0) == 3
    assert is_boulevard(rules, 36.0) is True
    assert is_boulevard(rules, 24.0) is False


def test_the_first_main_roads_are_dual() -> None:
    rules = road_rules(main_roads=4, dual=Dual(48.0, 3, 0.2))
    assert [main_road_width(rules, i) for i in range(4)] == [
        rules.dual.width,
        rules.dual.width,
        rules.dual.width,
        rules.main_width,
    ]


def test_p04_r07_every_street_line_has_one_of_the_widths_of_the_grid() -> None:
    rules = road_rules(boulevards=[Boulevard(4, 60.0, 0.2)])
    widths = {street_width(rules, float(c)) for c in range(-200, 200, 7)}
    assert widths <= {60.0, rules.dual.width, rules.main_width}
    assert widths >= {rules.main_width}


def test_street_lines_with_all_the_share_are_boulevards_and_none_are_avenues() -> None:
    boulevards = road_rules(boulevards=[Boulevard(3, 36.0, 1.0)])
    assert {street_width(boulevards, float(c)) for c in range(-50, 50)} == {36.0}
    plain = road_rules(dual=Dual(48.0, 1, 0.0))
    assert {street_width(plain, float(c)) for c in range(-50, 50)} == {plain.main_width}


def test_run_width_is_the_width_of_its_line() -> None:
    rules = road_rules(dual=Dual(48.0, 1, 1.0))
    assert run_width(rules, []) == rules.main_width
    row = [_point(-100.0, 40.0), _point(100.0, 40.0)]
    assert run_width(rules, row) == street_width(rules, 40.0)
    column = [_point(70.0, -100.0), _point(70.0, 100.0)]
    assert run_width(rules, column) == street_width(rules, 70.0)


def test_with_width_gives_each_point_the_width() -> None:
    points = with_width([_point(1.0, 2.0), _point(3.0, 4.0)], 12.0)
    assert [(p.x, p.z, p.width) for p in points] == [(1.0, 2.0, 12.0), (3.0, 4.0, 12.0)]
