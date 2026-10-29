import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import { CRANE_REST, HARBOUR_KRAKEN } from '../../../config/bosses/world-2/harbour-kraken';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { HULL_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { buildBossModel } from '../boss-model';
import { bossPoint } from '../boss-limbs';
import { barrels, edgeStrips, mirrored } from '../final-boss-shapes';
import { lamps, mast, plate, rect } from '../mini-boss-greebles';
import { organ } from '../../../../render/geometry/organic';
import { reactorSac } from '../../enemies/organic-parts';
import { crystals, fringe, glowVein, ICE_FLESH, shell } from './w2-organic';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { icicles, snowCap, spread } from './fjord-lynx-frost';
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
function drawHull(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R06: the mantle of a great kraken, cold crimson flesh under a ridged shell.
  flesh.bevelSlab(HULL, HULL_Y, [3, 2], ICE_FLESH.crimson, {}, ICE_FLESH.purple);
  shell(
    flesh,
    { tail: -64, nose: 46, segments: 6, width: 22, bottom: DECK_Y - 1, top: 11 },
    ICE_FLESH.purple,
  );
  flesh.bevelSlab(
    FORECASTLE,
    [DECK_Y - 1, DECK_Y, FORECASTLE_TOP],
    [0, 1],
    ICE_FLESH.sinew,
    {},
    ICE_FLESH.rime,
  );
  plate(hull, rect(14, 8), [FORECASTLE_TOP, 0.6], H.panel, { at: [0, 0, 56] });
  snowCap(
    flesh,
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
    glowVein(p, [s * 8, 11, 30], [s * 26, DECK_Y, -50], 1.2, ORANGE_NEON);
    fringe(flesh, [s * 29, -2, -30], [s, -0.3], 3, 9, ICE_FLESH.crimson);
    icicles(flesh, spread([s * 30.5, -1, 20], [s * 30.5, -1, -50], 7), 5);
    icicles(flesh, spread([s * 21, -1, 58], [s * 11, -1, 71], 3), 4);
    crystals(flesh, [s * 16, 10, -40], 4);
  }
}

/** The bridge tower: a lofted block, dark windows lit as it charges, a funnel and a mast. */
function drawBridge(p: EnemyParts): void {
  const { hull, flesh, neon, charge } = p;
  // The head amidships, its great eyes across its brow.
  flesh.loft(HULL_SECTION, BRIDGE, ICE_FLESH.purple, {}, {});
  snowCap(flesh, rect(16, 12), 17, { at: [0, 0, -1] });
  flesh.box([22, 2.4, 1], ICE_FLESH.seam, { at: [0, 13.4, 15.6], pitch: 0.4 });
  for (const s of SIDES) organ(p.vein, 2.2, 6, ORANGE_NEON, { at: [s * 11, 12, 12] }, 0.6);
  charge.box([18, 1, 0.6], WHITE, { at: [0, 14, 16.4], pitch: 0.4 });
  flesh.cylinder(4.5, 9, 6, ICE_FLESH.sinew, { at: [-6, 16, -9] }, 3);
  neon.ring(4.4, 1.2, 8, ORANGE_NEON, { at: [-6, 22, -9] });
  hull.cylinder(3.6, 0.5, 8, SHADE.soot, { at: [-6, 25, -9] });
  mast(p, [7, 17, -4], 9, ORANGE_NEON);
  lamps(neon, [[16, 9, 12]], 1.6, [1, 0.1, 0.12]);
  lamps(neon, [[-16, 9, 12]], 1.6, [0.2, 1, 0.35]);
}

/** The bow: the laser emitter, its neon rings, and the twin guns either side of it. */
function drawBow(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  // The beak, a metal emitter grafted in it.
  organ(p.flesh, 6, 6, ICE_FLESH.bone, { at: offset(EMITTER, 0, 0, -6), pitch: QUARTER }, 0.6);
  hull.cylinder(5, 6, 8, H.dark, { at: EMITTER, pitch: QUARTER }, 4.2);
  neon.ring(5.1, 1, 8, ORANGE_NEON, { at: offset(EMITTER, 0, 0, 2), pitch: QUARTER });
  charge.lathe(LENS, 8, WHITE, { at: offset(EMITTER, 0, 0, 6), pitch: QUARTER });
  p.muzzle(offset(EMITTER, 0, 0, 10.4), 'laser');
  for (const s of SIDES) {
    hull.box([5, 3, 6], H.panel, { at: [s * GUNS[0], FORECASTLE_TOP, GUNS[2] - 2] }, H.base);
    barrels(p, [s * GUNS[0], GUNS[1], GUNS[2]], [1, 0], [1.2, 8]);
  }
}

/** The stern: the reactors and the hull's rudder fins. */
function drawStern(p: EnemyParts): void {
  for (const s of SIDES) {
    reactorSac(p, [s * 12, 1.5, -66], 4, ORANGE_NEON, { flesh: ICE_FLESH.purple });
    p.flesh.box([1.4, 6, 8], ICE_FLESH.sinew, { at: [s * 21, -6, -62] });
  }
  reactorSac(p, [0, 1.5, -66], 3, ORANGE_NEON, { flesh: ICE_FLESH.crimson });
}

/**
 * P08-R10: the Harbour Kraken, a cargo crane-ship with four crane arms swinging at the shoulder
 * and the elbow, a grab cannon hanging from each, orange neon, frost over its deck.
 * P16-R06: now a living kraken, a shelled mantle of cold flesh with a head and beak amidships,
 * four tentacles ending in clawed gun-fists, a brood sac of eggs at its stern.
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
