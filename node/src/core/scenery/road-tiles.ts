// P15-R03, R04: the road pieces of the districts laid on tiles (phase 15), found from their
// straight streets: a junction piece where a row and a column meet, the size of the wider road,
// and straight pieces of N × N tiles along each road between them.
import type { Road } from './road-network';
import type { TileRules } from './scenery-level';

/** An open side of a piece: a road `size` tiles wide, `offset` tiles from the piece's low edge. */
export interface PieceSide {
  readonly size: number;
  readonly offset: number;
}

/** Sides of a piece, in this order: +Z, +X, -Z, -X. */
export type PieceSides = readonly [
  PieceSide | undefined,
  PieceSide | undefined,
  PieceSide | undefined,
  PieceSide | undefined,
];

export type PieceKind = 'straight' | 'turn' | 'tee' | 'cross';

/** A road piece: `size` × `size` tiles from tile (`x`, `z`), with its open sides. */
export interface RoadPiece {
  readonly x: number;
  readonly z: number;
  readonly size: number;
  readonly kind: PieceKind;
  /** Whether roads of two sizes meet in it (P15-R04). */
  readonly adapter: boolean;
  readonly sides: PieceSides;
}

/** A straight street on the grid: a row (along X) or a column, with its tiles. */
interface TileLine {
  readonly row: boolean;
  /** First tile across it, and its size in tiles. */
  readonly start: number;
  readonly size: number;
  /** Where its middle is across, and its ends along (world units). */
  readonly at: number;
  readonly from: number;
  readonly to: number;
}

const EPSILON = 1e-6;

function lineOf(road: Road, tile: TileRules): TileLine | undefined {
  const [a, b] = [road.points[0], road.points.at(-1)];
  if (!a || !b) return undefined;
  const row = Math.abs(a.z - b.z) < EPSILON;
  const size = Math.max(1, Math.round(road.width / tile.size));
  const at = row ? a.z : a.x;
  const [p, q] = row ? [a.x, b.x] : [a.z, b.z];
  const start = Math.round(at / tile.size - size / 2);
  return { row, start, size, at, from: Math.min(p, q), to: Math.max(p, q) };
}

/** The sides kind of a piece by its open sides. */
function kindOf(sides: PieceSides): PieceKind {
  const open = sides.map((s) => s !== undefined);
  const count = open.filter(Boolean).length;
  if (count === 4) return 'cross';
  if (count === 3) return 'tee';
  return open[0] === open[2] ? 'straight' : 'turn';
}

/** Whether `row` and `column` meet: each reaches the other's middle line. */
function meet(row: TileLine, column: TileLine): boolean {
  const inRow = column.at >= row.from - EPSILON && column.at <= row.to + EPSILON;
  return inRow && row.at >= column.from - EPSILON && row.at <= column.to + EPSILON;
}

/** Which ways the streets leave the junction of `row` and `column`: +Z, +X, -Z, -X. */
function ways(row: TileLine, column: TileLine): readonly boolean[] {
  return [
    column.to > row.at + EPSILON,
    row.to > column.at + EPSILON,
    column.from < row.at - EPSILON,
    row.from < column.at - EPSILON,
  ];
}

/**
 * The junction piece where `row` and `column` meet, or none. It is the wider road's size; the
 * narrower road enters it on whole tiles, the piece starting on a multiple of its size.
 */
function junction(row: TileLine, column: TileLine): RoadPiece | undefined {
  if (!meet(row, column)) return undefined;
  const size = Math.max(row.size, column.size);
  const rowWider = row.size >= column.size;
  const x = rowWider ? size * Math.floor(column.start / size) : column.start;
  const z = rowWider ? row.start : size * Math.floor(row.start / size);
  const across = { size: column.size, offset: column.start - x };
  const along = { size: row.size, offset: row.start - z };
  const sides = ways(row, column).map((open, i) =>
    open ? (i % 2 === 0 ? across : along) : undefined,
  ) as unknown as PieceSides;
  return { x, z, size, kind: kindOf(sides), adapter: row.size !== column.size, sides };
}

/** Tiles across a level, at most (keys stay unique within it). */
const ACROSS = 1 << 12;

/** Key of a tile: one number (keys are made a lot while packing blocks). */
export const tileKey = (x: number, z: number): number => z * ACROSS + x + ACROSS / 2;

/**
 * The junctions of `rows` and `columns`. Two streets of one line may meet at a junction (where
 * the runout's streets go on from those before it): one piece, with the open sides of both.
 */
function junctions(rows: readonly TileLine[], columns: readonly TileLine[]): RoadPiece[] {
  const found = new Map<number, RoadPiece>();
  for (const row of rows) {
    for (const column of columns) {
      const piece = junction(row, column);
      if (!piece) continue;
      const key = tileKey(piece.x, piece.z);
      const other = found.get(key);
      const sides = other
        ? (piece.sides.map((s, i) => s ?? other.sides[i]) as unknown as PieceSides)
        : piece.sides;
      found.set(key, { ...piece, sides, kind: kindOf(sides) });
    }
  }
  return [...found.values()];
}

/** Straight pieces of `line`, N × N tiles on its own N-tile lattice, where nothing is `taken`. */
function straights(line: TileLine, tile: TileRules, taken: ReadonlySet<number>): RoadPiece[] {
  const n = line.size;
  const side = { size: n, offset: 0 };
  const sides: PieceSides = line.row
    ? [undefined, side, undefined, side]
    : [side, undefined, side, undefined];
  const pieces: RoadPiece[] = [];
  const last = Math.floor(line.to / tile.size);
  for (let a = n * Math.floor(Math.floor(line.from / tile.size) / n); a <= last; a += n) {
    const [x, z] = line.row ? [a, line.start] : [line.start, a];
    if (!taken.has(tileKey(x, z)))
      pieces.push({ x, z, size: n, kind: 'straight', adapter: false, sides });
  }
  return pieces;
}

/**
 * The road pieces of the streets of `roads` (phase 15): the junctions, then straight pieces of
 * N × N tiles over the rest of each street.
 */
export function roadPieces(roads: readonly Road[], tile: TileRules): RoadPiece[] {
  const lines = roads.filter((r) => r.kind === 'street').flatMap((r) => lineOf(r, tile) ?? []);
  const pieces = junctions(
    lines.filter((l) => l.row),
    lines.filter((l) => !l.row),
  );
  const taken = roadTiles(pieces);
  for (const line of lines) {
    const more = straights(line, tile, taken);
    for (const p of more) for (const k of roadTiles([p])) taken.add(k);
    pieces.push(...more);
  }
  return pieces;
}

/** The tiles the pieces cover. */
export function roadTiles(pieces: readonly RoadPiece[]): Set<number> {
  const tiles = new Set<number>();
  for (const p of pieces) {
    for (let i = 0; i < p.size; i++)
      for (let j = 0; j < p.size; j++) tiles.add(tileKey(p.x + i, p.z + j));
  }
  return tiles;
}

/** Pieces found once per list of roads (they are asked for every chunk). */
const cache = new WeakMap<readonly Road[], RoadPiece[]>();

export function cachedRoadPieces(roads: readonly Road[], tile: TileRules): RoadPiece[] {
  let pieces = cache.get(roads);
  if (!pieces) {
    pieces = roadPieces(roads, tile);
    cache.set(roads, pieces);
  }
  return pieces;
}
