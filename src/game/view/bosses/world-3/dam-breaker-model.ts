import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import { DAM_BREAKER, DAM_CORE_GUNS, DAM_STACK } from '../../../config/bosses/world-3/dam-breaker';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { reactorSac } from '../../enemies/organic-parts';
import { ribs, ROUND_SECTION } from '../../../../render/geometry/organic';
import { F, JUNGLE_FLESH, veinTo } from './jungle-flesh';
import { bossPoint, buildBossModel } from '../boss-model';
import { barrels, edgeStrips, mirrored } from '../final-boss-shapes';
import { rod } from '../final-boss-greebles';
import { conduit } from '../mini-boss-mechanism';
import { hazard, lamps, seam, vent } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { DECK_Y, hangar, moss, plate, RUST, sluice, tank, TOXIC, vines } from './dam-breaker-parts';

// P09-R09, 3-4: the Dam Breaker. Logical pixels, nose +Z, Y up (towards the camera). A giant
// armoured barge: a long, flat hull, the pump house amidships with its stack, two sluice gate
// houses either side of the bow, the armour plate and the drone hangar on the bow, the chemical
// tanks on outriggers at its sides, rust, moss and vines all over.
type Vec3 = [number, number, number];

/** The hull seen from above (right half, bow to stern). */
const HULL = mirrored([
  [0, 74],
  [22, 72],
  [40, 64],
  [54, 48],
  [58, 30],
  [58, -52],
  [52, -66],
  [36, -72],
  [0, -72],
]);
/** Heights of the hull: its keel, its rim, its deck. */
const HULL_Y = [-8, -1, DECK_Y] as const;
/** The pump house amidships (loft stations along Z: z, half width, bottom, top). */
const PUMP_HOUSE = [
  [-22, 16, DECK_Y, 14],
  [-6, 20, DECK_Y, 18],
  [10, 18, DECK_Y, 17],
  [18, 13, DECK_Y, 12],
] as const;
/** Where the stack stands on the pump house's back. */
const STACK_FOOT: Vec3 = [0, 17, -8];

/** The hull, its green-lit rim, rusty patches, deck seams, and the swamp growing over it. */
function drawHull(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R06: a giant, bloated swamp beast wallowing like a barge: a broad back of moss-skinned
  // flesh, its rusty plates, sluices and tanks grafted on, veins of toxin pulsing through it.
  flesh.bevelSlab(HULL, HULL_Y, [4, 2], F.sinew, {}, JUNGLE_FLESH);
  for (const s of SIDES) {
    veinTo(
      p,
      [
        [s * 8, DECK_Y + 0.3, 40],
        [s * 30, DECK_Y + 0.3, -60],
      ],
      [s * 14, 0, 0],
      TOXIC,
      1.6,
    );
  }
  for (const s of SIDES) {
    edgeStrips(
      neon,
      [
        [s * 57.4, 28],
        [s * 57.4, -50],
      ],
      0.8,
      [DECK_Y - 3, DECK_Y - 2],
      TOXIC,
    );
    for (const z of [-40, -20, 34]) seam(hull, [s * 6, z], [s * 54, z], [DECK_Y, 0.8, 0.4], H.dark);
    seam(hull, [s * 30, 46], [s * 30, -62], [DECK_Y, 0.8, 0.4], H.dark);
    hull.box([14, 0.4, 12], RUST, { at: [s * 40, DECK_Y, -46 + s * 6] });
    vines(hull, [
      [s * 58, DECK_Y, 20],
      [s * 58, DECK_Y, -4],
      [s * 58, DECK_Y, -36],
      [s * 56, DECK_Y, -58],
    ]);
  }
  moss(hull, [
    [-38, DECK_Y, -30],
    [44, DECK_Y, -58],
    [24, DECK_Y, 50],
    [-30, DECK_Y, 46],
    [12, DECK_Y, -64],
  ]);
  hazard(hull, [0, DECK_Y, 46], [40, 3], 10, 0);
}

