import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyModel } from '../../../../render/game-view';
import { GEYSER_RIG, RIG_CORE_GUNS } from '../../../config/bosses/world-4/geyser-rig';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { mirrored, strip } from '../final-boss-shapes';
import { hazard, lamps, vent } from '../mini-boss-greebles';
import { conduit } from '../mini-boss-mechanism';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { segment } from '../world-3/toucan-jungle';
import { ashDrift, EMBER, moltenSeam, SCORCH, sootStreaks } from './ash-plains-soot';
import { armLimbs, DECK_Y, drillHead, hangar, RIG_YELLOW, steamVent } from './geyser-rig-parts';
import { backRibs, glands, magmaVein, reactorSacs, SKIN } from './living-forge';

// P10-R11, 4-2: the Geyser Rig. Logical pixels, nose +Z, Y up (towards the camera). A flying
// drilling platform: a heavy deck, a lattice derrick in its middle (the core), two drill arms
// reaching forward from its bow corners, two steam vents at its stern, a drone hangar jutting
// from its bow and a squat cooling tower aft.
// P16-R06: a living rock-tick, its back a scorched flesh shell veined molten, a bone spire over
// its core, its drills, pipes and guns metal grafts.
type Vec3 = [number, number, number];

/** The deck seen from above (right half, bow to stern), its stern corners cut. */
const DECK: readonly OutlinePoint[] = mirrored([
  [0, 38],
  [30, 38],
  [44, 26],
  [44, -54],
  [34, -70],
  [0, -70],
]);

/** The derrick's corner posts: their foot on the deck and their top, half spread (x = z). */
const DERRICK = { foot: 9, top: 3, height: 42 } as const;
/** The squat cooling tower aft (a lathe profile, from the deck up), around its centre. */
const COOLING_TOWER = [
  [10, 0],
  [8.2, 5],
  [7.2, 9],
  [7.6, 12],
  [8.4, 14],
] as const;
const TOWER_AT: Vec3 = [0, DECK_Y, -50];

/** The pipe rack along the `s` side of the deck: two pipes on trestles, a valve wheel. */
function pipeRack(hull: EnemyParts['hull'], s: number): void {
  for (const z of [16, -2, -18]) hull.box([7, 3, 1.6], H.dark, { at: [s * 35, DECK_Y, z] });
  for (const dx of [-1.8, 1.8]) {
    conduit(hull, [s * (35 + dx), DECK_Y + 3.6, 20], [s * (35 + dx), DECK_Y + 3.6, -21], 1.1, 4);
  }
  hull.cylinder(2.4, 0.6, 8, SHADE.edge, { at: [s * 35, DECK_Y + 5, 4] });
}

/** Deck plates, a little proud of the deck: worn, lighter metal. */
const PLATES = [
  [-20, 26, 14, 10],
  [22, 28, 12, 8],
  [-26, -14, 10, 14],
  [24, -44, 12, 10],
  [-8, -36, 10, 8],
] as const;

/** P16-R05, P16-R06: its living flesh: veins, glands and ribs. */
function deckVeins(p: EnemyParts, s: number): void {
  magmaVein(
    p,
    [
      [s * 8, DECK_Y + 0.2, 22],
      [s * 20, DECK_Y + 0.2, 4],
      [s * 16, DECK_Y + 0.2, -40],
    ],
    1.3,
  );
  glands(
    p,
    [
      [s * 28, DECK_Y, -44],
      [s * 6, DECK_Y, 30],
    ],
    2,
    RIG_YELLOW,
  );
}

/** The deck: dark bevelled plates, yellow neon along its sides, hazard paint, ash and soot. */
function drawDeck(p: EnemyParts): void {
  const { hull, neon } = p;
  p.flesh.bevelSlab(DECK, [0, 3, DECK_Y], [2, 1.5], SKIN.base, {}, SKIN.dark);
  backRibs(p, [-40, -28, 28], { halfWidth: 30, y: DECK_Y - 2, height: 3.5, thickness: 1 });
  for (const s of SIDES) {
    deckVeins(p, s);
    strip(neon, [s * 41.6, 22], [s * 41.6, -52], 0.8, [DECK_Y, DECK_Y + 0.4], RIG_YELLOW);
    pipeRack(hull, s);
    hazard(hull, [s * 33, DECK_Y, 33], [14, 4], 5, s * 0.75);
    sootStreaks(
      hull,
      [
        [
          [s * 26, -38],
          [s * 30, -56],
        ],
        [
          [s * 18, -20],
          [s * 14, -42],
        ],
      ],
      DECK_Y,
      2,
    );
    moltenSeam(p, [s * 12, 4], [s * 24, -14], DECK_Y);
    moltenSeam(p, [s * 30, 12], [s * 38, -6], DECK_Y);
    vent(hull, [s * 22, DECK_Y, -2], [6, 9], 3);
    ashDrift(hull, [s * 36, DECK_Y, 10], 3.4, s * 1.1);
    ashDrift(hull, [s * 14, DECK_Y, -62], 3, s * 2.4);
    conduit(hull, [s * 27, DECK_Y + 2, -30], [s * 8, DECK_Y + 2, -12], 1.3, 3);
  }
  reactorSacs(
    p,
    [
      [18, 3.6, -68],
      [-18, 3.6, -68],
    ],
    3.2,
    EMBER,
  );
  reactorSacs(p, [[0, 3.6, -70]], 3.6, EMBER);
  for (const [x, z, w, d] of PLATES) {
    hull.box([w, 0.3, d], SHADE.edge, { at: [x, DECK_Y, z] }, H.panel);
  }
}

