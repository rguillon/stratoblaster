import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import type { Placement } from '../../../../render/geometry/solids';
import { FJORD_LYNX } from '../../../config/bosses/world-2/fjord-lynx';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import {
  angryEyes,
  canopyPaint,
  decal,
  FIGHTER_SECTION,
  POD_SECTION,
  sideStripe,
  SIDES,
} from '../../enemies/enemy-shapes';
import { buildBossModel } from '../boss-model';
import { plate, seam, vent } from '../mini-boss-greebles';
import { ram } from '../mini-boss-mechanism';
import { H, offset, scaled, SHADE, socket } from '../mini-boss-shapes';
import { icicles, RIME, snowCap, spread } from './fjord-lynx-frost';
import {
  chinTurret,
  CYAN,
  paw,
  pawCentre,
  pawTurret,
  radarMast,
  WHITE_NEON,
} from './fjord-lynx-parts';

// P08-R10, 2-2: the Fjord Lynx. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** The low hull seen from above: a crouched body, broad at the shoulders, narrow at the haunches. */
const BODY = [
  [0, 46],
  [8, 42],
  [15, 30],
  [20, 14],
  [22, 0],
  [20, -18],
  [15, -34],
  [9, -46],
  [-9, -46],
  [-15, -34],
  [-20, -18],
  [-22, 0],
  [-20, 14],
  [-15, 30],
  [-8, 42],
] as const;
/** Heights of the hull: its belly, its rim, its deck. */
const HULL = [-3, 0, 5] as const;
/** The head and back along the centre line (loft stations: z, half width, bottom, top). */
const BACK = [
  [-44, 5, 4, 7.5],
  [-30, 9, 4, 10],
  [-6, 11, 4, 12],
  [10, 10, 4, 12.5],
  [20, 6, 4, 9],
  [24, 2, 4, 5.5],
] as const;
/** The right haunch's armour (mirrored on the left), raised over the rear of the hull. */
const HAUNCH = [
  [6, -16],
  [16, -12],
  [19, -22],
  [14, -38],
  [7, -40],
] as const;
/** The foreleg from the shoulder out to the paw (the right one; mirrored on the left). */
const FORELEG = [
  [14, 8],
  [20, 26],
  [27, 20],
  [21, 2],
] as const;
/** The sponson on the left flank carrying the radar mast (around the mast's centre). */
const SPONSON = [
  [-8, 10],
  [8, 7],
  [9, -7],
  [-8, -9],
] as const;
/** Snow packed on the rear deck, either side of the back. */
const REAR_SNOW = [
  [-12, -30],
  [12, -30],
  [9, -42],
  [-9, -42],
] as const;
/** The bobtail: a short stub behind the back (loft stations). */
const TAIL = [
  [-54, 0, 6, 6],
  [-50, 3, 3.5, 8],
  [-42, 4, 3, 8],
] as const;

/** The point `length` along the +Y axis of a solid placed by `place` (its tip). */
function tip(length: number, { at = [0, 0, 0], pitch = 0, roll = 0 }: Placement): Vec3 {
  const y1 = length * Math.cos(pitch);
  const z1 = length * Math.sin(pitch);
  return offset(at, -y1 * Math.sin(roll), y1 * Math.cos(roll), z1);
}

