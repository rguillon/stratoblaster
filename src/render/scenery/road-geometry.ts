import { hash2D } from '../../core/math/noise';
import type { Road, RoadPoint } from '../../core/scenery/road-network';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { HeightSource } from './terrain-geometry';

type Rgb = readonly [number, number, number];

/** How roads are drawn on the ground. */
export interface RoadLook {
  /** Colour of the main roads and of the paths. */
  readonly main: Rgb;
  readonly cross: Rgb;
  /** Opacity of the road surface (below 1, the ground texture shows through). */
  readonly opacity: { readonly main: number; readonly cross: number };
  /** Width of the soft edge on each side, where the road fades into the ground. */
  readonly shoulder: number;
  /** How much (0..1) colour and opacity vary along a road, so it looks worn. */
  readonly wear: number;
  /** Height of the road surface above the ground, so it does not sink into the terrain mesh. */
  readonly lift: number;
}

/** Offsets across a road (in half-widths) and opacity factors of its 4 vertex rows. */
const ROWS = [
  { across: -1, shoulder: -1, opacity: 0 },
  { across: -1, shoulder: 0, opacity: 1 },
  { across: 1, shoulder: 0, opacity: 1 },
  { across: 1, shoulder: 1, opacity: 0 },
] as const;

/** Runs of consecutive points whose segments start inside [zMin, zMax). */
function runs(points: readonly RoadPoint[], zMin: number, zMax: number): RoadPoint[][] {
  const out: RoadPoint[][] = [];
  let run: RoadPoint[] = [];
  points.forEach((a, i) => {
    const b = points[i + 1];
    if (b !== undefined && a.z >= zMin && a.z < zMax) {
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

/** Colour and opacity of point `i` of a road, worn by a hash of its position. */
function worn(road: Road, p: RoadPoint, look: RoadLook): [number, number, number, number] {
  const [r, g, b] = road.kind === 'main' ? look.main : look.cross;
  const opacity = road.kind === 'main' ? look.opacity.main : look.opacity.cross;
  const shade = 1 + (hash2D(Math.round(p.x), Math.round(p.z), road.index) - 0.5) * look.wear;
  const fade = 1 - hash2D(Math.round(p.z), Math.round(p.x), road.index + 1) * look.wear;
  return [r * shade, g * shade, b * shade, opacity * fade];
}

/**
 * Ribbons draped on the ground along the segments of `roads` that start in [zMin, zMax)
 * (P04-R07), so neighbouring terrain chunks draw each segment once. The ribbon follows the
 * width of each point (paths widen at their junction). Each ribbon
 * has a slightly see-through, worn surface and soft shoulders that fade to nothing on both
 * sides, so the road blends into the ground (phase 4 review).
 */
export function buildRoadGeometry(
  roads: readonly Road[],
  ground: HeightSource,
  zMin: number,
  zMax: number,
  look: RoadLook,
): ColoredGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  const rows = ROWS.length;
  for (const road of roads) {
    for (const run of runs(road.points, zMin, zMax)) {
      const base = geo.positions.length / 3;
      run.forEach((p, i) => {
        const [nx, nz] = across(run, i);
        const [r, g, b, a] = worn(road, p, look);
        for (const row of ROWS) {
          const offset = (row.across * p.width) / 2 + row.shoulder * look.shoulder;
          const x = p.x + nx * offset;
          const z = p.z + nz * offset;
          geo.positions.push(x, ground.height(x, z) + look.lift, z);
          geo.colors.push(r, g, b, a * row.opacity);
        }
        if (i === 0) return;
        for (let k = 0; k < rows - 1; k++) {
          const [l0, r0] = [base + rows * (i - 1) + k, base + rows * (i - 1) + k + 1];
          const [l1, r1] = [base + rows * i + k, base + rows * i + k + 1];
          // Front faces up (Babylon: normal = (c - a) × (b - a)).
          geo.indices.push(l0, r0, l1, r0, r1, l1);
        }
      });
    }
  }
  return geo;
}
