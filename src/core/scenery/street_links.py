"""The nodes and links of a district's street grid (phase 4 review), ported from
`core/scenery/street-links.ts`."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

LinksAt = Sequence[Sequence["Link"]]
__pragma__("noskip")


def to_fixed3(x: float) -> str:
    """`x.toFixed(3)`: the number with three decimals, as JavaScript writes it."""
    __pragma__("js", "{}", "return x.toFixed(3);")
    return str(round(x, 3))  # Only reached outside Transcrypt (CPython).


class Block:
    """A city block: the ground between the streets around one cell of a district's grid, up to
    the street edges (TypeScript `street-grid.ts`; defined here to keep `tile-streets` and
    `street-grid` free of an import cycle)."""

    def __init__(self, x_min: float, x_max: float, z_min: float, z_max: float) -> None:
        self.x_min = x_min
        self.x_max = x_max
        self.z_min = z_min
        self.z_max = z_max


class Node:
    """A point of the street network: one object per place (to within 0.001), numbered in the
    order it is first used (reviewer, 2026-10-28: numbers, not text keys, in the dead-end
    removal)."""

    def __init__(self, x: float, z: float, id: int) -> None:
        self.x = x
        self.z = z
        self.id = id
        """Order of first use, the order dead ends are fixed in; -1 until used."""


# Nodes of a district are numbered below this, so a pair of them makes one number.
NODE_LIMIT = 2097152


def _key(x: float, z: float) -> str:
    return to_fixed3(x) + "," + to_fixed3(z)


def pair(a: Node, b: Node) -> int:
    """One number for the link from `a` to `b`."""
    return a.id * NODE_LIMIT + b.id


class Nodes:
    """The nodes of a district, each place made once."""

    def __init__(self, buildable: Callable[[float, float], bool]) -> None:
        self._buildable = buildable
        self._by_place: dict[str, Node] = {}
        self._grounds: dict[str, bool] = {}
        self.used: list[Node] = []
        """The nodes used, by number."""

    def at(self, x: float, z: float) -> Node:
        """The node at (`x`, `z`)."""
        k = _key(x, z)
        node = self._by_place.get(k)
        if node is None:
            node = Node(x, z, -1)
            self._by_place[k] = node
        return node

    def use(self, node: Node) -> Node:
        """`node`, numbered if it was not used yet."""
        if node.id < 0:
            node.id = len(self.used)
            self.used.append(node)
        return node

    def ground(self, node: Node) -> bool:
        """Whether a street can be built on the ground at `node`."""
        # One node object per place, so the place's key stands for the node.
        k = _key(node.x, node.z)
        cached = self._grounds.get(k)
        if cached is None:
            cached = self._buildable(node.x, node.z)
            self._grounds[k] = cached
        return cached


class Link:
    """A stretch of street between two neighbouring crossings."""

    def __init__(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
        self,
        a: Node,
        b: Node,
        across: bool,
        required: bool,
        boulevard: bool,
        ground: bool,
        built: bool,
        cut: bool,
    ) -> None:
        self.a = a
        self.b = b
        self.across = across
        """Whether the stretch runs across the level."""
        self.required = required
        """Links on a district or section boundary are always built (if their ground allows)."""
        self.boulevard = boulevard
        """On a boulevard's line: always built, and never cut to undo a crossing."""
        self.ground = ground
        """Whether a street can be built on the ground there."""
        self.built = built
        self.cut = cut
        """Cut back while removing dead ends: with `tees`, never built again, so a street cannot
        keep going on and being cut back."""


def dedupe(links: Sequence[Link]) -> list[Link]:
    """Drops links laid twice (the shared boundary rows), keeping the first."""
    seen: dict[str, bool] = {}
    result: list[Link] = []
    for link in links:
        k = str(pair(link.a, link.b))
        if k in seen:
            continue
        seen[k] = True
        result.append(link)
    return result


def links_by_node(links: Sequence[Link], count: int) -> LinksAt:
    """The links at each of the `count` nodes, by node number."""
    at: list[list[Link]] = [[] for _ in range(count)]
    for link in links:
        for n in [link.a, link.b]:
            if 0 <= n.id < count:
                at[n.id].append(link)
    return at
