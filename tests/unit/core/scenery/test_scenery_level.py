"""Unit tests of `src/core/scenery/scenery_level.py`."""

import math

import pytest
from helpers.level_builders import (
    SAMPLE_POINTS,
    flat,
    hills,
    make_level,
    prop_rules,
    road_rules,
    section,
    street_grid,
    tile_rules,
)
from helpers.sample_level import block_kind, sample_level, sample_props, sample_roads, stick_kind
from helpers.sample_level import flat as flat_away
from helpers.sample_level import flat as flat_floats
from helpers.sample_level import flat as flat_props

from core.math.noise import create_noise2d
from core.math.rng import create_rng
from core.scenery.away_placement import Building, ZSpan, place_hamlets
from core.scenery.block_towers import tower_in
from core.scenery.district_packing import DistrictSite, RoadTilesCache, pack_districts
from core.scenery.districts import ZRange, find_districts
from core.scenery.float_placement import fixed_pieces, floating_props, line_pieces, place_landmark
from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField, terrain_ceiling
from core.scenery.ice_sculpt import LakeField, crevasse_depth, with_lakes
from core.scenery.lanes import main_road_width
from core.scenery.prop_placement import PropPlacer
from core.scenery.road_network import RoadNetwork, RoadNetworkOptions, level_roads
from core.scenery.scenery_level import (
    BlockFill,
    Boulevard,
    Channel,
    Crevasses,
    Dual,
    Dunes,
    Flatten,
    FloatRules,
    HamletRules,
    Lakes,
    Landmark,
    Loners,
    Meander,
    NoCrossings,
    PropGroupRule,
    PropKindRule,
    PropLine,
    PropRules,
    Relief,
    Shore,
    StreetGrid,
    Surface,
    TerrainSection,
    TileRules,
    layout_sections,
    level_duration,
    level_length,
    runout_start,
    with_runout,
)
from core.scenery.street_grid import street_runs
from core.scenery.street_links import Block


def _group(*kinds: PropKindRule) -> PropGroupRule:
    return PropGroupRule("g", 1.0, list(kinds))


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


def _pack(site, roads, within=lambda z: True):
    road = RoadTilesCache().of(roads.roads, TILE)
    pack_districts(site, within, TILE, road)
    return road


STRAIGHT = Meander(0.0, 0.0, 500.0)  # a line down the middle of the level, not winding


def _heights(field: HeightField) -> list[float]:
    return [field.height(x, z) for x, z in SAMPLE_POINTS]


def _level(terrain=None, streets=True, **rules):
    grid = street_grid(0.55) if streets else None
    secs = [
        section("a", 10, terrain or flat()),
        section("b", 10, terrain or flat(), streets=grid),
        section("c", 10, terrain or flat()),
    ]
    return make_level(secs, roads=road_rules(**rules))


def _network(level, seed: int = 4, options=None) -> RoadNetwork:
    field = HeightField(level)
    return RoadNetwork(field, level.roads, seed, SPAN, options)


def _mains(net):
    return [r for r in net.roads if r.kind == "main"]


def _distance_to_road(x: float, z: float, road) -> float:
    best = math.inf
    for a, b in zip(road.points, road.points[1:], strict=False):
        dx = b.x - a.x
        dz = b.z - a.z
        n = dx * dx + dz * dz
        t = 0.0 if n == 0 else max(0.0, min(1.0, ((x - a.x) * dx + (z - a.z) * dz) / n))
        best = min(best, math.hypot(a.x + t * dx - x, a.z + t * dz - z))
    return best


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


def kind(footprint: float = 3, frontage: float | None = None) -> PropKindRule:
    return PropKindRule("house", 1, footprint, [1, 1], frontage=frontage)


class FakeSite:
    """A site of a flat_away level: every spot is clear of the roads and of flat_away unless told
    otherwise.
    `add` keeps the buildings apart by their boxes and the gap, as the placer does."""

    def __init__(
        self,
        section: TerrainSection | None = None,
        group: PropGroupRule | None = None,
        clear: bool = True,
        ground: bool = True,
        accept: bool = True,
    ) -> None:
        self.length_ = 1000.0
        self.offscreen_x = 400.0
        self.seed = 3
        self.section = section if section is not None else flat_away("open", 10, 0)
        self.group = group if group is not None else PropGroupRule("g", 1, [kind()])
        self.clear = clear
        self.ground_ok = ground
        self.accept = accept
        self.added: list[Building] = []
        self.group_calls = 0

    def section_at(self, z: float) -> TerrainSection:
        return self.section

    def group_at(self, x: float, z: float, section: TerrainSection) -> PropGroupRule | None:
        self.group_calls += 1
        return self.group

    def clear_of_roads(self, x: float, z: float, clearance: float) -> bool:
        return self.clear

    def ground(self, x: float, z: float, radius: float) -> float | None:
        return 0.0 if self.ground_ok else None

    def add(self, building: Building, gap: float | None) -> bool:
        if not self.accept:
            return False
        self.added.append(building)
        return True


