import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import { curve, organ, segmentedBody, tendril, vein } from '../../../render/geometry/organic';
import type { EnemyModel } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { gunBarrel, eyePair, sinew, wingPair } from './basic-parts';
import { buildEnemyModel } from './enemy-mesh';
import { around, LOBE_SECTION, radial, SIDES } from './enemy-shapes';
import { reactorSac } from './organic-parts';

// P05-R01..R05, P16-R03: the lighter enemies, Cyber-Organic (P16-R01): swollen flesh bodies,
// membrane wings that flutter, metal only where grafted on (ducts, stingers, guns, nozzles).
// Logical pixels, nose +Z, Y up (towards the camera).
const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const N = ENEMY_LOOK.neon;
const QUARTER = Math.PI / 2;

/** P05-R01: the duct around each of the Gnat's fans (a metal graft, lathe profile). */
const GNAT_DUCT = [
  [2.3, -0.6],
  [3, 0],
  [2.3, 0.6],
  [2.3, -0.6],
] as const;

/**
 * P05-R01, P16-R03: a small insect drone: a swollen flesh bulb with a head and two eyes, three
 * metal-ducted fans on sinews at 120°, a neon ring around its middle and a feeler on its back.
 */
export function buildGnat(scene: Scene): EnemyModel {
  return buildEnemyModel('gnat', scene, N.gnat, (p) => {
    const { flesh, hull, neon, reactor, rotor } = p;
    organ(flesh, 3.6, 6, F.purple, { at: [0, -1.2, -0.4] }, 0.42);
    organ(flesh, 1.5, 4, F.sinew, { at: [0, -0.2, 3.3] }, 0.55);
    eyePair(p, [0, 0.6, 4.2], 0.6, 0.45, N.gnat);
    neon.ring(3.5, 0.5, 6, N.gnat, { at: [0, -0.4, -0.4] });
    for (const a of around(3)) {
      const duct = radial(a, 6, 0);
      sinew(p, radial(a, 2.6, 0), radial(a, 4, 0), [0, 0.4, 0], 0.6);
      hull.lathe(GNAT_DUCT, 5, H.panel, { at: duct }, false);
      rotor([duct[0], 0, duct[2]], 2.1);
    }
    tendril(flesh, curve([-0.8, 1, -1.6], [-1.6, 2.6, -3], [0, 0.4, 0], 2), [0.25, 0], 3, F.bone);
    reactor([0, 0, -4.4], 0.9);
  });
}

/**
 * P05-R02, P16-R03: a stinger diver: a wasp of three swollen segments, a metal stinger at its
 * nose under a single red eye, and swept, serrated membrane wings that flutter.
 */
export function buildHornet(scene: Scene): EnemyModel {
  return buildEnemyModel('hornet', scene, N.hornet, (p) => {
    const { flesh, hull, neon } = p;
    const body = { tail: -9, nose: 10.5, segments: 3, width: 2.6, bottom: -1.3, top: 2.4 };
    segmentedBody(flesh, body, F.crimson, {}, LOBE_SECTION);
    hull.cylinder(0.9, 3.2, 4, H.panel, { at: [0, 0.4, 9.3], pitch: QUARTER }, 0);
    vein(p.vein, curve([0, 2.3, -7], [0, 2.4, 6], [0, 0.6, 0], 3), 0.6, N.hornet);
    wingPair(
      p,
      {
        root: [1.6, 2],
        tips: [
          [11.5, -11],
          [8, -11],
          [3, -7],
        ],
        y: 1.6,
        strut: 0.45,
      },
      N.hornet,
    );
    reactorSac(p, [0, 0.1, -9], 1.2, N.hornet, { flesh: F.sinew, veinLength: 3 });
    const eye = [
      [0, -0.5],
      [0.9, 0],
      [0, 0.6],
    ] as const;
    neon.lathe(eye, 5, N.hornet, { at: [0, 1.4, 7.4] });
  });
}

/** P05-R03: the Scout's neon strip along each tail boom. */
const SCOUT_STRIP = [
  [-0.35, -14],
  [0.35, -14],
  [0.35, -5],
  [-0.35, -5],
] as const;

/**
 * P05-R03, P16-R03: a light winged scout: a slim flesh body, broad membrane wings that flutter,
 * two bone tail booms with a cyan neon strip and a reactor each, and a nose gun grafted on.
 */
export function buildScout(scene: Scene): EnemyModel {
  return buildEnemyModel('scout', scene, N.scout, (p) => {
    const { flesh, neon, reactor } = p;
    const body = { tail: -9, nose: 12.5, segments: 2, width: 2.5, bottom: -1, top: 2.3 };
    segmentedBody(flesh, body, F.teal, {}, LOBE_SECTION);
    eyePair(p, [0, 1.6, 8], 0.8, 0.4, N.scout);
    wingPair(
      p,
      {
        root: [1.8, 6],
        tips: [
          [13, -8],
          [10, -9],
          [5, -6],
        ],
        y: 0.6,
        strut: 0.5,
      },
      N.scout,
    );
    for (const s of SIDES) {
      tendril(
        flesh,
        curve([s * 2, 0.4, 2], [s * 7, 0.6, -15], [s * 1.5, 0, 0], 3),
        [1.3, 1],
        4,
        F.bone,
      );
      neon.slab(SCOUT_STRIP, [1.3, 1.7], N.scout, { at: [s * 7, 0, 0] });
      reactor([s * 7, 0.3, -15], 1.1);
    }
    // Its nose gun (phase 7 review).
    gunBarrel(p, [0, 1.3, 6], 6.5);
  });
}