/** The hull, the back and head, the haunches and the forelegs out to the paws. */
function drawBody({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(BODY, HULL, [2, 2.5], H.base, {}, H.panel);
  hull.loft(FIGHTER_SECTION, BACK, H.base, {}, { paint: canopyPaint([3, 4], H.dark) });
  for (const side of [1, 6]) {
    const stripe = sideStripe(FIGHTER_SECTION, side, [0.3, 0.75]);
    neon.loft(stripe, BACK.slice(1, 5), CYAN, {}, { open: true });
  }
  neon.box([0.8, 0.5, 22], WHITE_NEON, { at: [0, 12.1, -18] });
  for (const s of SIDES) {
    const haunch = HAUNCH.map(([x, z]): [number, number] => [s * x, z]);
    hull.bevelSlab(haunch, [4, 5, 8], [0.5, 1.4], H.panel, {}, RIME);
    snowCap(hull, scaled(haunch, 0.7, s * 3.5, -8.5), 8);
    const leg = FORELEG.map(([x, z]): [number, number] => [s * x, z]);
    hull.bevelSlab(leg, [-2, 0, 3.5], [0.6, 1], H.panel, {}, RIME);
    ram(hull, [s * 16, 4, 8], offset(pawCentre(s), -s * 7, 2.5, -8), 1.1);
    neon.box([0.8, 0.5, 18], CYAN, { at: [s * 20.6, 0.4, -6], yaw: s * -0.05 });
  }
  hull.loft(POD_SECTION, TAIL, H.panel);
}

/** The tufted antennas: an ear on each side of the head, a whip with a light on its tip. */
function drawEars({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    const ear = { at: [s * 6, 10, 14] as Vec3, pitch: -0.25, roll: -s * 0.35 };
    hull.cylinder(3.4, 8, 3, H.panel, { ...ear, yaw: s * 0.5 }, 0);
    const top = tip(7, ear);
    const whip = { at: top, pitch: -0.55, roll: -s * 0.5 };
    hull.cylinder(0.4, 9, 4, H.dark, whip, 0.25);
    const end = tip(9, whip);
    neon.lathe(
      [
        [0, 0],
        [1, 1.2],
        [0, 3.4],
      ],
      4,
      WHITE_NEON,
      { ...whip, at: end },
    );
    neon.box([0.6, 0.4, 3], CYAN, { at: offset(ear.at, s * 1.2, 3.4, 0.6), roll: -s * 0.35 });
  }
}

/** Deck details: vents, seams, the sponson for the radar mast, frost and icicles, the eyes. */
function drawDeck({ hull, neon }: EnemyParts): void {
  const mast = FJORD_LYNX.stats.parts[2];
  const at: Vec3 = [-(mast?.x ?? -25), 0, -(mast?.y ?? 22)];
  const sponson = SPONSON.map(([x, z]): [number, number] => [x + at[0], z + at[2]]);
  hull.bevelSlab(sponson, [-2, 0, 2.5], [0.6, 1], H.base, {}, H.panel);
  socket(hull, offset(at, 0, 2.5, 0), 6, 0.6);
  for (const s of SIDES) {
    vent(hull, [s * 13, HULL[2] - 0.1, 20], [4, 8], 3, s * 0.3);
    seam(hull, [s * 6, 34], [s * 13, 26], [HULL[2], 0.6, 0.5], H.dark);
    icicles(hull, spread([s * 20.5, -0.5, 8], [s * 19, -0.5, -22], 5), 4);
    icicles(hull, spread([s * 13, -0.5, -38], [s * 5, -0.5, -45], 3), 3);
  }
  plate(hull, scaled(SPONSON, 0.5, at[0] + 1, at[2] - 1), [2.5, 0.4], SHADE.patch);
  snowCap(hull, REAR_SNOW, HULL[2]);
  for (const eye of angryEyes([0, 41.5], 2.4, [5, 1.2], 0.35)) decal(neon, eye, 5.05, CYAN);
}

/**
 * P08-R10: the Fjord Lynx, a fast, low gunship crouched like a lynx: two forward paws with
 * cannons, tufted antennas over its head, a radar mast on its left flank, white and cyan neon,
 * snow on its back.
 */
export function buildFjordLynx(scene: Scene): EnemyModel {
  return buildBossModel(FJORD_LYNX, scene, CYAN, {
    core: (p) => {
      drawBody(p);
      drawEars(p);
      drawDeck(p);
      for (const s of SIDES) p.reactor([s * 7, 2.5, -46], 3);
    },
    parts: { 'paw-left': paw, 'paw-right': paw, 'radar-mast': radarMast },
    turrets: { core: chinTurret, 'paw-left': pawTurret, 'paw-right': pawTurret },
  });
}
