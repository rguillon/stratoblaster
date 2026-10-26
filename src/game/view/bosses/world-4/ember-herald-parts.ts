import type { Muzzle } from '../../../../core/entities/muzzle';
import { createRng } from '../../../../core/math/rng';
import type { Placement, SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint } from '../boss-limbs';
import { H, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';

// P10-R11, 4-5: the Ember Herald's colours, its ember lances (the parts on its turning ring),
// the spikes on its hull and the embers drifting round it. Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** Gold: the Ember Herald's registered neon (GD-61). */
export const GOLD: Rgb = BOSS_LOOK.neon['ember-herald'] ?? WHITE;
/** World 4 heat (P10-R11): molten seams, glowing embers, soot-black and heat-blued metal. */
export const HEAT = {
  molten: [1, 0.38, 0.05] as Rgb,
  ember: [1, 0.6, 0.14] as Rgb,
  soot: SHADE.soot,
  blued: [0.1, 0.09, 0.13] as Rgb,
};

/** A lance's shaft along its axis (lathe profile: radius, distance from its inner end). */
const SHAFT = [
  [3, 0],
  [4.4, 2],
  [4.4, 6],
  [2.8, 8],
  [2.6, 21],
  [3.6, 23],
] as const;
/** Its glowing blade, from the end of the shaft out to the charge light at its tip. */
const BLADE = [
  [3.6, 23],
  [5, 26.5],
  [0, 35],
] as const;
const LANCE_LENGTH = BLADE[BLADE.length - 1]?.[1] ?? 0;
/** The lance's charge light at its tip (lathe profile), where its spiral leaves from. */
const LANCE_TIP = [
  [1.4, 0],
  [0, 2],
] as const;
/** How far the lance's barbs stand along it, and their length. */
const BARBS = [
  [25, 7],
  [13, 5],
] as const;
/** A spike (lathe profile, in units of its radius and length). */
const SPIKE = [
  [1, 0],
  [0.45, 0.55],
  [0, 1],
] as const;

/**
 * A spike of `[radius, length]` growing from `at`, tilted by `[pitch, roll, yaw]` from straight
 * up: soot-black metal, a molten glow at its root.
 */
export function spike(
  { hull, neon }: EnemyParts,
  at: Vec3,
  [pitch, roll, yaw]: readonly [number, number, number],
  [radius, length]: readonly [number, number],
): void {
  const place: Placement = { at, pitch, roll, yaw };
  hull.lathe(
    SPIKE.map(([r, y]) => [r * radius, y * length] as const),
    4,
    HEAT.soot,
    place,
  );
  neon.ring(radius * 1.05, length * 0.1, 4, HEAT.molten, place);
}

/**
 * P10-R11: an ember lance on the turning ring, pointing out of it to its `muzzles`' tip (from the
 * design): a soot-black shaft with molten bands and a gold collar, a glowing gold blade, two pairs
 * of barbs, a clamp holding it to the ring, and a charge light at its tip where its spirals leave.
 */
export function emberLance(p: EnemyParts, muzzles: readonly Muzzle[], at: Vec3): void {
  const [m] = muzzles;
  if (!m) return;
  const tip = bossPoint(...m);
  const reach = Math.hypot(tip[0], tip[2]);
  const yaw = Math.atan2(tip[0], tip[2]);
  // A point `r` px in from the tip along the lance, `up` above its axis.
  const out = (r: number, up = 0): Vec3 => [
    Math.sin(yaw) * (reach - r),
    tip[1] + up,
    Math.cos(yaw) * (reach - r),
  ];
  const axis = (r: number): Placement => ({ at: out(r), pitch: QUARTER, yaw });
  const inner = LANCE_LENGTH + LANCE_TIP[1][1];
  p.hull.lathe(SHAFT, 6, H.dark, axis(inner));
  p.neon.lathe(BLADE, 6, GOLD, axis(inner), false);
  p.charge.lathe(LANCE_TIP, 6, WHITE, axis(LANCE_TIP[1][1]));
  p.muzzle(tip);
  p.neon.ring(4.5, 1.8, 6, GOLD, axis(inner - 3));
  for (const r of [inner - 10, inner - 16]) p.neon.ring(2.75, 1.2, 6, HEAT.molten, axis(r));
  for (const [along, size] of BARBS) {
    for (const s of [-1, 1]) {
      const root = out(inner - along);
      spike(p, root, [QUARTER - 0.3, 0, yaw + Math.PI + s * 0.7], [1.5, size]);
    }
  }
  const clamp = out(reach - Math.hypot(at[0], at[2]), -4.5);
  p.hull.box([6, 3, 5], SHADE.edge, { at: clamp, yaw }, H.panel);
}

/** The embers wreathing it: how many, how far out, and how high they drift. */
const EMBERS = { count: 26, inner: 18, outer: 62, low: 4, high: 26, size: [0.7, 1.5] } as const;

/** The embers' colours, in turn. */
const EMBER_COLOURS = [GOLD, HEAT.ember, HEAT.molten] as const;

/**
 * The embers wreathing the Ember Herald (P10-R11): small glowing motes scattered round the hull
 * and up past its ring, some molten orange, some bright gold, the same every time.
 */
export function embers(neon: SolidBuilder): void {
  const random = createRng(4_505);
  const { count, inner, outer, low, high, size } = EMBERS;
  for (let i = 0; i < count; i++) {
    const a = random() * Math.PI * 2;
    const r = inner + (outer - inner) * Math.sqrt(random());
    const s = size[0] + (size[1] - size[0]) * random();
    const at: Vec3 = [Math.sin(a) * r, low + (high - low) * random(), Math.cos(a) * r];
    neon.box([s, s, s], EMBER_COLOURS[i % EMBER_COLOURS.length] ?? GOLD, {
      at,
      yaw: a,
      pitch: 0.6,
    });
  }
}
