"""Unit tests of `src/core/scenery/road_tiles.py`."""

from helpers.level_builders import (
    flat,
    make_level,
    prop_rules,
    road_rules,
    section,
    street_grid,
    tile_rules,
)

from core.scenery.district_packing import DistrictSite, RoadTilesCache, pack_districts
from core.scenery.districts import ZRange
from core.scenery.height_field import HeightField
from core.scenery.road_network import RoadNetwork
from core.scenery.road_tiles import (
    FULL_SIDES,
    PieceCache,
    PieceSide,
    RoadPiece,
    _junction,
    _junctions,
    _kind_of,
    _line_of,
    _meet,
    _straights,
    _TileLine,
    _ways,
    cached_road_pieces,
    has_tile_key,
    road_pieces,
    road_tiles,
    tile_has,
    tile_key,
)
from core.scenery.road_types import Road, RoadPoint
from core.scenery.scenery_level import PropGroupRule, PropKindRule

SPAN = ZRange(-3000.0, 6000.0)

TILE = tile_rules()

ONE = PropKindRule("one", 1.0, 12.0, (0.5, 1.0), tiles=(1, 1))

TWO = PropKindRule("two", 1.0, 24.0, (0.5, 1.0), tiles=(2, 2))

LOT = PropKindRule("lot", 1.0, 12.0, (0.5, 1.0), tiles=(3, 1))


def _setup(group_at=None, lots=(LOT,), seed: int = 4):
    level = make_level(
        [
            section("a", 10, flat()),
            section("b", 10, flat(), streets=street_grid(0.8), building_density=1.0),
            section("c", 10, flat()),
        ],
        roads=road_rules(tiles=TILE),
        props=prop_rules(lots=list(lots)),
    )
    field = HeightField(level)
    roads = RoadNetwork(field, level.roads, seed, SPAN)
    group = PropGroupRule("g", 1.0, [ONE, TWO])
    placed: list = []
    site = DistrictSite(
        field,
        level.props,
        roads,
        seed,
        group_at if group_at is not None else (lambda x, z, section: group),
        placed.append,
    )
    return site, roads, placed


def _footprint_tiles(building) -> set[tuple[int, int]]:
    t = TILE.size
    p = building.placement
    i0 = round((p.x - building.half_x) / t)
    i1 = round((p.x + building.half_x) / t)
    j0 = round((p.z - building.half_z) / t)
    j1 = round((p.z + building.half_z) / t)
    return {(i, j) for i in range(i0, i1) for j in range(j0, j1)}


def _pack(site, roads, within=lambda z: True):
    road = RoadTilesCache().of(roads.roads, TILE)
    pack_districts(site, within, TILE, road)
    return road


TILE_ROADS = tile_rules()  # 24 units a side


def _street(
    index: int, a: tuple[float, float], b: tuple[float, float], width: float = 24.0
) -> Road:
    return Road(
        index, "street", width, 1, [RoadPoint(a[0], a[1], width), RoadPoint(b[0], b[1], width)]
    )


def _row(start: int, at: float, from_: float, to: float, size: int = 1) -> _TileLine:
    return _TileLine(True, start, size, at, from_, to)


def _column(start: int, at: float, from_: float, to: float, size: int = 1) -> _TileLine:
    return _TileLine(False, start, size, at, from_, to)


def test_p15_r07_buildings_stand_on_whole_tiles_off_the_roads_and_apart() -> None:
    site, roads, placed = _setup()
    road = _pack(site, roads)
    assert placed
    seen: set[tuple[int, int]] = set()
    for building in placed:
        tiles = _footprint_tiles(building)
        assert tiles
        assert not any(tile_has(road, i, j) for i, j in tiles)
        assert not (tiles & seen)
        seen |= tiles


def test_p15_r03_tile_keys_are_unique_and_found_as_numbers_or_text() -> None:
    keys = {tile_key(x, z) for x in range(-20, 20) for z in range(-20, 20)}
    assert len(keys) == 40 * 40
    assert has_tile_key({tile_key(3, 4): True}, tile_key(3, 4))
    assert has_tile_key({str(tile_key(3, 4)): True}, tile_key(3, 4))
    assert not has_tile_key({}, tile_key(3, 4))
    assert tile_has({str(tile_key(-2, 7)): True}, -2, 7)
    assert not tile_has({str(tile_key(-2, 7)): True}, 7, -2)


