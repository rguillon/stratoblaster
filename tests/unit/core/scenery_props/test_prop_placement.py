"""Props on a level (`core.scenery.prop_placement`, P04-R04, P04-R07): buildings along the roads,
trees on the grid of cells, placed in chunks, and the worker's and the snapshot's hand-over."""

import math

import pytest
from sample_level import (
    block_kind,
    flat,
    sample_level,
    sample_props,
    sample_roads,
    stick_kind,
)

from core.scenery.ground_boxes import GroundArea, overlap
from core.scenery.height_field import HeightField
from core.scenery.prop_placement import (
    CHUNK_SIZE,
    PropPlacer,
    chunk_of,
)
from core.scenery.road_network import RoadNetworkOptions, level_roads
from core.scenery.scenery_level import (
    BlockFill,
    Dual,
    FloatRules,
    HamletRules,
    Landmark,
    Loners,
    Meander,
    PropGroupRule,
    PropLine,
    Relief,
    StreetGrid,
    TerrainSection,
    TileRules,
)

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


def keys(placements) -> list[tuple]:
    """The placements as plain tuples (PropPlacement has no equality)."""
    return [(p.kind, p.x, p.y, p.z, p.rotation, p.scale) for p in placements]


def record_key(record) -> tuple:
    """A building record as a plain tuple of its prop's kind and place."""
    return (record.placement.kind, record.placement.x, record.placement.y, record.placement.z)


def dense_level():
    """The sample with a dense grid of streets over the whole level: many buildings to pack."""
    flat_section = flat("grid", 20, 10)
    flat_section.streets = StreetGrid([20, 25], [20, 30], 0.8)
    return sample_level(sections=[flat_section])


def test_p04_r04_the_same_seed_places_the_same_props() -> None:
    props = placer_for().place(AREA)
    assert len(props) > 20
    assert keys(placer_for().place(AREA)) == keys(props)
    assert {p.kind for p in props} == {"block", "stick"}
    assert keys(placer_for(seed=99).place(AREA)) != keys(props)


def test_p04_r04_props_stand_on_the_ground_they_are_placed_on() -> None:
    level = sample_level()
    field = HeightField(level, level.seed)
    for p in placer_for(level).place(AREA):
        if p.kind != "block":
            continue
        assert p.y <= field.height(p.x, p.z) + 1e-9


def test_p04_r07_buildings_stand_along_the_roads_set_back_and_facing_them() -> None:
    p = placer_for()
    buildings = [b for b in p.place(AREA) if b.kind == "block"]
    assert len(buildings) > 5
    footprint = 5
    for b in buildings:
        edge = p.roads.edge_distance(b.x, b.z)
        assert edge >= footprint + SETBACK - 1e-6
        assert edge < footprint + SETBACK + 1
        # The model's front (-Z), turned by the rotation, points at the nearest road.
        fx, fz = -math.sin(b.rotation), -math.cos(b.rotation)
        assert p.roads.edge_distance(b.x + fx * 3, b.z + fz * 3) < edge
    kinds = {r.kind for r in p.roads.roads}
    assert {"main", "cross"} <= kinds


def test_p04_review_buildings_never_overlap_even_packed_on_a_dense_street_grid() -> None:
    p = placer_for(dense_level())
    p.place(AREA)
    records = p.snapshot().buildings
    assert len(records) > 20
    for i, a in enumerate(records):
        for b in records[i + 1 :]:
            assert not overlap(a, b, 0)


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
        sections=[flat("low", 10, 10), flat("high", 10, 30)],
        props=sample_props(
            groups=[PropGroupRule("g", 1, [huge, small])],
            trees=[],
        ),
    )
    kinds = {p.kind for p in placer_for(level).place(AREA)}
    assert "small" in kinds


def test_p04_review_street_grids_without_blocks_keep_their_street_fronts() -> None:
    props = placer_for(dense_level()).place(AREA)
    buildings = [p for p in props if p.kind == "block"]
    assert buildings
    assert all(p.size is None for p in buildings)


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


def test_p04_r04_steep_ground_has_no_buildings() -> None:
    level = sample_level(props=sample_props(max_slope=1e-9, trees=[]))
    assert all(p.kind != "block" for p in placer_for(level).place(AREA))


