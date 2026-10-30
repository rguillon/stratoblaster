"""The dead ends and crossings of a district's street grid, fixed (phase 4 review, phase 6
review), split out of `street-grid.ts`. Ported from `core/scenery/street-dead-ends.ts`."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.math.rng import Random  # noqa: E402
from core.scenery.street_links import Link, LinksAt, Node  # noqa: E402

__pragma__("noskip")

from core.math.min_heap import MinHeap  # noqa: E402

# Most passes of the dead-end removal (each pass can extend or cut every dead end by a link).
MAX_PASSES = 500

SIDES = ["left", "right", "down", "up"]
# The chance of either way at a crossing (a coin toss).
HALF_SIDE = 0.5

# Bit set of the four sides of a crossing (all four sides: 0b1111).
ALL_SIDES = 15


def _links_of(at: LinksAt, node_id: int) -> Sequence[Link]:
    """`at[node_id]`, or no links for a node number out of range (or unused: -1)."""
    return at[node_id] if 0 <= node_id < len(at) else []


def _side_of(node: Node, link: Link) -> int:
    """The side of `node` that `link` leaves it by, as an index of `SIDES`."""
    if link.a is node:
        self_node, other = link.a, link.b
    else:
        self_node, other = link.b, link.a
    if link.across:
        return 0 if other.x < self_node.x else 1
    return 2 if other.z < self_node.z else 3


def _is_crossing(node: Node, around: Sequence[Link] | None, extra: Link | None = None) -> bool:
    """Whether built streets (and `extra`, if given) leave `node` on all four sides."""
    sides = 0
    if around is not None:
        for link in around:
            if link.built or link is extra:
                sides = sides | (1 << _side_of(node, link))
    return sides == ALL_SIDES


def _makes_crossing(link: Link, node: Node, at: LinksAt) -> bool:
    """Whether building `link`, from `node`, would make a crossing at its far end."""
    far = link.b if link.a is node else link.a
    return _is_crossing(far, _links_of(at, far.id), link)


def _fix_dead_end(
    node: Node,
    at: LinksAt,
    out_of_view: Callable[[Node], bool],
    tees: bool,
    keep_cut: bool,
) -> Link | None:
    """Fixes `node` if a single built street ends there on screen: the street goes on straight when
    the next link's ground allows it (and, with `tees`, its far end is no T-junction it would turn
    into a crossing, nor was cut back before), else it is cut back. Returns the link it changed."""
    around = _links_of(at, node.id)
    only: Link | None = None
    built = 0
    for link in around:
        if not link.built:
            continue
        built += 1
        if only is None:
            only = link
    if built != 1 or only is None or out_of_view(node):
        return None
    ahead: Link | None = None
    for link in around:
        if link is not only and link.across == only.across:
            ahead = link
            break
    if ahead is not None and _may_go_on(ahead, node, at, tees, keep_cut):
        ahead.built = True
        return ahead
    only.built = False
    only.cut = True
    return only


def _may_go_on(ahead: Link, node: Node, at: LinksAt, tees: bool, keep_cut: bool) -> bool:
    """Whether a dead end at `node` may go on through `ahead` (see `_fix_dead_end`)."""
    if not ahead.ground or (keep_cut and ahead.cut):
        return False
    return not (tees and (ahead.cut or _makes_crossing(ahead, node, at)))


def remove_dead_ends(
    at: LinksAt,
    nodes: Sequence[Node],
    out_of_view: Callable[[Node], bool],
    tees: bool,
    keep_cut: bool | None = None,
) -> None:
    """Fixes the dead ends, pass after pass over the nodes in order, until a pass changes nothing.
    Reviewer, 2026-10-28: a pass only looks at the nodes whose links changed since they were last
    looked at (those it would have fixed); the others would be left as they are. Same passes, same
    fixes in the same order, without going through every node each time.

    `keep_cut`: a link cut back is never built again, so a street cannot keep being cut from one
    end and built again from the other (the default; the removal flips until `MAX_PASSES`
    otherwise and can leave an on-screen dead end).
    """
    keep = True if keep_cut is None else keep_cut
    passes = _Passes(len(nodes))
    for _ in range(MAX_PASSES):
        changed = False
        node_id = passes.take()
        while node_id is not None:
            node = nodes[node_id] if node_id < len(nodes) else None
            link = _fix_dead_end(node, at, out_of_view, tees, keep) if node is not None else None
            if link is not None:
                changed = True
                passes.again(link.a.id, node_id)
                passes.again(link.b.id, node_id)
            node_id = passes.take()
        if not changed:
            return
        passes.turn()


class _Passes:
    """The nodes a pass of the dead-end removal still looks at, in order, and those of the next."""

    def __init__(self, count: int) -> None:
        self._now = MinHeap(list(range(count)))
        self._next: list[int] = []
        self._in_now: list[int] = [1 for _ in range(count)]
        self._in_next: list[int] = [0 for _ in range(count)]

    def take(self) -> int | None:
        """The next node this pass looks at, if any."""
        value = self._now.pop()
        if value is None:
            return None
        node_id = int(value)
        self._in_now[node_id] = 0
        return node_id

    def again(self, node_id: int, current: int) -> None:
        """Looks at node `node_id` again: later in this pass if it comes after `current`, else in
        the next."""
        if node_id > current and self._in_now[node_id] == 0:
            self._in_now[node_id] = 1
            self._now.push(node_id)
        elif node_id <= current and self._in_next[node_id] == 0:
            self._in_next[node_id] = 1
            self._next.append(node_id)

    def turn(self) -> None:
        """Starts the next pass."""
        nxt = sorted(self._next)
        for node_id in nxt:
            self._in_next[node_id] = 0
            self._in_now[node_id] = 1
        self._now = MinHeap(nxt)
        self._next = []


def _side_to_cut(around: Sequence[Link], random: Random) -> str | None:
    """The side of a crossing whose street goes: up or down the level, or left or right where a
    boulevard runs along the level, so it keeps going straight. None where two boulevards cross."""
    along = any(not link.across and link.boulevard for link in around)
    across = any(link.across and link.boulevard for link in around)
    if along and across:
        return None
    coin = random() < HALF_SIDE
    if along:
        return "left" if coin else "right"
    return "down" if coin else "up"


def remove_crossings(
    at: LinksAt,
    nodes: Sequence[Node],
    out_of_view: Callable[[Node], bool],
    random: Random,
) -> None:
    """Turns every crossing into a T-junction (see `straight_runs`): the streets leaving it up or
    down the level go. Cutting makes no crossing, nor does fixing the dead ends that leaves with
    `tees`, so one pass is enough."""
    for node in nodes:
        around = _links_of(at, node.id)
        if not _is_crossing(node, around):
            continue
        side = _side_to_cut(around, random)
        for link in around:
            if side is not None and link.built and SIDES[_side_of(node, link)] == side:
                link.built = False
    remove_dead_ends(at, nodes, out_of_view, True)
