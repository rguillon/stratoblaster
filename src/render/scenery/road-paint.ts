import type { RoadPiece } from '../../core/scenery/road-tiles';
import type { TileRules } from '../../core/scenery/scenery-level';
import { armLines, pieceRoadway, type Rect, type TileRoadLook } from './tile-road-geometry';

// Phase 15 (reviewer, 2026-10-28: better looking corners, T and X): a road piece painted pixel
// by pixel for the road atlas. The roadway's corners are rounded with distance fields: the
// sidewalk corners into a junction get a kerb radius, and the outside of a turn sweeps round.
// Junctions of three or four ways get zebra crossings on their arms, the lane lines stopping
// before them.

type Rgb = readonly [number, number, number];

/** Radius of the sidewalk corners into a junction, in world units. */
const KERB_RADIUS = 3;
/** Zebra crossings: depth along the arm, stripe width and gap, gap before the lines. */
const ZEBRA = { depth: 3, stripe: 0.6, gap: 0.6, before: 1 } as const;

/** A grid of pixels larger than the piece by `margin` on every side, where arms run on. */
interface Canvas {
  /** Pixels per world unit. */
  readonly scale: number;
  readonly margin: number;
  /** Side of the canvas in pixels. */
  readonly side: number;
}

/** The lower envelope of the parabolas of `f`'s finite values: their apexes and boundaries. */
function envelope(f: Float64Array): { v: Int32Array; z: Float64Array; count: number } {
  const n = f.length;
  const v = new Int32Array(n);
  const z = new Float64Array(n + 1);
  const at = (i: number): number => f[i] ?? Infinity;
  const meet = (p: number, q: number): number =>
    (at(q) + q * q - (at(p) + p * p)) / (2 * q - 2 * p);
  let k = -1;
  for (let q = 0; q < n; q++) {
    if (at(q) === Infinity) continue;
    while (k >= 0 && meet(v[k] ?? 0, q) <= (z[k] ?? -Infinity)) k--;
    k++;
    v[k] = q;
    z[k] = k === 0 ? -Infinity : meet(v[k - 1] ?? 0, q);
    z[k + 1] = Infinity;
  }
  return { v, z, count: k + 1 };
}

/** Squared distances along one line (Felzenszwalb and Huttenlocher). */
function line1d(f: Float64Array): Float64Array {
  const d = new Float64Array(f.length).fill(Infinity);
  const { v, z, count } = envelope(f);
  if (count === 0) return d;
  let j = 0;
  for (let q = 0; q < f.length; q++) {
    while ((z[j + 1] ?? Infinity) < q) j++;
    const p = v[j] ?? 0;
    d[q] = (q - p) * (q - p) + (f[p] ?? Infinity);
  }
  return d;
}

/** Exact distance (in pixels) from each pixel to the nearest pixel of `mask`. */
function distanceTo(mask: Uint8Array, side: number): Float32Array {
  const grid = Float64Array.from(mask, (m) => (m ? 0 : Infinity));
  const line = new Float64Array(side);
  for (const [stride, step] of [
    [side, 1],
    [1, side],
  ] as const) {
    for (let a = 0; a < side; a++) {
      for (let b = 0; b < side; b++) line[b] = grid[a * stride + b * step] ?? Infinity;
      const d = line1d(line);
      for (let b = 0; b < side; b++) grid[a * stride + b * step] = d[b] ?? Infinity;
    }
  }
  return Float32Array.from(grid, Math.sqrt);
}

const within = (mask: Uint8Array, side: number, r: number): Uint8Array =>
  Uint8Array.from(distanceTo(mask, side), (v) => (v <= r ? 1 : 0));
const invert = (mask: Uint8Array): Uint8Array => mask.map((v) => 1 - v);

/** `mask` with its concave corners rounded to radius `r` (a closing). */
const close = (mask: Uint8Array, side: number, r: number): Uint8Array =>
  invert(within(invert(within(mask, side, r)), side, r));

/** Sets the pixels of `rect` (piece frame, world units) in `mask`. */
function fill(mask: Uint8Array | Rgb[], c: Canvas, [x0, x1, z0, z1]: Rect, value: Rgb | 1): void {
  if (x1 <= x0 || z1 <= z0) return;
  const px = (v: number): number => Math.round(v * c.scale) + c.margin;
  const [i0, i1, j0, j1] = [
    px(x0),
    Math.max(px(x1), px(x0) + 1),
    px(z0),
    Math.max(px(z1), px(z0) + 1),
  ];
  for (let j = Math.max(0, j0); j < Math.min(c.side, j1); j++)
    for (let i = Math.max(0, i0); i < Math.min(c.side, i1); i++) mask[j * c.side + i] = value;
}

/** The roadway, with the arms run on past the edges of the piece so they stay straight there. */
function roadMask(piece: RoadPiece, tile: TileRules, c: Canvas): Uint8Array {
  const mask = new Uint8Array(c.side * c.side);
  const size = piece.size * tile.size;
  const out = c.margin / c.scale;
  for (const rect of pieceRoadway(piece, tile).roadway) fill(mask, c, rect, 1);
  piece.sides.forEach((s, i) => {
    if (!s) return;
    const [a, b] = [
      s.offset * tile.size + tile.sidewalk,
      (s.offset + s.size) * tile.size - tile.sidewalk,
    ];
    const run: Rect[] = [
      [a, b, size, size + out],
      [size, size + out, a, b],
      [a, b, -out, 0],
      [-out, 0, a, b],
    ];
    const rect = run[i];
    if (rect) fill(mask, c, rect, 1);
  });
  return mask;
}

