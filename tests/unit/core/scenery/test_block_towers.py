"""Unit tests of `src/core/scenery/block_towers.py`."""

from core.scenery.block_towers import TOWER_MARGIN, tower_in
from core.scenery.scenery_level import PropGroupRule, PropKindRule
from core.scenery.street_links import Block


def _group(*kinds: PropKindRule) -> PropGroupRule:
    return PropGroupRule("g", 1.0, list(kinds))


def test_no_tower_when_no_kind_fits() -> None:
    big = PropKindRule("big", 1.0, 10.0, (0.5, 1.0), frontage=10.0)
    assert tower_in(Block(0.0, 2.0, 0.0, 2.0), [_group(big)], 0.0, 0.5) is None
    assert tower_in(Block(0.0, 40.0, 0.0, 40.0), [], 0.0, 0.5) is None


def test_p04_r07_a_tower_stays_in_its_part_and_leaves_the_margin() -> None:
    kind = PropKindRule("tower", 1.0, 6.0, (0.5, 1.0), frontage=6.0)
    part = Block(100.0, 140.0, 200.0, 240.0)
    for r in (0.0, 0.2, 0.49, 0.5, 0.77, 0.99):
        building = tower_in(part, [_group(kind)], 0.0, r)
        assert building is not None
        x = building.placement.x
        z = building.placement.z
        assert (
            part.x_min + building.half_x + TOWER_MARGIN
            <= x
            <= part.x_max - building.half_x - TOWER_MARGIN
        )
        assert (
            part.z_min + building.half_z + TOWER_MARGIN
            <= z
            <= part.z_max - building.half_z - TOWER_MARGIN
        )
