import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import {
  around,
  CANOPY_SECTION,
  flipX,
  HULL_SECTION,
  POD_SECTION,
  radial,
  SIDES,
} from './enemy-shapes';

// P05-R01..R05: the lighter enemies. Logical pixels, nose +Z, Y up (towards the camera).
// Fuselages are lofts and wings bevelled slabs (phase 5 review: no more stacked boxes).
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;

/** P05-R01: a small flat disc with three short fins at 120° and a neon ring around its rim. */
export function buildGnat(scene: Scene): EnemyModel {
  return buildEnemyModel('gnat', scene, N.gnat, ({ hull, neon, reactor }) => {
    const profile = [
      [0, -1.4],
      [5.5, -1.1],
      [6.5, 0],
      [5.2, 1.2],
      [2.4, 2],
      [0, 2.6],
    ] as const;
    hull.lathe(profile, 10, H.base);
    // Blades swept the same way round, as if the disc spun.
    const blade = [
      [-1.2, -2.6],
      [1.2, -2.6],
      [-0.2, 1.8],
    ] as const;
    for (const a of around(3)) {
      hull.bevelSlab(blade, [-0.6, 0, 0.6], [0.3, 0.4], H.panel, { at: radial(a, 7, 0), yaw: a });
    }
    neon.ring(6.7, 0.7, 10, N.gnat, { at: [0, -0.35, 0] });
    reactor([0, 0, -6.5], 1.1);
  });
}

/** P05-R02: an arrow head with sharply swept wings and a single red neon eye at the nose. */
export function buildHornet(scene: Scene): EnemyModel {
  return buildEnemyModel('hornet', scene, N.hornet, ({ hull, neon, reactor }) => {
    hull.loft(
      HULL_SECTION,
      [
        [-9, 1.9, -1.2, 1.4],
        [-3, 2.6, -1.3, 1.7],
        [3, 2.4, -1.1, 1.6],
        [9, 1.2, -0.6, 0.8],
        [12, 0, 0, 0],
      ],
      H.base,
    );
    const wing = [
      [2, 3],
      [11.5, -11],
      [8, -11],
      [1.8, -6],
    ] as const;
    for (const outline of [wing, flipX(wing)]) {
      hull.bevelSlab(outline, [-0.5, 0, 0.4], [0.5, 0.9], H.base, {}, H.panel);
    }
    hull.loft(
      CANOPY_SECTION,
      [
        [-7, 0, 1.5, 1.5],
        [-1, 1.2, 1.6, 2.6],
        [7, 0, 0.8, 0.8],
      ],
      H.dark,
      {},
      true,
    );
    reactor([0, 0.1, -9], 1.4);
    neon.lathe(
      [
        [0, -0.9],
        [1.4, 0],
        [0, 0.9],
      ],
      6,
      N.hornet,
      { at: [0, 1.2, 8.5] },
    );
  });
}

/** P05-R03: the Scout's tail booms (tapering into the wing) and the neon strip on each. */
const SCOUT_BOOM = [
  [-15, 1.3, -1, 1.6],
  [-9, 1.5, -1.1, 1.8],
  [-3, 1.1, -0.7, 1.3],
  [1, 0, 0.3, 0.3],
] as const;
const SCOUT_STRIP = [
  [-0.35, -14],
  [0.35, -14],
  [0.35, -5],
  [-0.35, -5],
] as const;

