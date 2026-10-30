import { curve, organ, vein } from '../../../render/geometry/organic';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from './enemy-mesh';

// P16-R01: the Cyber-Organic pieces every enemy and boss model shares. Logical pixels, nose +Z,
// Y up.

type Vec3 = readonly [number, number, number];
type Rgb = readonly [number, number, number];

const F = ENEMY_LOOK.flesh;

/**
 * A reactor set in a glowing organ (P16-R01): a flesh sac swelling around its nozzle at `at`
 * (thrusting towards -Z), a gland lit on its back and a vein running from it `vein` forward.
 */
export function reactorSac(
  parts: EnemyParts,
  at: Vec3,
  radius: number,
  glow: Rgb,
  { flesh = F.crimson, veinLength = radius * 3 }: { flesh?: Rgb; veinLength?: number } = {},
): void {
  const [x, y, z] = at;
  // A sac lying along Z around the nozzle, its mouth at `at`.
  organ(
    parts.flesh,
    radius * 1.35,
    6,
    flesh,
    { at: [x, y, z + radius * 0.2], pitch: Math.PI / 2 },
    0.9,
  );
  parts.reactor(at, radius);
  const back: Vec3 = [x, y + radius * 1.2, z + radius * 1.2];
  vein(
    parts.vein,
    curve(back, [x, y + radius * 0.9, z + radius * 1.2 + veinLength], [0, radius * 0.4, 0], 2),
    radius * 0.35,
    glow,
  );
}

/** A cluster of `count` eyes across `at` (P16-R01), `size` each, `spacing` apart, lit as veins. */
export function eyes(
  parts: EnemyParts,
  at: Vec3,
  { count = 2, size = 0.6, spacing = 1.4 }: { count?: number; size?: number; spacing?: number },
  glow: Rgb,
): void {
  for (let i = 0; i < count; i++) {
    const x = at[0] + (i - (count - 1) / 2) * spacing;
    organ(parts.vein, size, 5, glow, { at: [x, at[1], at[2]] }, 0.7);
  }
}
