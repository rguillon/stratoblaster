import type { RoadPiece } from '../../core/scenery/road-tiles';
import type { TileRules } from '../../core/scenery/scenery-level';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { RoadAtlas } from './road-atlas';
import { addPiece, type TileRoadLook } from './tile-road-geometry';

// Phase 15 (experiment, reviewer 2026-10-28): each road piece as one surface draped on the
// ground, cut on a world lattice, its markings from the road atlas.

/** A geometry with texture coordinates. */
export interface TexturedGeometry extends ColoredGeometry {
  readonly uvs: number[];
}

/** The cuts of [a, b] on the world lattice of `cell`. */
function cuts(a: number, b: number, cell: number): number[] {
  const out = [a];
  for (let c = (Math.floor(a / cell) + 1) * cell; c < b - 1e-6; c += cell) out.push(c);
  out.push(b);
  return out;
}

function addSurface(
  geo: TexturedGeometry,
  piece: RoadPiece,
  [u0, v0, u1, v1]: readonly [number, number, number, number],
  [tile, lift]: readonly [TileRules, number],
  ground: (x: number, z: number) => number,
): void {
  const size = piece.size * tile.size;
  const [ox, oz] = [piece.x * tile.size, piece.z * tile.size];
  const cell = tile.size / 2;
  const xs = cuts(ox, ox + size, cell);
  const zs = cuts(oz, oz + size, cell);
  const base = geo.positions.length / 3;
  for (const z of zs) {
    for (const x of xs) {
      geo.positions.push(x, ground(x, z) + lift, z);
      geo.colors.push(1, 1, 1, 1);
      geo.uvs.push(u0 + ((x - ox) / size) * (u1 - u0), v0 + ((z - oz) / size) * (v1 - v0));
    }
  }
  const nx = xs.length - 1;
  for (let j = 0; j < zs.length - 1; j++) {
    for (let i = 0; i < nx; i++) {
      const a = base + j * (nx + 1) + i;
      const c = a + nx + 1;
      geo.indices.push(a, a + 1, c, a + 1, c + 1, c);
    }
  }
}

/**
 * The pieces whose middle is in [zMin, zMax): textured surfaces, and the layered geometry of
 * those the atlas has no room for.
 */
export function buildRoadSurfaces(
  pieces: readonly RoadPiece[],
  [tile, look]: readonly [TileRules, TileRoadLook],
  atlas: RoadAtlas,
  ground: (x: number, z: number) => number,
  [zMin, zMax]: readonly [number, number],
): { surfaces: TexturedGeometry; layered: ColoredGeometry } {
  const surfaces: TexturedGeometry = { positions: [], indices: [], colors: [], uvs: [] };
  const layered: ColoredGeometry = { positions: [], indices: [], colors: [] };
  for (const piece of pieces) {
    const mid = (piece.z + piece.size / 2) * tile.size;
    if (mid < zMin || mid >= zMax) continue;
    const rect = atlas.rectOf(piece);
    if (rect) addSurface(surfaces, piece, rect, [tile, look.lift], ground);
    else addPiece(layered, piece, tile, look, ground);
  }
  return { surfaces, layered };
}
