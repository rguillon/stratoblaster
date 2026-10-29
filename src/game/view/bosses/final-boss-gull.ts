import type { OutlinePoint } from '../../../render/geometry/outline';
import { organ } from '../../../render/geometry/organic';
import { BOSS_LOOK } from '../../config/boss-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { edgeStrips, shift, sided } from './final-boss-shapes';
import {
  barbs,
  F,
  graft,
  growth,
  M,
  polygon,
  sac,
  tentacle,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R06: the Gull Mothership's destroyable parts, its brood pouches and flak
// growths. Logical pixels, nose +Z, Y up.
type Vec3 = [number, number, number];

const N = BOSS_LOOK.neon['gull-mothership'] ?? [0.2, 1, 0.35];
const WHITE = [1, 1, 1] as const;

/** Height of the mantle's top. */
export const DECK_TOP = 4;
/** The right pouch around its centre, its outer side to +X, its inner side on the mantle. */
const HANGAR = [
  [-17, 20],
  [17, 20],
  [21, 14],
  [21, -16],
  [17, -21],
  [-17, -21],
] as const;
const HANGAR_TOP = 10;
/** The pouch's birth slit, glowing as the next launch charges (around the slit's centre). */
const SLIT = [
  [-6, 13],
  [6, 13],
  [8, 0],
  [6, -13],
  [-6, -13],
  [-8, 0],
] as const;

/**
 * A hangar bay (P16-R06): a swollen brood pouch on the mantle's flank, a glowing birth slit in
 * its top between fleshy lips, green glands down both sides, a grafted brace on its outer side.
 */
export function drawHangar(p: EnemyParts, at: Vec3): void {
  const s = Math.sign(at[0]) || 1;
  p.flesh.bevelSlab(
    sided(HANGAR, s),
    [-6, -1, HANGAR_TOP - 3],
    [2, 4],
    F.crimson,
    { at },
    F.purple,
  );
  organ(p.flesh, 16, 8, F.purple, { at: shift(at, [0, -1, -1]), yaw: Math.PI / 8 }, 0.32);
  const hatch = shift(at, [s * 2, HANGAR_TOP, -2]);
  p.charge.slab(SLIT, [HANGAR_TOP - 1.2, HANGAR_TOP - 0.4], WHITE, { at: hatch });
  for (const dx of [-1, 1]) {
    tentacle(
      p,
      shift(hatch, [dx * 8, -0.6, -13]),
      shift(hatch, [dx * 8, -0.6, 13]),
      [dx * 1.5, 1.5, 0],
      [1.8, 1.8],
      F.sinew,
      4,
    );
    for (let k = 0; k < 4; k++) {
      p.vein.box([1.6, 0.8, 2.4], N, { at: shift(hatch, [dx * 11.5, -2.4, -10.5 + k * 7]) });
    }
  }
  const [x, , z] = hatch;
  const front: OutlinePoint[] = [
    [x - 8, z + 16],
    [x + 8, z + 16],
  ];
  edgeStrips(p.neon, front, 1.4, [HANGAR_TOP - 2.4, HANGAR_TOP - 1.6], N);
  graft(
    p,
    polygon(4, 6, [0.7, 2.2]),
    [HANGAR_TOP - 3.5, HANGAR_TOP - 2.2],
    shift(at, [s * 16, 0, -2]),
    {
      color: M.base,
    },
  );
  veinLine(p, shift(at, [-s * 18, 2, 4]), shift(at, [-s * 34, -1, 10]), [0, 2, 0], 1.1, N);
  barbs(p, shift(at, [s * 15, 4, -14]), { count: 2, spacing: 6, size: 3, dir: [s, 0.3, -0.5] });
}

/**
 * A flak growth on the front of the mantle (P16-R06): a swollen, plated mound under its turret,
 * a feeding sac behind it.
 */
export function drawFlak(p: EnemyParts, at: Vec3): void {
  growth(p, shift(at, [0, DECK_TOP - 2.5, 0]), 12, N, { flesh: F.crimson, height: 0.38 });
  sac(p, shift(at, [Math.sign(at[0]) * 7, DECK_TOP, -9]), 3.5, F.purple, { stretch: 0.6 });
}
