import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { openHatch } from '../final-boss-shapes';
import { H, offset, QUARTER, WHITE } from '../mini-boss-shapes';
import { SPIDER_RED } from './canopy-spider-legs';
import { segment, VINE } from './toucan-jungle';
import { veinTo } from './jungle-flesh';

// P09-R09, 3-2: the Canopy Spider's egg sac, the part that launches its Gnat groups. Logical
// pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The sac's silk: a pale, dirty grey-green webbing. */
const SILK: Rgb = [0.42, 0.45, 0.38];
/** The cocoon along its axis (a lathe profile: radius, then length along -Z). */
const COCOON = [
  [0, -9],
  [7, -7.5],
  [10.5, -3],
  [11, 1.5],
  [8.6, 6],
  [4.6, 8.6],
  [0, 9.4],
] as const;
/** The eggs glowing through the silk (around the sac's centre: x, height, z). */
const EGGS: readonly Vec3[] = [
  [-4.5, 13.4, 1.5],
  [3.8, 13.8, -1],
  [0, 14.4, -5],
  [-5.4, 12.6, -7],
  [5.4, 12.6, -7.5],
];

/**
 * The egg sac at its centre `at` (P09-R09): a cocoon of silk hanging from the abdomen's tip,
 * wrapped in metal bands ringed with red neon, eggs glowing through it as the next brood
 * charges, and a hatch on top that the Gnats leave from.
 */
export function eggSac(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge } = p;
  const centre = offset(at, 0, 4, -3);
  // P16-R06: a living egg sac of pale membrane in grafted metal bands, veined with red.
  p.flesh.lathe(COCOON, 8, SILK, { at: centre, pitch: -QUARTER, yaw: Math.PI / 8 });
  for (const dz of [-4, 3]) {
    hull.cylinder(11.2, 1.6, 8, H.base, { at: offset(centre, 0, 0, dz), pitch: QUARTER });
    neon.ring(11.4, 0.6, 8, SPIDER_RED, { at: offset(centre, 0, 0, dz + 0.5), pitch: QUARTER });
  }
  for (const s of SIDES) {
    veinTo(
      p,
      [offset(centre, s * 9, 4, -8), offset(centre, s * 4, 9.2, 6)],
      [s * 2, 2, 0],
      SPIDER_RED,
    );
  }
  for (const egg of EGGS) charge.cylinder(1.8, 1.2, 6, WHITE, { at: offset(at, ...egg) }, 1);
  openHatch(p, offset(centre, 0, 11, 4), [6, 4]);
  for (const s of SIDES) {
    // Silk threads tying it to the abdomen.
    segment(
      hull,
      [offset(centre, s * 5, 6, 8), offset(centre, s * 3, 10, 14)],
      [0.4, 0.4],
      VINE,
      4,
    );
  }
}