/** The pump house: a lofted block, its windows lit as it charges, the stack and its pipes. */
function drawPumpHouse(p: EnemyParts): void {
  const { hull, flesh, neon, charge } = p;
  // P16-R06: the pump house a swollen hump of flesh over bone ribs, its stack grafted on.
  flesh.loft(ROUND_SECTION, PUMP_HOUSE, F.crimson);
  ribs(flesh, [-14, -2, 8], { halfWidth: 19, y: DECK_Y, height: 13.4, thickness: 0.9 }, F.bone);
  hull.box([30, 2.4, 1], H.dark, { at: [0, 13.6, 16.8], pitch: 0.5 });
  charge.box([26, 1, 0.6], WHITE, { at: [0, 14.1, 17.4], pitch: 0.5 });
  vent(hull, [10, 18, -12], [8, 7], 3);
  for (const s of SIDES) {
    neon.box([0.6, 0.4, 30], TOXIC, { at: [s * 19.4, 15.5, -4], yaw: s * 0.06 });
    conduit(hull, [s * 18, 10, -16], [s * 44, DECK_Y + 6, -10], 1.2, 3);
    conduit(hull, [s * 15, 8, 14], [s * 38, DECK_Y + 8, 20], 1, 2);
    lamps(neon, [[s * 14, 17.4, -20]], 1.4, TOXIC);
  }
  moss(hull, [
    [-8, 18, -16],
    [12, 17.4, 4],
  ]);
  rod(hull, [-12, 18, -16], [-12, 30, -16], 0.4);
  lamps(neon, [[-12, 30, -16]], 1, TOXIC);
}

/** The stack on the pump house's back, its top where the core's rings leave from. */
function drawStack({ hull, neon, charge, muzzle }: EnemyParts): void {
  const [top] = DAM_STACK.map((m) => bossPoint(...m));
  if (!top) return;
  const height = top[1] - STACK_FOOT[1];
  hull.cylinder(6, height - 1, 8, H.base, { at: STACK_FOOT }, 4.6);
  hull.ring(6.2, 1.6, 8, RUST, { at: offset(STACK_FOOT, 0, 3, 0) });
  neon.ring(4.8, 1, 8, TOXIC, { at: offset(top, 0, -2.4, 0) });
  charge.cylinder(3.6, 1, 8, WHITE, { at: offset(top, 0, -1, 0) });
  muzzle(top, 'ring');
}

/** The pump house's twin guns at its front (the core's aimed shots, bursts and fans). */
function drawGuns(p: EnemyParts): void {
  for (const tip of DAM_CORE_GUNS.map((m) => bossPoint(...m))) {
    const length = 7;
    const base: Vec3 = offset(tip, 0, 0, -length - 1.4);
    p.hull.box([5, 4, 6], H.base, { at: offset(base, 0, -2.4, -1) }, SHADE.edge);
    barrels(p, base, [1, 0], [1, length]);
  }
}

/** The stern: three reactors, a rudder housing and the dam-breaking ram's pistons. */
function drawStern(p: EnemyParts): void {
  for (const s of SIDES) {
    reactorSac(p, [s * 20, 0, -72], 4.5, TOXIC, { flesh: F.sinew });
    p.hull.box([1.6, 8, 10], H.panel, { at: [s * 40, -8, -64] });
  }
  reactorSac(p, [0, 0, -72], 4, TOXIC, { flesh: F.sinew });
  p.hull.box([30, 6, 8], H.base, { at: [0, DECK_Y, -64] }, SHADE.edge);
  p.neon.box([26, 0.5, 0.6], TOXIC, { at: [0, DECK_Y + 6, -59.8] });
}

/** A socket for each sluice and tank mount on the deck (left once the part is gone). */
function drawMounts({ hull }: EnemyParts): void {
  for (const s of SIDES) {
    hull.cylinder(9, 0.8, 8, H.dark, { at: [s * 46, DECK_Y, 20], yaw: Math.PI / 8 });
    hull.box([4, 2, 26], SHADE.edge, { at: [s * 56, DECK_Y - 4, -14], pitch: 0 });
  }
  hull.cylinder(1.2, 1, 4, H.dark, { at: [0, DECK_Y, 68], pitch: QUARTER });
}

/**
 * P09-R09: the Dam Breaker, a giant armoured barge with toxic green neon: sluice gate houses
 * letting out sludge, glowing chemical tanks at its sides, an armour plate and a drone hangar
 * on its bow, a pump house and its stack amidships, swamp growth over its rusty decks.
 */
export function buildDamBreaker(scene: Scene): EnemyModel {
  return buildBossModel(DAM_BREAKER, scene, TOXIC, {
    core: (p) => {
      drawHull(p);
      drawPumpHouse(p);
      drawStack(p);
      drawGuns(p);
      drawStern(p);
      drawMounts(p);
    },
    parts: {
      'sluice-left': sluice,
      'sluice-right': sluice,
      plate,
      'tank-left': tank,
      'tank-right': tank,
      hangar,
    },
  });
}
