import { ROUND_SECTION } from '../../../../render/geometry/organic';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { reactorSac } from '../../enemies/organic-parts';
import { F, gland, JUNGLE_FLESH, sinew, veinTo } from './jungle-flesh';
import { SUMMIT, TEMPLE_CYAN, TIERS } from './sky-temple-parts';

// P16-R06, 3-3: the living beast the Sky Temple grew on. Logical pixels, nose +Z, Y up: a huge,
// swollen body of moss-skinned flesh carrying the stone tiers on its back like a shell, roots
// of sinew hanging from it, veins climbing the stones to the sanctum.
type Vec3 = readonly [number, number, number];

/** The body under the lowest tier, tail to front (loft stations: z, half width, bottom, top). */
function bodyStations(): [number, number, number, number][] {
  const half = TIERS.halves[0];
  const top = TIERS.height + 1;
  return [
    [-half - 2, half * 0.55, 2, top - 4],
    [-half * 0.7, half * 0.98, -3, top],
    [0, half * 1.04, -4, top + 1],
    [half * 0.7, half * 0.98, -3, top],
    [half + 2, half * 0.55, 2, top - 4],
  ];
}

/** The body of the beast (P16-R06), in place of the lowest stone tier. */
export function templeBody(p: EnemyParts): void {
  p.flesh.loft(ROUND_SECTION, bodyStations(), JUNGLE_FLESH);
  const half = TIERS.halves[0];
  for (const s of SIDES) {
    for (const z of [-40, 0, 40]) {
      sinew(
        p,
        [
          [s * half * 0.9, 0, z],
          [s * (half + 3), -12, z + 6],
        ],
        [s * 2, -2, 0],
        2.4,
      );
    }
  }
  // Veins climbing the tiers along their diagonals up to the sanctum.
  for (const x of SIDES) {
    for (const z of SIDES) {
      const from: Vec3 = [x * half * 0.8, TIERS.height + 1.2, z * half * 0.8];
      const to: Vec3 = [x * 12, SUMMIT + 0.4, z * 12 - 8];
      veinTo(p, [from, to], [0, 6, 0], TEMPLE_CYAN, 1.6);
      gland(p, [x * half * 0.8, TIERS.height + 0.4, z * half * 0.8], 3, TEMPLE_CYAN);
    }
  }
}

/** Its reactors (P16-R01): each in a flesh sac at the back of the beast. */
export function templeReactors(p: EnemyParts, z: number, nozzles: readonly number[]): void {
  for (const x of nozzles) reactorSac(p, [x, 0, z], 4.5, TEMPLE_CYAN, { flesh: F.sinew });
}
