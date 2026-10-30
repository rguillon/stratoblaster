"""P15-R01, R05: the streets of a district laid on a grid of square tiles (phase 15). Rows (along
X) may be wide roads (avenues and boulevards, N tiles wide); columns are one tile wide. Every line
covers whole tiles, and the columns sit where the junction pieces of the wide rows they cross fall
on the rows' own N-tile lattice, so every wide row is made of whole N × N pieces."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.math.rng import Random  # noqa: E402
from core.scenery.districts import District, DistrictPart  # noqa: E402
from core.scenery.scenery_level import RoadRules, TileRules  # noqa: E402

__pragma__("noskip")

from core.math.noise import hash_2d  # noqa: E402
from core.math.rng import random_in  # noqa: E402
from core.scenery.ordering import stable_sort_by  # noqa: E402
from core.scenery.street_dead_ends import remove_dead_ends  # noqa: E402
from core.scenery.street_links import (  # noqa: E402
    Block,
    Link,
    Node,
    Nodes,
    dedupe,
    links_by_node,
    pair,
    to_fixed3,
)
from core.scenery.street_runs import Point, straight_runs  # noqa: E402

# `%` keeps JavaScript's sign rule.
__pragma__("jsmod")


class StreetRun:
    """A straight run of street, with its width (sidewalks included)."""

    def __init__(self, points: list[Point], width: float) -> None:
        self.points = points
        self.width = width


class Line:
    """A line of the grid: its first tile and its size in tiles (and, once placed, its middle
    `z`)."""

    def __init__(self, start: int, size: int, z: float = 0) -> None:
        self.start = start
        self.size = size
        self.z = z


class PartGrid:
    """What a part of a district laid on the grid is made of."""

    def __init__(self, lines: list[Line], xs: list[float], grid: list[list[Node]]) -> None:
        self.lines = lines
        self.xs = xs
        self.grid = grid


def _tile_at(v: float, size: float) -> int:
    """Tile index whose middle is nearest `v`."""
    x = v / size - 0.5
    return math.floor(x + 0.5)


def _middle(line: Line, size: float) -> float:
    """Coordinate of the middle of `line`."""
    return (line.start + line.size / 2) * size


def _mod(a: float, n: float) -> float:
    return ((a % n) + n) % n


def _int_set(values: Sequence[int]) -> dict[str, bool]:
    """A set of tile numbers, as a dictionary keyed by their text."""
    result: dict[str, bool] = {}
    for v in values:
        result[str(v)] = True
    return result


def _unique(values: Sequence[int]) -> list[int]:
    """The values once each, in their first order."""
    seen: dict[str, bool] = {}
    result: list[int] = []
    for v in values:
        k = str(v)
        if k not in seen:
            seen[k] = True
            result.append(v)
    return result


def _unique_nodes(values: Sequence[Node]) -> list[Node]:
    """The nodes once each (by identity), in their first order."""
    result: list[Node] = []
    for n in values:
        if not any(m is n for m in result):
            result.append(n)
    return result


def column_fits(s: int, size: int) -> bool:
    """Whether a one-tile column at tile `s` crosses a row of `size` tiles on that row's lattice
    (P15-R04): its junction piece, `size` wide, starts on a multiple of `size` with the column in
    it as close to its middle as the grid allows."""
    offset = _mod(s, size)
    return offset == math.floor((size - 1) / 2) or offset == math.ceil((size - 1) / 2)


def _row_size(rules: RoadRules, t: int) -> int:
    """Size in tiles of a row starting at tile `t`: a share of them are avenues or boulevards."""
    h = hash_2d(t, 29, 211)
    total = 0.0
    for b in rules.boulevards if rules.boulevards is not None else []:
        if h < total + b.share:
            return b.lanes
        total += b.share
    return 2 if h < total + rules.dual.avenues else 1


def _next_gap(gap: Sequence[float], tile: float, random: Random) -> int:
    """Tile gap to the next line: a spacing of `gap` world units between middles, in tiles."""
    return max(2, math.floor(random_in(random, gap[0], gap[1]) / tile + 0.5))


def _part_rows(rules: RoadRules, tile: TileRules, part: DistrictPart, random: Random) -> list[Line]:
    """The rows of a part, from its first to its last (both one tile wide)."""
    first = _tile_at(part.z_min, tile.size)
    last = _tile_at(part.z_max, tile.size)
    previous = Line(first, 1)
    rows = [previous]
    if last <= first:
        return rows
    while True:
        start = previous.start + previous.size - 1 + _next_gap(part.grid.rows, tile.size, random)
        size = _row_size(rules, start)
        # Room for a block of at least one tile before the last row.
        if start + size + 1 > last:
            break
        previous = Line(start, size)
        rows.append(previous)
    rows.append(Line(last, 1))
    return rows


def _fitting_tile(from_: int, step: int, sizes: Sequence[int], taken: dict[str, bool]) -> int:
    """The nearest tile from `from_` on, going `step` (±1), where a column fits every row size."""
    s = from_
    while True:
        fits = True
        for size in sizes:
            if not column_fits(s, size):
                fits = False
                break
        if fits and (str(s - 1) not in taken) and (str(s + 1) not in taken):
            return s
        s += step


def _part_columns(
    rules: RoadRules,
    tile: TileRules,
    part: DistrictPart,
    row_sizes: Sequence[int],
    before: Sequence[int],
    random: Random,
) -> list[int]:
    """The columns of a part, from past one screen edge to past the other. `before` are the
    columns of the part before (on the shared row): never one tile beside one of them."""
    edge = rules.offscreen_x + rules.step
    sizes = _unique([s for s in row_sizes if s > 1])
    taken = _int_set(before)
    first = _fitting_tile(_tile_at(-edge, tile.size), -1, sizes, taken)
    last = _fitting_tile(_tile_at(edge, tile.size), 1, sizes, taken)
    columns = [first]
    s = first
    while True:
        s = _fitting_tile(s + _next_gap(part.grid.columns, tile.size, random), 1, sizes, taken)
        if s >= last - 1:
            break
        columns.append(s)
    columns.append(last)
    return columns


def tile_street_runs(
    district: District,
    rules: RoadRules,
    tile: TileRules,
    random: Random,
    buildable: Callable[[float, float], bool],
    out_of_view: Callable[[Node], bool],
) -> tuple[list[StreetRun], list[Block]]:
    """The streets of a district on the tile grid (phase 15), as `street_runs` lays them
    otherwise: random links (rows of two tiles or more, the avenues and boulevards, are built along
    their whole line, and become one-tile streets where their ground does not allow it), then no
    dead end on screen. Streets cross: there is no T-junction-only rule here (P15-R05).

    Returns (runs, blocks)."""
    layout = _TileLayout(rules, tile, random, buildable)
    last_index = len(district.parts) - 1
    for p, part in enumerate(district.parts):
        layout.lay_part(part, p == 0, p == last_index, district)
    return layout.streets(out_of_view)


class _TileLayout:
    """The links of a district's grid, laid part after part (see `tile_street_runs`)."""

    def __init__(
        self,
        rules: RoadRules,
        tile: TileRules,
        random: Random,
        buildable: Callable[[float, float], bool],
    ) -> None:
        self._rules = rules
        self._tile = tile
        self._random = random
        self._buildable = buildable
        self._nodes = Nodes(buildable)
        self._links: list[Link] = []
        self._widths: dict[str, float] = {}
        self._parts: list[PartGrid] = []
        self._before: list[int] = []

    def lay_part(self, part: DistrictPart, first: bool, last: bool, district: District) -> None:
        """Lays one part of the district: its rows, its columns and the shared row before it."""
        tile = self._tile
        rows = _part_rows(self._rules, tile, part, self._random)
        sizes = [r.size for r in rows]
        columns = _part_columns(self._rules, tile, part, sizes, self._before, self._random)
        xs = [(s + 0.5) * tile.size for s in columns]
        # A wide row whose ground does not allow it along its whole line is a one-tile street, on
        # its first tile (so it stays on the grid).
        lines: list[Line] = []
        for r in rows:
            fixed = Line(r.start, 1) if (r.size > 1 and not self._fits(r, xs)) else r
            lines.append(Line(fixed.start, fixed.size, _middle(fixed, tile.size)))
        grid = [[self._nodes.at(x, line.z) for x in xs] for line in lines]
        laid = PartGrid(lines, xs, grid)
        # The rows shared with the part before or after are laid once, over both parts' columns.
        skip_first = (not first) or district.continues is True
        last_row = len(lines) - 1
        for r_index, line in enumerate(lines):
            if (r_index == 0 and skip_first) or (r_index == last_row and not last):
                continue
            boundary = r_index in (0, last_row)
            self._lay_row(
                grid[r_index] if r_index < len(grid) else [], line, boundary, part.grid.links
            )
        if (not first) and len(self._parts) > 0:
            previous = self._parts[len(self._parts) - 1]
            lower = previous.grid[len(previous.grid) - 1] if len(previous.grid) > 0 else []
            upper = grid[0] if len(grid) > 0 else []
            self._merge_row(lower, upper, part.grid.links)
        self._lay_columns(laid, part.grid.links)
        self._parts.append(laid)
        self._before = columns

    def _fits(self, r: Line, xs: Sequence[float]) -> bool:
        z = _middle(r, self._tile.size)
        for c, x in enumerate(xs):
            if not self._buildable(x, z):
                return False
            if c > 0 and not self._buildable((x + xs[c - 1]) / 2, z):
                return False
        return True

    def _lay_row(self, row: Sequence[Node], line: Line, boundary: bool, chance: float) -> None:
        self._widths["z" + to_fixed3(line.z)] = line.size * self._tile.size
        for c in range(1, len(row)):
            a = row[c - 1]
            b = row[c]
            self._add(a, b, True, boundary, line.size > 1, chance)

    def _lay_columns(self, laid: PartGrid, chance: float) -> None:
        grid = laid.grid
        for c, x in enumerate(laid.xs):
            self._widths["x" + to_fixed3(x)] = self._tile.size
            for r in range(len(laid.lines) - 1):
                a = grid[r][c] if r < len(grid) and c < len(grid[r]) else None
                b = grid[r + 1][c] if r + 1 < len(grid) and c < len(grid[r + 1]) else None
                if a is not None and b is not None:
                    self._add(a, b, False, False, False, chance)

    def _merge_row(self, lower: Sequence[Node], upper: Sequence[Node], chance: float) -> None:
        """The shared row between two parts, laid once over both parts' columns."""
        both = list(lower)
        both.extend(upper)
        row = stable_sort_by(_unique_nodes(both), lambda n: n.x)
        for c in range(1, len(row)):
            self._add(row[c - 1], row[c], True, True, False, chance)

    def _add(
        self,
        a0: Node,
        b0: Node,
        across: bool,
        required: bool,
        wide: bool,
        chance: float,
    ) -> None:
        """A link from `a0` to `b0`, built with the chance `chance` unless required or wide."""
        nodes = self._nodes
        a = nodes.use(a0)
        b = nodes.use(b0)
        ground = (
            nodes.ground(a)
            and self._buildable((a.x + b.x) / 2, (a.z + b.z) / 2)
            and nodes.ground(b)
        )
        built = ground and (required or wide or self._random() < chance)
        self._links.append(Link(a, b, across, required, wide, ground, built, False))

    def _width_of(self, key: str) -> float:
        return self._widths.get(key, self._tile.size)

    def streets(self, out_of_view: Callable[[Node], bool]) -> tuple[list[StreetRun], list[Block]]:
        """The straight runs and the blocks, once the dead ends on screen are removed."""
        all_links = dedupe(self._links)
        used = self._nodes.used
        remove_dead_ends(links_by_node(all_links, len(used)), used, out_of_view, False, True)
        built = [link for link in all_links if link.built]
        runs: list[StreetRun] = []
        for points in straight_runs(built, self._rules.step):
            first = points[0] if len(points) > 0 else Point(0, 0)
            last = points[len(points) - 1] if len(points) > 0 else first
            key = "z" + to_fixed3(first.z) if first.z == last.z else "x" + to_fixed3(first.x)
            runs.append(StreetRun(points, self._width_of(key)))
        has: dict[str, bool] = {}
        for link in built:
            has[str(pair(link.a, link.b))] = True
        blocks: list[Block] = []
        for part_grid in self._parts:
            blocks.extend(_tile_blocks(part_grid.grid, has, self._width_of))
        buildable = self._buildable
        kept = [b for b in blocks if buildable((b.x_min + b.x_max) / 2, (b.z_min + b.z_max) / 2)]
        return runs, kept


