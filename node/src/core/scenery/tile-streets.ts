// P15-R01, R05: the streets of a district laid on a grid of square tiles (phase 15). Rows (along
// X) may be wide roads (avenues and boulevards, N tiles wide); columns are one tile wide. Every
// line covers whole tiles, and the columns sit where the junction pieces of the wide rows they
// cross fall on the rows' own N-tile lattice, so every wide row is made of whole N × N pieces.
import { hash2D } from '../math/noise';
import { randomIn, type Random } from '../math/rng';
import type { District } from './districts';
import { removeDeadEnds } from './street-dead-ends';
import { dedupe, linksByNode, Nodes, pair, type Link, type Node } from './street-links';
import { straightRuns } from './street-runs';
import type { RoadRules, TileRules } from './scenery-level';
import type { Block } from './street-grid';

/** A straight run of street, with its width (sidewalks included). */
export interface StreetRun {
  readonly points: { x: number; z: number }[];
  readonly width: number;
}

/** A line of the grid: its first tile and its size in tiles. */
interface Line {
  readonly start: number;
  readonly size: number;
}

/** Tile index whose middle is nearest `v`. */
const tileAt = (v: number, size: number): number => Math.round(v / size - 0.5);
/** Coordinate of the middle of `line`. */
const middle = (line: Line, size: number): number => (line.start + line.size / 2) * size;
const mod = (a: number, n: number): number => ((a % n) + n) % n;

/**
 * Whether a one-tile column at tile `s` crosses a row of `size` tiles on that row's lattice
 * (P15-R04): its junction piece, `size` wide, starts on a multiple of `size` with the column in
 * it as close to its middle as the grid allows.
 */
export function columnFits(s: number, size: number): boolean {
  const offset = mod(s, size);
  return offset === Math.floor((size - 1) / 2) || offset === Math.ceil((size - 1) / 2);
}

/** Size in tiles of a row starting at tile `t`: a share of them are avenues or boulevards. */
function rowSize(rules: RoadRules, t: number): number {
  const h = hash2D(t, 29, 211);
  let from = 0;
  for (const b of rules.boulevards ?? []) {
    if (h < from + b.share) return b.lanes;
    from += b.share;
  }
  return h < from + rules.dual.avenues ? 2 : 1;
}

/** Tile gap to the next line: a spacing of `gap` world units between middles, in tiles. */
function nextGap(gap: readonly [number, number], tile: number, random: Random): number {
  return Math.max(2, Math.round(randomIn(random, gap) / tile));
}

/** The rows of a part, from its first to its last (both one tile wide). */
function partRows(
  rules: RoadRules,
  tile: TileRules,
  part: District['parts'][number],
  random: Random,
): Line[] {
  const first = tileAt(part.zMin, tile.size);
  const last = tileAt(part.zMax, tile.size);
  let previous: Line = { start: first, size: 1 };
  const rows: Line[] = [previous];
  if (last <= first) return rows;
  for (;;) {
    const start = previous.start + previous.size - 1 + nextGap(part.grid.rows, tile.size, random);
    const size = rowSize(rules, start);
    // Room for a block of at least one tile before the last row.
    if (start + size + 1 > last) break;
    previous = { start, size };
    rows.push(previous);
  }
  rows.push({ start: last, size: 1 });
  return rows;
}

/** The nearest tile from `from` on, going `step` (±1), where a column fits every row size. */
function fittingTile(from: number, step: 1 | -1, sizes: readonly number[], taken: Set<number>) {
  for (let s = from; ; s += step) {
    if (sizes.every((size) => columnFits(s, size)) && !taken.has(s - 1) && !taken.has(s + 1)) {
      return s;
    }
  }
}

/** The columns of a part, from past one screen edge to past the other. */
function partColumns(
  rules: RoadRules,
  tile: TileRules,
  part: District['parts'][number],
  rowSizes: readonly number[],
  /** Columns of the part before (on the shared row): never one tile beside one of them. */
  before: readonly number[],
  random: Random,
): number[] {
  const edge = rules.offscreenX + rules.step;
  const sizes = [...new Set(rowSizes.filter((s) => s > 1))];
  const taken = new Set(before);
  const first = fittingTile(tileAt(-edge, tile.size), -1, sizes, taken);
  const last = fittingTile(tileAt(edge, tile.size), 1, sizes, taken);
  const columns = [first];
  for (let s = first; ;) {
    s = fittingTile(s + nextGap(part.grid.columns, tile.size, random), 1, sizes, taken);
    if (s >= last - 1) break;
    columns.push(s);
  }
  columns.push(last);
  return columns;
}

