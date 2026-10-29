import type { OutlinePoint } from '../../../render/geometry/outline';
import { curve, tendril, vein } from '../../../render/geometry/organic';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from './enemy-mesh';
import { decal, SIDES } from './enemy-shapes';

// P16-R03: the pieces the basic kinds share: grafted gun barrels, a pair of fluttering membrane
// wings, sinews and eyes. Logical pixels, nose +Z, Y up.

type Vec3 = readonly [number, number, number];
type Rgb = readonly [number, number, number];

const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/**
 * A small gun barrel grafted on (P16-R01: metal), from `at` along `yaw` (0: to the nose),
 * `length` long, a charge light at its muzzle (phase 7 review), marked there.
 */
export function gunBarrel(
  { hull, charge, muzzle }: EnemyParts,
  at: Vec3,
  length: number,
  yaw = 0,
): void {
  const along = (d: number): [number, number, number] => [
    at[0] + Math.sin(yaw) * d,
    at[1],
    at[2] + Math.cos(yaw) * d,
  ];
  hull.cylinder(0.55, length, 5, H.dark, { at: [...at], pitch: QUARTER, yaw }, 0.45);
  charge.cylinder(0.6, 0.8, 5, WHITE, { at: along(length), pitch: QUARTER, yaw });
  muzzle(along(length + 0.8));
}

/** A right membrane wing: its root (x, z) and tips, mirrored for the left one. */
export interface WingShape {
  readonly root: OutlinePoint;
  readonly tips: readonly OutlinePoint[];
  readonly y: number;
  readonly strut: number;
  /** Optional steady lights on the right wing, drawn in neon: convex outlines on its top. */
  readonly lights?: readonly (readonly OutlinePoint[])[];
}

const mirror = (o: readonly OutlinePoint[], s: number): OutlinePoint[] =>
  o.map(([x, z]): OutlinePoint => [s * x, z]);

/**
 * P16-R01, P16-R07: a pair of membrane wings, each fluttering from its root: a `membrane` skin
 * spread from the root to its tips, a lean `bone` strut out to each tip, and either a steady
 * neon light on it or a vein along its leading strut.
 */
export function wingPair(parts: EnemyParts, shape: WingShape, glow: Rgb): void {
  const { root, tips, y, strut, lights } = shape;
  for (const s of SIDES) {
    const r: OutlinePoint = [s * root[0], root[1]];
    const ts = mirror(tips, s);
    const span = Math.max(...tips.map(([x]) => Math.abs(x - root[0])));
    parts.flap([r[0], y, r[1]], s, span, (w) => {
      w.flesh.slab([r, ...ts], [y - 0.25, y + 0.25], F.membrane);
      for (const [x, z] of ts) {
        const path = curve([r[0], y, r[1]], [x, y, z], [0, 0.6, 0], 2);
        tendril(w.flesh, path, [strut, 0], 3, F.bone);
      }
      const tip = ts[0] ?? r;
      const mid: Vec3 = [(r[0] + tip[0]) / 2, y + 0.5, (r[1] + tip[1]) / 2];
      for (const light of lights ?? []) decal(w.neon, mirror(light, s), y + 0.3, glow);
      if (!lights) vein(w.vein, [[r[0], y + 0.5, r[1]], mid], 0.5, glow);
    });
  }
}

/** A sinew from `from` to `to`, bowed by `bow`: three facets, thinning out. */
export function sinew(parts: EnemyParts, from: Vec3, to: Vec3, bow: Vec3, radius: number): void {
  tendril(parts.flesh, curve(from, to, bow, 2), [radius, radius * 0.5], 3, F.sinew);
}

/** A pair of small glowing eyes, `gap` apart across `at` (P16-R01: lit as veins): 8 triangles each. */
export function eyePair(parts: EnemyParts, at: Vec3, gap: number, size: number, glow: Rgb): void {
  const bead = [
    [0, -size * 0.5],
    [size, 0],
    [0, size * 0.5],
  ] as const;
  for (const s of SIDES) parts.vein.lathe(bead, 4, glow, { at: [at[0] + s * gap, at[1], at[2]] });
}
