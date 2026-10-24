import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import {
  angryEyes,
  around,
  decal,
  CANOPY_SECTION,
  HULL_SECTION,
  POD_SECTION,
  radial,
  SIDES,
  spike,
} from './enemy-shapes';

// P05-R06..R10: the bigger enemies. Logical pixels, nose +Z, Y up (towards the camera).
// Fuselages are lofts, plates and wings bevelled slabs (phase 5 review: no more stacked boxes),
// with horns, pincers, saw teeth and slanted neon eyes to look aggressive (phase 5 review).
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R06: the Spinner's ring (a lathe profile), spokes and pods. */
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
const SPINNER_POD = [
  [0, -2],
  [2.8, -1.2],
  [2.8, 1.2],
  [0, 2.2],
] as const;

/** P05-R06: a ring with four spokes, a pod at the end of each, and an orange neon core. */
export function buildSpinner(scene: Scene): EnemyModel {
  const podRadius = ENEMY_CONFIG.spinner.podRadius;
  return buildEnemyModel('spinner', scene, N.spinner, ({ hull, neon, charge }) => {
    hull.lathe(SPINNER_RING, 12, H.base, {}, false);
    for (const a of around(4)) {
      const spoke = { at: radial(a, 6.5, 0), yaw: a };
      hull.bevelSlab(SPINNER_SPOKE, [-0.8, 0, 0.8], [0.3, 0.5], H.panel, spoke);
      hull.lathe(SPINNER_POD, 6, H.panel, { at: radial(a, podRadius, 0) });
      // Saw teeth on the ring between the pods, hooked the way it turns.
      for (const t of [0.5, 1.05]) {
        const [x0, , z0] = radial(a + t, 11.8, 0);
        const [x1, , z1] = radial(a + t + 0.22, 15.5, 0);
        hull.slab(spike([x0, z0], [x1, z1], 2.4), [-0.6, 0.6], H.panel);
      }
      // The pods' muzzles light up while it fires.
      charge.ring(2.9, 0.7, 6, WHITE, { at: radial(a, podRadius, -0.35) });
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
  return buildEnemyModel('lancer', scene, N.lancer, ({ hull, neon, charge, reactor }) => {
    hull.loft(
      HULL_SECTION,
      [
        [-21, 2.3, -1.3, 1.2],
        [-6, 3.2, -1.5, 1.5],
        [6, 2.6, -1.3, 1.3],
        [nose - 4, 1.2, -0.6, 0.6],
        [nose - 1, 0, 0, 0],
      ],
      H.base,
    );
    reactor([0, 0, -21], 1.6);
    hull.loft(
      CANOPY_SECTION,
      [
        [-17, 0, 1.2, 1.2],
        [-12, 1, 1.4, 2.4],
        [4, 1, 1.3, 2.3],
        [13, 0, 0.8, 0.8],
      ],
      H.dark,
      {},
      true,
    );
    for (const s of SIDES) {
      const fin = LANCER_FIN.map(([x, z]): [number, number] => [s * x, z]);
      hull.bevelSlab(fin, [-0.5, 0, 0.5], [0.3, 0.5], H.base, {}, H.panel);
      neon.box([0.5, 0.4, 16], N.lancer, { at: [s * 1.8, 1.25, -4] });
      reactor([s * 6.5, 0, -17.8], 0.9);
      // Pincers either side of the emitter.
      const pincer = spike([s * 3, 4], [s * 1.7, nose - 0.5], 2);
      hull.bevelSlab(pincer, [-0.7, 0, 0.6], [0.2, 0.3], H.panel);
    }
    for (const eye of angryEyes([0, 8.5], 0.4, [1.3, 0.4], 0.45)) {
      decal(neon, eye, 1.9, N.lancer);
    }
    const emitter = [
      [0, -1.4],
      [1.8, 0],
      [0, 1.4],
    ] as const;
    // Brightens through the warning (its `charge`), full while the laser fires.
    charge.lathe(emitter, 6, WHITE, { at: [0, 0, nose] });
  });
}

/** P05-R08: the Rocketeer's body (a ram at the nose), armour, pod pylons and missile pods. */
const ROCKETEER_BODY = [
  [0, 17],
  [3, 11],
  [7, 10],
  [9, 0],
  [8, -12],
  [4, -15],
  [-4, -15],
  [-8, -12],
  [-9, 0],
  [-7, 10],
  [-3, 11],
] as const;
const ROCKETEER_ARMOUR = [
  [0, 9],
  [4.5, 5],
  [4.5, -8],
  [-4.5, -8],
  [-4.5, 5],
] as const;
const ROCKETEER_PYLON = [
  [-3.5, 3],
  [3.5, 1.5],
  [3.5, -3],
  [-3.5, -3],
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
  return buildEnemyModel('rocketeer', scene, N.rocketeer, ({ hull, neon, charge, reactor }) => {
    hull.bevelSlab(ROCKETEER_BODY, [-2.2, 0, 2.4], [1.4, 2], H.base, {}, H.panel);
    hull.bevelSlab(ROCKETEER_ARMOUR, [2.4, 2.4, 3.6], [0, 1], H.dark);
    for (const eye of angryEyes([0, 6.2], 0.8, [2.4, 0.6], 0.4)) {
      decal(neon, eye, 3.9, N.rocketeer);
    }
    for (const s of SIDES) {
      const pylon = { at: [s * 12, 0, 0] as [number, number, number] };
      hull.bevelSlab(ROCKETEER_PYLON, [-0.6, -0.2, 0.6], [0.3, 0.5], H.dark, pylon);
      hull.lathe(ROCKETEER_MISSILE, 8, H.panel, { at: [s * pod, 0, -11], pitch: QUARTER });
      // Swept fins at the back of the pods.
      const fin = spike([s * (pod + 3), -6], [s * (pod + 6.5), -12.5], 3.2);
      hull.bevelSlab(fin, [-0.4, 0, 0.4], [0.2, 0.3], H.panel);
      neon.box([1, 0.4, 12], N.rocketeer, { at: [s * pod, 3.9, -3] });
      charge.cylinder(2.6, 3.5, 8, WHITE, { at: [s * pod, 0, 11], pitch: QUARTER }, 0);
      reactor([s * 2.4, 0, -15], 1.6);
    }
  });
}

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

/** P05-R09: the Bulwark's front armour plates, its tower and its visor slit. */
const BULWARK_PLATE = [
  [-4.75, -3.5],
  [4.75, -3.5],
  [4.75, 3.5],
  [-4.75, 3.5],
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

/** P05-R09: a heavy, wide hull covered with front armour plates and a blue neon visor slit. */
export function buildBulwark(scene: Scene): EnemyModel {
  return buildEnemyModel('bulwark', scene, N.bulwark, ({ hull, neon, charge, reactor }) => {
    hull.bevelSlab(BULWARK_BODY, [-3, -0.6, 2.5], [2, 2.5], H.base, {}, H.panel);
    for (let k = -2; k <= 2; k++) {
      const at = [k * 10, 0, 8 - Math.abs(k) * 2.5] as [number, number, number];
      // Sloped armour: the plates' tops lean back from their edges.
      hull.bevelSlab(
        BULWARK_PLATE,
        [2.5, 2.5, 4.1],
        [0, 1.4],
        H.panel,
        { at, yaw: -k * 0.12 },
        H.base,
      );
    }
    hull.bevelSlab(BULWARK_TOWER, [2.5, 2.5, 5.5], [0, 1.6], H.dark, {}, H.base);
    neon.slab(BULWARK_VISOR, [3.9, 5], N.bulwark);
    for (const s of SIDES) {
      hull.loft(
        POD_SECTION,
        [
          [-20, 3, -1.7, 1.7],
          [-16, 3.4, -2, 2],
          [-11, 2, -1.2, 1.2],
        ],
        H.dark,
        { at: [s * 12, 0, 0] },
      );
      reactor([s * 12, 0, -20], 1.3);
      // Ram horns at the front, spikes at the wing corners.
      const horn = spike([s * 10, 11], [s * 6.5, 21.5], 5);
      hull.bevelSlab(horn, [-1.6, 0, 1.6], [0.3, 0.6], H.panel);
      const corner = spike([s * 25.5, 0.5], [s * 27, 8.5], 3);
      hull.bevelSlab(corner, [-1, 0, 1], [0.3, 0.5], H.panel);
    }
    charge.box([3, 1, 2.4], WHITE, { at: [0, 2.5, 15.5] });
    reactor([0, 0, -17], 2.2);
  });
}

/** The pod of a Splitter: a small hexagonal pod with a purple neon rim. */
function pod(hull: SolidBuilder, at: [number, number, number]): void {
  const profile = [
    [0, -2.6],
    [4.5, -2],
    [4.5, 2],
    [0, 2.8],
  ] as const;
  hull.lathe(profile, 6, H.panel, { at });
}

/** P05-R10: a hexagonal core with three pods around it, purple neon seams in between. */
export function buildSplitter(scene: Scene): EnemyModel {
  const offset = ENEMY_CONFIG.splitter.podOffset;
  return buildEnemyModel('splitter', scene, N.splitter, ({ hull, neon, charge, reactor }) => {
    const core = [
      [0, -3],
      [9, -2.5],
      [9, 2.5],
      [6, 3.5],
      [0, 4],
    ] as const;
    hull.lathe(core, 6, H.base);
    neon.ring(9.1, 0.7, 6, N.splitter, { at: [0, 1, 0] });
    for (const a of around(3)) {
      pod(hull, radial(a, offset, 0));
      neon.box([1, 0.8, 4.4], N.splitter, { at: radial(a, 10.6, 1.4), yaw: a });
    }
    // Blades in the two front gaps between the pods (the reactor is in the back one).
    for (const s of SIDES) {
      const [x0, , z0] = radial((s * Math.PI) / 3, 7.5, 0);
      const [x1, , z1] = radial((s * Math.PI) / 3 - s * 0.25, 16.5, 0);
      hull.bevelSlab(spike([x0, z0], [x1, z1], 3.4), [-0.8, 0, 0.8], [0.2, 0.4], H.panel);
    }
    const eye = [
      [0, 0],
      [2.2, 0.4],
      [0, 1.4],
    ] as const;
    charge.lathe(eye, 6, WHITE, { at: [0, 4, 0] });
    reactor([0, 0, -7.8], 1.6);
  });
}

/** P05-R10: a pod broken off a Splitter, diving nose first. */
export function buildSplitterPod(scene: Scene): EnemyModel {
  return buildEnemyModel('splitter-pod', scene, N.splitter, ({ hull, neon, reactor }) => {
    pod(hull, [0, 0, 0]);
    hull.cylinder(2.2, 4, 6, H.dark, { at: [0, 0, 3.5], pitch: QUARTER }, 0);
    neon.ring(4.6, 0.7, 6, N.splitter, { at: [0, -0.35, 0] });
    reactor([0, 0, -3.9], 1);
  });
}
