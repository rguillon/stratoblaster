"""The nodes and links of a district's street grid (`core/scenery/street_links.py`)."""

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
