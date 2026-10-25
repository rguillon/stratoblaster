import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import {
  angryEyes,
  around,
  canopyPaint,
  decal,
  FIGHTER_SECTION,
  flipX,
  POD_SECTION,
  radial,
  sideStripe,
  SIDES,
} from './enemy-shapes';

// P05-R06..R10: the bigger enemies. Logical pixels, nose +Z, Y up (towards the camera).
// Parts blend into each other (phase 5 review): pods faired or fitted into their bodies,
// canopies and stripes painted on, armour in one piece.
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R06: the Spinner's ring (a lathe profile), spokes, and pods growing out of the ring. */
const SPINNER_RING = [
  [10.2, -1.2],
  [11.8, -1.6],
  [12.6, 0],
  [11.8, 1.6],
  [10.2, 1.2],
  [10.2, -1.2],
] as const;
const SPINNER_SPOKE = [
  [-1.3, -4],
  [1.3, -4],
  [0.7, 4.5],
  [-0.7, 4.5],
] as const;
/** Around the pod's centre, outwards along +Z: its root wraps the ring. */
const SPINNER_POD = [
  [-2.6, -3.8],
  [2.6, -3.8],
  [3, 0.3],
  [1.6, 2.7],
  [-1.6, 2.7],
  [-3, 0.3],
] as const;
const SPINNER_MUZZLE = [
  [-1.5, 2.2],
  [1.5, 2.2],
  [1.3, 3.1],
  [-1.3, 3.1],
] as const;

/** P05-R06: a ring with four spokes, a pod at the end of each, and an orange neon core. */
export function buildSpinner(scene: Scene): EnemyModel {
  const podRadius = ENEMY_CONFIG.spinner.podRadius;
  return buildEnemyModel('spinner', scene, N.spinner, ({ hull, neon, charge, muzzle }) => {
    hull.lathe(SPINNER_RING, 12, H.base, {}, false);
    for (const a of around(4)) {
      const spoke = { at: radial(a, 6.5, 0), yaw: a };
      hull.bevelSlab(SPINNER_SPOKE, [-0.8, 0, 0.8], [0.3, 0.5], H.panel, spoke);
      const pod = { at: radial(a, podRadius, 0), yaw: a };
      hull.bevelSlab(SPINNER_POD, [-1.8, 0, 1.8], [0.4, 0.9], H.panel, pod, H.base);
      // The pods' muzzles light up while it fires.
      charge.slab(SPINNER_MUZZLE, [-0.7, 0.7], WHITE, pod);
      muzzle(radial(a, podRadius + 3.1, 0));
    }
    const core = [
      [0, -1.5],
      [3.2, -0.8],
      [3.2, 0.8],
      [0, 2],
    ] as const;
    neon.lathe(core, 8, N.spinner);
  });
}

/** P05-R07: the Lancer's right fin. */
const LANCER_FIN = [
  [3, -5],
  [10, -17],
  [9.5, -20],
  [2.5, -15],
] as const;

