import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import {
  AVALANCHE,
  AVALANCHE_ARM,
  AVALANCHE_CHUTE,
  AVALANCHE_CORE_GUNS,
} from '../../../config/bosses/world-2/avalanche';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import {
  angryEyes,
  canopyPaint,
  decal,
  FIGHTER_SECTION,
  sideStripe,
  SIDES,
} from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { hazard, lamps, plate, vent } from '../mini-boss-greebles';
import { GEAR } from '../mini-boss-mechanism';
import { H, neonBand, offset, QUARTER, SHADE, socket, WHITE } from '../mini-boss-shapes';
import { armLimbs, AVALANCHE_YELLOW as YELLOW, drill } from './avalanche-arms';
import { barrelTo, FROST, icicles, PACKED, snowCap } from './avalanche-frost';

// P08-R10, 2-4: the Avalanche. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** The chassis seen from above: a heavy, blunt-nosed hull between its two tracks. */
const CHASSIS = [
  [0, 33],
  [16, 31],
  [24, 23],
  [26, -8],
  [22, -30],
  [12, -36],
  [-12, -36],
  [-22, -30],
  [-26, -8],
  [-24, 23],
  [-16, 31],
] as const;
/** Heights of the chassis: its bottom, its waist, its deck. */
const DECK = [-4, 0, 7] as const;
/** The cab at the front (loft stations: z, half width, bottom, top). */
const CAB = [
  [4, 11, 6, 13],
  [12, 12, 6, 17],
  [20, 12, 6, 17.5],
  [27, 10, 6, 15],
  [32, 6, 6, 11],
] as const;
/** A track on each side: its centre across, its length and its height. */
const TRACK = { x: 31, z: -6, length: 58, height: 10 } as const;
/** The rock hopper's bin around its centre, and its heights (bottom, rim's foot, rim). */
const BIN = [
  [-15, -15],
  [15, -15],
  [13, 14],
  [-13, 14],
] as const;
const BIN_Y = [5, 8, 20] as const;
/** Rocks heaped in the bin: x, z, size, turn, and whether snow covers them. */
const ROCKS = [
  [-7, -6, 7, 0.3, true],
  [5, -8, 6, 1.1, false],
  [8, 4, 7.5, 0.6, true],
  [-6, 6, 6.5, 1.4, false],
  [0, -1, 8, 0.9, false],
] as const;

/** Snow caps on the deck and the cab's roof: outline, height, depth. */
const SNOW: readonly (readonly [readonly OutlinePoint[], number, number])[] = [
  [
    [
      [9, 2],
      [20, 0],
      [22, -14],
      [14, -18],
      [10, -10],
    ],
    DECK[2],
    1,
  ],
  [
    [
      [-12, -22],
      [-4, -20],
      [-2, -30],
      [-14, -32],
    ],
    DECK[2],
    0.8,
  ],
  [
    [
      [-4, 13],
      [6, 12],
      [8, 20],
      [-2, 21],
    ],
    17.3,
    0.8,
  ],
];
/** A weathered patch welded on the deck's right. */
const PATCH = [
  [-22, -6],
  [-15, -6],
  [-15, 4],
  [-21, 6],
] as const;

/** The chassis, its tracks, the cab and the engine deck. */
function drawBody(p: EnemyParts): void {
  const { hull, neon } = p;
  hull.bevelSlab(CHASSIS, DECK, [2, 2.2], H.base, {}, H.panel);
  neonBand(neon, CHASSIS, [-2.2, -0.6], [0.985, 1.02], YELLOW);
  hull.loft(FIGHTER_SECTION, CAB, H.base, {}, { paint: canopyPaint([1, 2], H.dark) });
  for (const side of [1, 6]) {
    const stripe = sideStripe(FIGHTER_SECTION, side, [0.3, 0.75]);
    neon.loft(stripe, CAB.slice(0, 3), YELLOW, {}, { open: true });
  }
  for (const eye of angryEyes([0, 30.5], 3, [5, 1.3], 0.3)) decal(neon, eye, 11.2, YELLOW);
  for (const s of SIDES) drawTrack(p, s);
  // The engine deck behind the cab, two exhaust stacks sooted at their tops.
  hull.box([26, 6, 18], H.panel, { at: [0, DECK[2], -9] }, H.base);
  vent(hull, [0, DECK[2] + 6.1, -9], [14, 10], 4);
  for (const s of SIDES) {
    hull.cylinder(2.4, 13, 6, H.dark, { at: [s * 10, DECK[2] + 4, -15] }, 2);
    hull.cylinder(2.1, 1.5, 6, SHADE.soot, { at: [s * 10, DECK[2] + 17, -15] });
    lamps(neon, [[s * 13.5, DECK[2] + 6, -2]], 1.4, YELLOW);
  }
}

