import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  VERDANT_CROWN,
  VERDANT_GUNS,
  VERDANT_HATCHES,
  VERDANT_LENS,
} from '../../../config/bosses/world-3/verdant-crown';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, flipX, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { edgeLights, symmetric } from '../overlord-city';
import { drawCity } from './verdant-crown-city';
import { reactorSac } from '../../enemies/organic-parts';
import { F, JUNGLE_FLESH, veinTo } from './jungle-flesh';
import { DECK_TOP, drawGarden, EMERALD, JUNGLE, MAGENTA } from './verdant-crown-garden';
import {
  OUTRIGGER_TOP,
  rect,
  rootGenerator,
  seedBattery,
  thornCannon,
  thornMount,
} from './verdant-crown-parts';

// P09-R09, 3-5: the Verdant Crown, World 3's last boss. Model space: logical pixels, nose +Z
// (down the screen), Y up towards the camera; +X is the screen's left. A city-ship: an overgrown
// deck carrying a glass garden dome over the core, a gun deck on its bow, outriggers out to the
// thorn cannons.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

const H = ENEMY_LOOK.hull;
const WHITE: Rgb = [1, 1, 1];
const QUARTER = Math.PI / 2;

/** The deck (right half, front to tail), closed across the bow. */
const DECK = symmetric(
  [
    [18, 88],
    [40, 72],
    [58, 44],
    [64, 0],
    [60, -40],
    [46, -70],
    [24, -88],
  ],
  92,
);
/** The right outrigger (mirrored on the left), out to the thorn cannon's turntable. */
const OUTRIGGER: OutlinePoint[] = [
  [56, 30],
  [94, 20],
  [102, 12],
  [102, -2],
  [94, -10],
  [56, -18],
];
/** The engine block across the stern. */
const ENGINES = rect(64, 12, [0, -88]);
/** The gun deck on the bow, and its top. */
const BOW = rect(26, 18, [0, 76]);
const BOW_TOP = 7;
/** The block the core's missile hatches open in, behind the dome. */
const HATCH_BLOCK = rect(26, 18, [0, -52]);
const LENS = [
  [0, 0],
  [3.4, 1],
  [2.2, 3],
  [0, 3.6],
] as const;

/** The deck with its lit rim, the engine block, the outriggers wrapped in vines. */
function drawHull(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R06: a colossal living plant-beast: its back a broad body of moss-skinned flesh, the
  // city grafted on it, its outriggers fleshy limbs, veins pulsing out from under the dome.
  flesh.bevelSlab(DECK, [-8, -2, DECK_TOP], [3, 3], F.sinew, {}, JUNGLE_FLESH);
  for (const a of [0.5, 1.6, 2.6, 3.7, 4.7, 5.8]) {
    const out: Vec3 = [Math.sin(a) * 74, DECK_TOP + 0.3, Math.cos(a) * 74];
    veinTo(p, [[Math.sin(a) * 34, DECK_TOP + 0.3, Math.cos(a) * 34], out], [0, 0, 6], EMERALD, 1.6);
  }
  edgeLights(
    neon,
    DECK,
    DECK.map((_, i) => i),
    [-2.6, -1.4],
    EMERALD,
  );
  hull.bevelSlab(ENGINES, [-7, -1, 5], [1, 1.5], H.dark, {}, H.base);
  for (const s of SIDES) {
    const wing = s > 0 ? OUTRIGGER : flipX(OUTRIGGER);
    flesh.bevelSlab(wing, [-4, -1, OUTRIGGER_TOP], [1, 2], F.sinew, {}, JUNGLE.moss);
    edgeLights(neon, wing, [0, 1, 2, 3, 4], [-1.5, -0.5], MAGENTA);
    for (const dz of [-6, 0, 6]) {
      hull.box([0.9, 0.5, 26], JUNGLE.leaf, {
        at: [s * 70, OUTRIGGER_TOP, 6 + dz],
        yaw: dz * 0.03,
      });
    }
  }
}

/** The gun deck on the bow: twin cannons and a laser lens, charging before they fire. */
function drawBow({ hull, neon, charge, muzzle }: EnemyParts): void {
  hull.bevelSlab(BOW, [DECK_TOP - 1, DECK_TOP, BOW_TOP], [0, 1], H.panel, {}, JUNGLE.stone);
  decal(neon, rect(18, 1.2, [0, 70]), BOW_TOP + 0.05, MAGENTA);
  const front = 84;
  for (const m of VERDANT_GUNS) {
    const tip = bossPoint(...m);
    const along = (z: number): Placement => ({ at: [tip[0], tip[1], z], pitch: QUARTER });
    hull.cylinder(1.8, tip[2] - 2 - (front - 12), 6, H.dark, along(front - 12), 1.5);
    charge.cylinder(1.7, 2, 6, WHITE, along(tip[2] - 2), 1.2);
    muzzle(tip);
  }
  const lens = bossPoint(...VERDANT_LENS);
  const lensAt = lens[2] - LENS[3][1];
  const along = (z: number): Placement => ({ at: [0, lens[1], z], pitch: QUARTER });
  hull.cylinder(4, lensAt - (front - 14), 8, JUNGLE.stone, along(front - 14));
  charge.lathe(LENS, 6, WHITE, along(lensAt));
  muzzle(lens, 'laser');
}

/** The missile hatches in their block behind the dome, lit as missiles load. */
function drawHatches({ hull, neon, charge, muzzle }: EnemyParts): void {
  const height = VERDANT_HATCHES[0]?.[2] ?? 9;
  hull.bevelSlab(HATCH_BLOCK, [DECK_TOP - 1, DECK_TOP, height - 0.08], [0, 1.5], H.base);
  for (const m of VERDANT_HATCHES) {
    const [x, y, z] = bossPoint(...m);
    decal(hull, rect(7, 5.4, [x, z]), y - 0.06, H.dark);
    decal(charge, rect(5, 3.6, [x, z]), y, WHITE);
    muzzle([x, y, z], 'missile');
  }
  neon.box([20, 0.8, 0.6], EMERALD, { at: [0, DECK_TOP + 1, -42.8] });
}

/**
 * P09-R09: the Verdant Crown, a city-ship (6 L) under emerald and magenta neon: an overgrown
 * city round a glass garden dome over its core, two thorn cannons on its outriggers, two seed
 * batteries aft, two root generators ahead, and a bow carrying twin cannons and a laser.
 */
export function buildVerdantCrown(scene: Scene): EnemyModel {
  return buildBossModel(VERDANT_CROWN, scene, EMERALD, {
    core: (p) => {
      drawHull(p);
      drawGarden(p);
      drawCity(p);
      drawBow(p);
      drawHatches(p);
      for (const s of SIDES) {
        reactorSac(p, [s * 12, -1, -94], 5.5, EMERALD, { flesh: F.sinew, veinLength: 8 });
        reactorSac(p, [s * 26, -1, -94], 4.2, EMERALD, { flesh: F.sinew, veinLength: 8 });
      }
    },
    parts: {
      'thorn-left': thornMount,
      'thorn-right': thornMount,
      'seed-left': seedBattery,
      'seed-right': seedBattery,
      'root-left': rootGenerator,
      'root-right': rootGenerator,
    },
    turrets: { 'thorn-left': thornCannon, 'thorn-right': thornCannon },
  });
}
