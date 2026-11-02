# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/scenery/cliff_blocks.py` (GFX-PROP-19)."""

import math

from helpers.level_builders import flat, make_level, section
from helpers.sample_level import sample_level, sample_props

from core.scenery.cliff_blocks import cliff_blocks
from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField
from core.scenery.prop_placement import PropPlacer
from core.scenery.road_network import level_roads
from core.scenery.scenery_level import CliffRules, Scarps

RULES = CliffRules(["crag-a", "crag-b"], 0.5, 7.0, (6.0, 10.0), (4.0, 8.0), 2.0)
# No block below this height (the props' `min_height`).
SEA = -1000.0
AREA = GroundArea(-200.0, 200.0, 0.0, 400.0)
# Straight ridges facing +Z, their faces a tenth of a 300 cycle: a slope of about 1.3 to 2.
STEEP = Scarps(40.0, 300.0, 0.0, 0.0, 0.1, 1.0)


def _field(scarps: Scarps | None = None) -> HeightField:
    return HeightField(make_level([section("a", 10, flat(10), scarps=scarps)]))


def test_gfx_prop_19_flat_ground_has_no_blocks() -> None:
    assert cliff_blocks(_field(), RULES, 3, AREA, SEA) == []


def test_gfx_prop_19_blocks_stand_only_where_the_ground_is_steep_enough() -> None:
    field = _field(STEEP)
    blocks = cliff_blocks(field, RULES, 3, AREA, SEA)
    assert blocks
    for b in blocks:
        assert field.slope(b.x, b.z, 3.5) > RULES.min_slope * 0.5
        assert AREA.x_min <= b.x < AREA.x_max + RULES.spacing
        assert AREA.z_min <= b.z < AREA.z_max + RULES.spacing
    # The gentle backs (most of the ground) have none.
    assert len(blocks) < 0.3 * (400 / 7) * (400 / 7)


def test_gfx_prop_19_a_block_is_sunk_into_the_ground_sized_and_of_a_listed_kind() -> None:
    field = _field(STEEP)
    for b in cliff_blocks(field, RULES, 3, AREA, SEA):
        assert b.kind in RULES.kinds
        assert b.y < field.height(b.x, b.z)
        assert b.y > field.height(b.x, b.z) - RULES.embed - 2.0
        assert b.size is not None
        width, height, depth = b.size
        assert 1.0 * RULES.spacing <= width <= 1.45 * RULES.spacing
        assert RULES.height[0] <= height <= RULES.height[1]
        assert RULES.depth[0] <= depth <= RULES.depth[1]


def test_gfx_prop_19_no_block_stands_below_the_props_min_height() -> None:
    """The shelves under the sea are steep too: no block on them."""
    field = _field(STEEP)
    blocks = cliff_blocks(field, RULES, 3, AREA, SEA)
    tops = [field.height(b.x, b.z) for b in blocks]
    limit = (min(tops) + max(tops)) / 2
    above = cliff_blocks(field, RULES, 3, AREA, limit)
    assert 0 < len(above) < len(blocks)
    for b in above:
        assert field.height(b.x, b.z) >= limit - 1.0


def test_gfx_prop_19_a_block_faces_downhill() -> None:
    """The faces drop towards +Z, so the blocks' fronts turn to +Z (a yaw near 0)."""
    blocks = cliff_blocks(_field(STEEP), RULES, 3, AREA, SEA)
    assert blocks
    for b in blocks:
        assert abs(math.sin(b.rotation)) < 0.5
        assert math.cos(b.rotation) > 0.5


def test_gfx_prop_19_blocks_are_the_same_for_the_same_seed_and_once_across_areas() -> None:
    field = _field(STEEP)
    whole = cliff_blocks(field, RULES, 3, AREA, SEA)
    again = cliff_blocks(field, RULES, 3, AREA, SEA)
    assert [(b.x, b.z, b.kind) for b in whole] == [(b.x, b.z, b.kind) for b in again]
    left = cliff_blocks(field, RULES, 3, GroundArea(-200.0, 0.0, 0.0, 400.0), SEA)
    right = cliff_blocks(field, RULES, 3, GroundArea(0.0, 200.0, 0.0, 400.0), SEA)
    assert sorted((b.x, b.z) for b in left + right) == sorted((b.x, b.z) for b in whole)
    assert cliff_blocks(field, RULES, 4, AREA, SEA) != whole


def test_gfx_prop_19_no_kinds_or_an_empty_area_give_no_blocks() -> None:
    field = _field(STEEP)
    none = CliffRules([], 0.5, 7.0, (6.0, 10.0), (4.0, 8.0), 2.0)
    assert cliff_blocks(field, none, 3, AREA, SEA) == []
    assert cliff_blocks(field, RULES, 3, GroundArea(0.0, 0.0, 0.0, 0.0), SEA) == []


def test_gfx_prop_19_the_placer_hands_the_blocks_out_with_the_buildings() -> None:
    level = sample_level(
        sections=[section("a", 10, flat(10), scarps=STEEP)], props=sample_props(cliffs=RULES)
    )
    field = HeightField(level, level.seed)
    placer = PropPlacer(field, level.props, level.seed, level_roads(field, level.roads, 1))
    kinds = {p.kind for p in placer.place_without_trees(AREA)}
    assert "crag-a" in kinds or "crag-b" in kinds