HAMLETS = HamletRules(spacing=[100, 100], buildings=[3, 3], radius=20, gap=2, clearance=1)

ICE = PropKindRule("ice", 1, 2, [1, 1])


def deep_sea(float_density: float | None = 1) -> TerrainSection:
    """A section of sea bed, about 20 units under the sea (level 0)."""
    return TerrainSection(
        "sea",
        20,
        Relief(-20, 1, 1 / 100, 1, "smooth"),
        building_density=0,
        tree_density=0,
        float_density=float_density,
    )


def field_of(section: TerrainSection) -> HeightField:
    return HeightField(sample_level(sections=[section]))


AREA = GroundArea(-200, 200, 0, 400)

SETBACK = 1


def placer_for(
    level=None,
    seed: int | None = None,
    sea_level: float | None = 0,
    runout_from: float | None = None,
) -> PropPlacer:
    """A placer of `level` (the sample by default), with its roads laid."""
    level = level if level is not None else sample_level()
    seed = level.seed if seed is None else seed
    field = HeightField(level, seed)
    options = RoadNetworkOptions(runout_from=runout_from) if runout_from is not None else None
    roads = level_roads(field, level.roads, seed, options)
    return PropPlacer(field, level.props, seed, roads, sea_level=sea_level)


def dense_level():
    """The sample with a dense grid of streets over the whole level: many buildings to pack."""
    flat_section = flat_props("grid", 20, 10)
    flat_section.streets = StreetGrid([20, 25], [20, 30], 0.8)
    return sample_level(sections=[flat_section])


class _Ground:
    """A box of ground for the overlap checks: a tree's box is `half` each way."""

    def __init__(self, x: float, z: float, half: float) -> None:
        from core.scenery.ground_boxes import PropPlacement  # noqa: PLC0415

        self.placement = PropPlacement("", x, 0, z, 0, 1)
        self.half_x = half
        self.half_z = half


def test_p04_r07_the_largest_kind_that_fits_stands_on_the_part() -> None:
    big = PropKindRule("big", 1.0, 10.0, (0.5, 1.0), frontage=10.0)
    small = PropKindRule("small", 1.0, 3.0, (0.5, 1.0), frontage=3.0)
    part = Block(0.0, 40.0, 0.0, 40.0)
    building = tower_in(part, [_group(big, small)], 5.0, 0.5)
    assert building is not None
    assert building.placement.kind == "big"
    assert building.half_x == 10.0
    assert building.placement.y == 5.0


def test_a_smaller_kind_is_taken_when_only_it_fits() -> None:
    big = PropKindRule("big", 1.0, 10.0, (0.5, 1.0), frontage=10.0)
    small = PropKindRule("small", 1.0, 3.0, (0.5, 1.0), frontage=3.0)
    part = Block(0.0, 10.0, 0.0, 10.0)
    building = tower_in(part, [_group(big, small)], 0.0, 0.5)
    assert building is not None
    assert building.placement.kind == "small"


def test_p04_r07_a_kind_without_frontage_is_fitted_by_its_footprint() -> None:
    kind = PropKindRule("plain", 1.0, 5.0, (0.5, 1.0))
    building = tower_in(Block(0.0, 40.0, 0.0, 40.0), [_group(kind)], 0.0, 0.2)
    assert building is not None
    assert building.placement.scale == 1.0
    assert building.half_x == 5.0


def test_p15_r08_a_group_without_tile_kinds_leaves_the_lots() -> None:
    empty = PropGroupRule("empty", 1.0, [])
    site, roads, placed = _setup(group_at=lambda x, z, section: empty)
    _pack(site, roads)
    assert {b.placement.kind for b in placed} == {"lot"}