/** P05-R07: a long needle hull with a glowing emitter at the nose and two small side fins. */
export function buildLancer(scene: Scene): EnemyModel {
  const nose = ENEMY_CONFIG.lancer.emitterOffset;
  return buildEnemyModel('lancer', scene, N.lancer, ({ hull, neon, charge, reactor, muzzle }) => {
    const needle = [
      [-21, 2.3, -1.3, 1.2],
      [-12, 3, -1.5, 1.6],
      [-6, 3.2, -1.5, 2.4],
      [4, 2.6, -1.3, 2.3],
      [10, 1.8, -1, 1.3],
      [nose - 4, 1.2, -0.6, 0.6],
      [nose - 1, 0, 0, 0],
    ] as const;
    hull.loft(FIGHTER_SECTION, needle, H.base, {}, { paint: canopyPaint([2, 3], H.dark) });
    reactor([0, 0, -21], 1.6);
    // Neon stripes painted along both flanks, from the fins to the canopy's front.
    for (const side of [1, 6]) {
      const stripe = sideStripe(FIGHTER_SECTION, side, [0.3, 0.7]);
      neon.loft(stripe, needle.slice(1, 5), N.lancer, {}, { open: true });
    }
    for (const s of SIDES) {
      const fin = LANCER_FIN.map(([x, z]): OutlinePoint => [s * x, z]);
      hull.bevelSlab(fin, [-0.5, 0, 0.5], [0.3, 0.5], H.base, {}, H.panel);
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

/** P05-R08: the Rocketeer's body, armour, the fairings out to its pods, and the pods. */
const ROCKETEER_BODY = [
  [0, 14],
  [7, 10],
  [9, 0],
  [8, -12],
  [4, -15],
  [-4, -15],
  [-8, -12],
  [-9, 0],
  [-7, 10],
] as const;
const ROCKETEER_ARMOUR = [
  [0, 9],
  [4.5, 5],
  [4.5, -8],
  [-4.5, -8],
  [-4.5, 5],
] as const;
const ROCKETEER_MISSILE = [
  [2.6, 0],
  [4, 2.5],
  [4, 18.5],
  [3.3, 22],
] as const;

/** P05-R08: a bulky hull with a missile pod on each side; the missile tips glow when loaded. */
export function buildRocketeer(scene: Scene): EnemyModel {
  const pod = ENEMY_CONFIG.rocketeer.podOffset;
  return buildEnemyModel('rocketeer', scene, N.rocketeer, (p) => {
    const { hull, neon, charge, reactor } = p;
    hull.bevelSlab(ROCKETEER_BODY, [-2.2, 0, 2.4], [1.4, 2], H.base, {}, H.panel);
    hull.bevelSlab(ROCKETEER_ARMOUR, [2.4, 2.4, 3.6], [0, 1], H.dark);
    for (const eye of angryEyes([0, 6.2], 0.8, [2.4, 0.6], 0.4)) {
      decal(neon, eye, 3.62, N.rocketeer);
    }
    // A thick, swept fairing from the hull into each pod, instead of a pylon.
    const fairing = [
      [7.5, 8],
      [pod - 1, 9.5],
      [pod - 1, -9.5],
      [7.5, -11],
    ] as const;
    for (const outline of [fairing, flipX(fairing)]) {
      hull.bevelSlab(outline, [-1.4, -0.2, 1.2], [0.4, 0.9], H.base, {}, H.panel);
    }
    for (const s of SIDES) {
      hull.lathe(ROCKETEER_MISSILE, 8, H.panel, { at: [s * pod, 0, -11], pitch: QUARTER });
      neon.box([1, 0.4, 12], N.rocketeer, { at: [s * pod, 3.9, -3] });
      charge.cylinder(2.6, 3.5, 8, WHITE, { at: [s * pod, 0, 11], pitch: QUARTER }, 0);
      p.muzzle([s * pod, 0, 14.5], 'missile');
      reactor([s * 2.4, 0, -15], 1.6);
    }
  });
}

/** P05-R09: the Bulwark's hull, its armour (one band along the front), tower and visor. */
const BULWARK_BODY = [
  [0, 16],
  [14, 13],
  [27, 2],
  [27, -8],
  [18, -17],
  [-18, -17],
  [-27, -8],
  [-27, 2],
  [-14, 13],
] as const;
const BULWARK_ARMOUR = [
  [0, 13],
  [12.5, 10.3],
  [23, 1],
  [19.5, -1],
  [10.5, 6.5],
  [0, 9],
  [-10.5, 6.5],
  [-19.5, -1],
  [-23, 1],
  [-12.5, 10.3],
] as const;
const BULWARK_TOWER = [
  [0, 4],
  [9, 0],
  [9, -12],
  [-9, -12],
  [-9, 0],
] as const;
/** Follows the tower's sloped front, just below its top. */
const BULWARK_VISOR = [
  [-7, 0.2],
  [0, 3.3],
  [7, 0.2],
  [7, -0.6],
  [0, 2.5],
  [-7, -0.6],
] as const;
/** The engine nacelles, sunk into the back of the hull. */
const BULWARK_NACELLE = [
  [-20.5, 3, -2.2, 1.2],
  [-16, 3.4, -2.6, 1.6],
  [-10, 2, -1.6, 0.6],
] as const;

/** P05-R09: a heavy, wide hull covered with front armour plates and a blue neon visor slit. */
export function buildBulwark(scene: Scene): EnemyModel {
  return buildEnemyModel('bulwark', scene, N.bulwark, ({ hull, neon, charge, reactor, muzzle }) => {
    hull.bevelSlab(BULWARK_BODY, [-3, -0.6, 2.5], [2, 2.5], H.base, {}, H.panel);
    hull.bevelSlab(BULWARK_ARMOUR, [2.5, 2.5, 3.9], [0, 1.1], H.panel, {}, H.base);
    hull.bevelSlab(BULWARK_TOWER, [2.5, 2.5, 5.5], [0, 1.6], H.dark, {}, H.base);
    neon.slab(BULWARK_VISOR, [3.9, 5], N.bulwark);
    for (const s of SIDES) {
      hull.loft(POD_SECTION, BULWARK_NACELLE, H.dark, { at: [s * 12, 0, 0] });
      reactor([s * 12, -0.5, -20.5], 1.3);
      // The twin cannon on the tower's front, over the armour (phase 7 review).
      hull.cylinder(0.9, 11, 6, H.dark, { at: [s * 3, 4.2, 2], pitch: QUARTER }, 0.75);
      charge.cylinder(0.95, 1, 6, WHITE, { at: [s * 3, 4.2, 13], pitch: QUARTER });
      muzzle([s * 3, 4.2, 14]);
    }
    reactor([0, 0, -17], 2.2);
  });
}

/**
 * A Splitter pod: a wedge fitted around a flat of the core, `inner` to `outer` from the core's
 * centre, outwards along +Z, around its own centre `offset` out.
 */
function splitterPodOutline(offset: number, inner: number, outer: number): OutlinePoint[] {
  const rim = (a: number): OutlinePoint => [outer * Math.sin(a), outer * Math.cos(a) - offset];
  return [[-4, inner - offset], rim(-0.42), rim(-0.21), rim(0.21), rim(0.42), [4, inner - offset]];
}

/** A pod of the Splitter, and the neon seam along its inner side. */
function pod(
  hull: SolidBuilder,
  neon: SolidBuilder,
  place: { at?: [number, number, number]; yaw?: number },
): void {
  const offset = ENEMY_CONFIG.splitter.podOffset;
  const inner = 8.3;
  hull.bevelSlab(
    splitterPodOutline(offset, inner, 16.4),
    [-2.2, 0, 2.4],
    [0.5, 1.2],
    H.panel,
    place,
    H.base,
  );
  const z0 = inner - offset - 0.45;
  const seam = [
    [-4.3, z0],
    [4.3, z0],
    [4.3, z0 + 0.4],
    [-4.3, z0 + 0.4],
  ] as const;
  neon.slab(seam, [-1.6, 1.8], N.splitter, place);
}

/** P05-R10: a hexagonal core with three pods around it, purple neon seams in between. */
export function buildSplitter(scene: Scene): EnemyModel {
  const offset = ENEMY_CONFIG.splitter.podOffset;
  return buildEnemyModel(
    'splitter',
    scene,
    N.splitter,
    ({ hull, neon, charge, reactor, muzzle }) => {
      const core = [
        [0, -3],
        [9, -2.5],
        [9, 2.5],
        [6, 3.5],
        [0, 4],
      ] as const;
      // Six sides: one flat faces each pod, and the back one the reactor.
      hull.lathe(core, 6, H.base);
      neon.ring(9.1, 0.7, 6, N.splitter, { at: [0, 1, 0] });
      for (const a of around(3)) pod(hull, neon, { at: radial(a, offset, 0), yaw: a });
      const eye = [
        [0, 0],
        [2.2, 0.4],
        [0, 1.4],
      ] as const;
      charge.lathe(eye, 6, WHITE, { at: [0, 4, 0] });
      muzzle([0, 5.4, 0]);
      reactor([0, 0, -7.8], 1.6);
    },
  );
}

/** P05-R10: a pod broken off a Splitter, diving outer side first. */
export function buildSplitterPod(scene: Scene): EnemyModel {
  const { podOffset } = ENEMY_CONFIG.splitter;
  return buildEnemyModel('splitter-pod', scene, N.splitter, ({ hull, neon, reactor }) => {
    pod(hull, neon, {});
    reactor([0, 0, 8.3 - podOffset], 1);
  });
}
