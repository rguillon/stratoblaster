import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { cable } from '../mini-boss-greebles';
import { ram } from '../mini-boss-mechanism';
import { H, SHADE } from '../mini-boss-shapes';
import { FROST, icicle } from './floe-breaker-frost';

// P08-R10, 2-1: the Floe Breaker's deck dressing (phase 7 review: detail and some asymmetry,
// World 2 frost). Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];

/**
 * Along the bridge: portholes lit `n` down its sides, a lifeboat in its davits to port (+X),
 * a towing winch on the stern to starboard.
 */
export function floeDressing(p: EnemyParts, n: Rgb): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    for (const z of [-12, -18, -24]) neon.box([0.4, 1, 1.4], n, { at: [s * 13.1, 6.4, z] });
    icicle(hull, [s * 12.6, 11, -6.8], 2.4);
  }
  // A lifeboat hanging in its davits, a tarpaulin of snow over it.
  hull.box([3.2, 2.6, 10], SHADE.hazard, { at: [17.5, 5.6, -18] }, FROST.snow);
  for (const z of [-22, -14]) ram(hull, [15, 4.6, z], [17.5, 10, z], 0.5);
  // The towing winch, its cable led aft to the stern.
  hull.cylinder(2.4, 6, 8, H.panel, { at: [-9, 5.4, -40], roll: Math.PI / 2 });
  cable(
    hull,
    [
      [-12, -40],
      [-9, -43],
      [-5, -44],
    ],
    3.2,
    0.8,
  );
  hull.box([4, 1.6, 2.4], H.dark, { at: [-4, 3, -44] }, SHADE.edge);
}