/** P05-R03: a small delta wing with twin tail booms and a cyan neon strip along each boom. */
export function buildScout(scene: Scene): EnemyModel {
  return buildEnemyModel('scout', scene, N.scout, ({ hull, neon, charge, reactor }) => {
    const delta = [
      [0, 12],
      [13, -8],
      [11, -9],
      [-11, -9],
      [-13, -8],
    ] as const;
    hull.bevelSlab(delta, [-0.8, -0.1, 0.8], [1, 1.8], H.base, {}, H.panel);
    hull.loft(
      CANOPY_SECTION,
      [
        [-6, 0, 0.8, 0.8],
        [-1, 1.9, 0.8, 2.3],
        [4, 1.8, 0.8, 2.5],
        [9.5, 0, 0.8, 0.8],
      ],
      H.dark,
      {},
      true,
    );
    for (const s of SIDES) {
      hull.loft(POD_SECTION, SCOUT_BOOM, H.base, { at: [s * 7, 0, 0] });
      neon.slab(SCOUT_STRIP, [1.6, 2], N.scout, { at: [s * 7, 0.1, 0] });
      reactor([s * 7, 0.3, -15], 1.1);
    }
    // Its gun, under the nose, glows as the next shot comes.
    charge.loft(
      POD_SECTION,
      [
        [9.5, 0.7, -1, 0.2],
        [12.5, 0, -0.4, -0.4],
      ],
      WHITE,
    );
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

/** P05-R04: a wide, flat flying wing with a row of magenta neon lights along the leading edge. */
export function buildStrafer(scene: Scene): EnemyModel {
  return buildEnemyModel('strafer', scene, N.strafer, ({ hull, neon, reactor }) => {
    const wing = [
      [0, 8],
      [20.5, -1.5],
      [20.5, -5],
      [6, -3.5],
      [0, -6],
      [-6, -3.5],
      [-20.5, -5],
      [-20.5, -1.5],
    ] as const;
    hull.bevelSlab(wing, [-0.9, -0.2, 0.9], [1.2, 2.2], H.base, {}, H.panel);
    hull.loft(
      CANOPY_SECTION,
      [
        [-6, 0, 0.9, 0.9],
        [-2, 3.6, 0.9, 2.4],
        [2.5, 3.4, 0.9, 2.6],
        [6.5, 0, 0.9, 0.9],
      ],
      H.dark,
      {},
      true,
    );
    for (const x of [-12, -4, 4, 12]) reactor([x, 0, Math.abs(x) === 4 ? -4.3 : -4.1], 1);
    for (const s of SIDES) {
      for (let k = 1; k <= 5; k++) {
        const light = edgeLight([0, 8], [s * 20.5, -1.5], k / 6, 2.5, [2, 0.7]);
        neon.slab(light, [0.85, 1.15], N.strafer);
      }
    }
  });
}

/** P05-R05: the Weaver's hulls, and the swept strut between them (under the neon bar). */
const WEAVER_HULL = [
  [-15, 2, -1.4, 1.2],
  [-9, 2.6, -1.5, 1.5],
  [6, 2.6, -1.5, 1.5],
  [11, 1.6, -1, 1],
  [15.5, 0, -0.2, -0.2],
] as const;
const WEAVER_STRUT = [
  [-9, 0.5],
  [0, 2.5],
  [9, 0.5],
  [9, -3],
  [0, -1.5],
  [-9, -3],
] as const;

/** P05-R05: a twin-hull catamaran, the two hulls joined by a glowing green neon bar. */
export function buildWeaver(scene: Scene): EnemyModel {
  return buildEnemyModel('weaver', scene, N.weaver, ({ hull, neon, charge, reactor }) => {
    hull.bevelSlab(WEAVER_STRUT, [-1, -0.4, 0.2], [0.3, 0.6], H.dark);
    for (const s of SIDES) {
      hull.loft(HULL_SECTION, WEAVER_HULL, H.base, { at: [s * 10, 0, 0] });
      hull.loft(
        CANOPY_SECTION,
        [
          [-1, 0, 1.5, 1.5],
          [3, 1.4, 1.5, 2.6],
          [8, 1.3, 1.5, 2.4],
          [12, 0, 1, 1],
        ],
        H.dark,
        { at: [s * 10, 0, 0] },
        true,
      );
      charge.loft(
        POD_SECTION,
        [
          [13.5, 0.6, -1.1, -0.2],
          [16, 0, -0.6, -0.6],
        ],
        WHITE,
        { at: [s * 10, 0, 0] },
      );
      reactor([s * 10, 0, -15], 1.5);
    }
    neon.slab(
      WEAVER_STRUT.map(([x, z]): OutlinePoint => [x * 0.88, z * 0.4 - 0.3]),
      [0.2, 0.7],
      N.weaver,
    );
  });
}
