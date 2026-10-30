import { organ } from '../../../../render/geometry/organic';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { crystals, gland, ICE_FLESH, sinew } from './w2-organic';

// P08-R10, 2-1: the Floe Breaker's dressing (phase 7 review: detail and some asymmetry).
// P16-R05: glands down its flanks, an egg sac to port, a coiled tow sinew to starboard.
// Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];

/**
 * Along the hump: glands lit `n` down its sides, an egg sac to port (+X), a coiled tow sinew on
 * the stern to starboard.
 */
export function floeDressing(p: EnemyParts, n: Rgb): void {
  for (const s of SIDES) {
    for (const z of [-12, -24]) gland(p, [s * 12.6, 6.4, z], 0.8, n);
    crystals(p.flesh, [s * 12, 10, -7], 2.4, 2);
  }
  organ(p.flesh, 3.4, 6, ICE_FLESH.membrane, { at: [17.5, 4, -18], pitch: Math.PI / 2 }, 1.4);
  sinew(p.flesh, [15, 5, -22], [17.5, 7, -14], 0.6);
  organ(p.flesh, 2.6, 5, ICE_FLESH.sinew, { at: [-9, 4, -40] }, 0.8);
  sinew(p.flesh, [-12, 4, -40], [-5, 3, -44], 0.8, ICE_FLESH.sinew, [0, 0, -3]);
}
