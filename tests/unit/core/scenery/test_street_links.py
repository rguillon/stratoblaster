"""Unit tests of `src/core/scenery/street_links.py`."""

import pytest

from core.math.rng import create_rng
from core.scenery.street_dead_ends import remove_crossings
from core.scenery.street_links import (
    NODE_LIMIT,
    Block,
    Link,
    Node,
    Nodes,
    dedupe,
    links_by_node,
    pair,
    to_fixed3,
)
from core.scenery.street_runs import straight_runs


def _link(
    nodes: Nodes, a: tuple[float, float], b: tuple[float, float], across: bool = True
) -> Link:
    na = nodes.use(nodes.at(*a))
    nb = nodes.use(nodes.at(*b))
    return Link(na, nb, across, False, False, True, True, False)


def test_p04_r08_crossings_are_turned_into_t_junctions() -> None:
    nodes = Nodes(lambda x, z: True)
    centre = nodes.use(nodes.at(10.0, 0.0))
    ends = [
        nodes.use(nodes.at(0.0, 0.0)),
        nodes.use(nodes.at(20.0, 0.0)),
        nodes.use(nodes.at(10.0, -10.0)),
        nodes.use(nodes.at(10.0, 10.0)),
    ]
    links = [
        Link(ends[0], centre, True, False, False, True, True, False),
        Link(centre, ends[1], True, False, False, True, True, False),
        Link(ends[2], centre, False, False, False, True, True, False),
        Link(centre, ends[3], False, False, False, True, True, False),
    ]
    at = links_by_node(links, len(nodes.used))
    out = lambda n: n is not centre  # noqa: E731
    remove_crossings(at, nodes.used, out, create_rng(1))
    built_at_centre = [link for link in links if link.built and centre in (link.a, link.b)]
    assert len(built_at_centre) == 3
    assert links[0].built and links[1].built
    assert sum(1 for link in links[2:] if link.built) == 1


def test_p04_r08_crossing_boulevards_are_both_kept() -> None:
    nodes = Nodes(lambda x, z: True)
    centre = nodes.use(nodes.at(10.0, 0.0))
    ends = [
        nodes.use(nodes.at(0.0, 0.0)),
        nodes.use(nodes.at(20.0, 0.0)),
        nodes.use(nodes.at(10.0, -10.0)),
        nodes.use(nodes.at(10.0, 10.0)),
    ]
    links = [
        Link(ends[0], centre, True, False, True, True, True, False),
        Link(centre, ends[1], True, False, True, True, True, False),
        Link(ends[2], centre, False, False, True, True, True, False),
        Link(centre, ends[3], False, False, True, True, True, False),
    ]
    at = links_by_node(links, len(nodes.used))
    remove_crossings(at, nodes.used, lambda n: n is not centre, create_rng(1))
    assert all(link.built for link in links)


def test_p04_r08_a_crossing_of_boulevards_along_the_level_keeps_its_cross_streets_straight() -> (
    None
):
    nodes = Nodes(lambda x, z: True)
    centre = nodes.use(nodes.at(10.0, 0.0))
    ends = [
        nodes.use(nodes.at(0.0, 0.0)),
        nodes.use(nodes.at(20.0, 0.0)),
        nodes.use(nodes.at(10.0, -10.0)),
        nodes.use(nodes.at(10.0, 10.0)),
    ]
    # Only the streets along the level (Z) are boulevards: the streets across it are cut instead.
    links = [
        Link(ends[0], centre, True, False, False, True, True, False),
        Link(centre, ends[1], True, False, False, True, True, False),
        Link(ends[2], centre, False, False, True, True, True, False),
        Link(centre, ends[3], False, False, True, True, True, False),
    ]
    at = links_by_node(links, len(nodes.used))
    remove_crossings(at, nodes.used, lambda n: n is not centre, create_rng(1))
    assert not (links[0].built and links[1].built)
    assert links[2].built and links[3].built


def test_to_fixed3_writes_three_decimals() -> None:
    assert to_fixed3(1.23456) == "1.235"
    assert to_fixed3(-4.0) == "-4.0"


