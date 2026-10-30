"""Unit tests of `src/core/scenery/draws.py`."""

from types import SimpleNamespace

from core.scenery.draws import allowed, between, weighted


def _item(id: str, weight: float) -> SimpleNamespace:
    return SimpleNamespace(id=id, weight=weight)


def test_weighted_gives_each_item_a_share_as_big_as_its_weight() -> None:
    items = [_item("a", 1.0), _item("b", 3.0)]
    assert weighted(items, 0.1).id == "a"
    assert weighted(items, 0.2).id == "a"
    assert weighted(items, 0.3).id == "b"
    assert weighted(items, 0.99).id == "b"


def test_weighted_of_no_items_or_no_weight() -> None:
    assert weighted([], 0.5) is None
    zero = [_item("a", 0.0), _item("b", 0.0)]
    assert weighted(zero, 0.5).id == "b"


def test_allowed_keeps_the_listed_ids_or_all_of_them() -> None:
    items = [_item("a", 1.0), _item("b", 1.0), _item("c", 1.0)]
    assert [i.id for i in allowed(items)] == ["a", "b", "c"]
    assert [i.id for i in allowed(items, ["c", "a"])] == ["a", "c"]
    assert allowed(items, []) == []


def test_between_maps_a_draw_onto_the_range() -> None:
    assert between([2.0, 4.0], 0.0) == 2.0
    assert between([2.0, 4.0], 0.25) == 2.5
    assert between([-1.0, 1.0], 0.5) == 0.0
