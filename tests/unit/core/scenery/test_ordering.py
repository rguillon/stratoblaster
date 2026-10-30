"""Stable sorts of the scenery (`core/scenery/ordering.py`)."""

from core.scenery.ordering import stable_sort_by


def test_sorts_by_the_key_in_increasing_order() -> None:
    assert stable_sort_by([3, 1, 2], lambda v: v) == [1, 2, 3]
    assert stable_sort_by([3, 1, 2], lambda v: -v) == [3, 2, 1]


def test_equal_keys_keep_their_original_order() -> None:
    items = [("a", 1), ("b", 0), ("c", 1), ("d", 0)]
    assert stable_sort_by(items, lambda t: t[1]) == [("b", 0), ("d", 0), ("a", 1), ("c", 1)]


def test_short_lists_are_copied_not_sorted_in_place() -> None:
    items = [5]
    result = stable_sort_by(items, lambda v: v)
    assert result == [5] and result is not items
    assert stable_sort_by([], lambda v: v) == []
    original = [2, 1]
    assert stable_sort_by(original, lambda v: v) == [1, 2]
    assert original == [2, 1]