/** A light along an edge from `a` to `b`, `inward` away from it, `length` long at `t` of it. */
function edgeLight(
  a: OutlinePoint,
  b: OutlinePoint,
  t: number,
  inward: number,
  [length, width]: readonly [number, number],
): OutlinePoint[] {
  const [dx, dz] = [b[0] - a[0], b[1] - a[1]];
  const d = Math.hypot(dx, dz);
  const [ux, uz] = [dx / d, dz / d];
  // The side of the edge behind it, towards the trailing edge.
  const [nx, nz] = ux < 0 ? [-uz, ux] : [uz, -ux];
  const [cx, cz] = [a[0] + dx * t + nx * inward, a[1] + dz * t + nz * inward];
  const along = (k: number, w: number): OutlinePoint => [
    cx + (ux * (k * length)) / 2 + nx * w,
    cz + (uz * (k * length)) / 2 + nz * w,
  ];
  return [along(-1, 0), along(1, 0), along(1, width), along(-1, width)];
}

/**
 * P05-R04, P16-R03: a fan shooter: a wide pair of membrane wings out of a squat flesh body, a
 * row of magenta neon glands along each leading edge, four reactors and a gun on each flank.
 */
export function buildStrafer(scene: Scene): EnemyModel {
  return buildEnemyModel('strafer', scene, N.strafer, (p) => {
    const { flesh, reactor } = p;
    const body = { tail: -6.5, nose: 10.5, segments: 2, width: 4.2, bottom: -1.3, top: 2.3 };
    segmentedBody(flesh, body, F.purple, {}, LOBE_SECTION);
    eyePair(p, [0, 1.5, 7], 1, 0.5, N.strafer);
    wingPair(
      p,
      {
        root: [3, 4],
        tips: [
          [20.5, -1.5],
          [20.5, -5],
          [7, -4],
        ],
        y: 0.2,
        strut: 0.6,
        lights: [1, 2, 3].map((k) => edgeLight([3, 6], [20.5, -1.5], k / 4, 1.6, [2.4, 0.7])),
      },
      N.strafer,
    );
    for (const x of [-12, -4, 4, 12]) reactor([x, 0, Math.abs(x) === 4 ? -4.3 : -4.1], 1);
    for (const s of SIDES) {
      // A gun on each side of the body, pointing out sideways: it flies across the screen
      // and fires down it from the one facing down (phase 7 review).
      gunBarrel(p, [s * 4.6, 1.5, 1.5], 3.6, s * QUARTER);
    }
  });
}

/** P05-R05: the Weaver's web of sinew between its two serpents, under the neon bar. */
const WEAVER_WEB = [
  [-9, 0.5],
  [0, 2.5],
  [9, 0.5],
  [9, -3],
  [0, -1.5],
  [-9, -3],
] as const;

/**
 * P05-R05, P16-R03: a sine flyer: two serpents side by side, each a swollen head and a wavy
 * tail, joined by a web of flesh under a glowing green neon bar, a gun grafted on each snout.
 */
export function buildWeaver(scene: Scene): EnemyModel {
  return buildEnemyModel('weaver', scene, N.weaver, (p) => {
    const { flesh, neon, reactor } = p;
    flesh.bevelSlab(WEAVER_WEB, [-1, -0.4, 0.2], [0.3, 0.6], F.membrane);
    for (const s of SIDES) {
      const at: [number, number, number] = [s * 10, 0, 0];
      const head = { tail: -6, nose: 15.5, segments: 2, width: 2.6, bottom: -1.5, top: 2.6 };
      segmentedBody(flesh, head, F.teal, { at }, LOBE_SECTION);
      const tail = [-6, -9, -12, -15].map((z, i): [number, number, number] => [
        s * 10 + s * Math.sin(i * 1.8) * 1.4,
        0.4,
        z,
      ]);
      tendril(flesh, tail, [2, 1.2], 4, F.sinew);
      eyePair(p, [s * 10, 2, 11], 0.9, 0.4, N.weaver);
      reactor([s * 10, 0, -15], 1.5);
      // A gun along each serpent's snout (phase 7 review).
      gunBarrel(p, [s * 10, 1.9, 8], 7);
    }
    neon.slab(
      WEAVER_WEB.map(([x, z]): OutlinePoint => [x * 0.88, z * 0.4 - 0.3]),
      [0.2, 0.7],
      N.weaver,
    );
  });
}
