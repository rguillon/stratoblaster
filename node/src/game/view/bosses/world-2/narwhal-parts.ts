import type { SectionPoint } from '../../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { POD_SECTION, sideStripe } from '../../enemies/enemy-shapes';
import { barrels, shift } from '../final-boss-shapes';
import { organ } from '../../../../render/geometry/organic';
import { crystals, ICE_FLESH, sinew } from './w2-organic';

// P08-R10, 2-1: the Narwhal's destroyable parts (its horn lance, torpedo tubes and ballast
// pods). Logical pixels, nose +Z, Y up; each drawn around its centre `at`.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;
/** Light metal: the horn's ridges and the tubes' rims. */
const EDGE = [0.24, 0.24, 0.27] as const;
/** The horn's darker bone bands. */
const BONE_DARK = [0.12, 0.11, 0.1] as const;

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/**
 * A submarine's round hull section (`SolidBuilder.loft`), counter-clockwise seen from the nose:
 * a rounded belly, full sides, shoulders and a flat back (side 4) where snow settles.
 */
export const SUB_SECTION: readonly SectionPoint[] = [
  [0.4, 0],
  [0.92, 0.2],
  [1, 0.5],
  [0.85, 0.8],
  [0.35, 1],
  [-0.35, 1],
  [-0.85, 0.8],
  [-1, 0.5],
  [-0.92, 0.2],
  [-0.4, 0],
];

/** The horn: segments from its root to its tip, each turned a little more (a spiral). */
const HORN = { root: 52, tip: 90, height: 4.5, radius: 4.2, segments: 7, twist: 0.55 } as const;

/**
 * The horn lance (P08-R10): a collar on the nose and a long spiral horn, a teal light winding
 * round it, its tip glowing as its laser charges.
 */
export function hornLance(
  { hull, flesh, neon, charge, muzzle }: EnemyParts,
  at: Vec3,
  n: Rgb,
): void {
  // P16-R06: a spiral horn of bone, a metal collar grafted where it leaves the head.
  const { root, tip, height, radius, segments, twist } = HORN;
  hull.cylinder(5.4, 5, 8, H.panel, { at: [at[0], height, root - 4], pitch: QUARTER }, 4.4);
  neon.ring(5.5, 0.8, 8, n, { at: [at[0], height, root - 2], pitch: QUARTER });
  const step = (tip - root - 3) / segments;
  for (let i = 0; i < segments; i++) {
    const [r0, r1] = [radius * (1 - i / segments), radius * (1 - (i + 1) / segments) + 0.3];
    const place = { at: [at[0], height, root + i * step] as Vec3, pitch: QUARTER, roll: i * twist };
    flesh.cylinder(r0, step, 5, i % 2 === 0 ? ICE_FLESH.bone : BONE_DARK, place, r1);
    // The light winding round the horn, a bead on each segment.
    const a = i * 1.3;
    const r = r0 * 0.9;
    neon.box([0.9, 0.9, step * 0.7], n, {
      at: [at[0] + Math.sin(a) * r, height + Math.cos(a) * r - 0.45, root + (i + 0.3) * step],
    });
  }
  const end = root + segments * step;
  charge.cylinder(0.6, tip - end, 5, WHITE, { at: [at[0], height, end], pitch: QUARTER }, 0);
  muzzle([at[0], height, tip], 'laser');
}

/** A torpedo tube's blister (loft stations around its centre: z, half width, bottom, top). */
const BLISTER = [
  [-14, 3.5, 1, 8],
  [-6, 6, 0, 10],
  [8, 6, 0, 10],
  [11, 5, 0.5, 9.5],
] as const;

/**
 * A torpedo tube (P08-R10): a blister on the hull's flank, two tube mouths at its front (their
 * torpedoes glowing as a salvo charges), a teal line along its outer side.
 */
export function torpedoTube(p: EnemyParts, at: Vec3, n: Rgb): void {
  const s = Math.sign(at[0]);
  // P16-R06: a swollen blister of flesh on the flank, metal tube mouths grafted at its front.
  p.flesh.loft(
    POD_SECTION,
    BLISTER,
    ICE_FLESH.purple,
    { at },
    { paint: (side) => (side === 2 ? ICE_FLESH.rime : undefined) },
  );
  organ(p.vein, 1, 5, n, { at: shift(at, [s * 4, 8, -6]) }, 0.6);
  const outer = s > 0 ? 0 : 4;
  p.neon.loft(
    sideStripe(POD_SECTION, outer, [0.3, 0.8], 1.06),
    BLISTER.slice(0, 3),
    n,
    { at },
    { open: true },
  );
  p.hull.box([11, 7, 0.6], EDGE, { at: shift(at, [0, 1.5, 11]) });
  barrels(p, shift(at, [0, 5, 11]), [2, 5], [1.8, 1.5], 'missile');
  crystals(p.flesh, shift(at, [s * 3, 9, -10]), 2.6, 2);
}

/** A ballast pod (loft stations around its centre: z, half width, bottom, top). */
const POD = [
  [-21, 3, 2, 8],
  [-14, 8, -2, 12],
  [10, 8, -2, 12],
  [18, 4.5, 1, 9],
] as const;

/**
 * A ballast pod (P08-R10): a long tank on its pylon, frost on its back, a teal ring round its
 * middle, two fan guns at its front and a flood vent on top.
 */
export function ballastPod(p: EnemyParts, at: Vec3, n: Rgb): void {
  const s = Math.sign(at[0]);
  // P16-R06: a ballast sac of flesh, held in metal bands, a gland on its back.
  p.flesh.loft(
    POD_SECTION,
    POD,
    ICE_FLESH.membrane,
    { at },
    { paint: (side, band) => (side === 2 && band !== 1 ? ICE_FLESH.rime : undefined) },
  );
  for (const z of [-6, 2]) {
    p.neon.ring(8.4, 0.8, 6, n, { at: shift(at, [0, 5, z]), pitch: QUARTER, roll: Math.PI / 6 });
  }
  p.hull.ring(8.6, 2, 6, H.panel, {
    at: shift(at, [0, 5, -13]),
    pitch: QUARTER,
    roll: Math.PI / 6,
  });
  organ(p.vein, 1.4, 5, n, { at: shift(at, [0, 11.4, -16]) }, 0.6);
  barrels(p, shift(at, [0, 6, 18]), [2, 5], [1.2, 4]);
  crystals(p.flesh, shift(at, [-s * 3, 11.6, 6]), 2.6);
  sinew(p.flesh, shift(at, [-s * 6, 6, -12]), shift(at, [-s * 14, 7, -14]), 1.4);
}