/** Where the lines of an arm stop for its zebra crossing, and the crossing; none on a through road. */
function crossing(
  line: Rect,
  alongX: boolean,
  size: number,
): { line: Rect; zebra: Rect } | undefined {
  const [x0, x1, z0, z1] = line;
  const [p0, p1] = alongX ? [x0, x1] : [z0, z1];
  const atStart = p1 >= size - 1e-6 && p0 > 1e-6;
  const atEnd = p0 <= 1e-6 && p1 < size - 1e-6;
  if (!atStart && !atEnd) return undefined;
  // As deep as the arm allows, short of the edge; none on an arm too short for one.
  const z = Math.min(ZEBRA.depth, p1 - p0 - 0.4);
  if (z < 1) return undefined;
  const [zebra, rest] = atStart
    ? [
        [p0, p0 + z],
        [p0 + z + ZEBRA.before, p1],
      ]
    : [
        [p1 - z, p1],
        [p0, p1 - z - ZEBRA.before],
      ];
  const rect = ([a, b]: number[]): Rect =>
    alongX ? [a ?? 0, b ?? 0, z0, z1] : [x0, x1, a ?? 0, b ?? 0];
  return { line: rect(rest), zebra: rect(zebra) };
}

/** The zebra stripes of `zebra`, running along the arm, across its width. */
function stripes([x0, x1, z0, z1]: Rect, alongX: boolean): Rect[] {
  const [a, b] = alongX ? [z0, z1] : [x0, x1];
  const out: Rect[] = [];
  for (let c = a + ZEBRA.gap; c + ZEBRA.stripe <= b - ZEBRA.gap / 2; c += ZEBRA.stripe + ZEBRA.gap)
    out.push(alongX ? [x0, x1, c, c + ZEBRA.stripe] : [c, c + ZEBRA.stripe, z0, z1]);
  return out;
}

/** The roadway of `piece`, the sidewalk corners into its junction rounded to the kerb radius. */
const roundedRoad = (piece: RoadPiece, tile: TileRules, c: Canvas): Uint8Array =>
  close(roadMask(piece, tile, c), c.side, KERB_RADIUS * c.scale);

/** The lane lines of the arms, and zebra crossings on those of a T or an X. */
function paintLines(
  pixels: Rgb[],
  piece: RoadPiece,
  [tile, look]: readonly [TileRules, TileRoadLook],
  c: Canvas,
): void {
  const size = piece.size * tile.size;
  const junction = piece.kind === 'tee' || piece.kind === 'cross';
  for (const arm of pieceRoadway(piece, tile).arms) {
    const cut = junction ? crossing(arm.line, arm.alongX, size) : undefined;
    const { centre, lanes } = armLines({ ...arm, line: cut?.line ?? arm.line }, look.lineWidth);
    for (const rect of lanes) fill(pixels, c, rect, look.laneLine);
    for (const rect of centre) fill(pixels, c, rect, look.centreLine);
    for (const rect of cut ? stripes(cut.zebra, arm.alongX) : [])
      fill(pixels, c, rect, look.laneLine);
  }
}

/**
 * A turn, drawn as a quarter ring round the corner its two open sides share: the roadway keeps
 * its width round the bend, and its lines follow it as arcs.
 */
function paintTurn(
  piece: RoadPiece,
  [tile, look]: readonly [TileRules, TileRoadLook],
  n: number,
): Rgb[] {
  const size = piece.size * tile.size;
  const [cx, cz] = [piece.sides[1] ? size : 0, piece.sides[0] ? size : 0];
  const [inner, outer] = [tile.sidewalk, size - tile.sidewalk];
  const lane = (outer - inner) / (2 * piece.size);
  const half = look.lineWidth / 2;
  const arcs: [number, Rgb][] = [[size / 2, look.centreLine]];
  for (let k = 1; k < piece.size; k++)
    arcs.push([size / 2 - k * lane, look.laneLine], [size / 2 + k * lane, look.laneLine]);
  const colour = (r: number): Rgb => {
    if (r >= inner && r <= outer)
      return arcs.find(([at]) => Math.abs(r - at) <= half)?.[1] ?? look.roadway;
    const kerb = r >= inner - look.kerbWidth && r <= outer + look.kerbWidth;
    return kerb ? look.kerb : look.sidewalk;
  };
  const out: Rgb[] = [];
  for (let j = 0; j < n; j++)
    for (let i = 0; i < n; i++)
      out.push(colour(Math.hypot(((i + 0.5) / n) * size - cx, ((j + 0.5) / n) * size - cz)));
  return out;
}

/** The colour of each pixel of `piece`, `n` × `n`, row by row along +Z. */
export function paintPiece(
  piece: RoadPiece,
  tile: TileRules,
  look: TileRoadLook,
  n: number,
): Rgb[] {
  if (piece.kind === 'turn') return paintTurn(piece, [tile, look], n);
  const scale = n / (piece.size * tile.size);
  const margin = Math.ceil((KERB_RADIUS + look.kerbWidth) * 2 * scale);
  const c: Canvas = { scale, margin, side: n + 2 * margin };
  const road = roundedRoad(piece, tile, c);
  const kerb = within(road, c.side, look.kerbWidth * scale);
  const pixels: Rgb[] = Array.from({ length: c.side * c.side }, (_, i) =>
    road[i] ? look.roadway : kerb[i] ? look.kerb : look.sidewalk,
  );
  paintLines(pixels, piece, [tile, look], c);
  const out: Rgb[] = [];
  for (let j = 0; j < n; j++)
    for (let i = 0; i < n; i++)
      out.push(pixels[(j + margin) * c.side + i + margin] ?? look.sidewalk);
  return out;
}
