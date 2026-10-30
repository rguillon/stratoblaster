"""Unit tests of `src/render/node_pool.py`."""

from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, patch_babylon

from render import node_pool
from render.node_pool import NodePool


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, node_pool)


def _pool(made: list[tuple[int, FakeNode]]) -> NodePool:
    scene = FakeScene()

    def create(index: int) -> FakeNode:
        node = scene.add_node(f"shot-{index}")
        made.append((index, node))
        return node

    return NodePool(create)


def test_show_creates_only_the_missing_nodes() -> None:
    made: list[tuple[int, FakeNode]] = []
    pool = _pool(made)
    assert len(pool.show(2)) == 2
    assert [index for index, _ in made] == [0, 1]
    pool.show(3)
    assert [index for index, _ in made] == [0, 1, 2]


def test_show_enables_the_first_count_and_hides_the_others() -> None:
    made: list[tuple[int, FakeNode]] = []
    pool = _pool(made)
    pool.show(3)
    shown = pool.show(1)
    assert shown == [pool.nodes[0]]
    assert [node.enabled for node in pool.nodes] == [True, False, False]


def test_nodes_are_reused_when_shown_again() -> None:
    made: list[tuple[int, FakeNode]] = []
    pool = _pool(made)
    pool.show(2)
    first = pool.nodes[0]
    pool.show(0)
    assert pool.show(1)[0] is first
    assert len(made) == 2


def test_dispose_disposes_every_node_and_empties_the_pool() -> None:
    made: list[tuple[int, FakeNode]] = []
    pool = _pool(made)
    pool.show(2)
    nodes: list[Any] = list(pool.nodes)
    pool.dispose()
    assert all(node.disposed for node in nodes)
    assert pool.nodes == []
    assert pool.show(1)[0] is not nodes[0]
