import type { MembraneWing } from '../../../render/geometry/organic';
import { curve, tendril } from '../../../render/geometry/organic';
import type { SectionPoint, SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from './enemy-mesh';
import { SIDES } from './enemy-shapes';

// P16-R04: Cyber-Organic pieces shared by the veteran and elite models. Logical pixels, nose +Z,
// Y up.

type Vec3 = readonly [number, number, number];
type Rgb = readonly [number, number, number];

const F = ENEMY_LOOK.flesh;

/** `wing` (drawn on the right) mirrored to side `s`. */
function sided(wing: MembraneWing, s: 1 | -1): MembraneWing {
  return {
    ...wing,
    root: [s * wing.root[0], wing.root[1]],
    tips: wing.tips.map(([x, z]) => [s * x, z] as const),
  };
}

/**
 * P16-R04: a pair of membrane wings (`wing` is the right one), a `membrane` skin on a `bone` strut,
 * each fluttering on its root (P16-R07).
 */
export function membranePair(p: EnemyParts, wing: MembraneWing, span: number): void {
  for (const s of SIDES) {
    const w = sided(wing, s);
    p.flap([w.root[0], w.y, w.root[1]], s, span, (parts) => {
      // A `membrane` skin, and one `bone` strut along its leading tip (lean on triangles).
      const { root, tips, y, thickness, strut } = w;
      parts.flesh.slab([root, ...tips], [y - thickness / 2, y + thickness / 2], F.membrane);
      const [x, z] = tips[0] ?? root;
      const path = curve([root[0], y, root[1]], [x, y, z], [0, thickness * 2, 0], 2);
      tendril(parts.flesh, path, [strut, strut * 0.2], 3, F.bone);
    });
  }
}

/** A pair of mandibles hooking forward and in from `at` (`spread` out, `length` long), in bone. */
export function mandibles(
  b: SolidBuilder,
  [x, y, z]: Vec3,
  [spread, length, radius]: readonly [number, number, number],
): void {
  for (const s of SIDES) {
    const path = curve(
      [x + s * spread * 0.5, y, z],
      [x + s * spread * 0.3, y, z + length],
      [s * spread * 0.6, 0, 0],
      2,
    );
    tendril(b, path, [radius, 0], 3, F.bone);
  }
}

/** A sinew (a thin flesh tendril, `sides` facets) from `a` to `b`, bowed by `bow`. */
export function sinew(
  b: SolidBuilder,
  from: Vec3,
  to: Vec3,
  [r0, r1]: readonly [number, number],
  color: Rgb = F.sinew,
  bow: Vec3 = [0, 0.6, 0],
): void {
  tendril(b, curve(from, to, bow, 2), [r0, r1], 4, color);
}

/** A lean rounded cross-section (7 points instead of 9): a swollen body on fewer triangles. */
export const LEAN_SECTION: readonly SectionPoint[] = [
  [0.5, 0],
  [1, 0.4],
  [0.6, 0.9],
  [0, 1],
  [-0.6, 0.9],
  [-1, 0.4],
  [-0.5, 0],
];
