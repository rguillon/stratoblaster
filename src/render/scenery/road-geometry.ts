import type { Road, RoadPoint } from '../../core/scenery/road-network';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { HeightSource } from './terrain-geometry';

type Rgb = readonly [number, number, number];

/** How roads are drawn on the ground. */
export interface RoadLook {
  /** Colour of the main roads and of the paths. */
  readonly main: Rgb;
  readonly cross: Rgb;
  /** Height of the road surface above the ground, so it does not sink into the terrain mesh. */
  readonly lift: number;
}

/** Runs of consecutive valid points whose segments start inside [zMin, zMax). */
function runs(points: readonly RoadPoint[], zMin: number, zMax: number): RoadPoint[][] {
  const out: RoadPoint[][] = [];
  let run: RoadPoint[] = [];
  points.forEach((a, i) => {
    const b = points[i + 1];
    const keep = b !== undefined && a.valid && b.valid && a.z >= zMin && a.z < zMax;
    if (keep) {
      if (run.length === 0) run.push(a);
      run.push(b);
    } else if (run.length > 0) {
      out.push(run);
      run = [];
    }
  });
  if (run.length > 0) out.push(run);
  return out;
}

/** Unit vector across the road at point `i` of a run (from the neighbouring points). */
function across(run: readonly RoadPoint[], i: number): [number, number] {
  const a = run[Math.max(0, i - 1)];
  const b = run[Math.min(run.length - 1, i + 1)];
  if (!a || !b) return [1, 0];
  const length = Math.hypot(b.x - a.x, b.z - a.z) || 1;
  return [(b.z - a.z) / length, -(b.x - a.x) / length];
}

/**
 * Ribbons draped on the ground along the valid pieces of `roads` whose segments start in
 * [zMin, zMax) (P04-R07), so neighbouring terrain chunks draw each segment once.
 */
export function buildRoadGeometry(
  roads: readonly Road[],
  ground: HeightSource,
  zMin: number,
  zMax: number,
  look: RoadLook,
): ColoredGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  for (const road of roads) {
    const color = road.kind === 'main' ? look.main : look.cross;
    for (const run of runs(road.points, zMin, zMax)) {
      const base = geo.positions.length / 3;
      run.forEach((p, i) => {
        const [nx, nz] = across(run, i);
        for (const side of [-1, 1]) {
          const x = p.x + (side * nx * road.width) / 2;
          const z = p.z + (side * nz * road.width) / 2;
          geo.positions.push(x, ground.height(x, z) + look.lift, z);
          geo.colors.push(...color, 1);
        }
        if (i === 0) return;
        const [l0, r0, l1, r1] = [
          base + 2 * (i - 1),
          base + 2 * (i - 1) + 1,
          base + 2 * i,
          base + 2 * i + 1,
        ];
        // Front faces up (Babylon: normal = (c - a) × (b - a)).
        geo.indices.push(l0, r0, l1, r0, r1, l1);
      });
    }
  }
  return geo;
}
