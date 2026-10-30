"""The streets of a district on a grid of square tiles (P15-R01, R04, R05; `tile_streets.py`)."""

from types import SimpleNamespace

import pytest
from level_builders import flat, make_level, road_rules, section, street_grid, tile_rules

from core.math.rng import create_rng
from core.scenery.districts import ZRange, find_districts
from core.scenery.scenery_level import Boulevard, layout_sections
from core.scenery.street_links import Node
from core.scenery.tile_streets import (
    _fitting_tile,
    _int_set,
    _mod,
    _next_gap,
    _part_columns,
    _part_rows,
    _row_size,
    _tile_at,
    _unique,
    _unique_nodes,
    column_fits,
    tile_street_runs,
)

SPAN = ZRange(-3000.0, 6000.0)
TILE = tile_rules()


def _district(sections):
    return find_districts(layout_sections(make_level(sections)), SPAN)[0]


def _in_view(node: Node) -> bool:
    return abs(node.x) >= 300.0


def _grid_district(links: float = 0.8):
    grid = street_grid(links)
    return _district(
        [section("a", 10, flat()), section("b", 10, flat(), streets=grid), section("c", 10, flat())]
    )


def _runs(district, rules=None, buildable=lambda x, z: True, seed: int = 4):
    rules = rules if rules is not None else road_rules(tiles=TILE)
    return tile_street_runs(district, rules, TILE, create_rng(seed), buildable, _in_view)


def test_p15_r04_a_column_fits_where_its_junction_lands_on_the_row_lattice() -> None:
    assert column_fits(4, 3) is True  # 4 mod 3 == 1, the middle of a three-tile row
    assert column_fits(3, 3) is False
    assert column_fits(7, 1) is True
    assert all(column_fits(s, 2) for s in range(-4, 4))


def test_p15_r01_helpers_round_and_order_as_the_grid_needs() -> None:
    # The tile whose middle is nearest: the middles of tiles 0, 1 and 2 are 12, 36 and 60.
    assert _tile_at(12.0, 24.0) == 0
    assert _tile_at(35.0, 24.0) == 1
    assert _tile_at(60.0, 24.0) == 2
    assert _mod(-1.0, 4.0) == 3.0
    assert _int_set([1, 2, 1]) == {"1": True, "2": True}
    assert _unique([3, 1, 3, 2, 1]) == [3, 1, 2]
    a = Node(0.0, 0.0, 0)
    b = Node(1.0, 0.0, 1)
    assert _unique_nodes([a, b, a]) == [a, b]
    assert _next_gap((0.0, 0.0), 24.0, create_rng(1)) == 2


def test_p15_r05_a_row_is_one_or_two_tiles_wide_or_a_boulevard_size() -> None:
    assert {_row_size(road_rules(), t) for t in range(-50, 50)} <= {1, 2}
    rules = road_rules(boulevards=[Boulevard(4, 96.0, 1.0)])
    assert {_row_size(rules, t) for t in range(-20, 20)} == {4}


def test_fitting_tile_skips_tiles_next_to_taken_ones() -> None:
    assert _fitting_tile(2, 1, [3], {}) == 4
    # Tile 4 is next to the taken 3; the next tile where a three-tile row's column fits is 7.
    assert _fitting_tile(2, 1, [3], {"3": True}) == 7
    assert _fitting_tile(0, -1, [3], {}) == -2


def test_part_rows_run_from_the_first_row_to_the_last_one_tile_wide() -> None:
    part = _grid_district().parts[0]
    rows = _part_rows(road_rules(), TILE, part, create_rng(2))
    assert rows[0].size == 1 and rows[-1].size == 1
    assert all(b.start > a.start for a, b in zip(rows, rows[1:], strict=False))


def test_part_rows_of_a_part_shorter_than_a_tile_is_one_row() -> None:
    thin = SimpleNamespace(z_min=100.0, z_max=101.0, grid=street_grid())
    assert len(_part_rows(road_rules(), TILE, thin, create_rng(2))) == 1


def test_part_columns_reach_past_both_screen_edges() -> None:
    rules = road_rules()
    part = _grid_district().parts[0]
    columns = _part_columns(rules, TILE, part, [1, 2], [], create_rng(3))
    centres = [(c + 0.5) * TILE.size for c in columns]
    assert centres[0] <= -rules.offscreen_x
    assert centres[-1] >= rules.offscreen_x
    assert columns == sorted(columns)


def test_p15_r01_the_streets_cover_whole_tiles_and_are_straight() -> None:
    runs, blocks = _runs(_grid_district())
    assert runs and blocks
    for run in runs:
        assert (
            len({round(p.x, 6) for p in run.points}) == 1
            or len({round(p.z, 6) for p in run.points}) == 1
        )
        assert run.width % TILE.size == pytest.approx(0.0) or run.width == TILE.size
    assert all(b.x_max > b.x_min and b.z_max > b.z_min for b in blocks)


def test_p15_r01_the_streets_are_the_same_for_the_same_seed() -> None:
    def shape(seed):
        runs, blocks = _runs(_grid_district(), seed=seed)
        return [len(r.points) for r in runs], [b.x_min for b in blocks]

    assert shape(4) == shape(4)


def test_p15_r05_two_sections_of_tiles_share_their_row() -> None:
    grid = street_grid(0.6)
    district = _district(
        [section("a", 10, flat(), streets=grid), section("b", 10, flat(), streets=grid)]
    )
    runs, blocks = _runs(district)
    assert runs
    assert all(b.x_max > b.x_min for b in blocks)


def test_p15_r01_ground_that_is_not_buildable_gets_no_street_there() -> None:
    # Streets join ground nodes only, and blocks keep to buildable ground: nothing crosses to
    # X >= 0.
    runs, blocks = _runs(_grid_district(), buildable=lambda x, z: x < 0.0)
    assert runs
    assert all(p.x < 0.0 for run in runs for p in run.points)
    assert all((b.x_min + b.x_max) / 2 < 0.0 for b in blocks)


def test_p15_r01_a_district_one_row_tall_has_no_blocks() -> None:
    # A middle section a centimetre long (1 unit): the district is one tile row, with no block.
    thin = _district(
        [
            section("a", 10, flat()),
            section("b", 0.01, flat(), streets=street_grid()),
            section("c", 10, flat()),
        ]
    )
    _, blocks = _runs(thin)
    assert blocks == []
