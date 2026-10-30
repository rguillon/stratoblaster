"""Unit tests of `src/core/scenery/street_grid.py`."""

from helpers.level_builders import flat, make_level, road_rules, section

from core.math.rng import create_rng
from core.scenery.districts import ZRange, find_districts
from core.scenery.lanes import main_road_width
from core.scenery.scenery_level import StreetGrid, layout_sections
from core.scenery.street_grid import _merge_columns, _spaced, block_parts, street_runs
from core.scenery.street_links import Block

SPAN = ZRange(-3000.0, 6000.0)


def _district(grid: StreetGrid, middle: bool = True):
    """A district of one section (the middle one of three, so its rows start and end inside)."""
    sections = [
        section("a", 10, flat()),
        section("b", 10, flat(), streets=grid),
        section("c", 10, flat()),
    ]
    if not middle:
        sections = [section("b", 10, flat(), streets=grid)]
    placed = layout_sections(make_level(sections))
    return find_districts(placed, SPAN)[0]


def _ground(x: float, z: float) -> bool:
    return True


def _in_view(node) -> bool:
    return abs(node.x) >= 300.0


def test_p04_r07_with_no_chance_of_links_only_the_rows_at_the_ends_are_laid() -> None:
    district = _district(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.0))
    runs, _ = street_runs(district, road_rules(), create_rng(4), _ground, _in_view)
    z_rows = {round(run.points[0].z, 6) for run in runs}
    assert z_rows <= {round(district.z_min, 6), round(district.z_max, 6)}
    assert z_rows


def test_block_parts_cut_a_block_into_equal_parts() -> None:
    parts = block_parts(Block(0.0, 40.0, 0.0, 20.0), 2, 4)
    assert len(parts) == 8
    assert sum((b.x_max - b.x_min) * (b.z_max - b.z_min) for b in parts) == 800.0
    assert (parts[0].x_min, parts[0].z_min) == (0.0, 0.0)


def test_spaced_positions_include_both_ends() -> None:
    positions = _spaced(0.0, 100.0, (30.0, 30.0), create_rng(1))
    assert positions[0] == 0.0 and positions[-1] == 100.0
    assert all(b - a >= 15.0 for a, b in zip(positions, positions[1:], strict=False))


def test_merged_columns_are_the_sorted_union() -> None:
    assert _merge_columns([0.0, 10.0, 20.0], [10.0, 15.0]) == [0.0, 10.0, 15.0, 20.0]
    assert main_road_width(road_rules(), 0) == road_rules().dual.width
