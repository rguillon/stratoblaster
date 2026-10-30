"""Unit tests of `src/core/scenery/height_field.py`."""

import math

import pytest
from helpers.level_builders import (
    SAMPLE_POINTS,
    flat,
    hills,
    make_level,
    road_rules,
    section,
    street_grid,
)
from helpers.sample_level import sample_level

from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField, _octaves_steepness, _section_steepness, soft_cap
from core.scenery.prop_placement import PropPlacer
from core.scenery.road_network import RoadNetworkOptions, level_roads
from core.scenery.scenery_level import Channel, Flatten, Lakes, Meander

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


AREA = GroundArea(-200, 200, 0, 400)


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


def test_p04_r01_heights_are_the_same_for_the_same_seed() -> None:
    level = make_level([section("a", 10, hills()), section("b", 10, hills(80))], seed=3)
    assert _heights(HeightField(level)) == _heights(HeightField(level))


def test_p04_r01_heights_change_with_the_seed() -> None:
    a = HeightField(make_level([section("a", 10, hills())], seed=3))
    b = HeightField(make_level([section("a", 10, hills())], seed=4))
    assert _heights(a) != _heights(b)


def test_p04_r01_an_explicit_seed_overrides_the_level_seed() -> None:
    level = make_level([section("a", 10, hills())], seed=3)
    other = make_level([section("a", 10, hills())], seed=9)
    assert _heights(HeightField(level, seed=9)) == _heights(HeightField(other))


def test_p04_r01_sections_are_placed_end_to_end_and_found_by_z() -> None:
    level = make_level([section("a", 10, flat(10)), section("b", 20, flat(50))])
    field = HeightField(level)
    assert field.length_ == pytest.approx(3000.0)
    assert field.section_index_at(-50) == 0
    assert field.section_index_at(999.9) == 0
    assert field.section_index_at(1000) == 1
    assert field.section_index_at(99999) == 1
    assert field.section_at(1500).section.name == "b"


def test_p04_r01_before_the_level_and_after_it_the_ends_continue() -> None:
    field = HeightField(make_level([section("a", 10, flat(10)), section("b", 10, flat(50))]))
    assert field.height(0, -500) == pytest.approx(10)
    assert field.height(0, 99999) == pytest.approx(50)


def test_p04_r01_sections_blend_over_the_transition() -> None:
    level = make_level([section("a", 10, flat(10)), section("b", 10, flat(50))], transition=200)
    field = HeightField(level)
    assert field.height(0, 900) == pytest.approx(10)
    assert field.height(0, 1000) == pytest.approx(30)
    assert field.height(0, 1100) == pytest.approx(50)
    assert field.height(0, 1050) == pytest.approx(43.75)  # still in the blend band


def test_p04_r01_without_transition_the_change_is_sudden() -> None:
    field = HeightField(make_level([section("a", 10, flat(10)), section("b", 10, flat(50))]))
    assert field.height(0, 999) == pytest.approx(10)
    assert field.height(0, 1000) == pytest.approx(50)


def test_negative_transition_is_no_transition() -> None:
    a = make_level([section("a", 10, flat(10)), section("b", 10, flat(50))], transition=-5)
    b = make_level([section("a", 10, flat(10)), section("b", 10, flat(50))])
    assert _heights(HeightField(a)) == _heights(HeightField(b))


def test_flat_ground_has_no_slope_and_no_steepness() -> None:
    field = HeightField(make_level([section("a", 10, flat(10))]))
    assert field.slope(12.0, 40.0) == pytest.approx(0.0)
    assert field.steepness(12.0, 40.0, 30.0) == pytest.approx(0.0)


def test_p04_r01_the_ceiling_bounds_the_ground() -> None:
    level = make_level([section("a", 10, hills(50, 30, 60.0)), section("b", 10, hills(70, 20))])
    field = HeightField(level)
    assert field.ceiling == pytest.approx(max(60.0, 90.0))
    assert max(_heights(field)) <= field.ceiling + 1e-9


def test_soft_cap_leaves_low_heights_and_squashes_high_ones() -> None:
    assert soft_cap(5.0, 10.0) == 5.0
    assert soft_cap(7.5, 10.0) == pytest.approx(7.5)
    assert 7.5 < soft_cap(20.0, 10.0) < soft_cap(30.0, 10.0) < 10.0
    assert soft_cap(-5.0, 0.0) == -5.0
    assert soft_cap(5.0, 0.0) < 0.001


def test_p04_r01_max_height_keeps_the_peaks_under_it() -> None:
    field = HeightField(make_level([section("a", 10, hills(50, 30, 60.0))]))
    assert max(_heights(field)) <= 60.0 + 1e-9