/** A track on side `s`: its belt, fender, road wheels and the packed snow in its treads. */
function drawTrack({ hull }: EnemyParts, s: number): void {
  const x = s * TRACK.x;
  hull.box([9, TRACK.height, TRACK.length], H.dark, { at: [x, -6, TRACK.z] }, GEAR);
  hull.bevelSlab(
    [
      [x - 5.5, TRACK.z - TRACK.length / 2 + 3],
      [x + 5.5, TRACK.z - TRACK.length / 2 + 3],
      [x + 5.5, TRACK.z + TRACK.length / 2 - 2],
      [x - 5.5, TRACK.z + TRACK.length / 2 - 2],
    ],
    [3.5, 4.5, 6.5],
    [0.4, 1],
    H.base,
    {},
    H.panel,
  );
  // Snow drifted on the fender's rear half, packed into the treads at the front.
  snowCap(
    hull,
    [
      [x - 4.5, TRACK.z - 24],
      [x + 4.5, TRACK.z - 22],
      [x + 4, TRACK.z - 4],
      [x - 4, TRACK.z - 9],
    ],
    6.5,
    0.8,
  );
  for (let i = 0; i < 4; i++) {
    const z = TRACK.z - 21 + i * 14;
    hull.cylinder(3.6, 1.2, 6, H.panel, { at: [x + s * 4.6, -1.5, z], roll: -s * QUARTER });
  }
  hull.box([9.4, 2, 5], PACKED, { at: [x, -2, TRACK.z + TRACK.length / 2 - 3] });
}

/** Frost over the deck, icicles under the nose and along the flanks, hazard paint, sockets. */
function drawFrost({ hull }: EnemyParts): void {
  for (const [outline, y, thick] of SNOW) snowCap(hull, outline, y, thick);
  const nose: Vec3[] = [-14, -8, -2, 4, 10, 15].map((x) => [
    x,
    DECK[0] + 0.5,
    31.5 - Math.abs(x) * 0.12,
  ]);
  icicles(hull, nose, 4.5);
  for (const s of SIDES) {
    const flank: Vec3[] = [
      [s * 24, DECK[0] + 0.5, 12],
      [s * 25, DECK[0] + 0.5, 0],
    ];
    icicles(hull, flank, 3.5);
    const [x, y] = AVALANCHE_ARM.shoulder;
    socket(hull, bossPoint(s * x, y, DECK[2]), 6, 1.5);
  }
  hazard(hull, [0, DECK[2] - 0.2, 29], [14, 3], 5);
  plate(hull, PATCH, [DECK[2], 0.6], SHADE.patch);
}

/** The core's twin guns under the cab's chin, on a mount. */
function drawGuns(p: EnemyParts): void {
  p.hull.box([18, 4, 7], H.dark, { at: [0, 3, 28] }, H.panel);
  for (const tip of AVALANCHE_CORE_GUNS) barrelTo(p, tip, [1.7, 9]);
  p.charge.box([8, 0.6, 2], WHITE, { at: [0, 17.6, 15] });
}

/**
 * P08-R10: the Avalanche, a heavy drilling machine 3.5 L across, yellow neon: a tracked chassis
 * crusted with snow and icicles, a cab at its nose, two drill arms swinging in front of it and a
 * rock hopper heaped with ice and stone on its back.
 */
export function buildAvalanche(scene: Scene): EnemyModel {
  return buildBossModel(AVALANCHE, scene, YELLOW, {
    core: (p) => {
      drawBody(p);
      drawFrost(p);
      drawGuns(p);
      for (const s of SIDES) p.reactor([s * 16, 2, -36.5], 3.4);
    },
    parts: { 'drill-left': drill, 'drill-right': drill, hopper },
    limbs: { ...armLimbs('left'), ...armLimbs('right') },
  });
}

/**
 * The rock hopper (P08-R10): a bin on struts, heaped with rocks and snow, a yellow band round
 * its rim and a chute at its front, where its rocks drop from.
 */
function hopper(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge } = p;
  const bin = BIN.map(([x, z]): OutlinePoint => [x + at[0], z + at[2]]);
  hull.bevelSlab(bin, BIN_Y, [2.5, 0.8], H.base, {}, H.panel);
  hull.box([22, 1, 22], H.dark, { at: offset(at, 0, BIN_Y[2] - 1, 0) });
  neonBand(neon, BIN, [BIN_Y[2] - 2.5, BIN_Y[2] - 1.2], [1.01, 1.02], YELLOW, { at });
  for (const [x, z, size, turn, snowy] of ROCKS) {
    hull.box(
      [size, size * 0.6, size * 0.8],
      snowy ? FROST : PACKED,
      {
        at: offset(at, x, BIN_Y[2] - 1.5, z),
        yaw: turn,
        roll: turn * 0.3,
      },
      snowy ? FROST : H.panel,
    );
  }
  const [chute] = AVALANCHE_CHUTE;
  if (chute) {
    const lip = bossPoint(...chute);
    hull.box([9, 2, 5], H.dark, { at: offset(lip, 0, -1.5, -2.5), pitch: -0.3 }, GEAR);
    charge.box([6, 0.5, 1.2], WHITE, { at: offset(lip, 0, -0.5, -0.8) });
    p.muzzle(lip);
  }
  for (const s of SIDES) hull.box([2, 6, 2], GEAR, { at: offset(at, s * 10, 0, 6) });
  icicles(
    hull,
    [offset(at, -11, BIN_Y[0], -13), offset(at, 0, BIN_Y[0], -13.5), offset(at, 10, BIN_Y[0], -13)],
    4,
  );
}