def _tile_blocks(
    grid: Sequence[Sequence[Node]],
    has: dict[str, bool],
    width_of: Callable[[str], float],
) -> list[Block]:
    """The blocks of the cells of a part's grid, on whole tiles: up to the edge of each street
    around them, and over the tiles of a missing street on their upper and right sides (so the
    lower and left blocks take them, and blocks never share a tile)."""
    blocks: list[Block] = []
    for r in range(len(grid) - 1):
        for c in range(len(grid[r]) - 1):
            block = _cell_block(grid, c, r, has, width_of)
            if block is not None:
                blocks.append(block)
    return blocks


def _corners(
    grid: Sequence[Sequence[Node]], c: int, r: int
) -> tuple[Node, Node, Node, Node] | None:
    """The corners of cell (`c`, `r`): bottom left, bottom right, top left, top right."""
    found: list[Node] = []
    for rr, cc in [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]:
        if 0 <= rr < len(grid) and 0 <= cc < len(grid[rr]):
            found.append(grid[rr][cc])
        else:
            return None
    return found[0], found[1], found[2], found[3]


def _cell_block(
    grid: Sequence[Sequence[Node]],
    c: int,
    r: int,
    has: dict[str, bool],
    width_of: Callable[[str], float],
) -> Block | None:
    """The block of cell (`c`, `r`), if it has room (see `_tile_blocks`)."""
    cell = _corners(grid, c, r)
    if cell is None:
        return None
    n00, n10, n01, n11 = cell

    def built(a: Node, b: Node) -> bool:
        return (str(pair(a, b)) in has) or (str(pair(b, a)) in has)

    def w(x: float) -> float:
        return width_of("x" + to_fixed3(x)) / 2

    def d(z: float) -> float:
        return width_of("z" + to_fixed3(z)) / 2

    right = -1 if built(n10, n11) else 1
    top = -1 if built(n01, n11) else 1
    x_min = n00.x + w(n00.x)
    x_max = n11.x + right * w(n11.x)
    z_min = n00.z + d(n00.z)
    z_max = n11.z + top * d(n11.z)
    if x_max > x_min and z_max > z_min:
        return Block(x_min, x_max, z_min, z_max)
    return None
