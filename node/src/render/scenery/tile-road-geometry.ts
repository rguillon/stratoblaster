import type { PieceSide, RoadPiece } from '../../core/scenery/road-tiles';
import type { TileRules } from '../../core/scenery/scenery-level';
import type { ColoredGeometry } from '../geometry/gradient-shapes';

// Phase 15 (P15-R02, R03, R04): the road pieces of the districts on tiles: a sidewalk over the
// whole piece, a kerb and the roadway of each open side, joined in the middle, and the lane
// markings up to the junction. Draped on the ground, so pieces meet with no step.

type Rgb = readonly [number, number, number];

/** How the road pieces look. */
export interface TileRoadLook {
  readonly roadway: Rgb;
  readonly sidewalk: Rgb;
  readonly kerb: Rgb;
  /** Width of the kerb along the roadway's edges. */
  readonly kerbWidth: number;
  readonly centreLine: Rgb;
  readonly laneLine: Rgb;
  readonly lineWidth: number;
  /** Height of the sidewalks above the ground. */
  readonly lift: number;
}

/** A rectangle in the piece's own frame: [x0, x1] × [z0, z1]. */
export type Rect = readonly [number, number, number, number];

/** Layers above the sidewalk, so the kerb, the roadway and the lines each show over the last. */
const LAYER = 0.1;

/** Where the roadway of an open side runs across the piece, from its low edge. */
const roadwayOf = (s: PieceSide, tile: TileRules): [number, number] => [
  s.offset * tile.size + tile.sidewalk,
  (s.offset + s.size) * tile.size - tile.sidewalk,
];

/** The span of the roadways of `sides` across the piece, if any of them is open. */
function spanOf(
  sides: readonly (PieceSide | undefined)[],
  tile: TileRules,
): [number, number] | undefined {
  const spans = sides.flatMap((s) => (s ? [roadwayOf(s, tile)] : []));
  if (spans.length === 0) return undefined;
  return [Math.min(...spans.map((p) => p[0])), Math.max(...spans.map((p) => p[1]))];
}

/**
 * How each side's arm runs, in the order of `PieceSides` (+Z, +X, -Z, -X): whether it runs along
 * X, and from which edge (the high one or the low one).
 */
const ARMS = [
  { alongX: false, high: true },
  { alongX: true, high: true },
  { alongX: false, high: false },
  { alongX: true, high: false },
] as const;

/**
 * The roadway of an open side, from its edge to the far side of the roads `across` it (or right
 * across without one), and the rectangle its lines stop in, at their near side.
 */
function armOf(
  side: PieceSide,
  how: (typeof ARMS)[number],
  across: readonly [number, number] | undefined,
  [size, tile]: readonly [number, TileRules],
): { rect: Rect; line: Rect } {
  const [a, b] = roadwayOf(side, tile);
  const [lo, hi] = across ?? (how.high ? [0, 0] : [size, size]);
  const [far, near] = how.high ? [lo, hi] : [hi, lo];
  const span = (to: number): [number, number] => (how.high ? [to, size] : [0, to]);
  const rect = (to: number): Rect => (how.alongX ? [...span(to), a, b] : [a, b, ...span(to)]);
  return { rect: rect(far), line: rect(near) };
}

/**
 * The roadway of a piece and the lines of its arms, as rectangles: each open side's roadway runs
 * from its edge to the far side of the roads across it (or right across without one), and its
 * lines stop at their near side.
 */
export function pieceRoadway(piece: RoadPiece, tile: TileRules): { roadway: Rect[]; arms: Arm[] } {
  const size = piece.size * tile.size;
  const [north, east, south, west] = piece.sides;
  // The roads across each way: those along Z span X, those along X span Z.
  const spans = { x: spanOf([north, south], tile), z: spanOf([east, west], tile) };
  const roadway: Rect[] = [];
  const arms: Arm[] = [];
  piece.sides.forEach((side, i) => {
    const how = ARMS[i];
    if (!side || !how) return;
    const { rect, line } = armOf(side, how, how.alongX ? spans.x : spans.z, [size, tile]);
    roadway.push(rect);
    arms.push({ lanes: side.size, line, alongX: how.alongX });
  });
  return { roadway, arms };
}

/** An arm of a piece: its roadway up to the junction, where its lines stop. */
interface Arm {
  readonly lanes: number;
  readonly line: Rect;
  readonly alongX: boolean;
}

/** The line rectangles of an arm: the centre line, and lane lines on wide roads. */
export function armLines(arm: Arm, width: number): { centre: Rect[]; lanes: Rect[] } {
  const [x0, x1, z0, z1] = arm.line;
  const [a, b] = arm.alongX ? [z0, z1] : [x0, x1];
  const lane = (b - a) / (2 * arm.lanes);
  const at = (c: number): Rect =>
    arm.alongX ? [x0, x1, c - width / 2, c + width / 2] : [c - width / 2, c + width / 2, z0, z1];
  const mid = (a + b) / 2;
  const lanes: Rect[] = [];
  for (let k = 1; k < arm.lanes; k++) lanes.push(at(mid - k * lane), at(mid + k * lane));
  return { centre: [at(mid)], lanes };
}

