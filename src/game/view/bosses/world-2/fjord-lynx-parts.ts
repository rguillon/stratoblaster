import type { OutlinePoint } from '../../../../render/geometry/outline';
import { BOSS_LOOK } from '../../../config/boss-look';
import { FJORD_LYNX } from '../../../config/bosses/world-2/fjord-lynx';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { hazard } from '../mini-boss-greebles';
import { GEAR } from '../mini-boss-mechanism';
import { crystals, gland, ICE_FLESH, sinew } from './w2-organic';
import { H, offset, SHADE, turret, WHITE } from '../mini-boss-shapes';
import { icicles, RIME, snowCap, spread } from './fjord-lynx-frost';

// P08-R10, 2-2: the Fjord Lynx's parts: its two paw cannons and its radar mast. Logical pixels,
// nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** The lynx's neon: cyan, and white for its secondary lights. */
export const CYAN = BOSS_LOOK.neon['fjord-lynx'] ?? [0.55, 0.95, 1];
export const WHITE_NEON = [0.9, 0.95, 1] as const;

/** A paw seen from above, around its centre: a broad pad, wider at the toes. */
const PAD = [
  [0, 12],
  [7, 10],
  [10, 3],
  [9, -6],
  [5, -10],
  [-5, -10],
  [-9, -6],
  [-10, 3],
  [-7, 10],
] as const;
/** One toe claw, its root on the pad's front edge, pointing to the nose. */
const CLAW = [
  [-1.6, 0],
  [1.6, 0],
  [0.4, 5],
  [-0.4, 5.4],
] as const;
/** Height of the pad's top, where the paw cannon's turret stands. */
export const PAD_TOP = 3.5;
/** The radar mast's mount (an octagon, around the part's centre). */
const MOUNT = Array.from({ length: 8 }, (_, k): OutlinePoint => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a) * 7, Math.cos(a) * 7];
});
/** The radar mast's height, and the scanner bar's turn on it. */
const MAST_HEIGHT = 15;
const SCANNER_YAW = 0.45;

/** `outline` moved to `[x, z]`. */
const at2 = (outline: readonly OutlinePoint[], [x, , z]: Vec3): OutlinePoint[] =>
  outline.map(([px, pz]): OutlinePoint => [px + x, pz + z]);

/**
 * A paw (P08-R10): an armoured pad with three toe claws, frosted on top, its cannon on a turret
 * ({@link pawTurret}); a ram from the foreleg works it.
 */
export function paw(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon } = p;
  const s = Math.sign(at[0]) || 1;
  // P16-R05: a fleshy paw, bone claws, a metal armour plate where the cannon is grafted.
  flesh.bevelSlab(
    at2(PAD, at),
    [-2.5, 0, PAD_TOP - 1],
    [1.2, 1.6],
    ICE_FLESH.sinew,
    {},
    ICE_FLESH.rime,
  );
  hull.bevelSlab(
    at2(PAD.slice(2, 7), offset(at, 0, 0, 0)),
    [PAD_TOP - 1.2, PAD_TOP - 0.6, PAD_TOP],
    [0, 0.6],
    H.panel,
  );
  for (const dx of [-5, 0, 5]) {
    flesh.bevelSlab(CLAW, [-1.5, -0.5, 1.2], [0.2, 0.4], ICE_FLESH.bone, {
      at: offset(at, dx, 0, dx === 0 ? 11.5 : 9.5),
      yaw: -dx * 0.05,
    });
  }
  snowCap(flesh, at2(PAD.slice(3, 7), offset(at, 0, 0, -1)), PAD_TOP);
  neon.box([1, 0.5, 9], CYAN, { at: offset(at, s * 9, 1.4, -1), yaw: s * 0.15 });
  neon.box([5, 0.5, 0.8], WHITE_NEON, { at: offset(at, 0, PAD_TOP - 0.2, -9.6) });
  sinew(flesh, offset(at, -s * 8, 1.5, -12), offset(at, -s * 5, 2, -6), 1.4);
  gland(p, offset(at, s * 5, 1.5, -7), 0.9, CYAN);
  icicles(flesh, spread(offset(at, s * 9.5, 0, -6), offset(at, s * 9.5, 0, 3), 3), 3.5);
}

/** A paw's twin-barrelled cannon, on its turret. */
export function pawTurret(p: EnemyParts, at: Vec3): void {
  turret(p, offset(at, 0, PAD_TOP, 0), {
    radius: 8,
    barrels: 2,
    gap: 3.6,
    bore: 1.2,
    length: 6,
    neon: CYAN,
    hatch: -Math.sign(at[0]),
  });
}

/** The chin cannon (the core's gun), turning on the deck in front of the head. */
export function chinTurret(p: EnemyParts, at: Vec3): void {
  turret(p, offset(at, 0, 5, 0), {
    radius: 6,
    barrels: 1,
    gap: 0,
    bore: 1.4,
    length: 6,
    neon: CYAN,
  });
}

/**
 * The radar mast (P08-R10): a mount on the sponson, a tapered mast, a scanner bar with a dish
 * and white lights at its ends; while it stands, the guns aim at the player.
 */
export function radarMast(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge } = p;
  // P16-R05: a metal mast grafted in a swollen mound of flesh, crystals around it.
  p.flesh.bevelSlab(at2(MOUNT, at), [-1, 0, 2.5], [0.5, 1], ICE_FLESH.purple, {}, ICE_FLESH.rime);
  crystals(p.flesh, offset(at, 4, 2, 3), 3);
  hazard(hull, offset(at, 0, 2.5, -5), [6, 1.6], 4, 0);
  hull.cylinder(2, MAST_HEIGHT, 4, H.panel, { at: offset(at, 0, 2.5, 0), yaw: 0.3 }, 0.9);
  for (const h of [6, 10]) {
    hull.cylinder(2.2 - h * 0.08, 0.8, 6, GEAR, { at: offset(at, 0, 2.5 + h, 0) });
  }
  const top = offset(at, 0, 2.5 + MAST_HEIGHT, 0);
  hull.box([14, 1.4, 2.4], H.base, { at: top, yaw: SCANNER_YAW }, RIME);
  hull.lathe(
    [
      [0.4, 0],
      [4.5, 1.6],
      [3.8, 2.2],
      [0, 0.8],
    ],
    8,
    SHADE.edge,
    { at: offset(top, 0, 1.4, 0), pitch: -0.6, yaw: SCANNER_YAW },
  );
  for (const k of [-1, 1]) {
    const end = offset(top, k * 6.6 * Math.cos(SCANNER_YAW), 0.6, -k * 6.6 * Math.sin(SCANNER_YAW));
    neon.box([1.2, 1, 1.2], WHITE_NEON, { at: end });
  }
  charge.box([1.6, 1.6, 1.6], WHITE, { at: offset(top, 0, 4, 0) });
  neon.ring(7.2, 0.6, 8, CYAN, { at: offset(at, 0, 0.6, 0), yaw: Math.PI / 8 });
  icicles(hull, spread(offset(top, -5, 0, 2), offset(top, 5, 0, -2), 4), 3);
}

/** The left paw's centre in model space (for the forelegs drawn on the core). */
export function pawCentre(side: number): Vec3 {
  const spec = FJORD_LYNX.stats.parts[0];
  return [side * -(spec?.x ?? -30), 0, -(spec?.y ?? -26)];
}
