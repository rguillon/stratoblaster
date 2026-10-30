import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import {
  SALAMANDER_FIN_GUNS,
  SALAMANDER_STINGER,
  SALAMANDER_TAIL,
} from '../../../config/bosses/world-4/magma-salamander';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { POD_SECTION } from '../../enemies/enemy-shapes';
import { bossPoint, type LimbDrawing } from '../boss-model';
import { sided } from '../final-boss-shapes';
import { seam } from '../mini-boss-greebles';
import { H, offset, QUARTER, WHITE } from '../mini-boss-shapes';
import { segment } from '../world-3/toucan-jungle';
import { glands, SKIN } from './living-forge';

// P10-R11, 4-3: the Magma Salamander's parts (its back fins and its tail) and its molten look.
// Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Salamander's orange-yellow neon. */
export const SALAMANDER_NEON: Rgb = BOSS_LOOK.neon['magma-salamander'] ?? [1, 0.62, 0.08];
/** The molten glow between its plates (World 4: magma seams), hotter and redder than its neon. */
export const MOLTEN: Rgb = [1, 0.36, 0.04];
/** Soot-blackened, heat-blued metal on its plates (World 4: heavy industry). */
export const SCORCH: Rgb = [0.05, 0.045, 0.05];

/**
 * A gun barrel along +Z ending at `tip`, `radius` thick and `length` long: dark steel, a charge
 * light at its mouth, the muzzle marked there (`fires`: what it fires).
 */