/** What a part of a district laid on the grid is made of. */
interface PartGrid {
  readonly lines: readonly (Line & { readonly z: number })[];
  readonly xs: readonly number[];
  readonly grid: readonly (readonly Node[])[];
}

/**
 * The streets of a district on the tile grid (phase 15), as {@link streetRuns} lays them
 * otherwise: random links (rows of two tiles or more, the avenues and boulevards, are built along
 * their whole line, and become one-tile streets where their ground does not allow it), then no
 * dead end on screen. Streets cross: there is no T-junction-only rule here (P15-R05).
 */
export function tileStreetRuns(
  district: District,
  rules: RoadRules,
  tile: TileRules,
  random: Random,
  buildable: (x: number, z: number) => boolean,
  outOfView: (node: Node) => boolean,
): { runs: StreetRun[]; blocks: Block[] } {
  const layout = new TileLayout(rules, tile, random, buildable);
  district.parts.forEach((part, p) => {
    layout.layPart(part, { first: p === 0, last: p === district.parts.length - 1 }, district);
  });
  return layout.streets(outOfView);
}

/** The links of a district's grid, laid part after part (see {@link tileStreetRuns}). */
class TileLayout {
  readonly #nodes: Nodes;
  readonly #links: Link[] = [];
  readonly #widths = new Map<string, number>();
  readonly #parts: PartGrid[] = [];
  #before: number[] = [];

  constructor(
    private readonly rules: RoadRules,
    private readonly tile: TileRules,
    private readonly random: Random,
    private readonly buildable: (x: number, z: number) => boolean,
  ) {
    this.#nodes = new Nodes(buildable);
  }

  layPart(
    part: District['parts'][number],
    { first, last }: { readonly first: boolean; readonly last: boolean },
    district: District,
  ): void {
    const { tile, random } = this;
    const rows = partRows(this.rules, tile, part, random);
    const sizes = rows.map((r) => r.size);
    const columns = partColumns(this.rules, tile, part, sizes, this.#before, random);
    const xs = columns.map((s) => (s + 0.5) * tile.size);
    // A wide row whose ground does not allow it along its whole line is a one-tile street, on
    // its first tile (so it stays on the grid).
    const lines = rows
      .map((r) => (r.size > 1 && !this.#fits(r, xs) ? { start: r.start, size: 1 } : r))
      .map((r) => ({ ...r, z: middle(r, tile.size) }));
    const grid = lines.map(({ z }) => xs.map((x) => this.#nodes.at(x, z)));
    const laid: PartGrid = { lines, xs, grid };
    // The rows shared with the part before or after are laid once, over both parts' columns.
    const skipFirst = !first || district.continues === true;
    lines.forEach((line, r) => {
      if ((r === 0 && skipFirst) || (r === lines.length - 1 && !last)) return;
      this.#layRow(grid[r] ?? [], line, r === 0 || r === lines.length - 1, part.grid.links);
    });
    const previous = this.#parts.at(-1);
    if (!first && previous)
      this.#mergeRow(previous.grid.at(-1) ?? [], grid[0] ?? [], part.grid.links);
    this.#layColumns(laid, part.grid.links);
    this.#parts.push(laid);
    this.#before = columns;
  }

  #fits(r: Line, xs: readonly number[]): boolean {
    const z = middle(r, this.tile.size);
    return xs.every(
      (x, c) => this.buildable(x, z) && (c === 0 || this.buildable((x + (xs[c - 1] ?? x)) / 2, z)),
    );
  }

  #layRow(row: readonly Node[], line: Line & { z: number }, boundary: boolean, chance: number) {
    this.#widths.set(`z${line.z.toFixed(3)}`, line.size * this.tile.size);
    row.slice(1).forEach((b, c) => {
      const a = row[c];
      if (a) this.#add([a, b], true, boundary, line.size > 1, chance);
    });
  }

  #layColumns({ lines, xs, grid }: PartGrid, chance: number): void {
    xs.forEach((x, c) => {
      this.#widths.set(`x${x.toFixed(3)}`, this.tile.size);
      lines.slice(1).forEach((_, r) => {
        const a = grid[r]?.[c];
        const b = grid[r + 1]?.[c];
        if (a && b) this.#add([a, b], false, false, false, chance);
      });
    });
  }

  /** The shared row between two parts, laid once over both parts' columns. */
  #mergeRow(lower: readonly Node[], upper: readonly Node[], chance: number): void {
    const row = [...new Set([...lower, ...upper])].sort((p, q) => p.x - q.x);
    row.slice(1).forEach((b, c) => {
      const a = row[c];
      if (a) this.#add([a, b], true, true, false, chance);
    });
  }

  /** A link from `a` to `b`, built with the chance `chance` unless required or on a wide row. */
  #add(
    [a0, b0]: readonly [Node, Node],
    across: boolean,
    required: boolean,
    wide: boolean,
    chance: number,
  ) {
    const nodes = this.#nodes;
    const [a, b] = [nodes.use(a0), nodes.use(b0)];
    const ground =
      nodes.ground(a) && this.buildable((a.x + b.x) / 2, (a.z + b.z) / 2) && nodes.ground(b);
    const built = ground && (required || wide || this.random() < chance);
    this.#links.push({ a, b, across, required, boulevard: wide, ground, built, cut: false });
  }

