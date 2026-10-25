import type { LoftStation, SectionPoint } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { hullPlate, stationAt, TITAN_HULL } from './refinery-titan-hull';
import { TITAN_NEON } from './refinery-titan-parts';

// P07-R05 (phase 7 review: fat armour over complex machinery): thick plates along the Refinery
// Titan's upper flanks, with gaps between them showing gears, rams, cables and lit conduits
// underneath. Model space: logical pixels, nose +Z, Y up; +X is the screen's left.
const H = ENEMY_LOOK.hull;
const QUARTER = Math.PI / 2;

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** Weathered colours of the hull: rust on a patched plate, faded amber hazard paint, soot. */
export const TITAN_WEAR = {
  rust: [0.22, 0.12, 0.06],
  hazard: [0.45, 0.32, 0.06],
  soot: [0.03, 0.028, 0.03],
} as const satisfies Record<string, Rgb>;

/**
 * An armour plate's section over the hull's +X shoulder (`HULL_SECTION`: the upper flank and the
 * edge of the back): its underside on the hull, its face proud of it, counter-clockwise seen
 * from the nose.
 */
const PLATE: readonly SectionPoint[] = [
  [0.84, 0.62],
  [0.94, 0.67],
  [0.68, 1.14],
  [0.47, 1.13],
  [0.47, 1],
  [0.6, 1],
];

/** The plate's stations from `z0` to `z1`: chamfered ends, sunk a little into the hull. */
function plateStations([z0, z1]: readonly [number, number]): LoftStation[] {
  const sunk = (z: number, k: number): LoftStation => {
    const [, w, b, t] = stationAt(TITAN_HULL, z);
    return [z, w * k, b, b + (t - b) * k];
  };
  const inside = TITAN_HULL.filter(([z]) => z > z0 + 1.5 && z < z1 - 1.5);
  const ends = [sunk(z0 + 1.5, 1), ...inside, sunk(z1 - 1.5, 1)];
  return [sunk(z0, 0.95), ...ends, sunk(z1, 0.95)];
}

/** Where a fraction `f` of the flank (0: chine, 1: top edge) is at `z`, `lift` off it, and its tilt. */
function onFlank(s: number, f: number, z: number, lift: number): { at: Vec3; roll: number } {
  const [, w, b, t] = stationAt(TITAN_HULL, z);
  const [nx, ny] = [s * 0.6 * (t - b), 0.4 * w];
  const n = Math.hypot(nx, ny);
  const x = s * w * (1 - 0.4 * f) + (nx / n) * lift;
  const y = b + (t - b) * (0.4 + 0.6 * f) + (ny / n) * lift;
  return { at: [x, y, z], roll: Math.atan2(-nx, ny) };
}

/** A gear rim lying on the flank: a low-sided cog, its hub. */
const COG = [
  [3.4, 0],
  [3.4, 1.1],
  [1.6, 1.6],
  [0, 1.6],
] as const;

/** The machinery in a gap at `z` on flank `s`: a cog, twin rams across, cables, a lit conduit. */
function drawWorks({ hull, neon, charge }: EnemyParts, s: number, z: number, lit: boolean): void {
  // The gap's floor, dark, under the works.
  hullPlate(hull, s > 0 ? 1 : 3, s > 0 ? [0.3, 1] : [0, 0.7], [z - 5.5, z + 5.5], H.dark, 1.01);
  hullPlate(hull, 2, s > 0 ? [0, 0.14] : [0.86, 1], [z - 5.5, z + 5.5], H.dark);
  hull.lathe(COG, 8, H.dark, onFlank(s, 0.72, z, 0.8));
  charge.cylinder(1, 0.4, 6, [1, 1, 1], onFlank(s, 0.72, z, 2.4));
  // Hydraulic rams spanning the gap from plate to plate: a fat barrel, a bright rod.
  for (const f of [0.42, 1]) {
    const { at } = onFlank(s, f, z - 6, 1.3);
    hull.cylinder(1.1, 6, 6, H.dark, { at, pitch: QUARTER });
    hull.cylinder(0.55, 5, 6, H.panel, { at: [at[0], at[1], z + 1], pitch: QUARTER });
  }
  // A cable bundle low in the gap, and a conduit glowing deep inside.
  const cable = onFlank(s, 0.36, z - 4, 0.6);
  hull.cylinder(0.7, 8, 5, H.panel, { at: cable.at, pitch: QUARTER });
  const conduit = onFlank(s, 0.86, z, 0.5);
  if (lit) neon.box([1.6, 0.9, 11], TITAN_NEON, conduit);
  else charge.box([1.4, 0.9, 11], [1, 1, 1], conduit);
}

/** A flank's plates (z ranges, colour) and the gaps between them where the works show. */
interface Flank {
  readonly side: 1 | -1;
  readonly plates: readonly (readonly [number, number, Rgb])[];
}

const FLANKS: readonly Flank[] = [
  {
    side: 1,
    plates: [
      [-46, -36, H.panel],
      [-26, -12, H.base],
      [-2, 10, TITAN_WEAR.rust],
      [20, 28, H.panel],
    ],
  },
  // The right flank carries the pipe rack at the back: armour only from the bridge forward.
  {
    side: -1,
    plates: [
      [-2, 10, H.base],
      [20, 28, H.panel],
    ],
  },
];

/** P07-R05 (phase 7 review): the flank armour, and the machinery showing between its plates. */
export function drawTitanArmour(parts: EnemyParts): void {
  for (const { side, plates } of FLANKS) {
    const section = side > 0 ? PLATE : PLATE.map(([u, v]): SectionPoint => [-u, v]).reverse();
    plates.forEach(([z0, z1, color], i) => {
      parts.hull.loft(section, plateStations([z0, z1]), color);
      const next = plates[i + 1];
      if (next) drawWorks(parts, side, (z1 + next[0]) / 2, i % 2 === 0);
    });
  }
}