export function barrel(
  p: EnemyParts,
  tip: Vec3,
  [radius, length]: [number, number],
  fires = 'gun',
) {
  const [x, y, z] = tip;
  p.hull.cylinder(radius, length, 6, H.dark, { at: [x, y, z - length - 0.6], pitch: QUARTER });
  p.charge.cylinder(radius * 1.05, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
  p.muzzle(tip, fires);
}

/**
 * A molten seam between two armour plates: a glowing band `width` across at height `y`, at
 * `z`, sunk a little under the plates around it.
 */
export function moltenSeam(neon: SolidBuilder, [width, y, z]: readonly [number, number, number]) {
  neon.box([width, 0.6, 1.4], MOLTEN, { at: [0, y, z] });
}

/** The left fin seen from above (model +X), from its root's leading edge out and back. */
const FIN: OutlinePoint[] = [
  [20, 8],
  [33, 10],
  [46, 6],
  [53, 0],
  [49, -4],
  [52, -10],
  [44, -12],
  [46, -18],
  [34, -16],
  [22, -12],
];
/** The fin's spines, root to tip (left fin): each lit along its ridge. */
const SPINES: readonly (readonly [OutlinePoint, OutlinePoint])[] = [
  [
    [22, 6],
    [52, 0],
  ],
  [
    [22, -2],
    [50, -9],
  ],
  [
    [22, -9],
    [45, -17],
  ],
];
/** Height of the fin: a thick, heat-scarred frill over its gun pod. */
const FIN_Y = 6;
/** The gun pod under the fin's leading edge (loft stations around the part's centre). */
const POD = [
  [-6, 3, -2, 2],
  [0, 4.4, -2.5, 3],
  [7, 3.8, -2, 2.6],
  [11, 2.4, -1, 1.6],
] as const;

/**
 * A back fin around its centre `at` (P10-R11): a spiny frill of soot-black armour, its spines
 * lit orange, a molten glow at its root, and under its leading edge a pod with two fan barrels.
 */
export function fin(p: EnemyParts, at: Vec3): void {
  const { hull, neon, flesh } = p;
  const s = Math.sign(at[0]);
  // P16-R05: a membrane frill on bone spines, a gland at its root.
  flesh.bevelSlab(
    sided(FIN, s),
    [FIN_Y - 1.4, FIN_Y, FIN_Y + 1.2],
    [0.4, 0.6],
    SKIN.dark,
    {},
    SKIN.base,
  );
  glands(p, [[s * 22, FIN_Y + 0.8, 4]], 1.5, MOLTEN);
  for (const [[ax, az], [bx, bz]] of SPINES) {
    seam(flesh, [s * ax, az], [s * bx, bz], [FIN_Y + 1.1, 1.4, 0.8], SKIN.bone);
    seam(neon, [s * ax, az], [s * bx, bz], [FIN_Y + 1.8, 0.45, 0.3], SALAMANDER_NEON);
  }
  neon.box([3, 0.8, 18], MOLTEN, { at: [s * 20, FIN_Y + 0.6, -2] });
  hull.loft(POD_SECTION, POD, H.panel, { at: [at[0], 0, at[2]] });
  // The left fin (screen left) is on the model's +X side.
  const guns = s > 0 ? SALAMANDER_FIN_GUNS : mirror(SALAMANDER_FIN_GUNS);
  for (const tip of guns.map((m) => bossPoint(...m))) barrel(p, tip, [0.9, 5]);
}

/** The model-space points of the tail at rest: its root, its knuckle, its stinger's tip. */
export function tailPoints(): [root: Vec3, knuckle: Vec3, tip: Vec3] {
  const [rx, ry] = SALAMANDER_TAIL.root;
  const [kx, ky] = SALAMANDER_TAIL.knuckle;
  const [tip] = SALAMANDER_STINGER.map((m) => bossPoint(...m));
  return [bossPoint(rx, ry, 4), bossPoint(kx, ky, 4), tip ?? bossPoint(kx, ky, 4)];
}

/** A point `t` of the way from `a` to `b`. */
const lerp = (a: Vec3, b: Vec3, t: number): Vec3 => [
  a[0] + (b[0] - a[0]) * t,
  a[1] + (b[1] - a[1]) * t,
  a[2] + (b[2] - a[2]) * t,
];

/**
 * The tail's root, on its root joint (D-061): two armoured rings tapering to the knuckle, a
 * molten glow between them, a spine of neon studs along its back.
 */
function tailRoot({ hull, neon, flesh }: EnemyParts): void {
  const [root, knuckle] = tailPoints();
  segment(flesh, [offset(root, 0, -3, 0), offset(knuckle, 0, -2, 0)], [6.4, 4.8], SKIN.base, 6);
  for (const [a, b, r] of [
    [0, 0.45, 7],
    [0.52, 0.95, 5.8],
  ] as const) {
    segment(flesh, [lerp(root, knuckle, a), lerp(root, knuckle, b)], [r, r * 0.9], SKIN.panel, 6);
  }
  for (const t of [0.2, 0.7])
    neon.box([1.2, 1, 1.2], SALAMANDER_NEON, { at: offset(lerp(root, knuckle, t), 0, 5.6, 0) });
  hull.cylinder(5.4, 3, 7, H.panel, { at: offset(knuckle, 0, -2, 0) });
}

/** The limbs on its tail's joints: the root segment (the tip is the tail part itself). */
export function tailLimbs(): Record<string, LimbDrawing> {
  return { 'tail-root': { draw: tailRoot } };
}

/** The stinger's bulb at the tail's tip (a lathe profile around its axis, +Y). */
const BULB = [
  [0, -5],
  [4.4, -3.4],
  [5.2, 0],
  [4, 3.6],
  [0, 5],
] as const;

/**
 * The tail's tip around its centre (P10-R11), on its knuckle joint: a tapering, plated segment,
 * a glowing bulb of magma at its end and the stinger barrel on top of it, pointing forward,
 * that sweeps its lines of bullets across the screen.
 */
export function tail(p: EnemyParts): void {
  const { hull, neon, charge, flesh } = p;
  const [, knuckle, tip] = tailPoints();
  const bulb: Vec3 = [tip[0], 3, tip[2] - 4];
  segment(flesh, [knuckle, bulb], [4.8, 3.6], SKIN.base, 6);
  segment(flesh, [lerp(knuckle, bulb, 0.15), lerp(knuckle, bulb, 0.55)], [5.4, 4.6], SKIN.panel, 6);
  neon.box([5, 0.6, 1.2], MOLTEN, {
    at: offset(lerp(knuckle, bulb, 0.6), 0, 4, 0),
    yaw: Math.atan2(bulb[0] - knuckle[0], bulb[2] - knuckle[2]),
  });
  flesh.lathe(BULB, 7, SKIN.dark, { at: bulb, pitch: QUARTER });
  charge.ring(5.3, 1, 7, WHITE, { at: offset(bulb, 0, 0, -0.5), pitch: QUARTER });
  hull.box([3.4, tip[1] - bulb[1] - 1, 5], H.panel, { at: offset(bulb, 0, 1, 2) });
  barrel(p, tip, [1.2, 5]);
  neon.ring(1.7, 0.7, 6, SALAMANDER_NEON, { at: offset(tip, 0, 0, -4.4), pitch: QUARTER });
}
