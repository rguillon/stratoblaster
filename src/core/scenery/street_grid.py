"""The straight streets of a district (phase 4 review), as maximal straight runs of built links,
each a list of points every `rules.step`. Ported from `core/scenery/street-grid.ts`.

- every section of the district has its own random columns, from past one screen edge to past the
  other, and rows; its first and last rows are full streets, so the columns of two sections meet
  them at T-junctions;
- each other link is built with the chance `links`, if its ground is buildable;
- then dead ends on screen are removed: a street that stops at a crossing goes on straight, or is
  cut back, until every street ends at a crossing, a junction, or off the screen;
- without crossings (`rules.no_crossings`, phase 6 review), every crossing then becomes a
  T-junction: one of its two stretches along the level goes, and the dead ends that leaves are
  removed again, without making new crossings;
- boulevards (`rules.boulevards`, reviewer 2026-10-28) are built along their whole line and run
  straight: at a crossing, the street across them is cut instead.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.math.rng import Random  # noqa: E402
from core.scenery.districts import District  # noqa: E402
from core.scenery.scenery_level import RoadRules  # noqa: E402

__pragma__("noskip")

from core.math.rng import random_in  # noqa: E402
from core.scenery.lanes import is_boulevard, run_width, street_width  # noqa: E402
from core.scenery.street_dead_ends import remove_crossings, remove_dead_ends  # noqa: E402
from core.scenery.street_links import (  # noqa: E402
    Block,
    Link,
    Node,
    Nodes,
    dedupe,
    links_by_node,
    pair,
)
from core.scenery.street_runs import straight_runs  # noqa: E402
from core.scenery.tile_streets import StreetRun, tile_street_runs  # noqa: E402

# Gap between a street's edge and the block beside it.
BLOCK_KERB = 0.5


class Layout:
    """The nodes of one section of a district, by row and column."""

    def __init__(self, grid: list[list[Node]], laid_before: bool) -> None:
        self.grid = grid
        """Rows of nodes, each row a list of columns."""
        self.laid_before = laid_before
        """Its first row was laid before it (by the section, or the district, before it)."""


def _spaced(from_: float, to: float, gap: Sequence[float], random: Random) -> list[float]:
    """Positions from `from_` to `to`, spaced by random gaps in `gap`, both ends included."""
    out = [from_]
    v = from_ + random_in(random, gap[0], gap[1])
    while v < to - gap[0] / 2:
        out.append(v)
        v = v + random_in(random, gap[0], gap[1])
    out.append(to)
    return out


def _concat(a: Sequence[float], b: Sequence[float]) -> list[float]:
    """`a` then `b`, as one new list."""
    result = list(a)
    result.extend(b)
    return result


def _merge_columns(a: Sequence[float], b: Sequence[float]) -> list[float]:
    """The union of two column lists, in increasing order."""
    seen: dict[str, bool] = {}
    union: list[float] = []
    for v in _concat(a, b):
        k = str(v)
        if k not in seen:
            seen[k] = True
            union.append(v)
    return sorted(union)


def street_runs(
    district: District,
    rules: RoadRules,
    random: Random,
    buildable: Callable[[float, float], bool],
    out_of_view: Callable[[Node], bool],
) -> tuple[list[StreetRun], list[Block]]:
    """The runs and the blocks of a district (see the module doc). Returns (runs, blocks)."""
    # Phase 15: on a grid of tiles.
    if rules.tiles is not None:
        return tile_street_runs(district, rules, rules.tiles, random, buildable, out_of_view)
    links, layouts, nodes = _grid_links(district, rules, random, buildable)
    at = links_by_node(links, len(nodes))
    remove_dead_ends(at, nodes, out_of_view, False)
    if rules.no_crossings is not None:
        remove_crossings(at, nodes, out_of_view, random)

    def inset(coord: float) -> float:
        return street_width(rules, coord) / 2 + BLOCK_KERB

    blocks = [
        b
        for b in _grid_blocks(layouts, links, inset)
        if buildable((b.x_min + b.x_max) / 2, (b.z_min + b.z_max) / 2)
    ]
    built_links = [link for link in links if link.built]
    runs = [
        StreetRun(points, run_width(rules, points))
        for points in straight_runs(built_links, rules.step)
    ]
    return runs, blocks


def _grid_blocks(
    layouts: Sequence[Layout],
    links: Sequence[Link],
    inset: Callable[[float], float],
) -> list[Block]:
    built: dict[str, bool] = {}
    for link in links:
        if link.built:
            built[str(pair(link.a, link.b))] = True

    def has(a: Node, b: Node) -> bool:
        return str(pair(a, b)) in built

    blocks: list[Block] = []
    for layout in layouts:
        grid = layout.grid
        for r in range(len(grid) - 1):
            for c in range(len(grid[r]) - 1):
                cell = _corners(grid, c, r)
                # The first row of a later section was laid on the merged columns (or, going on
                # from another district, with it): it is a full street.
                if cell is None:
                    continue
                block = _cell_block(cell, has, r == 0 and layout.laid_before, inset)
                if block is not None:
                    blocks.append(block)
    return blocks


def _corners(
    grid: Sequence[Sequence[Node]], c: int, r: int
) -> tuple[Node, Node, Node, Node] | None:
    """The corners of cell (`c`, `r`) of `grid`: bottom left, bottom right, top left, top right."""
    found: list[Node] = []
    for rr, cc in [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]:
        if 0 <= rr < len(grid) and 0 <= cc < len(grid[rr]):
            found.append(grid[rr][cc])
        else:
            return None
    return found[0], found[1], found[2], found[3]


def _cell_block(
    cell: tuple[Node, Node, Node, Node],
    has: Callable[[Node, Node], bool],
    bottom: bool,
    inset: Callable[[float], float],
) -> Block | None:
    """The block of a cell, up to the edge of the street along each side it has (avenues are
    wider); `bottom` when its first row is known to be a street."""
    n00, n10, n01, n11 = cell
    x0 = n00.x
    x1 = n11.x
    z0 = n00.z
    z1 = n11.z

    def cut(side: bool, coord: float) -> float:
        return inset(coord) if side else 0

    x_min = x0 + cut(has(n00, n01), x0)
    x_max = x1 - cut(has(n10, n11), x1)
    z_min = z0 + cut(bottom or has(n00, n10), z0)
    z_max = z1 - cut(has(n01, n11), z1)
    if x_max > x_min and z_max > z_min:
        return Block(x_min, x_max, z_min, z_max)
    return None


def _grid_links(
    district: District,
    rules: RoadRules,
    random: Random,
    buildable: Callable[[float, float], bool],
) -> tuple[list[Link], list[Layout], list[Node]]:
    edge = rules.offscreen_x + rules.step
    links: list[Link] = []
    nodes = Nodes(buildable)
    layouts: list[Layout] = []
    columns_of: list[list[float]] = []
    for p, part in enumerate(district.parts):
        chance = part.grid.links
        xs = _spaced(-edge, edge, part.grid.columns, random)
        columns_of.append(xs)
        zs = _spaced(part.z_min, part.z_max, part.grid.rows, random)
        goes_on = p == 0 and district.continues is True
        grid = [[nodes.at(x, z) for x in xs] for z in zs]
        layouts.append(Layout(grid, p > 0 or goes_on))
        last_row = len(zs) - 1
        for r, z in enumerate(zs):
            # Going on from another district: its first row was laid with it.
            if r == 0 and goes_on:
                continue
            boundary = r in (0, last_row)
            # A boundary row shared with the previous section was already laid with its columns.
            columns = _merge_columns(columns_of[p - 1], xs) if r == 0 and p > 0 else xs
            for c in range(len(columns) - 1):
                _add_link(
                    links, nodes, rules, buildable, random,
                    (columns[c], z), (columns[c + 1], z), True, boundary, chance,
                )  # fmt: skip
        for x in xs:
            for r in range(len(zs) - 1):
                _add_link(
                    links, nodes, rules, buildable, random,
                    (x, zs[r]), (x, zs[r + 1]), False, False, chance,
                )  # fmt: skip
    return dedupe(links), layouts, nodes.used


def _add_link(  # noqa: PLR0917 (positional data fields: Transcrypt drops keyword arguments)
    links: list[Link],
    nodes: Nodes,
    rules: RoadRules,
    buildable: Callable[[float, float], bool],
    random: Random,
    a_at: tuple[float, float],
    b_at: tuple[float, float],
    across: bool,
    required: bool,
    chance: float,
) -> None:
    ax, az = a_at
    bx, bz = b_at
    a = nodes.use(nodes.at(ax, az))
    b = nodes.use(nodes.at(bx, bz))
    ground = nodes.ground(a) and buildable((ax + bx) / 2, (az + bz) / 2) and nodes.ground(b)
    boulevard = is_boulevard(rules, street_width(rules, az if across else ax))
    built = ground and (required or boulevard or random() < chance)
    links.append(Link(a, b, across, required, boulevard, ground, built, False))


def block_parts(block: Block, nx: int, nz: int) -> list[Block]:
    """`block` cut into `nx` × `nz` equal parts."""
    w = (block.x_max - block.x_min) / nx
    d = (block.z_max - block.z_min) / nz
    parts: list[Block] = []
    for i in range(nx):
        for j in range(nz):
            x_min = block.x_min + i * w
            z_min = block.z_min + j * d
            parts.append(Block(x_min, x_min + w, z_min, z_min + d))
    return parts
