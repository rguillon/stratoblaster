import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import { CRANE_REST, HARBOUR_KRAKEN } from '../../../config/bosses/world-2/harbour-kraken';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { HULL_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { buildBossModel } from '../boss-model';
import { bossPoint } from '../boss-limbs';
import { barrels, edgeStrips, mirrored } from '../final-boss-shapes';
import { lamps, mast, rect, seam } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { icicles, RIME, snowCap, spread } from './fjord-lynx-frost';
import { containerBay, hatchCovers } from './harbour-kraken-cargo';
import { craneLimbs, DECK_Y, grab, ORANGE_NEON, pedestal } from './harbour-kraken-cranes';

// P08-R10, 2-2: the Harbour Kraken. Logical pixels, nose +Z, Y up (towards the camera). A cargo
// ship flying over the harbour: a long hull, a forecastle with its laser emitter and twin guns,
// a bridge tower amidships, four crane pedestals, the container bay at the stern.
type Vec3 = [number, number, number];

/** The hull seen from above (right half, bow to stern). */
const HULL = mirrored([
  [0, 78],
  [10, 72],
  [22, 56],
  [28, 36],
  [30, 10],
  [30, -40],
  [27, -58],
  [18, -66],
  [0, -66],
]);
/** Heights of the hull: its keel, its rim, its deck. */
const HULL_Y = [-7, -1, DECK_Y] as const;
/** The forecastle, raised over the bow (right half). */
const FORECASTLE = mirrored([
  [0, 72],
  [9, 68],
  [19, 54],
  [22, 48],
  [0, 48],
]);
const FORECASTLE_TOP = 8;
/** The bridge tower amidships (loft stations along Z: z, half width, bottom, top). */
const BRIDGE = [
  [-14, 15, DECK_Y, 15],
  [6, 16, DECK_Y, 18],
  [14, 13, DECK_Y, 17],
  [17, 9, DECK_Y, 13],
] as const;
/** The laser emitter's lens (a lathe profile along its axis), at the bow. */
const LENS = [
  [0, 0],
  [4, 1.2],
  [3.4, 3.4],
  [0, 4.4],
] as const;
/** Where the emitter's barrel starts, and the twin guns' barrels. */
const EMITTER: Vec3 = [0, 6, 68];
const GUNS: Vec3 = [9, 9.5, 58];

/** The hull, its orange-lit rim, the forecastle, frost and icicles along its sides. */
function drawHull({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(HULL, HULL_Y, [3, 2], H.base, {}, H.panel);
  hull.bevelSlab(FORECASTLE, [DECK_Y - 1, DECK_Y, FORECASTLE_TOP], [0, 1], H.panel, {}, RIME);
  snowCap(
    hull,
    [
      [-12, 62],
      [12, 62],
      [17, 52],
      [-17, 52],
    ],
    FORECASTLE_TOP,
  );
  for (const s of SIDES) {
    edgeStrips(
      neon,
      [
        [s * 29.4, 28],
        [s * 29.6, 10],
        [s * 29.6, -40],
      ],
      0.8,
      [DECK_Y - 2, DECK_Y - 1],
      ORANGE_NEON,
    );
    seam(hull, [s * 26, 30], [s * 26, -54], [DECK_Y, 1, 0.8], H.dark);
    icicles(hull, spread([s * 30.5, -1, 20], [s * 30.5, -1, -50], 7), 5);
    icicles(hull, spread([s * 21, -1, 58], [s * 11, -1, 71], 3), 4);
  }
}

/** The bridge tower: a lofted block, dark windows lit as it charges, a funnel and a mast. */
function drawBridge(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  hull.loft(HULL_SECTION, BRIDGE, H.panel, {}, {});
  snowCap(hull, rect(16, 12), 17, { at: [0, 0, -1] });
  hull.box([22, 2.4, 1], H.dark, { at: [0, 13.4, 15.6], pitch: 0.4 });
  charge.box([18, 1, 0.6], WHITE, { at: [0, 14, 16.4], pitch: 0.4 });
  hull.cylinder(4.5, 9, 8, H.base, { at: [-6, 16, -9] }, 4);
  neon.ring(4.4, 1.2, 8, ORANGE_NEON, { at: [-6, 22, -9] });
  hull.cylinder(3.6, 0.5, 8, SHADE.soot, { at: [-6, 25, -9] });
  mast(p, [7, 17, -4], 9, ORANGE_NEON);
  lamps(neon, [[16, 9, 12]], 1.6, [1, 0.1, 0.12]);
  lamps(neon, [[-16, 9, 12]], 1.6, [0.2, 1, 0.35]);
}

/** The bow: the laser emitter, its neon rings, and the twin guns either side of it. */
function drawBow(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  hull.cylinder(5, 6, 8, H.dark, { at: EMITTER, pitch: QUARTER }, 4.2);
  neon.ring(5.1, 1, 8, ORANGE_NEON, { at: offset(EMITTER, 0, 0, 2), pitch: QUARTER });
  charge.lathe(LENS, 8, WHITE, { at: offset(EMITTER, 0, 0, 6), pitch: QUARTER });
  p.muzzle(offset(EMITTER, 0, 0, 10.4), 'laser');
  for (const s of SIDES) {
    hull.box([5, 3, 6], H.panel, { at: [s * GUNS[0], FORECASTLE_TOP, GUNS[2] - 2] }, RIME);
    barrels(p, [s * GUNS[0], GUNS[1], GUNS[2]], [1, 0], [1.2, 8]);
  }
}

/** The stern: the reactors and the hull's rudder fins. */
function drawStern(p: EnemyParts): void {
  for (const s of SIDES) {
    p.reactor([s * 12, 1.5, -66], 4);
    p.hull.box([1.4, 6, 8], H.panel, { at: [s * 21, -6, -62] });
  }
  p.reactor([0, 1.5, -66], 3);
}

/**
 * P08-R10: the Harbour Kraken, a cargo crane-ship with four crane arms swinging at the shoulder
 * and the elbow, a grab cannon hanging from each, orange neon, frost over its deck.
 */
export function buildHarbourKraken(scene: Scene): EnemyModel {
  return buildBossModel(HARBOUR_KRAKEN, scene, ORANGE_NEON, {
    core: (p) => {
      drawHull(p);
      drawBridge(p);
      drawBow(p);
      drawStern(p);
      hatchCovers(p);
      for (const end of ['fore', 'aft'] as const) {
        const [x, y] = CRANE_REST[end][0] ?? [0, 0];
        for (const s of SIDES) pedestal(p, offset(bossPoint(s * x, y), 0, DECK_Y, 0));
      }
    },
    parts: {
      'crane-fore-left': grab,
      'crane-fore-right': grab,
      'crane-aft-left': grab,
      'crane-aft-right': grab,
      'container-bay': containerBay,
    },
    limbs: craneLimbs(),
  });
}