def test_kind_of_a_piece_is_set_by_its_open_sides() -> None:
    side = PieceSide(1, 0)
    assert _kind_of([side, side, side, side]) == "cross"
    assert _kind_of([side, side, side, None]) == "tee"
    assert _kind_of([side, None, side, None]) == "straight"
    assert _kind_of([None, side, None, side]) == "straight"
    assert _kind_of([side, side, None, None]) == "turn"
    assert _kind_of([None, None, None, None]) == "straight"
    assert FULL_SIDES == 4


def test_meeting_and_the_open_ways_of_a_junction() -> None:
    row = _row(5, 120.0, -300.0, 72.0)
    column = _column(3, 72.0, 200.0, 300.0)
    assert _meet(row, column) is False
    through = _column(3, 72.0, -300.0, 300.0)
    assert _meet(row, through) is True
    assert _ways(row, through) == [True, False, True, True]


def test_p15_r03_a_junction_is_the_wider_road_size_on_its_lattice() -> None:
    row = _row(5, 120.0, -300.0, 300.0, size=2)
    column = _column(3, 72.0, -300.0, 300.0)
    piece = _junction(row, column)
    assert piece is not None
    assert piece.size == 2
    assert (piece.x, piece.z) == (2, 5)  # the wider row's own tile row
    assert piece.adapter is True
    assert piece.kind == "cross"


def test_no_junction_where_the_streets_do_not_meet() -> None:
    assert _junction(_row(5, 120.0, -300.0, 10.0), _column(3, 72.0, 100.0, 300.0)) is None


def test_p15_r03_two_streets_meeting_at_one_junction_share_its_piece() -> None:
    column = _column(3, 72.0, -300.0, 300.0)
    left = _row(5, 120.0, -300.0, 72.0)
    right = _row(5, 120.0, 72.0, 300.0)
    pieces = _junctions([left, right], [column])
    assert len(pieces) == 1
    assert pieces[0].kind == "cross"


def test_p15_r03_a_street_turning_at_a_junction_is_a_turn_and_one_ending_is_a_tee() -> None:
    column = _column(3, 72.0, 120.0, 300.0)
    row = _row(5, 120.0, -300.0, 72.0)
    turn = _junction(row, column)
    assert turn is not None and turn.kind == "turn"
    tee = _junction(_row(5, 120.0, -300.0, 72.0), _column(3, 72.0, -300.0, 300.0))
    assert tee is not None and tee.kind == "tee"


def test_p15_r03_road_pieces_cover_each_tile_once() -> None:
    roads = [
        _street(0, (-300.0, 120.0), (300.0, 120.0)),
        _street(1, (72.0, -300.0), (72.0, 300.0)),
        _street(2, (-300.0, 240.0), (300.0, 240.0), width=48.0),
    ]
    pieces = road_pieces(roads, TILE_ROADS)
    counted = sum(p.size * p.size for p in pieces)
    assert len(road_tiles(pieces)) == counted
    assert any(p.kind == "cross" for p in pieces)
    assert any(p.kind == "straight" and p.size == 2 for p in pieces)


def test_straight_pieces_skip_tiles_already_taken() -> None:
    line = _row(5, 120.0, -300.0, 300.0, size=2)
    taken = {str(tile_key(-2, 5)): True}
    pieces = _straights(line, TILE_ROADS, taken)
    assert pieces
    assert all(p.size == 2 and p.x % 2 == 0 for p in pieces)
    assert not any(p.x == -2 and p.z == 5 for p in pieces)


def test_p15_r03_the_pieces_of_a_street_are_cached_per_list_of_roads() -> None:
    roads = [_street(0, (-300.0, 120.0), (300.0, 120.0))]
    assert cached_road_pieces(roads, TILE_ROADS) is cached_road_pieces(roads, TILE_ROADS)
    cache = PieceCache()
    first = cache.get(roads, TILE_ROADS)
    assert cache.get(roads, TILE_ROADS) is first
    assert cache.get(list(roads), TILE_ROADS) is not first


def test_road_tiles_marks_every_tile_of_each_piece() -> None:
    piece = RoadPiece(2, 3, 2, "straight", False, [None, None, None, None])
    tiles = road_tiles([piece])
    assert {k for k in tiles} == {str(tile_key(2 + i, 3 + j)) for i in range(2) for j in range(2)}
    line = _line_of(_street(0, (72.0, -300.0), (72.0, 300.0)), TILE_ROADS)
    assert line is not None and not line.row and line.start == 3
    assert _line_of(Road(0, "street", 24.0, 1, []), TILE_ROADS) is None
