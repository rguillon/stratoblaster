import { carapace, organ, segmentedBody } from '../../../render/geometry/organic';
import { BOSS_LOOK } from '../../config/boss-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { barrels, edgeStrips, missileTips, shift } from './final-boss-shapes';
import { barbs, F, graft, growth, M, polygon, sac, veinLine } from './world-1-organic-kit';

// P07-R05, P16-R06: the Storm Petrel's destroyable parts, growths on its wings, tail and
// breast. Logical pixels, nose +Z, Y up.
type Vec3 = [number, number, number];

const N = BOSS_LOOK.neon['storm-petrel'] ?? [1, 0.1, 0.85];

/**
 * A wing gun pod (P16-R06): a swollen gun gland on the wing, a grafted collar at its front and
 * twin barrels at its nose, a vein along each flank.
 */
export function drawPod(p: EnemyParts, at: Vec3): void {
  growth(p, shift(at, [0, 8, -2]), 13, N, { flesh: F.crimson, height: 0.3, armour: false });
  const pod = shift(at, [0, 10, 0]);
  segmentedBody(
    p.flesh,
    { tail: -16, nose: 14, segments: 3, width: 7, bottom: 0, top: 9 },
    F.purple,
    { at: pod },
  );
  graft(p, polygon(6, 5), [7.5, 9.3], shift(pod, [0, 0, 10]));
  for (const s of [-1, 1]) {
    veinLine(p, shift(pod, [s * 6.6, 5, -10]), shift(pod, [s * 6.4, 5, 8]), [s, 0.5, 0], 1, N);
  }
  p.neon.box([1, 0.4, 10], N, { at: shift(pod, [0, 9.2, -4]) });
  barrels(p, shift(pod, [0, 4.3, 14]), [2, 5], [1.3, 7]);
}

/**
 * The tail missile rack (P16-R06): a brood sac on the tail, a grafted rim round six missile
 * tips standing in it like eggs, a neon lip along its front.
 */
export function drawRack(p: EnemyParts, at: Vec3): void {
  organ(p.flesh, 13, 8, F.crimson, { at: shift(at, [0, 6, 0]), yaw: Math.PI / 8 }, 0.25);
  sac(p, shift(at, [0, 8, -2]), 10, F.purple, { stretch: 0.25 });
  graft(p, polygon(8, 11, [1, 1.1]), [11.6, 12.6], at, { color: M.base });
  missileTips(p, shift(at, [0, 12.6, 0]), [2, 3], [6.2, 1.8]);
  const [x, , z] = at;
  edgeStrips(
    p.neon,
    [
      [x - 10, z + 13.6],
      [x + 10, z + 13.6],
    ],
    1,
    [9.4, 10.6],
    N,
  );
  for (const s of [-1, 1])
    veinLine(p, shift(at, [s * 12, 8, -4]), shift(at, [s * 4, 4, -14]), [0, 1, 0], 1, N);
}

/**
 * The belly plate (P16-R06): a bony breast shell wrapped over the body's front, its plates
 * seamed, magenta veins along its shoulders, a riveted plate and bone barbs on its keel.
 */
export function drawPlate(p: EnemyParts, at: Vec3): void {
  const z = at[2];
  const shell = { tail: z - 17, nose: z + 18, segments: 4, width: 15, bottom: -1, top: 16.5 };
  carapace(p.flesh, shell, [F.bone, F.sinew], { at: [at[0], 0, 0] });
  for (const s of [-1, 1]) {
    veinLine(p, [at[0] + s * 12, 12, z - 12], [at[0] + s * 8, 9, z + 12], [s * 2, 2, 0], 1.2, N);
  }
  graft(p, polygon(5, 4, [1.4, 1.4]), [15.6, 17], [at[0], 0, z - 4]);
  barbs(p, [at[0], 4, z + 16], { count: 3, spacing: 4, size: 3, dir: [0, -0.3, 1] });
}
