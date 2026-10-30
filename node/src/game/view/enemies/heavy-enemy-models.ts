import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { curve, organ, segmentedBody, tendril, vein } from '../../../render/geometry/organic';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { eyePair, sinew } from './basic-parts';
import { buildEnemyModel } from './enemy-mesh';
import { angryEyes, around, decal, LOBE_SECTION, radial, SIDES } from './enemy-shapes';

// P05-R06..R08, P16-R03: the bigger enemies, Cyber-Organic (P16-R01): swollen flesh bodies and
// organs, metal grafted on for armour, nozzles and guns. Logical pixels, nose +Z, Y up.
// The Bulwark and the Splitter are in `heavy-beetle-models.ts`.
const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R06: the Spinner's pod muzzles, lit while it fires. */
const SPINNER_MUZZLE = [
  [-1.5, 2.2],
  [1.5, 2.2],
  [1.3, 3.1],
  [-1.3, 3.1],
] as const;

/**
 * P05-R06, P16-R03: a spiral turret: an organic core spinning four sinew arms curled the same
 * way round, a flesh pod at the end of each with a metal muzzle collar, an orange neon heart.
 */
export function buildSpinner(scene: Scene): EnemyModel {
  const podRadius = ENEMY_CONFIG.spinner.podRadius;
  return buildEnemyModel('spinner', scene, N.spinner, (p) => {
    const { flesh, hull, neon, charge, muzzle } = p;
    organ(flesh, 5, 6, F.purple, { at: [0, -1.6, 0] }, 0.35);
    for (const a of around(4)) {
      // Each arm leaves the core a quarter turn behind its pod: a spiral.
      const arm = curve(radial(a - 0.9, 4.2, 0), radial(a, podRadius - 3.4, 0), [0, 0.5, 0], 3);
      const bowed = arm.map((q, i): [number, number, number] => {
        const k = Math.sin((Math.PI * i) / 3) * 2.2;
        return [q[0] + Math.cos(a) * k, q[1], q[2] - Math.sin(a) * k];
      });
      tendril(flesh, bowed, [1.3, 1], 3, F.sinew);
      const pod = { at: radial(a, podRadius - 3.6, -0.2), pitch: QUARTER, yaw: a };
      organ(flesh, 2.4, 5, F.crimson, pod, 1.1);
      hull.ring(1.6, 1, 5, H.panel, { at: radial(a, podRadius + 1.2, 0), pitch: QUARTER, yaw: a });
      // The pods' muzzles light up while it fires.
      charge.slab(SPINNER_MUZZLE, [-0.7, 0.7], WHITE, { at: radial(a, podRadius, 0), yaw: a });
      muzzle(radial(a, podRadius + 3.1, 0));
    }
    const core = [
      [0, -1.5],
      [3.2, -0.6],
      [0, 2.6],
    ] as const;
    neon.lathe(core, 6, N.spinner);
  });
}

/** P05-R07: the Lancer's right fin, a flesh blade at its tail. */
const LANCER_FIN = [
  [2.5, -6],
  [10, -17],
  [9.5, -20],
  [2.5, -15],
] as const;

/**
 * P05-R07, P16-R03: a laser lance: a long body of swollen segments, a metal lance grafted on
 * its head ending in the glowing emitter, two flesh fins and violet veins along its back.
 */
export function buildLancer(scene: Scene): EnemyModel {
  const nose = ENEMY_CONFIG.lancer.emitterOffset;
  return buildEnemyModel('lancer', scene, N.lancer, (p) => {
    const { flesh, hull, neon, charge, reactor, muzzle } = p;
    const body = { tail: -21, nose: 9, segments: 4, width: 3.2, bottom: -1.5, top: 2.4 };
    segmentedBody(flesh, body, F.purple, {}, LOBE_SECTION);
    hull.cylinder(1.5, nose - 6, 5, H.panel, { at: [0, 0, 5], pitch: QUARTER }, 0.6);
    eyePair(p, [0, 1.6, 6], 1, 0.5, N.lancer);
    reactor([0, 0, -21], 1.6);
    for (const s of SIDES) {
      neon.box([0.5, 0.4, 14], N.lancer, { at: [s * 1.6, 2.1, -6] });
      const fin = LANCER_FIN.map(([x, z]): OutlinePoint => [s * x, z]);
      flesh.bevelSlab(fin, [-0.5, 0, 0.5], [0.3, 0.5], F.membrane, {}, F.sinew);
      reactor([s * 6.5, 0, -17.8], 0.9);
    }
    const emitter = [
      [0, -1.4],
      [1.8, 0],
      [0, 1.4],
    ] as const;
    // Brightens through the warning (its `charge`), full while the laser fires.
    charge.lathe(emitter, 6, WHITE, { at: [0, 0, nose] });
    muzzle([0, 0, nose + 1.8], 'laser');
  });
}

/** P05-R08: the Rocketeer's armour plate, grafted on its back. */
const ROCKETEER_ARMOUR = [
  [0, 9],
  [4.5, 5],
  [4.5, -8],
  [-4.5, -8],
  [-4.5, 5],
] as const;

/**
 * P05-R08, P16-R03: a bulky flesh body with an armour plate on its back, carrying on sinews a
 * long egg sac on each side: its missiles, their tips glowing when loaded.
 */
export function buildRocketeer(scene: Scene): EnemyModel {
  const pod = ENEMY_CONFIG.rocketeer.podOffset;
  return buildEnemyModel('rocketeer', scene, N.rocketeer, (p) => {
    const { flesh, hull, neon, charge, reactor } = p;
    const body = { tail: -15, nose: 14, segments: 3, width: 9, bottom: -2.2, top: 3.4 };
    segmentedBody(flesh, body, F.crimson, {}, LOBE_SECTION);
    hull.bevelSlab(ROCKETEER_ARMOUR, [2.4, 2.4, 3.6], [0, 1], H.panel, {}, H.base);
    for (const eye of angryEyes([0, 6.2], 0.8, [2.4, 0.6], 0.4)) {
      decal(neon, eye, 3.62, N.rocketeer);
    }
    for (const s of SIDES) {
      sinew(p, [s * 7, 0.5, 6], [s * (pod - 3), 0.5, 4], [0, 1, 1], 1.4);
      sinew(p, [s * 7, 0.5, -8], [s * (pod - 3), 0.5, -6], [0, 1, -1], 1.4);
      // The egg sac: a long organ lying along Z, its missile tip at the front.
      organ(flesh, 4, 6, F.membrane, { at: [s * pod, 0, -11], pitch: QUARTER }, 2.75);
      vein(p.vein, curve([s * pod, 3.6, -8], [s * pod, 3.6, 6], [0, 0.8, 0], 3), 0.9, N.rocketeer);
      charge.cylinder(2.4, 3.5, 6, WHITE, { at: [s * pod, 0, 11], pitch: QUARTER }, 0);
      p.muzzle([s * pod, 0, 14.5], 'missile');
      reactor([s * 2.4, 0, -15], 1.6);
    }
  });
}

export { buildBulwark, buildSplitter, buildSplitterPod } from './heavy-beetle-models';
