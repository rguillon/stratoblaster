# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/scenery/street_dead_ends.py`."""

from typing import Any

from core.scenery.street_dead_ends import MAX_PASSES, remove_dead_ends
from core.scenery.street_links import Link, Nodes, links_by_node


def _chain(xs: list[float], built: list[bool], ground: list[bool] | None = None) -> Any:
    """Nodes along X at `xs`, linked in turn by across links, built as `built` says."""
    nodes = Nodes(lambda _x, _z: True)
    ns = [nodes.use(nodes.at(x, 0.0)) for x in xs]
    grounds = ground if ground is not None else [True] * (len(xs) - 1)
    links = [
        Link(
            ns[i],
            ns[i + 1],
            across=True,
            required=False,
            boulevard=False,
            ground=grounds[i],
            built=built[i],
            cut=False,
        )
        for i in range(len(xs) - 1)
    ]
    return nodes, links


def _run(xs: Any, built: Any, out: Any, ground: Any = None, keep_cut: Any = None) -> Any:
    nodes, links = _chain(xs, built, ground)
    at = links_by_node(links, len(nodes.used))
    remove_dead_ends(at, nodes.used, out, tees=False, keep_cut=keep_cut)
    return links


def _on_screen_dead_ends(nodes: Any, links: Any, out: Any) -> list[float]:
    at = links_by_node(links, len(nodes.used))
    return [
        n.x for n in nodes.used if not out(n) and sum(1 for link in at[n.id] if link.built) == 1
    ]


def test_gfx_road_16_a_dead_end_on_screen_goes_on_when_the_ground_allows() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    links = _run(xs, [True, True, False], lambda n: n.x in (0.0, 30.0))
    assert [link.built for link in links] == [True, True, True]


def test_gfx_road_16_a_dead_end_on_screen_is_cut_back_when_nothing_goes_on() -> None:
    xs = [0.0, 10.0, 20.0]
    links = _run(xs, [True, True], lambda n: n.x in (0.0, 10.0))
    assert [link.built for link in links] == [True, False]
    assert links[1].cut is True


def test_gfx_road_16_with_cut_kept_a_cut_link_is_never_built_again() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    links = _run(xs, [True, True, False], lambda n: n.x == 0.0, keep_cut=True)
    assert [link.built for link in links] == [False, False, False]
    assert links[1].cut is True


def test_gfx_road_16_a_dead_end_is_not_extended_over_unbuildable_ground() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    links = _run(xs, [True, True, False], lambda n: n.x in (0.0, 30.0), ground=[True, True, False])
    assert links[2].built is False


def test_gfx_road_16_the_default_removal_leaves_no_dead_end_on_screen() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    nodes, links = _chain(xs, [True, True, False], [True, True, False])

    def out(n: Any) -> bool:
        return n.x in (0.0, 30.0)

    remove_dead_ends(links_by_node(links, len(nodes.used)), nodes.used, out, tees=False)
    assert _on_screen_dead_ends(nodes, links, out) == []


def test_gfx_road_16_without_keep_cut_a_flipping_street_stops_after_max_passes() -> None:
    """A street built from one end and cut from the other flips until `MAX_PASSES`.

    It then leaves a dead end on screen, as `remove_dead_ends` says.
    """
    nodes, links = _chain([0.0, 10.0, 20.0], [True, False])
    looks: list[float] = []

    def out(n: Any) -> bool:
        looks.append(n.x)
        return n.x == 0.0

    at = links_by_node(links, len(nodes.used))
    remove_dead_ends(at, nodes.used, out, tees=False, keep_cut=False)
    # Each pass builds the last link again from x = 10, and x = 20 cuts it back.
    assert looks.count(20.0) == MAX_PASSES
    assert [link.built for link in links] == [True, False]
    assert links[1].cut is True
    assert _on_screen_dead_ends(nodes, links, lambda n: n.x == 0.0) == [10.0]


def test_gfx_road_16_a_street_cut_back_link_after_link_reaches_back_off_the_screen() -> None:
    """Its far end, numbered after the others, is looked at again in the pass that cuts to it."""
    nodes = Nodes(lambda _x, _z: True)
    # Numbered in this order: the middle nodes first, the one off the screen (x = 0) last.
    middle, near, far, off = [nodes.use(nodes.at(x, 0.0)) for x in (10.0, 20.0, 30.0, 0.0)]
    links = [
        Link(a, b, True, False, False, True, built, False)
        for a, b, built in [(off, middle, True), (middle, near, False), (near, far, False)]
    ]

    def out(n: Any) -> bool:
        return n is off

    remove_dead_ends(links_by_node(links, len(nodes.used)), nodes.used, out, tees=False)
    # It goes on to the last node, which has nothing ahead: cut back from there, link by link.
    assert [link.built for link in links] == [False, False, False]
    assert all(link.cut for link in links)