def test_p04_r04_trees_stand_on_the_grid_away_from_the_roads_and_buildings() -> None:
    p = placer_for()
    props = p.place(AREA)
    trees = [t for t in props if t.kind == "stick"]
    assert trees
    for t in trees:
        assert p.roads.edge_distance(t.x, t.z) >= 1 + 1 - 1e-6
        assert 1 <= t.scale <= 2
        assert 0 <= t.rotation < 2 * math.pi
    buildings = p.snapshot().buildings
    for t in trees:
        tree = _Ground(t.x, t.z, 1)
        assert all(not overlap(b, tree, 0) for b in buildings)


class _Ground:
    """A box of ground for the overlap checks: a tree's box is `half` each way."""

    def __init__(self, x: float, z: float, half: float) -> None:
        from core.scenery.ground_boxes import PropPlacement  # noqa: PLC0415

        self.placement = PropPlacement("", x, 0, z, 0, 1)
        self.half_x = half
        self.half_z = half


def test_trees_need_a_kind_a_count_a_density_and_flat_ground() -> None:
    assert all(
        p.kind != "stick"
        for p in placer_for(sample_level(props=sample_props(trees_per_cell=0))).place(AREA)
    )
    assert all(
        p.kind != "stick"
        for p in placer_for(sample_level(props=sample_props(trees=[]))).place(AREA)
    )
    lazy = [flat("low", 10, 10), flat("high", 10, 30)]
    for section in lazy:
        section.tree_density = 0
    assert all(p.kind != "stick" for p in placer_for(sample_level(sections=lazy)).place(AREA))
    steep = sample_level(props=sample_props(tree_max_slope=1e-9))
    assert all(p.kind != "stick" for p in placer_for(steep).place(AREA))
    unknown = [flat("low", 10, 10), flat("high", 10, 30)]
    for section in unknown:
        section.trees = ["nothing"]
    assert all(p.kind != "stick" for p in placer_for(sample_level(sections=unknown)).place(AREA))


def test_p04_r04_no_building_density_no_buildings() -> None:
    sections = [flat("low", 10, 10), flat("high", 10, 30)]
    for section in sections:
        section.building_density = 0
    props = placer_for(sample_level(sections=sections)).place(AREA)
    assert all(p.kind != "block" for p in props)


def test_p04_r04_a_section_with_no_groups_or_a_group_without_kinds_has_no_buildings() -> None:
    sections = [flat("low", 10, 10), flat("high", 10, 30)]
    for section in sections:
        section.groups = []
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


def test_chunk_of_is_the_floor_of_z_over_the_chunk_size() -> None:
    assert CHUNK_SIZE == 200
    assert chunk_of(-1) == -1
    assert chunk_of(0) == 0
    assert chunk_of(199.9) == 0
    assert chunk_of(200) == 1


def test_p04_r04_chunks_give_the_same_buildings_whatever_the_order_they_are_asked_for() -> None:
    all_at_once = placer_for()
    chunks = all_at_once.ensure_placed_chunks(1000)
    assert [c.k for c in chunks] == sorted(c.k for c in chunks)
    in_steps = placer_for()
    made = []
    for z in (-300, 100, 300, 1000):
        made.extend(in_steps.ensure_placed(z))
    flat_chunks = [b for c in chunks for b in c.buildings]
    assert len(made) == len(flat_chunks) > 0
    assert [record_key(b) for b in made] == [record_key(b) for b in flat_chunks]


def test_p04_r04_placing_is_idempotent_and_a_chunk_is_placed_once() -> None:
    p = placer_for()
    first = p.ensure_placed(500)
    assert first
    assert p.ensure_placed(500) == []
    assert p.ensure_placed(-1000) == []


def test_p04_r04_the_placement_of_an_area_does_not_depend_on_earlier_queries() -> None:
    fresh = keys(placer_for().place(AREA))
    busy = placer_for()
    busy.place(GroundArea(-200, 200, 600, 1000))
    busy.place(GroundArea(-200, 200, 0, 100))
    assert keys(busy.place(AREA)) == fresh


def test_p04_r04_the_chunks_of_the_level_are_all_placed_at_its_end() -> None:
    p = placer_for()
    assert not p.chunks_done
    p.ensure_placed(10_000)
    assert p.chunks_done
    assert p.placed_to == chunk_of(400 + 400) + 1


def test_want_placed_places_here_when_nothing_else_places() -> None:
    p = placer_for()
    p.want_placed(300)
    assert p.placed_to == chunk_of(300) + 1


