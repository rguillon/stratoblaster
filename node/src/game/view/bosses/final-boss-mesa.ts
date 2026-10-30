import { organ } from '../../../render/geometry/organic';
import { BOSS_LOOK } from '../../config/boss-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { edgeStrips, missileTips, shift } from './final-boss-shapes';
import { barbs, F, graft, M, polygon, sac, tentacle, veinLine } from './world-1-organic-kit';

// P07-R05, P16-R06: the Mesa Fortress's destroyable parts, the lances its forelimbs cradle and
// the spore silos on its back. Logical pixels, nose +Z, Y up.
type Vec3 = [number, number, number];

const N = BOSS_LOOK.neon['mesa-fortress'] ?? [1, 0.1, 0.12];
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** Height of the skirt's top. */
export const BASE_TOP = 7;

/** The lance's lens (a lathe profile along its axis). */
const LENS = [
  [0, 0],
  [4, 1],
  [3.2, 3],
  [0, 3.8],
] as const;

/**
 * A laser lance (P16-R06): a swollen gland in the forelimb's cradle, a long grafted barrel out
 * of it ringed with neon, sinews binding it, its lens glowing as it charges.
 */
export function drawLance(p: EnemyParts, at: Vec3): void {
  organ(p.flesh, 12, 8, F.crimson, { at: shift(at, [0, -2, -4]), yaw: Math.PI / 8 }, 0.5);
  graft(p, polygon(6, 7, [1, 1.4]), [10, 11.4], shift(at, [0, 0, -6]));
  const [x, , z] = at;
  edgeStrips(
    p.neon,
    [
      [x, z - 13],
      [x, z + 4],
    ],
    1.4,
    [11.4, 12],
    N,
  );
  const barrel = shift(at, [0, 6, 8]);
  p.hull.cylinder(5.5, 28, 8, M.dark, { at: barrel, pitch: QUARTER }, 3.6);
  for (const dz of [6, 13, 20]) {
    const r = 5.5 - (dz / 28) * 1.9 + 0.3;
    p.neon.ring(r, 1.2, 8, N, { at: shift(barrel, [0, 0, dz]), pitch: QUARTER });
  }
  for (const s of [-1, 1]) {
    tentacle(
      p,
      shift(at, [s * 9, 4, -2]),
      shift(barrel, [s * 4.6, 0, 9]),
      [s * 2, 2, 0],
      [1.6, 1],
      F.sinew,
      4,
    );
    veinLine(p, shift(at, [s * 11, 2, -12]), shift(at, [s * 6, 8, 4]), [s * 2, 2, 0], 1, N);
  }
  // The lens glows through the warning line and while the laser fires.
  p.charge.lathe(LENS, 8, WHITE, { at: shift(barrel, [0, 0, 27.5]), pitch: QUARTER });
  p.muzzle(shift(barrel, [0, 0, 31.3]), 'laser');
}

/**
 * A missile silo (P16-R06): a swollen spore pod on the shell's rear, a grafted collar round its
 * mouth and four missile tips standing in it like seeds, a vein ring at its foot.
 */
export function drawSilo(p: EnemyParts, at: Vec3): void {
  const base = shift(at, [0, BASE_TOP, 0]);
  organ(p.flesh, 12.5, 7, F.purple, { at: shift(base, [0, -4, 0]) }, 0.4);
  p.neon.ring(12.7, 0.8, 7, N, { at: shift(base, [0, 0.6, 0]) });
  sac(p, shift(base, [0, 0, 0]), 9, F.crimson, { stretch: 0.3 });
  const hatch = shift(base, [0, 5, 0]);
  graft(p, polygon(6, 8.5), [4.6, 5.4], base, { color: M.base });
  p.charge.slab(polygon(6, 6.5), [4.8, 5.6], WHITE, { at: base });
  missileTips(p, shift(hatch, [0, 0.4, 0]), [2, 2], [5.6, 1.9]);
  barbs(p, shift(base, [0, 3, -10]), { count: 3, spacing: 4, size: 3, dir: [0, 0.6, -1] });
}