/**
 * The cuts of [a, b] (world units): its ends, and every multiple of `cell` between them. All the
 * layers of the roads are cut on the same world lattice, so their vertices line up and, draped
 * on uneven ground, one layer never bulges through the one above it (z-fighting on the wide
 * roads of World 4, reviewer 2026-10-28).
 */
function cuts(a: number, b: number, cell: number): number[] {
  const out = [a];
  for (let c = (Math.floor(a / cell) + 1) * cell; c < b - 1e-6; c += cell) out.push(c);
  out.push(b);
  return out;
}

/** Appends `rect` (piece frame) to `geo`, cut on the world lattice of `cell`, draped on `height`. */
function addRect(
  geo: ColoredGeometry,
  rect: Rect,
  [ox, oz]: readonly [number, number],
  height: (x: number, z: number) => number,
  color: Rgb,
  cell: number,
): void {
  const [x0, x1, z0, z1] = rect;
  if (x1 - x0 <= 0 || z1 - z0 <= 0) return;
  const xs = cuts(ox + x0, ox + x1, cell);
  const zs = cuts(oz + z0, oz + z1, cell);
  const base = geo.positions.length / 3;
  for (const z of zs) {
    for (const x of xs) {
      geo.positions.push(x, height(x, z), z);
      geo.colors.push(...color, 1);
    }
  }
  const nx = xs.length - 1;
  for (let j = 0; j < zs.length - 1; j++) {
    for (let i = 0; i < nx; i++) {
      const a = base + j * (nx + 1) + i;
      const b = a + 1;
      const c = a + nx + 1;
      const d = c + 1;
      // Facing up (Babylon's front faces).
      geo.indices.push(a, b, c, b, d, c);
    }
  }
}

/**
 * Appends the geometry of `piece` to `geo`, at `height(x, z)` of the ground under it (world
 * coordinates; flat ground at 0 for the `props/` page).
 */
export function addPiece(
  geo: ColoredGeometry,
  piece: RoadPiece,
  tile: TileRules,
  look: TileRoadLook,
  ground: (x: number, z: number) => number,
): void {
  const size = piece.size * tile.size;
  const origin = [piece.x * tile.size, piece.z * tile.size] as const;
  const at = (layer: number) => (x: number, z: number) => ground(x, z) + look.lift + layer * LAYER;
  const cell = tile.size / 2;
  addRect(geo, [0, size, 0, size], origin, at(0), look.sidewalk, cell);
  const { roadway, arms } = pieceRoadway(piece, tile);
  const k = look.kerbWidth;
  for (const [x0, x1, z0, z1] of roadway) {
    const kerb: Rect = [
      Math.max(0, x0 - k),
      Math.min(size, x1 + k),
      Math.max(0, z0 - k),
      Math.min(size, z1 + k),
    ];
    addRect(geo, kerb, origin, at(1), look.kerb, cell);
  }
  for (const rect of roadway) addRect(geo, rect, origin, at(2), look.roadway, cell);
  for (const arm of arms) {
    const { centre, lanes } = armLines(arm, look.lineWidth);
    for (const rect of centre) addRect(geo, rect, origin, at(3), look.centreLine, cell);
    for (const rect of lanes) addRect(geo, rect, origin, at(3), look.laneLine, cell);
  }
}

/**
 * P15-R10 (`tiles=1`): thin lines along the tile edges over the districts whose pieces are in
 * [zMin, zMax), from one end of their pieces to the other.
 */
export function buildTileGrid(
  pieces: readonly RoadPiece[],
  tile: TileRules,
  ground: (x: number, z: number) => number,
  [zMin, zMax]: readonly [number, number],
  color: Rgb,
): ColoredGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  const inChunk = pieces.filter((p) => {
    const mid = (p.z + p.size / 2) * tile.size;
    return mid >= zMin && mid < zMax;
  });
  if (inChunk.length === 0) return geo;
  const [x0, x1] = [
    Math.min(...inChunk.map((p) => p.x)),
    Math.max(...inChunk.map((p) => p.x + p.size)),
  ];
  const [z0, z1] = [
    Math.min(...inChunk.map((p) => p.z)),
    Math.max(...inChunk.map((p) => p.z + p.size)),
  ];
  const width = 0.25;
  const above = (x: number, z: number): number => ground(x, z) + 1;
  const t = tile.size;
  for (let i = x0; i <= x1; i++) {
    addRect(geo, [i * t - width, i * t + width, z0 * t, z1 * t], [0, 0], above, color, t);
  }
  for (let j = z0; j <= z1; j++) {
    addRect(geo, [x0 * t, x1 * t, j * t - width, j * t + width], [0, 0], above, color, t);
  }
  return geo;
}

/** The pieces of `pieces` whose middle is in [zMin, zMax), on `ground`. */
export function buildTileRoadGeometry(
  pieces: readonly RoadPiece[],
  tile: TileRules,
  look: TileRoadLook,
  ground: (x: number, z: number) => number,
  [zMin, zMax]: readonly [number, number],
): ColoredGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  for (const piece of pieces) {
    const mid = (piece.z + piece.size / 2) * tile.size;
    if (mid >= zMin && mid < zMax) addPiece(geo, piece, tile, look, ground);
  }
  return geo;
}
