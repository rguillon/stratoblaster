"""Unit tests of `src/core/scenery/street_dead_ends.py`."""

from core.scenery.street_dead_ends import remove_dead_ends
from core.scenery.street_links import Link, Nodes, links_by_node


def _chain(xs: list[float], built: list[bool], ground: list[bool] | None = None):
    """Nodes along X at `xs`, linked in turn by across links, built as `built` says."""
    nodes = Nodes(lambda x, z: True)
    ns = [nodes.use(nodes.at(x, 0.0)) for x in xs]
    grounds = ground if ground is not None else [True] * (len(xs) - 1)
    links = [
        Link(ns[i], ns[i + 1], True, False, False, grounds[i], built[i], False)
        for i in range(len(xs) - 1)
    ]
    return nodes, links


def _run(xs, built, out, ground=None, keep_cut=None):
    nodes, links = _chain(xs, built, ground)
    at = links_by_node(links, len(nodes.used))
    remove_dead_ends(at, nodes.used, out, False, keep_cut)
    return links


def _on_screen_dead_ends(nodes, links, out) -> list[float]:
    at = links_by_node(links, len(nodes.used))
    return [
        n.x for n in nodes.used if not out(n) and sum(1 for link in at[n.id] if link.built) == 1
    ]


def test_p04_r08_a_dead_end_on_screen_goes_on_when_the_ground_allows() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    links = _run(xs, [True, True, False], lambda n: n.x in (0.0, 30.0))
    assert [link.built for link in links] == [True, True, True]


def test_p04_r08_a_dead_end_on_screen_is_cut_back_when_nothing_goes_on() -> None:
    xs = [0.0, 10.0, 20.0]
    links = _run(xs, [True, True], lambda n: n.x in (0.0, 10.0))
    assert [link.built for link in links] == [True, False]
    assert links[1].cut is True


def test_p04_r08_with_cut_kept_a_cut_link_is_never_built_again() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    links = _run(xs, [True, True, False], lambda n: n.x == 0.0, keep_cut=True)
    assert [link.built for link in links] == [False, False, False]
    assert links[1].cut is True


def test_p04_r08_a_dead_end_is_not_extended_over_unbuildable_ground() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    links = _run(xs, [True, True, False], lambda n: n.x in (0.0, 30.0), ground=[True, True, False])
    assert links[2].built is False


def test_p04_r08_the_default_removal_leaves_no_dead_end_on_screen() -> None:
    xs = [0.0, 10.0, 20.0, 30.0]
    nodes, links = _chain(xs, [True, True, False], [True, True, False])
    out = lambda n: n.x in (0.0, 30.0)  # noqa: E731
    remove_dead_ends(links_by_node(links, len(nodes.used)), nodes.used, out, False)
    assert _on_screen_dead_ends(nodes, links, out) == []
