import type { PieceKind, PieceSides, RoadPiece } from '../core/scenery/road-tiles';

// The `props/` page on the grid of tiles (phase 15): each prop on whole tiles, in a cell of the
// layout, and with streets, the cells ringed by one-tile roads, so the buildings stand in blocks.

/** Where the props and the roads go, in tiles. */
export interface TileLayout {
  /** Centre of each prop, in tiles (a half tile for an odd footprint). */
  readonly centres: readonly (readonly [number, number])[];
  readonly roads: readonly RoadPiece[];
  /** The tiles the layout covers: [x0, x1, z0, z1]. */
  readonly bounds: readonly [number, number, number, number];
}

/** Steps to the neighbour beyond each side (+Z, +X, -Z, -X). */
const STEPS = [
  [0, 1],
  [1, 0],
  [0, -1],
  [-1, 0],
] as const;

const KINDS: Readonly<Record<number, PieceKind>> = { 3: 'tee', 4: 'cross' };

/** The one-tile road pieces on the tiles of `roads`, each open toward its road neighbours. */
function roadPieces(roads: ReadonlySet<string>, tiles: readonly [number, number][]): RoadPiece[] {
  const side = { size: 1, offset: 0 };
  return tiles.map(([x, z]) => {
    const open = STEPS.map(([dx, dz]) => roads.has(`${String(x + dx)},${String(z + dz)}`));
    const count = open.filter(Boolean).length;
    const straight = open[0] === open[2] && open[1] === open[3];
    const kind = KINDS[count] ?? (count === 2 && !straight ? 'turn' : 'straight');
    const sides = open.map((o) => (o ? side : undefined)) as unknown as PieceSides;
    return { x, z, size: 1, kind, adapter: false, sides };
  });
}

/** Where a footprint of `w` tiles starts in a block of `room` tiles from `start`, centred. */
const centre = (start: number, room: number, w: number): number =>
  start + Math.floor((room - w) / 2) + w / 2;

/**
 * Without streets: rows of props side by side, each `gap` tiles from the next, so a large prop
 * (the road sample) does not spread the small ones apart.
 */
function packedLayout(footprints: readonly (readonly [number, number])[], gap: number): TileLayout {
  const columns = Math.max(1, Math.ceil(Math.sqrt(footprints.length)));
  const rows: (readonly [number, number])[][] = [];
  footprints.forEach((f, i) => {
    if (i % columns === 0) rows.push([]);
    rows.at(-1)?.push(f);
  });
  const widths = rows.map((r) => r.reduce((sum, [w]) => sum + w + gap, gap));
  const depths = rows.map((r) => Math.max(...r.map(([, d]) => d)));
  const width = Math.max(...widths);
  const depth = depths.reduce((sum, d) => sum + d + gap, gap);
  const [ox, oz] = [-Math.floor(width / 2), -Math.floor(depth / 2)];
  const centres: [number, number][] = [];
  let z = oz + depth - gap;
  rows.forEach((row, r) => {
    const rowDepth = depths[r] ?? 1;
    z -= rowDepth;
    let x = ox + gap;
    for (const [w, d] of row) {
      centres.push([x + w / 2, centre(z, rowDepth, d)]);
      x += w + gap;
    }
    z -= gap;
  });
  return { centres, roads: [], bounds: [ox, ox + width, oz, oz + depth] };
}

/**
 * Lays out props whose footprints are `footprints` (in tiles, width × depth) on a square-ish
 * grid of cells, `gap` tiles between them; with `streets`, the gaps are roads one tile wide.
 */
export function tileLayout(
  footprints: readonly (readonly [number, number])[],
  gap: number,
  streets: boolean,
): TileLayout {
  if (!streets) return packedLayout(footprints, gap);
  const room = Math.max(1, ...footprints.flat());
  const cell = room + gap;
  const columns = Math.max(1, Math.ceil(Math.sqrt(footprints.length)));
  const rows = Math.max(1, Math.ceil(footprints.length / columns));
  const [ox, oz] = [-Math.floor((columns * cell + gap) / 2), -Math.floor((rows * cell + gap) / 2)];
  const centres = footprints.map(([w, d], i): [number, number] => [
    centre(ox + (i % columns) * cell + gap, room, w),
    centre(oz + (rows - 1 - Math.floor(i / columns)) * cell + gap, room, d),
  ]);
  const bounds = [ox, ox + columns * cell + gap, oz, oz + rows * cell + gap] as const;
  if (gap === 0) return { centres, roads: [], bounds };
  const tiles: [number, number][] = [];
  for (let x = bounds[0]; x < bounds[1]; x++) {
    for (let z = bounds[2]; z < bounds[3]; z++) {
      if ((x - ox) % cell < gap || (z - oz) % cell < gap) tiles.push([x, z]);
    }
  }
  const set = new Set(tiles.map(([x, z]) => `${String(x)},${String(z)}`));
  return { centres, roads: roadPieces(set, tiles), bounds };
}
