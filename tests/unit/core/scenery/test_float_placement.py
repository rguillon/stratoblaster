"""Unit tests of `src/core/scenery/float_placement.py`."""

import math

from helpers.sample_level import flat, sample_level

from core.scenery.float_placement import _along_path, floating_in, floating_props, place_landmark
from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField
from core.scenery.scenery_level import (
    FloatRules,
    Landmark,
    Meander,
    PropKindRule,
    Relief,
    TerrainSection,
)

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


def shallow_sea() -> TerrainSection:
    """A section of sea bed a unit under the sea: too shallow for ice."""
    return TerrainSection(
        "shore",
        20,
        Relief(-1, 0.1, 1 / 100, 1, "smooth"),
        building_density=0,
        tree_density=0,
        float_density=1,
    )


def field_of(section: TerrainSection) -> HeightField:
    return HeightField(sample_level(sections=[section]))


RULES = FloatRules(cell_size=40, per_cell=2, depth=3, kinds=[ICE])


def test_floating_props_float_on_the_sea_where_it_is_deep() -> None:
    field = field_of(deep_sea())
    props = [
        p
        for i in range(-2, 4)
        for j in range(0, 6)
        for p in floating_props(RULES, field, 0, 7, i, j)
    ]
    assert props
    assert all(p.kind == "ice" and p.y == 0 for p in props)


def test_floating_props_need_a_section_with_float_density() -> None:
    assert floating_props(RULES, field_of(deep_sea(0)), 0, 7, 0, 1) == []
    assert floating_props(RULES, field_of(deep_sea(None)), 0, 7, 0, 1) == []


def test_floating_props_are_refused_where_the_sea_is_shallow() -> None:
    field = field_of(shallow_sea())
    props = [
        p
        for i in range(-2, 4)
        for j in range(0, 6)
        for p in floating_props(RULES, field, 0, 7, i, j)
    ]
    assert props == []


def test_floating_props_are_the_same_for_a_seed() -> None:
    field = field_of(deep_sea())
    first = floating_props(RULES, field, 0, 7, 0, 2)
    second = floating_props(RULES, field, 0, 7, 0, 2)
    assert [(p.x, p.z, p.rotation) for p in first] == [(p.x, p.z, p.rotation) for p in second]


def test_floating_in_is_the_cells_whose_corner_lies_in_the_area() -> None:
    field = field_of(deep_sea())
    area = GroundArea(0, 80, 0, 80)
    got = floating_in(RULES, field, 0, 7, area)
    expected = [
        p
        for j in range(0, 2)
        for i in range(0, 2)
        for p in floating_props(RULES, field, 0, 7, i, j)
    ]
    assert [(p.x, p.z) for p in got] == [(p.x, p.z) for p in expected]


def test_along_path_turns_a_model_with_its_path() -> None:
    field = field_of(flat("land", 20, 10))
    assert _along_path(field, Meander(0, 0, 100), 50) == -math.pi / 2


def test_landmarks_on_water_float_at_the_sea_level_when_it_is_higher() -> None:
    field = field_of(deep_sea())
    building = place_landmark(Landmark("dock", 40, (5, 3), x=0, on_water=True), field, 0)
    assert building.placement.y == 0
    no_water = place_landmark(Landmark("dock", 40, (5, 3), x=0), field, 0)
    assert no_water.placement.y == field.height(0, 40)
