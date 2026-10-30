"""Unit tests of `src/core/scenery/prop_placement.py`."""

import math

from helpers.sample_level import flat, sample_level, sample_props, sample_roads

from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField
from core.scenery.prop_placement import CHUNK_SIZE, PropPlacer, chunk_of
from core.scenery.road_network import RoadNetworkOptions, level_roads
from core.scenery.scenery_level import StreetGrid

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


class _Ground:
    """A box of ground for the overlap checks: a tree's box is `half` each way."""

    def __init__(self, x: float, z: float, half: float) -> None:
        from core.scenery.ground_boxes import PropPlacement  # noqa: PLC0415

        self.placement = PropPlacement("", x, 0, z, 0, 1)
        self.half_x = half
        self.half_z = half


def test_p04_r04_the_same_seed_places_the_same_props() -> None:
    props = placer_for().place(AREA)
    assert len(props) > 20
    assert keys(placer_for().place(AREA)) == keys(props)
    assert {p.kind for p in props} == {"block", "stick"}
    assert keys(placer_for(seed=99).place(AREA)) != keys(props)


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


def test_p04_review_street_grids_without_blocks_keep_their_street_fronts() -> None:
    props = placer_for(dense_level()).place(AREA)
    buildings = [p for p in props if p.kind == "block"]
    assert buildings
    assert all(p.size is None for p in buildings)


def test_p04_r04_steep_ground_has_no_buildings() -> None:
    level = sample_level(props=sample_props(max_slope=1e-9, trees=[]))
    assert all(p.kind != "block" for p in placer_for(level).place(AREA))


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


def test_a_level_without_a_runout_has_no_gate() -> None:
    p = placer_for()
    p.ensure_placed(1000)
    assert not p.runout_laid


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


def _trees(level) -> list:
    return [p for p in placer_for(level).place(AREA) if p.kind == "stick"]


def test_d212_woods_keep_the_trees_where_their_noise_is_high() -> None:
    from core.scenery.scenery_level import Forests  # noqa: PLC0415

    everywhere = _trees(sample_level(props=sample_props(trees_per_cell=20)))
    nowhere = _trees(
        sample_level(props=sample_props(trees_per_cell=20, forests=Forests(1 / 300, 1.1, 0)))
    )
    woods = _trees(
        sample_level(props=sample_props(trees_per_cell=20, forests=Forests(1 / 300, 0.5, 0.05)))
    )
    assert len(everywhere) > 0
    assert nowhere == []
    assert len(woods) > 0


def test_d212_with_woods_every_cell_tries_about_the_most_trees() -> None:
    from core.scenery.scenery_level import Forests  # noqa: PLC0415

    # A threshold of 0: every tree grows, so the count is the cells' own.
    level = sample_level(props=sample_props(trees_per_cell=20, forests=Forests(1 / 300, 0, 0)))
    placer = placer_for(level)
    counts = [placer._tree_count(i, 0, 1) for i in range(50)]  # noqa: SLF001
    assert min(counts) >= 16
    assert max(counts) <= 24
    assert placer._tree_count(0, 0, 0) == 0  # noqa: SLF001


def test_d212_a_lower_tree_density_means_fewer_woods() -> None:
    from core.scenery.scenery_level import Forests  # noqa: PLC0415

    def count(density: float) -> int:
        sections = [flat("low", 10, 10), flat("high", 10, 30)]
        for section in sections:
            section.tree_density = density
        props = sample_props(trees_per_cell=20, forests=Forests(1 / 300, 0.3, 0))
        return len(_trees(sample_level(sections=sections, props=props)))

    assert count(1) > count(0.4) >= 0