def test_block_and_node_hold_their_fields() -> None:
    block = Block(0.0, 10.0, -5.0, 5.0)
    assert (block.x_min, block.x_max, block.z_min, block.z_max) == (0.0, 10.0, -5.0, 5.0)
    node = Node(1.0, 2.0, -1)
    assert (node.x, node.z, node.id) == (1.0, 2.0, -1)


def test_nodes_make_one_object_per_place_and_number_them_on_first_use() -> None:
    nodes = Nodes(lambda x, z: True)
    a = nodes.at(10.0, 20.0)
    assert nodes.at(10.0, 20.0) is a
    assert a.id == -1
    assert nodes.use(a) is a and a.id == 0
    b = nodes.use(nodes.at(0.0, 0.0))
    assert b.id == 1
    assert nodes.use(a).id == 0
    assert nodes.used == [a, b]


def test_nodes_ask_the_ground_once_per_place() -> None:
    asked: list[tuple[float, float]] = []

    def buildable(x: float, z: float) -> bool:
        asked.append((x, z))
        return x > 0

    nodes = Nodes(buildable)
    node = nodes.at(5.0, 5.0)
    assert nodes.ground(node) is True
    assert nodes.ground(nodes.at(5.0, 5.0)) is True
    assert nodes.ground(nodes.at(-5.0, 5.0)) is False
    assert asked == [(5.0, 5.0), (-5.0, 5.0)]


def test_pair_numbers_a_link_from_its_two_nodes() -> None:
    nodes = Nodes(lambda x, z: True)
    a = nodes.use(nodes.at(0.0, 0.0))
    b = nodes.use(nodes.at(1.0, 0.0))
    assert pair(a, b) == 0 * NODE_LIMIT + 1
    assert pair(b, a) == 1 * NODE_LIMIT + 0
    assert pair(a, b) != pair(b, a)


def test_dedupe_keeps_the_first_of_each_link() -> None:
    nodes = Nodes(lambda x, z: True)
    a = nodes.use(nodes.at(0.0, 0.0))
    b = nodes.use(nodes.at(1.0, 0.0))
    first = Link(a, b, True, True, False, True, True, False)
    again = Link(a, b, True, False, False, True, False, False)
    other = Link(b, nodes.use(nodes.at(2.0, 0.0)), True, False, False, True, True, False)
    assert dedupe([first, again, other]) == [first, other]


def test_links_by_node_lists_each_link_at_both_its_ends() -> None:
    nodes = Nodes(lambda x, z: True)
    a = nodes.use(nodes.at(0.0, 0.0))
    b = nodes.use(nodes.at(1.0, 0.0))
    c = nodes.use(nodes.at(2.0, 0.0))
    ab = Link(a, b, True, False, False, True, True, False)
    bc = Link(b, c, True, False, False, True, True, False)
    stray = Link(Node(9.0, 9.0, -1), a, True, False, False, True, True, False)
    at = links_by_node([ab, bc, stray], 3)
    assert at[0] == [ab, stray]
    assert at[1] == [ab, bc]
    assert at[2] == [bc]


def test_p04_r08_built_links_in_a_line_make_one_straight_run() -> None:
    nodes = Nodes(lambda x, z: True)
    links = [
        _link(nodes, (20.0, 0.0), (30.0, 0.0)),
        _link(nodes, (0.0, 0.0), (10.0, 0.0)),
        _link(nodes, (10.0, 0.0), (20.0, 0.0)),
    ]
    runs = straight_runs(links, 5.0)
    assert len(runs) == 1
    assert [p.x for p in runs[0]] == pytest.approx([0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])
    assert all(p.z == 0.0 for p in runs[0])


def test_a_gap_in_the_line_starts_another_run() -> None:
    nodes = Nodes(lambda x, z: True)
    links = [
        _link(nodes, (0.0, 0.0), (10.0, 0.0)),
        _link(nodes, (30.0, 0.0), (40.0, 0.0)),
    ]
    runs = straight_runs(links, 5.0)
    assert [len(run) for run in runs] == [3, 3]


def test_runs_across_and_along_are_separate_lines() -> None:
    nodes = Nodes(lambda x, z: True)
    runs = straight_runs(
        [
            _link(nodes, (0.0, 0.0), (10.0, 0.0), across=True),
            _link(nodes, (0.0, 0.0), (0.0, 10.0), across=False),
        ],
        5.0,
    )
    assert len(runs) == 2