def test_want_placed_asks_the_worker_once_for_each_new_chunk() -> None:
    p = placer_for()
    asked: list[float] = []
    p.ask = asked.append
    p.want_placed(100)
    p.want_placed(120)
    p.want_placed(300)
    assert asked == [100, 300]


def test_a_worker_hands_its_chunks_over_and_they_are_taken_as_they_are() -> None:
    worker = placer_for()
    chunks = worker.ensure_placed_chunks(1000)
    main = placer_for()
    main.ask = lambda z: None
    main.receive(chunks)
    assert main.placed_to == worker.placed_to
    assert keys(main.place(AREA)) == keys(worker.place(AREA))


def test_a_chunk_placed_already_is_not_taken_twice() -> None:
    worker = placer_for()
    chunks = worker.ensure_placed_chunks(1000)
    main = placer_for()
    main.ensure_placed(1000)
    before = len(main.snapshot().buildings)
    main.receive(chunks)
    assert len(main.snapshot().buildings) == before


def test_p13_r03_a_snapshot_makes_the_same_placer_without_placing_again() -> None:
    level = sample_level()
    field = HeightField(level, level.seed)
    original = PropPlacer(
        field, level.props, level.seed, level_roads(field, level.roads, level.seed), sea_level=0
    )
    original.ensure_placed(600)
    snapshot = original.snapshot()
    roads = level_roads(
        field,
        level.roads,
        level.seed,
        RoadNetworkOptions(made=original.roads.snapshot()),
    )
    again = PropPlacer(field, level.props, level.seed, roads, sea_level=0, made=snapshot)
    assert again.placed_to == original.placed_to
    assert keys(again.place(AREA)) == keys(original.place(AREA))


def test_the_runout_is_laid_before_the_chunk_that_needs_it() -> None:
    p = placer_for(runout_from=300)
    assert not p.runout_laid
    p.ensure_placed(-300)
    assert not p.runout_laid
    p.ensure_placed(-100)
    assert p.runout_laid
    assert p.runout_added is not None


def test_the_runout_is_laid_once_and_what_it_added_is_kept() -> None:
    p = placer_for(runout_from=300)
    first = p.lay_runout()
    kept = p.runout_added
    assert kept is not None
    second = p.lay_runout()
    assert second.roads == []
    assert p.runout_added is kept
    assert first.roads is not None


def test_placing_an_area_past_the_runout_lays_it() -> None:
    p = placer_for(runout_from=300)
    p.place(GroundArea(-200, 200, -300, -100))
    assert p.runout_laid


def test_a_level_without_a_runout_has_no_gate() -> None:
    p = placer_for()
    p.ensure_placed(1000)
    assert not p.runout_laid


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


def test_p08_r03_set_pieces_are_placed_first_and_the_buildings_keep_clear() -> None:
    level = sample_level(props=sample_props(landmarks=[Landmark("dam", 100, (5, 3), x=0)]))
    p = placer_for(level)
    dams = [q for q in p.place(AREA) if q.kind == "dam"]
    assert len(dams) == 1
    dam_record = p.snapshot().buildings[0]
    assert dam_record.placement.kind == "dam"
    for b in p.snapshot().buildings[1:]:
        assert not overlap(dam_record, b, 0)


def test_a_set_piece_keeps_the_buildings_off_its_ground() -> None:
    level = sample_level(props=sample_props(landmarks=[Landmark("dam", 100, (5, 3), x=0)]))
    p = placer_for(level)
    assert not p.free(_Ground(0, 100, 1), 0)
    assert p.free(_Ground(50, 100, 1), 0)


def test_p04_r04_free_keeps_the_gap_clear_of_the_placed_buildings() -> None:
    p = placer_for()
    p.ensure_placed(1000)
    assert p.free(_Ground(0, 0, 0.5), 0) is True
    records = p.snapshot().buildings
    near = records[0].placement
    assert not p.free(_Ground(near.x, near.z, 0.5), 0)
    assert not p.free(_Ground(near.x, near.z, 0.5))


def test_without_a_road_it_can_be_built_there_are_no_buildings() -> None:
    level = sample_level(roads=sample_roads(min_height=1000))
    props = placer_for(level).place(AREA)
    assert all(p.kind != "block" for p in props)


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
