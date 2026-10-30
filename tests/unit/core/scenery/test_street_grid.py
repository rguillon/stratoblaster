"""The straight streets of a district (`core/scenery/street_grid.py`, phase 4 review)."""

from level_builders import flat, make_level, road_rules, section, tile_rules

from core.math.rng import create_rng
from core.scenery.districts import ZRange, find_districts
from core.scenery.lanes import main_road_width
from core.scenery.scenery_level import Boulevard, NoCrossings, StreetGrid, layout_sections
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


def _runs(grid: StreetGrid, rules, seed: int = 4, buildable=_ground):
    return street_runs(_district(grid), rules, create_rng(seed), buildable, _in_view)


def test_p04_r07_streets_are_straight_runs_across_and_along() -> None:
    runs, _ = _runs(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.55), road_rules())
    assert runs
    for run in runs:
        xs = {round(p.x, 6) for p in run.points}
        zs = {round(p.z, 6) for p in run.points}
        assert len(xs) == 1 or len(zs) == 1


def test_p04_r07_the_streets_are_the_same_for_the_same_seed() -> None:
    def shape(seed: int):
        runs, blocks = _runs(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.55), road_rules(), seed)
        return (
            [[(round(p.x, 6), round(p.z, 6)) for p in r.points] for r in runs],
            [(b.x_min, b.z_min) for b in blocks],
        )

    assert shape(4) == shape(4)
    assert shape(4) != shape(5)


def test_p04_r07_the_blocks_between_streets_have_room() -> None:
    _, blocks = _runs(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.55), road_rules())
    assert blocks
    assert all(b.x_max > b.x_min and b.z_max > b.z_min for b in blocks)


def test_p04_r07_with_no_chance_of_links_only_the_rows_at_the_ends_are_laid() -> None:
    district = _district(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.0))
    runs, _ = street_runs(district, road_rules(), create_rng(4), _ground, _in_view)
    z_rows = {round(run.points[0].z, 6) for run in runs}
    assert z_rows <= {round(district.z_min, 6), round(district.z_max, 6)}
    assert z_rows


def test_p04_r07_unbuildable_ground_gets_no_streets() -> None:
    runs, blocks = _runs(
        StreetGrid((60.0, 110.0), (70.0, 130.0), 1.0), road_rules(), buildable=lambda x, z: False
    )
    assert runs == [] and blocks == []


def test_p04_r07_a_boulevard_is_built_along_its_line() -> None:
    rules = road_rules(boulevards=[Boulevard(3, 36.0, 0.5)])
    runs, _ = _runs(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.0), rules)
    widths = {run.width for run in runs}
    assert 36.0 in widths


def test_p04_r07_without_crossings_the_streets_are_still_straight() -> None:
    rules = road_rules(no_crossings=NoCrossings(20.0))
    runs, _ = _runs(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.8), rules)
    assert runs
    for run in runs:
        assert (
            len({round(p.x, 6) for p in run.points}) == 1
            or len({round(p.z, 6) for p in run.points}) == 1
        )


def test_p15_r01_on_tiles_the_streets_are_whole_tiles_wide() -> None:
    rules = road_rules(tiles=tile_rules(), main_width=24.0, dual=road_rules().dual)
    runs, blocks = _runs(StreetGrid((60.0, 110.0), (70.0, 130.0), 0.8), rules)
    assert runs and blocks
    assert {run.width for run in runs} <= {24.0, 48.0, 72.0, 96.0}


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
