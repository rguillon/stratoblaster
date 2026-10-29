import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';
import type { PropGeometry, PropModelFactory } from '../../../render/scenery/scenery-look';
import { BUILDING_MARGIN, TILE } from '../../config/tile-buildings';

// Phase 15 (reviewer, 2026-10-28): every prop follows the block size rule, placed on the grid of
// tiles or not: its footprint is stretched along X and Z to the nearest whole number of tiles,
// less the margin of the buildings, centred on the origin. Heights are kept.

/** The whole tiles nearest to `size`, at least one. */
export const tilesFor = (size: number): number => Math.max(1, Math.round(size / TILE.size));

/** Width of a footprint of `tiles` tiles. */
const fitted = (tiles: number): number => tiles * TILE.size - 2 * BUILDING_MARGIN;

function moved(
  geo: ColoredGeometry,
  map: (x: number, z: number) => [number, number],
): ColoredGeometry {
  const positions = [...geo.positions];
  for (let i = 0; i < positions.length; i += 3) {
    [positions[i], positions[i + 2]] = map(positions[i] ?? 0, positions[i + 2] ?? 0);
  }
  return { ...geo, positions };
}

/** `geometry` stretched to a footprint of whole tiles (see above). */
export function fitToTiles(geometry: PropGeometry): PropGeometry {
  const { positions } = geometry.structure;
  const xs = positions.filter((_, i) => i % 3 === 0);
  const zs = positions.filter((_, i) => i % 3 === 2);
  if (xs.length === 0) return geometry;
  const [x0, x1, z0, z1] = [Math.min(...xs), Math.max(...xs), Math.min(...zs), Math.max(...zs)];
  const sx = x1 > x0 ? fitted(tilesFor(x1 - x0)) / (x1 - x0) : 1;
  const sz = z1 > z0 ? fitted(tilesFor(z1 - z0)) / (z1 - z0) : 1;
  const [cx, cz] = [(x0 + x1) / 2, (z0 + z1) / 2];
  const map = (x: number, z: number): [number, number] => [(x - cx) * sx, (z - cz) * sz];
  const plumes = geometry.plumes?.map((p) => {
    const [x, z] = map(p.at[0], p.at[2]);
    return { ...p, at: [x, p.at[1], z] as const };
  });
  return {
    structure: moved(geometry.structure, map),
    ...(geometry.lights ? { lights: moved(geometry.lights, map) } : {}),
    ...(plumes ? { plumes } : {}),
  };
}

/** `models` with each one stretched to whole tiles. */
export const onTiles = (
  models: Readonly<Record<string, PropModelFactory>>,
): Record<string, PropModelFactory> =>
  Object.fromEntries(Object.entries(models).map(([id, f]) => [id, () => fitToTiles(f())]));
