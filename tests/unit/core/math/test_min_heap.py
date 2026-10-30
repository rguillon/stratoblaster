"""Binary min-heap (`core.math.min_heap`)."""

from core.math.min_heap import MinHeap
from core.math.rng import create_rng, random_in


def _drain(heap: MinHeap) -> list[float]:
    out: list[float] = []
    while heap.size > 0:
        value = heap.pop()
        assert value is not None
        out.append(value)
    return out


def test_empty_heap_has_no_size_and_pops_none() -> None:
    heap = MinHeap([])
    assert heap.size == 0
    assert heap.pop() is None


def test_initial_increasing_values_are_a_valid_heap() -> None:
    heap = MinHeap([1, 2, 3, 4, 5])
    assert heap.size == 5
    assert heap.pop() == 1


def test_pop_returns_the_smallest_first() -> None:
    heap = MinHeap([])
    for value in [5, 1, 4, 2, 3]:
        heap.push(value)
    assert heap.size == 5
    assert _drain(heap) == [1, 2, 3, 4, 5]


def test_push_smaller_than_the_top_becomes_the_top() -> None:
    heap = MinHeap([10, 20, 30])
    heap.push(5)
    assert heap.pop() == 5


def test_duplicates_come_out_in_order() -> None:
    heap = MinHeap([2, 2])
    heap.push(1)
    heap.push(2)
    assert _drain(heap) == [1, 2, 2, 2]


def test_single_element_round_trip() -> None:
    heap = MinHeap([])
    heap.push(7.5)
    assert heap.pop() == 7.5
    assert heap.size == 0
    assert heap.pop() is None


def test_heap_sorts_a_seeded_random_sequence() -> None:
    random = create_rng(99)
    values = [random_in(random, -100, 100) for _ in range(200)]
    heap = MinHeap(sorted(values[:50]))
    for value in values[50:]:
        heap.push(value)
    assert _drain(heap) == sorted(values)
