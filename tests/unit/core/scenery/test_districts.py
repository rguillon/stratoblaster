"""Unit tests of `src/core/scenery/districts.py`."""

from helpers.level_builders import flat, make_level, section, street_grid

from core.scenery.districts import (
    District,
    ZRange,
    districts_from,
    find_districts,
    laid_districts,
    split_districts,
)
from core.scenery.scenery_level import layout_sections

SPAN = ZRange(-100.0, 4100.0)


def _placed():
    """Four sections of 1000 units: streets in the first two and the last, none in the third."""
    grid = street_grid()
    return layout_sections(
        make_level(
            [
                section("a", 10, flat(), streets=grid),
                section("b", 10, flat(), streets=grid),
                section("c", 10, flat()),
                section("d", 10, flat(), streets=grid),
            ]
        )
    )


def test_p04_r07_runs_of_sections_with_streets_make_one_district() -> None:
    districts = find_districts(_placed(), SPAN)
    assert len(districts) == 2
    first, second = districts
    assert (first.z_min, first.z_max) == (-100.0, 2000.0)
    assert len(first.parts) == 2
    assert (second.z_min, second.z_max) == (3000.0, 4100.0)
    assert len(second.parts) == 1


def test_a_range_cut_to_a_stretch() -> None:
    districts = find_districts(_placed(), SPAN)
    cut = districts_from(districts, 500.0)
    assert [(d.z_min, d.z_max) for d in cut] == [(500.0, 2000.0), (3000.0, 4100.0)]
    assert [(p.z_min, p.z_max) for p in cut[0].parts] == [(500.0, 1000.0), (1000.0, 2000.0)]


def test_p04_r07_districts_split_at_the_runout_go_on_from_its_row() -> None:
    districts = find_districts(_placed(), SPAN)
    before, after = split_districts(districts, 1500.0)
    assert [(d.z_min, d.z_max) for d in before] == [(-100.0, 1500.0)]
    assert [(d.z_min, d.z_max, d.continues) for d in after] == [
        (1500.0, 2000.0, True),
        (3000.0, 4100.0, None),
    ]


def test_laid_districts_lays_all_without_a_runout_or_a_start() -> None:
    districts = find_districts(_placed(), SPAN)
    assert laid_districts(districts) == (districts, [])
    before, after = laid_districts(districts, streets_from=500.0, runout_from=1500.0)
    assert [(d.z_min, d.z_max) for d in before] == [(500.0, 1500.0)]
    assert [d.continues for d in after] == [True, None]


def test_a_district_without_parts_left_in_a_range_is_dropped() -> None:
    districts = find_districts(_placed(), SPAN)
    assert districts_from(districts, 9000.0) == []
    assert all(isinstance(d, District) for d in districts)