/**
 * The derrick (the core): a lattice tower of four posts braced crosswise, its crown block lit
 * yellow, the drill pipe glowing hot down its middle.
 */
function drawDerrick({ hull, neon, flesh }: EnemyParts): void {
  const { foot, top, height } = DERRICK;
  hull.box([26, 3, 26], H.panel, { at: [0, DECK_Y, 0] }, SCORCH);
  // P16-R06: a spire of bone, braced by sinews.
  const corners = [
    [1, 1],
    [1, -1],
    [-1, -1],
    [-1, 1],
  ] as const;
  const at = (x: number, z: number, k: number): Vec3 => {
    const spread = foot + (top - foot) * k;
    return [x * spread, DECK_Y + 3 + height * k, z * spread];
  };
  corners.forEach(([x, z], i) => {
    const [nx, nz] = corners[(i + 1) % 4] ?? [x, z];
    segment(flesh, [at(x, z, 0), at(x, z, 1)], [1.4, 0.8], SKIN.bone, 4);
    segment(flesh, [at(x, z, 0.08), at(nx, nz, 0.45)], [0.5, 0.5], SKIN.panel, 4);
    segment(flesh, [at(nx, nz, 0.08), at(x, z, 0.45)], [0.5, 0.5], SKIN.panel, 4);
    segment(flesh, [at(x, z, 0.45), at(nx, nz, 0.8)], [0.4, 0.4], SKIN.panel, 4);
  });
  hull.box([9, 4, 9], H.panel, { at: [0, DECK_Y + 3 + height, 0] }, H.base);
  neon.ring(5, 0.8, 8, RIG_YELLOW, { at: [0, DECK_Y + 4 + height, 0], yaw: Math.PI / 8 });
  lamps(neon, [[0, DECK_Y + 7.4 + height, 0]], 1.6, EMBER);
  neon.cylinder(1.1, height, 6, EMBER, { at: [0, DECK_Y + 3, 0] });
}

/** The drill floor's house at the derrick's foot, its twin fan guns pointing forward. */
function drawGunHouse({ hull, neon, charge, muzzle }: EnemyParts): void {
  hull.box([28, 8, 13], H.base, { at: [0, DECK_Y, 14] }, H.panel);
  strip(neon, [-12, 20.6], [12, 20.6], 0.7, [DECK_Y + 6.4, DECK_Y + 7.2], RIG_YELLOW);
  for (const tip of RIG_CORE_GUNS.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.cylinder(2.6, 2, 6, H.dark, { at: [x, y, z - 5], pitch: QUARTER });
    hull.cylinder(1.4, 3.4, 6, H.dark, { at: [x, y, z - 4], pitch: QUARTER });
    charge.cylinder(1.45, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/** The cooling tower aft: a squat flared stack, hot metal glowing in its mouth, ash on its rim. */
function drawCoolingTower({ hull, neon, flesh }: EnemyParts): void {
  flesh.lathe(COOLING_TOWER, 10, SKIN.panel, { at: TOWER_AT }, false);
  hull.cylinder(7.6, 0.4, 10, SHADE.soot, { at: offset(TOWER_AT, 0, 8, 0) });
  neon.ring(5.6, 1.2, 10, EMBER, { at: offset(TOWER_AT, 0, 8.2, 0) });
  neon.ring(8.5, 0.6, 10, RIG_YELLOW, { at: offset(TOWER_AT, 0, 12.6, 0) });
  ashDrift(hull, offset(TOWER_AT, 4, 14, 5), 2.2, 0.6);
}

/**
 * P10-R11: the Geyser Rig, a flying drilling rig with two drill heads and steam vents, yellow
 * neon, soot, ash and molten seams on its deck.
 */
export function buildGeyserRig(scene: Scene): EnemyModel {
  return buildBossModel(GEYSER_RIG, scene, RIG_YELLOW, {
    core: (p) => {
      drawDeck(p);
      drawDerrick(p);
      drawGunHouse(p);
      drawCoolingTower(p);
    },
    parts: {
      'drill-left': drillHead,
      'drill-right': drillHead,
      'vent-left': steamVent,
      'vent-right': steamVent,
      hangar,
    },
    limbs: armLimbs(),
  });
}
