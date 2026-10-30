import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { barrel, H, WHITE } from './elite-shapes';
import { around, radial } from './enemy-shapes';
import { reactorSac } from './organic-parts';
import { buildJointedModel } from './jointed-model';

// P05-R23, P16-R04: the Hive. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.hive;
const NEON = ELITE_NEON.hive;
const F = ENEMY_LOOK.flesh;

/** The rounded hull, a lathe profile from its belly up to its back under the ring. */
const DOME = [
  [20, -4.5],
  [30, -2],
  [32, 0.5],
  [30, 3.5],
  [24, 6.5],
  [16, 8.5],
  [0, 8.8],
] as const;
/** The honey-amber cells on the dome's shoulder: their distance out, height and tilt. */
const CELLS = { count: 10, radius: 26.8, y: 4.9, tilt: 0.46, size: 2.6 } as const;
/** An armour plate on the dome's back, out along +Z (turned round it). */
const ARMOUR = [
  [-4, 17],
  [4, 17],
  [5.5, 23],
  [-5.5, 23],
] as const;
/** The launch ring on its back (a lathe profile, closed), turning with the enemy's spin. */
const RING = [
  [12, 8.4],
  [16.5, 8.4],
  [16, 10.6],
  [12.5, 10.6],
  [12, 8.4],
] as const;

/** The swollen flesh dome, its glowing brood cells, the vents round its rim, reactor sacs. */
function body(p: EnemyParts): void {
  const { hull, flesh, vein } = p;
  // P16-R04: a living hive, metal only where grafted on (vents, ring, plates, nozzles).
  flesh.lathe(DOME, 12, F.sinew);
  // The brood cells: hexagons on the shoulder, tilted with it, pulsing.
  for (const a of around(CELLS.count)) {
    const place = { at: radial(a, CELLS.radius, CELLS.y), pitch: CELLS.tilt, yaw: a };
    vein.cylinder(CELLS.size, 0.6, 5, NEON, place);
  }
  // Armour plates between the cells and the ring.
  for (const a of around(3)) {
    hull.bevelSlab(ARMOUR, [8.4, 8.4, 9.4], [0, 0.8], H.panel, { yaw: a + Math.PI / 3 });
  }
  // The vents its rings of bullets leave from, pointing out.
  CFG.ringMuzzles.forEach((m, k) => {
    barrel(p, bossPoint(...m), (-2 * Math.PI * k) / CFG.ringCount, [1.2, 2.5], 'ring');
  });
  for (const x of [-9, 9]) reactorSac(p, [x, 0, -31], 2.4, NEON, { flesh: F.crimson });
}

/** The launch ring with its hatch, glowing as the next Wasp comes. */
function ring({ hull, neon, charge, muzzle }: EnemyParts): void {
  hull.lathe(RING, 12, H.panel, {}, false);
  for (const a of around(6)) {
    neon.box([1, 0.4, 3], NEON, { at: radial(a + Math.PI / 6, 14.2, 10.6), yaw: a + Math.PI / 6 });
  }
  const hatch = bossPoint(...CFG.port);
  hull.box([6, 2.2, 5], H.dark, { at: [hatch[0], 9.2, hatch[2]] });
  charge.box([4.2, 0.4, 3.2], WHITE, { at: [hatch[0], 11.4, hatch[2]] });
  muzzle(hatch, 'launch');
}

/**
 * P05-R23, P16-R04: a huge swollen hive of flesh, a metal launch ring turning on its back,
 * glowing honey-amber brood cells, armour plates and vents grafted on.
 */
export function buildHive(scene: Scene): EnemyModel {
  return buildJointedModel('hive', scene, NEON, CFG.design, { body, ring, parts: {} });
}