def test_p15_r08_areas_of_different_groups_pack_with_their_own_kinds() -> None:
    other = PropGroupRule("other", 1.0, [ONE])
    group = PropGroupRule("g", 1.0, [TWO])
    site, roads, placed = _setup(group_at=lambda x, z, section: group if x < 0.0 else other)
    _pack(site, roads)
    assert placed
    kinds = {b.placement.kind for b in placed}
    assert kinds <= {"one", "two", "lot"}
    assert {"one", "two"} <= kinds


def test_terrain_ceiling_takes_the_highest_of_the_sections_parts() -> None:
    flatten = Flatten(STRAIGHT, 10.0, 10.0, 40.0, 5.0)
    assert terrain_ceiling(make_level([section("a", 10, flat(10), flatten=flatten)])) == 45
    dunes = Dunes(7.0, 100.0, 0.0, 0.0)
    assert terrain_ceiling(make_level([section("a", 10, flat(10), dunes=dunes)])) == 17
    lakes = Lakes(200.0, 1.0, (40.0, 60.0), 3.0, 20.0)
    assert terrain_ceiling(make_level([section("a", 10, flat(0), lakes=lakes)])) == 3
    shore = Shore(STRAIGHT, 1.0, 20.0, -20.0)
    assert terrain_ceiling(make_level([section("a", 10, flat(0), shore=shore)])) == 0


def test_p04_r01_ridged_relief_stays_between_base_and_top() -> None:
    ridged = Relief(50.0, 30.0, 1 / 300, 4, "ridged")
    field = HeightField(make_level([section("a", 10, ridged)]))
    assert all(50 - 1e-9 <= h <= 80 + 1e-9 for h in _heights(field))


def test_flatten_is_exactly_flat_on_its_line() -> None:
    flatten = Flatten(STRAIGHT, 10.0, 10.0, 40.0, 0.0)
    field = HeightField(make_level([section("a", 10, hills(), flatten=flatten)]))
    for z in (100.0, 400.0, 777.0):
        assert field.height(field.path_x(STRAIGHT, z), z) == pytest.approx(40.0)


def test_shore_drops_the_ground_on_the_sea_side_only() -> None:
    shore = Shore(STRAIGHT, 1.0, 20.0, -30.0)
    field = HeightField(make_level([section("a", 10, flat(10), shore=shore)]))
    assert field.height(-100.0, 300.0) == pytest.approx(-30.0)
    assert field.height(100.0, 300.0) == pytest.approx(10.0)


def test_p04_r01_dunes_add_between_zero_and_their_height() -> None:
    dunes = Dunes(12.0, 80.0, 30.0, 0.5)
    field = HeightField(make_level([section("a", 10, flat(10), dunes=dunes)]))
    added = [h - 10.0 for h in _heights(field)]
    assert all(-1e-9 <= d <= 12.0 + 1e-9 for d in added)
    assert max(added) > 0.0


def test_crevasses_only_cut_into_the_ground() -> None:
    crevasses = Crevasses(120.0, 10.0, 30.0, 0.0, 0.5, 0.8)
    field = HeightField(make_level([section("a", 10, flat(10), crevasses=crevasses)]))
    heights = _heights(field)
    assert all(h <= 10.0 + 1e-9 for h in heights)
    assert min(heights) < 10.0


def test_p04_r01_ground_cover_is_blended_like_the_height() -> None:
    lush = section("a", 10, flat(), surface=Surface(1.0, None, 0.0))
    paved = section("b", 10, flat(), surface=Surface(0.0, 0.5, None))
    field = HeightField(make_level([lush, paved], transition=200))
    cover = field.surface(500.0)
    assert (cover.lush, cover.paved, cover.sandy) == (1.0, 0.0, 0.0)
    cover = field.surface(1500.0)
    assert (cover.lush, cover.paved, cover.sandy) == (0.0, 0.5, 0.0)
    assert field.surface(1000.0).lush == pytest.approx(0.5)


def test_steepness_is_unknown_near_a_channel() -> None:
    channel = Channel(STRAIGHT, 10.0, 10.0, -5.0)
    field = HeightField(make_level([section("a", 10, flat(10), channel=channel)]))
    assert field.steepness(0.0, 300.0, 5.0) == math.inf
    assert math.isfinite(field.steepness(200.0, 300.0, 5.0))


