import { hash2D } from '../../core/math/noise';
import {
  cachedStreetLines,
  meetingWidth,
  roadZSpan,
  type StreetLine,
} from '../../core/scenery/road-traffic';
import type { Road, RoadPoint } from '../../core/scenery/road-network';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import { paintCentreLines, type CentreLineLook } from './road-lines';
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
  /** Narrower soft edge of the streets, so their crossings and corners stay clean. */
  readonly streetShoulder: number;
  /** The yellow line along the streets and main roads, if any (phase 4 review). */
  readonly centreLine?: CentreLineLook;
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

/**
 * The points of a road; a street goes on past both ends by half the width of the street it meets
 * there (its own if none), under it, so two streets meeting at a corner leave no notch and an
 * avenue does not stick out past a narrower street (phase 4 review).
 */
function ribbonPoints(road: Road, lines: readonly StreetLine[]): readonly RoadPoint[] {
  const [a, b, y, z] = [road.points[0], road.points[1], road.points.at(-2), road.points.at(-1)];
  if (road.kind !== 'street' || !a || !b || !y || !z) return road.points;
  const past = (end: RoadPoint, next: RoadPoint): RoadPoint => {
    const length = Math.hypot(end.x - next.x, end.z - next.z) || 1;
    const k = (meetingWidth(lines, road.index, end.x, end.z) ?? road.width) / 2 / length;
    return { ...end, x: end.x + (end.x - next.x) * k, z: end.z + (end.z - next.z) * k };
  };
  return [past(a, b), ...road.points, past(z, y)];
}

/** Colour and opacity of a point of a road, worn by a hash of its position (not streets). */
function worn(road: Road, p: RoadPoint, look: RoadLook): [number, number, number, number] {
  // Streets are opaque and even, so where they cross or meet they merge without a seam.
  if (road.kind === 'street') return [...look.main, 1];
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
 * sides, so the road blends into the ground (phase 4 review). Streets and main roads get a
 * yellow centre line.
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
  const lines = cachedStreetLines(roads);
  // How far past its points a street's ribbon may reach (see `ribbonPoints`).
  const reach = Math.max(0, ...lines.map((l) => l.width)) / 2 + 1;
  for (const road of roads) {
    // P13-R04: a road with no point near the chunk has no segment in it.
    const [zLow, zHigh] = roadZSpan(road);
    if (zHigh < zMin - reach || zLow >= zMax + reach) continue;
    const shoulder = road.kind === 'street' ? look.streetShoulder : look.shoulder;
    for (const run of runs(ribbonPoints(road, lines), zMin, zMax)) {
      const base = geo.positions.length / 3;
      run.forEach((p, i) => {
        const [nx, nz] = across(run, i);
        const [r, g, b, a] = worn(road, p, look);
        for (const row of ROWS) {
          const offset = (row.across * p.width) / 2 + row.shoulder * shoulder;
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
  // Painted after the ribbons, so they draw over them.
  if (look.centreLine) {
    paintCentreLines(
      { geo, ground, look: look.centreLine, roadLift: look.lift },
      roads,
      zMin,
      zMax,
    );
  }
  return geo;
}