  #widthOf(key: string): number {
    return this.#widths.get(key) ?? this.tile.size;
  }

  /** The straight runs and the blocks, once the dead ends on screen are removed. */
  streets(outOfView: (node: Node) => boolean): { runs: StreetRun[]; blocks: Block[] } {
    const all = dedupe(this.#links);
    const used = this.#nodes.used;
    removeDeadEnds(linksByNode(all, used.length), used, outOfView, false, true);
    const built = all.filter((l) => l.built);
    const runs = straightRuns(built, this.rules.step).map((points) => {
      const first = points[0] ?? { x: 0, z: 0 };
      const last = points.at(-1) ?? first;
      const key = first.z === last.z ? `z${first.z.toFixed(3)}` : `x${first.x.toFixed(3)}`;
      return { points, width: this.#widthOf(key) };
    });
    const has = new Set(built.map((l) => pair(l.a, l.b)));
    const blocks = this.#parts.flatMap(({ grid }) =>
      tileBlocks(grid, has, (key) => this.#widthOf(key)),
    );
    const { buildable } = this;
    return {
      runs,
      blocks: blocks.filter((b) => buildable((b.xMin + b.xMax) / 2, (b.zMin + b.zMax) / 2)),
    };
  }
}

/**
 * The blocks of the cells of a part's grid, on whole tiles: up to the edge of each street around
 * them, and over the tiles of a missing street on their upper and right sides (so the lower and
 * left blocks take them, and blocks never share a tile).
 */
function tileBlocks(
  grid: readonly (readonly Node[])[],
  has: ReadonlySet<number>,
  widthOf: (key: string) => number,
): Block[] {
  const blocks: Block[] = [];
  for (let r = 0; r + 1 < grid.length; r++) {
    for (let c = 0; c + 1 < (grid[r]?.length ?? 0); c++) {
      const block = cellBlock(grid, [c, r], has, widthOf);
      if (block) blocks.push(block);
    }
  }
  return blocks;
}

/** The corners of cell (`c`, `r`): bottom left, bottom right, top left, top right. */
function corners(grid: readonly (readonly Node[])[], c: number, r: number) {
  const nodes = [grid[r]?.[c], grid[r]?.[c + 1], grid[r + 1]?.[c], grid[r + 1]?.[c + 1]];
  return nodes.every((n) => n !== undefined) ? (nodes as [Node, Node, Node, Node]) : undefined;
}

/** The block of cell (`c`, `r`), if it has room (see {@link tileBlocks}). */
function cellBlock(
  grid: readonly (readonly Node[])[],
  [c, r]: readonly [number, number],
  has: ReadonlySet<number>,
  widthOf: (key: string) => number,
): Block | undefined {
  const cell = corners(grid, c, r);
  if (!cell) return undefined;
  const [n00, n10, n01, n11] = cell;
  const built = (a: Node, b: Node): boolean => has.has(pair(a, b)) || has.has(pair(b, a));
  const w = (x: number): number => widthOf(`x${x.toFixed(3)}`) / 2;
  const d = (z: number): number => widthOf(`z${z.toFixed(3)}`) / 2;
  const right = built(n10, n11) ? -1 : 1;
  const top = built(n01, n11) ? -1 : 1;
  const block = {
    xMin: n00.x + w(n00.x),
    xMax: n11.x + right * w(n11.x),
    zMin: n00.z + d(n00.z),
    zMax: n11.z + top * d(n11.z),
  };
  return block.xMax > block.xMin && block.zMax > block.zMin ? block : undefined;
}
