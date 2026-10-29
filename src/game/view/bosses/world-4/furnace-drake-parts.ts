import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { DRAKE_MAW, DRAKE_WING_GUNS } from '../../../config/bosses/world-4/furnace-drake';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { FIGHTER_SECTION, POD_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { rod } from '../final-boss-greebles';
import { sided } from '../final-boss-shapes';
import { lamps, seam } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { FL, glands, SKIN } from './living-forge';

// P10-R11, 4-4: the Furnace Drake's parts (its beating wings and its jaw) and its forge colours.
// Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Drake's red neon, and the orange of its molten seams and flame (World 4: heat glow). */
export const DRAKE_RED: Rgb = BOSS_LOOK.neon['furnace-drake'] ?? [1, 0.22, 0.05];
export const DRAKE_ORANGE: Rgb = [1, 0.55, 0.08];
/** Soot-blackened plates, and the dark, heat-stained hide of its wing membranes. */
export const SOOT: Rgb = SHADE.soot;
export const HIDE: Rgb = [0.08, 0.035, 0.03];

/** A fin or spike standing on `at`: a three-sided cone `height` tall, leaning back by `lean`. */
export function spike(
  builder: SolidBuilder,
  at: Vec3,
  [radius, height]: readonly [number, number],
  color: Rgb = H.dark,
  lean = 0,
): void {
  const profile = [
    [radius, 0],
    [0, height],
  ] as const;
  builder.lathe(profile, 3, color, { at, pitch: -lean });
}

/** The left wing seen from above (model +X), from its root's leading edge out and back. */
const WING: OutlinePoint[] = [
  [12, 8],
  [30, 15],
  [48, 12],
  [59, 2],
  [52, -7],
  [45, -3],
  [39, -15],
  [31, -9],
  [23, -19],
  [15, -11],
  [12, -6],
];
/** The wing's bones: from the shoulder out along the leading edge, and the fingers to each scallop. */
const BONES: readonly (readonly [Vec3, Vec3])[] = [
  [
    [12, 5, 6],
    [30, 5.6, 14],
  ],
  [
    [30, 5.6, 14],
    [48, 5, 11],
  ],
  [
    [48, 5, 11],
    [59, 4.6, 2],
  ],
  [
    [30, 5.6, 14],
    [52, 4.6, -7],
  ],
  [
    [30, 5.6, 14],
    [39, 4.6, -15],
  ],
  [
    [24, 5.4, 11],
    [23, 4.6, -19],
  ],
];
/** Height of the membrane, stretched between the bones. */
const WING_Y = 4;
/** A wing's gun pod under the membrane (loft stations around the pod's centre). */
const NACELLE = [
  [-9, 2.4, -2, 2],
  [-3, 4, -2.5, 3.2],
  [5, 3.8, -2, 3],
  [8, 2.8, -1, 2.4],
] as const;

/** The membrane and its bones, lit along their length by molten seams. */
function membrane({ flesh: hull, neon }: EnemyParts, s: number): void {
  // P16-R05: a membrane stretched on bone, veined molten.
  hull.bevelSlab(sided(WING, s), [WING_Y - 0.4, WING_Y, WING_Y + 0.5], [0.3, 0.3], FL.membrane);
  BONES.forEach(([a, b], i) => {
    const side = (v: Vec3): Vec3 => [s * v[0], v[1], v[2]];
    rod(hull, side(a), side(b), i < 3 ? 1.1 : 0.7, SKIN.bone);
    seam(neon, [s * a[0], a[2]], [s * b[0], b[2]], [a[1] + 0.6, 0.45, 0.25], DRAKE_ORANGE);
  });
  // A claw at the wing's thumb, and soot along its trailing edge.
  spike(hull, [s * 30, 5.6, 14], [1.4, 5], SKIN.bone, -0.9);
  seam(hull, [s * 15, -10], [s * 38, -14], [WING_Y + 0.5, 1.6, 0.3], HIDE);
}

/**
 * A wing around its pod's centre `at` (P10-R11), drawn on its beating joint: a scalloped hide
 * membrane on heavy bones, molten seams along them, and under it the gun pod with its two fan
 * barrels.
 */
export function wing(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = Math.sign(at[0]);
  membrane(p, s);
  hull.loft(POD_SECTION, NACELLE, H.base, { at: [at[0], -1, at[2]] });
  neon.box([0.5, 0.6, 9], DRAKE_RED, { at: [at[0] + s * 3.9, 0.6, at[2]] });
  // The left wing (screen left) is on the model's +X side.
  const guns = s > 0 ? DRAKE_WING_GUNS : mirror(DRAKE_WING_GUNS);
  for (const tip of guns.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.cylinder(1, 6.4, 6, H.dark, { at: [x, y, z - 7], pitch: QUARTER });
    charge.cylinder(1.05, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/** The neck, shoulders to skull (loft stations, model space). */
const NECK = [
  [15, 6.5, -1, 7.5],
  [22, 5, -0.5, 6.8],
  [29, 5.2, 0, 7],
] as const;
/** The skull and its upper jaw, ending in a blunt snout over the maw. */
const SKULL = [
  [27, 7, 1, 8.5],
  [35, 8, 2, 9],
  [43, 6.5, 4.6, 8],
  [50, 4.2, 4.6, 6.8],
  [55, 2.6, 4.6, 5.8],
] as const;
/** The left half of the lower jaw (model +X), hinged under the skull, open outwards. */
const LOWER_JAW: OutlinePoint[] = [
  [1, 34],
  [7, 34],
  [6.5, 46],
  [4.5, 55],
  [2.5, 55],
  [1, 44],
];

/** The skull: horns swept back, red eyes, the open lower jaw with its teeth. */
function skull(p: EnemyParts): void {
  const { flesh: hull, neon } = p;
  hull.loft(FIGHTER_SECTION, SKULL, SKIN.base);
  for (const s of SIDES) {
    rod(hull, [s * 4.5, 8.4, 33], [s * 7, 12.5, 27], 1.2, SKIN.bone);
    rod(hull, [s * 7, 12.5, 27], [s * 8, 13.4, 23.5], 0.6, SKIN.bone);
    lamps(neon, [[s * 4.6, 8.4, 41]], 1.6, DRAKE_RED);
    glands(p, [[s * 4.6, 8.6, 38]], 1, DRAKE_ORANGE);
    p.hull.bevelSlab(sided(LOWER_JAW, s), [0.4, 1.4, 2.8], [0.3, 0.3], H.panel);
    for (const z of [42, 47, 52]) spike(hull, [s * 4.5, 2.8, z], [0.6, 1.8], SKIN.bone);
  }
  seam(neon, [0, 30], [0, 48], [8.9, 0.5, 0.3], DRAKE_ORANGE);
}

/**
 * The drake's jaw around the head's centre `at` (P10-R11), on its swaying neck: the neck and
 * skull, the open maw glowing as the flame charges, and the flame nozzle in its throat.
 */
export function jaw(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  p.flesh.loft(POD_SECTION, NECK, SKIN.panel);
  for (const s of SIDES) seam(neon, [s * 5.2, 17], [s * 5, 28], [3.4, 0.4, 0.4], DRAKE_ORANGE);
  for (const z of [18, 24]) spike(p.flesh, [0, 7, z], [1.2, 3.4], SKIN.bone, 0.6);
  skull(p);
  const [tip] = DRAKE_MAW.map((m) => bossPoint(...m));
  if (!tip) return;
  const [x, y, z] = tip;
  charge.box([5, 1.2, 12], WHITE, { at: offset(at, 0, 1.6, 8) });
  hull.cylinder(1.3, 9, 6, H.dark, { at: [x, y, z - 9.6], pitch: QUARTER }, 1.1);
  charge.cylinder(1.15, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
  muzzle(tip);
}
