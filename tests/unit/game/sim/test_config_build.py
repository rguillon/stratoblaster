"""Unit tests of `src/game/sim/config_build.py`."""

from game.sim.config_build import mapped, maybe, opt


def test_opt_passes_a_present_value_and_maps_a_missing_one_to_none() -> None:
    assert opt(3) == 3
    assert opt(0) == 0
    assert opt(None) is None


def test_maybe_converts_a_present_value_only() -> None:
    assert maybe(2, lambda v: v * 10) == 20
    assert maybe(None, lambda v: v * 10) is None


def test_mapped_converts_each_item_in_order_and_an_absent_list_is_empty() -> None:
    assert mapped([1, 2, 3], lambda v: v + 1) == [2, 3, 4]
    assert mapped(None, lambda v: v + 1) == []
    assert mapped([], lambda v: v + 1) == []