def test_steepness_is_unknown_for_rough_sections() -> None:
    dunes = Dunes(12.0, 80.0, 30.0, 0.5)
    field = HeightField(make_level([section("a", 10, flat(10), dunes=dunes)]))
    assert field.steepness(0.0, 300.0, 5.0) == math.inf


def test_the_first_main_roads_are_dual() -> None:
    rules = road_rules(main_roads=4, dual=Dual(48.0, 3, 0.2))
    assert [main_road_width(rules, i) for i in range(4)] == [
        rules.dual.width,
        rules.dual.width,
        rules.dual.width,
        rules.main_width,
    ]


def test_p04_r07_without_crossings_each_main_road_keeps_its_gap_from_the_ones_before() -> None:
    gap = 20.0
    net = _network(_level(streets=False, no_crossings=NoCrossings(gap), main_roads=3))
    mains = _mains(net)
    assert len(mains) >= 2
    for k in range(1, len(mains)):
        for p in mains[k].points:
            for j in range(k):
                edge = _distance_to_road(p.x, p.z, mains[j]) - mains[j].width / 2
                assert edge >= mains[k].width / 2 + gap - 1e-6


def test_p04_r07_boulevards_have_their_lanes() -> None:
    level = _level(boulevards=[Boulevard(3, 36.0, 0.5)])
    net = _network(level)
    assert any(r.width == 36.0 and r.lanes == 3 for r in net.roads if r.kind == "street")


def test_p04_r01_sections_are_laid_end_to_end_from_zero() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    placed = layout_sections(level)
    assert [(p.start, p.end) for p in placed] == [(0.0, 1000.0), (1000.0, 1500.0)]
    assert placed[1].section.name == "b"


def test_p04_r01_a_level_needs_sections_speed_and_lengths() -> None:
    with pytest.raises(ValueError):
        layout_sections(make_level([]))
    with pytest.raises(ValueError):
        layout_sections(make_level([section("a", 10, flat())], speed=0.0))
    with pytest.raises(ValueError):
        layout_sections(make_level([section("a", 0.0, flat())]))


def test_p04_r06_the_duration_and_length_add_up_the_sections() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    assert level_duration(level) == pytest.approx(15.0)
    assert level_length(level) == pytest.approx(1500.0)


def test_p07_r03_a_runout_extends_the_last_section_and_adds_up() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    assert with_runout(level, 0.0) is level
    extended = with_runout(level, 30.0)
    assert extended.runout == pytest.approx(30.0)
    assert [s.seconds for s in extended.sections] == [10.0, 35.0]
    assert level_duration(extended) == pytest.approx(45.0)
    again = with_runout(extended, 20.0)
    assert again.runout == pytest.approx(50.0)
    # The level it was made from is as it was.
    assert level.runout is None and level.sections[1].seconds == 5.0


def test_p07_r03_the_runout_starts_where_its_seconds_begin() -> None:
    level = make_level([section("a", 10, flat()), section("b", 5, flat())], speed=100.0)
    assert runout_start(level) is None
    assert runout_start(with_runout(level, 0.0)) is None
    # The runout is the last 30 seconds: it starts where the level stopped before it.
    assert runout_start(with_runout(level, 30.0)) == pytest.approx(1500.0)


def test_a_runout_keeps_the_fields_of_the_last_section() -> None:
    streets = street_grid()
    last = section("b", 5, flat(), streets=streets, building_density=0.7)
    extended = with_runout(make_level([section("a", 10, flat()), last]), 3.0)
    copy = extended.sections[1]
    assert copy.streets is streets
    assert copy.building_density == 0.7
    assert copy.seconds == pytest.approx(8.0)


def test_with_runout_of_a_level_without_sections_is_the_same_level() -> None:
    empty = make_level([])
    assert with_runout(empty, 10.0) is empty


