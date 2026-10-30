import type { Muzzle } from '../../../../core/entities/muzzle';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint } from '../boss-limbs';
import { H, QUARTER, WHITE } from '../mini-boss-shapes';
import { organ } from '../../../../render/geometry/organic';
import { ICE_FLESH } from './w2-organic';

// P08-R10, 2-5: the Ice Queen's crystals: its shards (the parts on its crown ring), the crystals
// growing on its wings and ring, its icicles. Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** Pale blue: the Ice Queen's registered neon (GD-61). */
export const PALE_BLUE: Rgb = BOSS_LOOK.neon['ice-queen'] ?? WHITE;
/** Violet: the Ice Queen's second neon colour, on its edges (P08-R10). */
export const VIOLET: Rgb = [0.62, 0.3, 1];

/** World 2 frost (P08-R10): snow on top faces, pale faceted ice (the palest at the facets' tips),
 * frosted (snow-dusted) panels. */
export const FROST = {
  snow: [0.75, 0.82, 0.9] as Rgb,
  ice: [0.56, 0.7, 0.92] as Rgb,
  pale: [0.84, 0.92, 1] as Rgb,
  frosted: [0.36, 0.4, 0.47] as Rgb,
};

/** A crystal's faceted body (a lathe profile, in units of its radius and length). */
const CRYSTAL = [
  [0.6, 0],
  [1, 0.3],
  [0.8, 0.72],
] as const;
const CRYSTAL_TIP = [
  [0.8, 0.72],
  [0, 1],
] as const;

/**
 * A six-sided crystal growing from `at`, `radius` thick and `length` long, tilted by
 * `[pitch, roll, yaw]` from straight up: blue ice, its tip the palest.
 */
export function crystal(
  hull: SolidBuilder,
  at: Vec3,
  [pitch, roll, yaw]: readonly [number, number, number],
  [radius, length]: readonly [number, number],
): void {
  const place = { at, pitch, roll, yaw };
  const scale = ([r, y]: readonly [number, number]) => [r * radius, y * length] as const;
  hull.lathe(CRYSTAL.map(scale), 6, FROST.ice, place);
  hull.lathe(CRYSTAL_TIP.map(scale), 6, FROST.pale, place, false);
}

/** Icicles hanging under a wing on side `s`, at the `[x, z]` given (x for the right wing). */
export function icicles(
  hull: SolidBuilder,
  s: number,
  points: readonly (readonly [number, number])[],
): void {
  points.forEach(([x, z], i) => {
    const place = { at: [s * x, 0.2, z] as Vec3, pitch: Math.PI };
    hull.cylinder(0.7, 2.5 + (i % 3) * 1.2, 4, FROST.ice, place, 0);
  });
}

/** A shard's body along its axis (a lathe profile: radius, distance from its centre). */
const SHARD = [
  [0, -10.8],
  [2.6, -7],
  [4, -1.5],
  [3.6, 4],
  [2.4, 8.5],
  [0, 10.8],
] as const;
/** The pale crystal on its back, the charge light at each tip. */
const SHARD_RIDGE = [
  [0, -6],
  [1.7, 0],
  [0, 6],
] as const;
const SHARD_TIP = [
  [1.2, 0],
  [0, 2.2],
] as const;

/**
 * P08-R10: a crystal shard on the crown ring, lying along the ring between its two `muzzles`
 * (from the design, `height` high): faceted ice banded with violet neon, a light at each tip
 * where its bullets leave, a pale spike pointing out of the ring, a dark clamp under it.
 */
export function iceShard(p: EnemyParts, muzzles: readonly Muzzle[], height: number): void {
  const [a, b] = muzzles.map((m): Vec3 => bossPoint(...m));
  if (!a || !b) return;
  const centre: Vec3 = [(a[0] + b[0]) / 2, height, (a[2] + b[2]) / 2];
  const yaw = Math.atan2(b[0] - a[0], b[2] - a[2]);
  const axis = (along: number, up = 0, turn = yaw) => ({
    at: [
      centre[0] + Math.sin(yaw) * along,
      centre[1] + up,
      centre[2] + Math.cos(yaw) * along,
    ] as Vec3,
    pitch: QUARTER,
    yaw: turn,
  });
  p.hull.lathe(SHARD, 6, FROST.ice, axis(0));
  p.hull.lathe(SHARD_RIDGE, 4, FROST.pale, axis(0, 3.4));
  p.neon.ring(4.1, 0.9, 6, VIOLET, axis(-1.9));
  p.charge.lathe(SHARD_TIP, 4, WHITE, axis(10.8));
  p.charge.lathe(SHARD_TIP, 4, WHITE, axis(-10.8, 0, yaw + Math.PI));
  p.muzzle(a);
  p.muzzle(b);
  // P16-R05: each crystal is grown from a sac of flesh, held to the ring by a metal clamp.
  organ(p.flesh, 4.5, 6, ICE_FLESH.purple, { at: [centre[0], height - 5, centre[2]], yaw }, 0.5);
  p.hull.box([5, 1.2, 3], H.dark, { at: [centre[0], height - 5.2, centre[2]], yaw });
  const out = Math.atan2(centre[0], centre[2]);
  const spike: Vec3 = [
    centre[0] + Math.sin(out) * 2.5,
    height + 1.5,
    centre[2] + Math.cos(out) * 2.5,
  ];
  crystal(p.hull, spike, [1, 0, out], [1.5, 6.5]);
}