def test_flatten_is_the_relief_away_from_its_band() -> None:
    flatten = Flatten(STRAIGHT, 10.0, 10.0, 40.0, 0.0)
    plain = HeightField(make_level([section("a", 10, flat(10))]))
    field = HeightField(make_level([section("a", 10, flat(10), flatten=flatten)]))
    assert field.height(60.0, 300.0) == pytest.approx(plain.height(60.0, 300.0))


def test_channel_is_carved_below_the_ground_and_not_beyond_its_walls() -> None:
    channel = Channel(STRAIGHT, 10.0, 10.0, -5.0)
    plain = HeightField(make_level([section("a", 10, flat(10))]))
    field = HeightField(make_level([section("a", 10, flat(10), channel=channel)]))
    assert field.height(0.0, 300.0) == pytest.approx(-5.0, abs=1.0)
    assert field.height(40.0, 300.0) == pytest.approx(plain.height(40.0, 300.0))


def test_lakes_dip_the_ground_into_basins() -> None:
    lakes = Lakes(200.0, 1.0, (40.0, 60.0), 0.0, 20.0)
    field = HeightField(make_level([section("a", 10, flat(50), lakes=lakes)]))
    assert min(_heights(field)) < 50.0
    again = HeightField(make_level([section("a", 10, flat(50), lakes=lakes)]))
    assert _heights(again) == _heights(field)


def test_a_section_without_cover_has_none() -> None:
    field = HeightField(make_level([section("a", 10, flat())]))
    cover = field.surface(10.0)
    assert (cover.lush, cover.paved, cover.sandy) == (0, 0, 0)


def test_p04_r01_steepness_bounds_the_change_along_x() -> None:
    field = HeightField(make_level([section("a", 10, hills())]))
    reach = 20.0
    for x, z in [(0.0, 50.0), (33.0, 300.0), (-120.0, 700.0)]:
        bound = field.steepness(x, z, reach)
        assert math.isfinite(bound) and bound > 0
        for dx in (2.0, 5.0, 10.0):
            change = abs(field.height(x + dx, z) - field.height(x, z))
            assert change <= bound * dx + 1e-9


def test_steepness_is_unknown_for_sections_shorter_than_the_transition() -> None:
    field = HeightField(make_level([section("a", 1, hills())], transition=200))
    assert _section_steepness(field.sections[0], 200) is None
    assert field.steepness(0.0, 50.0, 5.0) == math.inf


def test_steepness_blends_with_the_next_section_near_their_boundary() -> None:
    level = make_level([section("a", 10, flat(10)), section("b", 10, flat(50))], transition=200)
    field = HeightField(level)
    assert field.steepness(0.0, 1000.0, 10.0) == pytest.approx((1.5 / 200) * 40)
    assert field.steepness(0.0, 500.0, 10.0) == pytest.approx(0.0)


def test_p04_r01_slope_is_at_most_root_two_times_the_steepness() -> None:
    field = HeightField(make_level([section("a", 10, hills())]))
    for x, z in [(0.0, 50.0), (33.0, 300.0)]:
        assert field.slope(x, z, 1) <= math.sqrt(2) * field.steepness(x, z, 1) + 1e-9


def test_octaves_steepness_grows_with_the_octaves() -> None:
    assert _octaves_steepness(0) == 0
    assert _octaves_steepness(1) == pytest.approx(1.0)
    assert _octaves_steepness(2) == pytest.approx(4 / 3)


def test_p04_r01_the_section_before_blends_into_the_next_near_the_boundary() -> None:
    level = make_level([section("a", 10, flat(10)), section("b", 10, flat(50))], transition=200)
    field = HeightField(level)
    # 950 is in the band (900 to 1100) of section a's end: a smoothstep of 0.25,
    # here 10 + 40 * 0.15625.
    assert field.height(0, 950) == pytest.approx(16.25)


def test_p04_r07_a_level_roads_span_runs_past_both_ends_of_the_level() -> None:
    level = _level(streets=False)
    net = level_roads(HeightField(level), level.roads, 4)
    assert net.range.z_min == -3000.0
    assert net.range.z_max == pytest.approx(HeightField(level).length_ + 3000.0)
    assert net.blocks is not None


def test_p04_r04_props_stand_on_the_ground_they_are_placed_on() -> None:
    level = sample_level()
    field = HeightField(level, level.seed)
    for p in placer_for(level).place(AREA):
        if p.kind != "block":
            continue
        assert p.y <= field.height(p.x, p.z) + 1e-9