def test_the_terrain_and_prop_data_records_keep_their_fields() -> None:
    from core.scenery.scenery_level import (  # noqa: PLC0415
        BlockFill,
        CarRules,
        Drift,
        FloatRules,
        HamletRules,
        Landmark,
        Loners,
        Meander,
        PropGroupRule,
        PropKindRule,
        PropLine,
        Sea,
        TileRules,
    )

    drift = Drift(2.0, 3.0, 4.0)
    assert (drift.x, drift.z, drift.period) == (2.0, 3.0, 4.0)
    kind = PropKindRule("k", 1.0, 2.0, (0.5, 1.0), drift=drift)
    assert kind.drift is drift
    floating = FloatRules(40.0, 2, 5.0, [kind])
    assert (floating.cell_size, floating.per_cell, floating.depth) == (40.0, 2, 5.0)
    line = PropLine("pipe", Meander(0.0, 1.0, 2.0), 30.0, 4.0, 0.2, over_water=True)
    assert (line.kind, line.spacing, line.over_water) == ("pipe", 30.0, True)
    landmark = Landmark("dam", 100.0, (5.0, 5.0), on_water=True)
    assert (landmark.kind, landmark.z, landmark.on_water) == ("dam", 100.0, True)
    group = PropGroupRule("g", 2.0, [kind])
    assert (group.id, group.weight, group.kinds) == ("g", 2.0, [kind])
    loners = Loners(50.0, 0.1, 6.0)
    assert (loners.cell, loners.chance, loners.clearance) == (50.0, 0.1, 6.0)
    hamlets = HamletRules((100.0, 200.0), (3.0, 5.0), 40.0, 8.0, 6.0)
    assert (hamlets.radius, hamlets.gap, hamlets.clearance) == (40.0, 8.0, 6.0)
    cars = CarRules(["car"], 0.2, 1.0, 1.5, 12.0, (10.0, 20.0), sidewalk=3.0)
    assert (cars.length_, cars.sidewalk, cars.kinds) == (12.0, 3.0, ["car"])
    assert TileRules(24.0, 4.0).sidewalk == 4.0
    assert Sea(12.0).level == 12.0
    block = BlockFill(["p1"], (1.0, 2.0), (3.0, 4.0))
    assert (block.podiums, block.podium_height, block.towers) == (["p1"], (1.0, 2.0), (3.0, 4.0))


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


def test_hamlets_skip_streets_and_sections_without_buildings() -> None:
    grid = TerrainSection(
        "grid",
        10,
        flat_away("grid", 10, 0).relief,
        1,
        1,
        streets=StreetGrid([50, 60], [50, 60], 1),
    )
    empty = TerrainSection("empty", 10, flat_away("empty", 10, 0).relief, 0, 1)
    for sect in (grid, empty):
        site = FakeSite(section=sect)
        place_hamlets(site, HAMLETS, ZSpan(-math.inf, math.inf))
        assert site.added == []


def test_floating_props_need_a_kind_and_a_count() -> None:
    field = field_of(deep_sea())
    no_kinds = FloatRules(40, 2, 3, [])
    assert floating_props(no_kinds, field, 0, 7, 0, 1) == []
    none_per_cell = FloatRules(40, 0, 3, [ICE])
    assert floating_props(none_per_cell, field, 0, 7, 0, 1) == []


def test_line_pieces_stand_on_dry_ground_along_the_path() -> None:
    field = field_of(flat_floats("land", 20, 10))
    line = PropLine("pipe", Meander(0, 0, 100), 20, 1, 10)
    pieces = line_pieces(line, field, 0)
    assert len(pieces) == math.ceil(field.length_ / 20)
    for piece in pieces:
        p = piece.placement
        assert piece.footprint == 1
        assert p.kind == "pipe"
        assert p.x == 0
        assert p.y == field.height(p.x, p.z)
        assert p.rotation == -math.pi / 2


def test_line_pieces_stay_in_their_sections_and_gentle_ground() -> None:
    field = field_of(flat_floats("land", 20, 10))
    only_other = PropLine("pipe", Meander(0, 0, 100), 20, 1, 10, sections=["nowhere"])
    assert line_pieces(only_other, field, 0) == []
    too_steep = PropLine("pipe", Meander(0, 0, 100), 20, 1, -1)
    assert line_pieces(too_steep, field, 0) == []


def test_line_pieces_cross_water_only_when_over_water() -> None:
    field = field_of(deep_sea())
    line = PropLine("pipe", Meander(0, 0, 100), 20, 1, 10)
    assert line_pieces(line, field, 0) == []
    on_stilts = PropLine("pipe", Meander(0, 0, 100), 20, 1, 10, over_water=True)
    pieces = line_pieces(on_stilts, field, 0)
    assert pieces
    assert all(p.placement.y == 0 for p in pieces)


def test_landmarks_stand_at_their_x_on_the_ground() -> None:
    field = field_of(flat_floats("land", 20, 10))
    lm = Landmark("dam", 40, (5, 3), x=12)
    building = place_landmark(lm, field, None)
    p = building.placement
    assert (p.kind, p.x, p.z) == ("dam", 12, 40)
    assert p.y == field.height(12, 40)
    assert (p.rotation, p.scale) == (0, 1)
    assert (building.half_x, building.half_z) == (5, 3)


def test_landmarks_on_a_path_are_turned_across_it() -> None:
    field = field_of(flat_floats("land", 20, 10))
    path = Meander(0, 0, 100)
    lm = Landmark("waterfall", 40, (5, 3), path=path, rotation=0.25, scale=2)
    p = place_landmark(lm, field, None).placement
    assert p.x == field.path_x(path, 40)
    assert p.rotation == (-math.pi / 2 + math.pi / 2) + 0.25
    assert p.scale == 2


def test_fixed_pieces_are_the_landmarks_then_the_lines() -> None:
    field = field_of(flat_floats("land", 20, 10))
    rules: PropRules = sample_props(
        lines=[PropLine("pipe", Meander(0, 0, 100), 100, 1, 10)],
        landmarks=[Landmark("dam", 40, (5, 3), x=0)],
    )
    pieces = fixed_pieces(rules, field, None)
    assert [b.placement.kind for b in pieces][0] == "dam"
    assert {b.placement.kind for b in pieces[1:]} == {"pipe"}
    assert fixed_pieces(sample_props(), field, None) == []


def test_no_chance_means_no_lakes() -> None:
    none = Lakes(spacing=100, chance=0, radius=(20, 20), level=-5, edge=10)
    assert with_lakes(none, 7, 50, 50, 10) == 10


def test_a_lake_square_too_small_for_its_lake_is_centred() -> None:
    big = Lakes(spacing=20, chance=1, radius=(30, 30), level=-5, edge=10)
    lake = LakeField(big, 7)._lake(0, 0)
    assert lake is not None
    assert lake.cx == pytest.approx(10)
    assert lake.cz == pytest.approx(10)


def test_crevasses_with_no_share_or_no_width_cut_nothing() -> None:
    noise = create_noise2d(5)
    nothing = Crevasses(spacing=100, width=20, depth=8, angle_deg=0, warp=0, share=0)
    assert crevasse_depth(nothing, noise, 0, 0) == 0
    thin = Crevasses(spacing=100, width=0, depth=8, angle_deg=0, warp=0, share=1)
    assert crevasse_depth(thin, noise, 0, 30) == 0


def test_p04_review_square_plans_stand_at_the_setback_and_pack_apart() -> None:
    square = block_kind(footprint=8, frontage=5)
    level = dense_level()
    level = sample_level(
        sections=level.sections,
        props=sample_props(groups=[PropGroupRule("g", 1, [square])]),
    )
    p = placer_for(level)
    blocks = [b for b in p.place(AREA) if b.kind == "block"]
    assert len(blocks) > 20
    for b in blocks:
        assert p.roads.edge_distance(b.x, b.z) == pytest.approx(5 + SETBACK, abs=1e-5)
    for i, a in enumerate(blocks):
        for b in blocks[i + 1 :]:
            assert max(abs(a.x - b.x), abs(a.z - b.z)) >= 10 - 1e-6


def test_p04_review_a_slot_whose_building_does_not_fit_tries_a_smaller_kind() -> None:
    # Where the large building does not fit (it is 400 wide, next to a road), the smaller one does.
    huge = block_kind(footprint=400)
    small = stick_kind(id="small", weight=0, footprint=4)
    level = sample_level(
        sections=[
            flat_props("low", 10, 10),
            flat_props("high", 10, 30),
        ],
        props=sample_props(
            groups=[PropGroupRule("g", 1, [huge, small])],
            trees=[],
        ),
    )
    kinds = {p.kind for p in placer_for(level).place(AREA)}
    assert "small" in kinds


def test_p04_review_blocks_get_a_podium_covering_them_with_towers_on_its_roof() -> None:
    level = dense_level()
    section = level.sections[0]
    section.blocks = BlockFill(["pod"], [5, 5], [4, 4])
    section.trees = []
    p = placer_for(level)
    props = p.place(AREA)
    podiums = [q for q in props if q.kind == "pod"]
    assert len(podiums) > 5
    for podium in podiums:
        w, h, d = podium.size or [0, 0, 0]
        block = next(
            b
            for b in p.roads.blocks
            if abs((b.x_min + b.x_max) / 2 - podium.x) < 1e-6
            and abs((b.z_min + b.z_max) / 2 - podium.z) < 1e-6
        )
        assert w == pytest.approx(block.x_max - block.x_min)
        assert d == pytest.approx(block.z_max - block.z_min)
        assert h >= 5
    towers = [q for q in props if q.kind == "block"]
    assert towers
    assert all(t.y > min(q.y for q in podiums) for t in towers)


def test_p04_review_blocks_without_podiums_stand_on_the_ground() -> None:
    level = dense_level()
    level.sections[0].blocks = BlockFill([], [5, 5], [2, 2])
    level.sections[0].trees = []
    props = placer_for(level).place(AREA)
    assert props
    assert all(p.size is None for p in props)
    assert any(p.kind == "block" for p in props)


def test_p04_r04_a_section_with_no_groups_or_a_group_without_kinds_has_no_buildings() -> None:
    sections = [flat_props("low", 10, 10), flat_props("high", 10, 30)]
    for sect in sections:
        sect.groups = []
    assert all(p.kind != "block" for p in placer_for(sample_level(sections=sections)).place(AREA))
    empty = sample_level(props=sample_props(groups=[PropGroupRule("g", 1, [])]))
    assert all(p.kind != "block" for p in placer_for(empty).place(AREA))


def test_the_group_of_an_area_is_one_of_those_its_section_allows() -> None:
    level = sample_level()
    p = placer_for(level)
    section = p.field.section_at(10).section
    group = p.group_at(0, 10, section)
    assert group is not None
    assert group.id == "blocks"
    section_none = TerrainSection("x", 10, Relief(0, 0, 1, 1, "smooth"), 1, 1, groups=[])
    assert p.group_at(0, 10, section_none) is None


def test_p08_r03_a_line_of_props_stands_along_the_level_before_the_buildings() -> None:
    level = sample_level(
        props=sample_props(lines=[PropLine("pipe", Meander(0, 0, 100), 50, 1, 10)])
    )
    p = placer_for(level)
    pipes = [q for q in p.place(AREA) if q.kind == "pipe"]
    assert pipes
    for pipe in pipes:
        assert pipe.x == pytest.approx(0)
    buildings = [b for b in p.snapshot().buildings if b.placement.kind == "pipe"]
    assert len(buildings) == len(pipes)


def test_p08_r07_floating_props_float_on_the_sea() -> None:
    deep = TerrainSection(
        "sea",
        20,
        Relief(-20, 1, 1 / 100, 1, "smooth"),
        building_density=0,
        tree_density=0,
        float_density=1,
    )
    level = sample_level(
        sections=[deep],
        props=sample_props(
            floating=FloatRules(40, 2, 3, [stick_kind(id="ice", footprint=2)]), trees=[]
        ),
    )
    floats = [q for q in placer_for(level, sea_level=0).place(AREA) if q.kind == "ice"]
    assert floats
    assert all(q.y == 0 for q in floats)
    assert all(q.kind != "ice" for q in placer_for(level, sea_level=None).place(AREA))


def test_a_set_piece_keeps_the_buildings_off_its_ground() -> None:
    level = sample_level(props=sample_props(landmarks=[Landmark("dam", 100, (5, 3), x=0)]))
    p = placer_for(level)
    assert not p.free(_Ground(0, 100, 1), 0)
    assert p.free(_Ground(50, 100, 1), 0)


def test_p04_r04_a_level_with_loners_places_its_first_chunk() -> None:
    level = sample_level(props=sample_props(loners=Loners(40, 1, 2)))
    placer_for(level).place(AREA)


def test_hamlets_add_bunches_of_buildings_away_from_the_roads() -> None:
    plain = placer_for().place(AREA)
    level = sample_level(
        props=sample_props(hamlets=HamletRules([100, 100], [3, 3], 20, 2, 1)),
    )
    with_hamlets = placer_for(level).place(AREA)
    assert len([p for p in with_hamlets if p.kind == "block"]) > len(
        [p for p in plain if p.kind == "block"]
    )


def test_the_tile_districts_are_packed_when_the_roads_have_tiles() -> None:
    level = sample_level(roads=sample_roads(tiles=TileRules(40, 4)))
    p = placer_for(level)
    p.place(AREA)
    assert p.roads.tiles is not None


def test_dual_roads_are_laid_when_asked() -> None:
    level = sample_level(roads=sample_roads(dual=Dual(12, 1, 0)))
    assert placer_for(level).roads.roads
