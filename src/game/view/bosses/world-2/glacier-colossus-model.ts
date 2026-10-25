import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import {
  COLOSSUS_CORE_GUNS,
  COLOSSUS_STACK,
  GLACIER_COLOSSUS,
} from '../../../config/bosses/world-2/glacier-colossus';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { mirrored } from '../final-boss-shapes';
import { hazard, lamps, mast, plate, seam, vent } from '../mini-boss-greebles';
import { H, neonBand, offset, scaled, SHADE, WHITE } from '../mini-boss-shapes';
import { barrelTo, FROST, icicles, PACKED, snowCap } from './avalanche-frost';
import {
  COLOSSUS_NEON as N,
  cutter,
  heatSink,
  missilePod,
  oreCannon,
} from './glacier-colossus-parts';

// P08-R10, 2-4: the Glacier Colossus. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** The hull seen from above (its right half, bow to stern): a broad, blunt mining ship. */
const HULL = mirrored([
  [0, 62],
  [22, 58],
  [46, 44],
  [60, 22],
  [64, -6],
  [60, -40],
  [46, -66],
  [22, -78],
  [0, -78],
]);
/** Heights of the hull: its keel, its waist (the widest), its deck. */
const HULL_Y = [-8, 0, 10] as const;
/** The raised upper deck along the middle. */
const UPPER = mirrored([
  [0, 40],
  [18, 38],
  [30, 24],
  [32, -30],
  [24, -56],
  [0, -60],
]);
const UPPER_Y = [10, 11, 16] as const;
/** The bridge tower on the upper deck, ahead of the heat stack. */
const TOWER = [
  [-15, 8],
  [15, 8],
  [15, 24],
  [10, 28],
  [-10, 28],
  [-15, 24],
] as const;
const TOWER_Y = [16, 18, 28] as const;
/** The heat vents along each side of the deck (centres along Z, on the right at +X). */
const VENTS_Z = [-40, -26, -12, 2] as const;
const VENT_X = 45;

type Rgb = readonly [number, number, number];

/** Snow caps on the decks and the tower's roof: outline, height, colour. */
const SNOW: readonly (readonly [readonly OutlinePoint[], number, Rgb])[] = [
  [
    [
      [20, 44],
      [40, 40],
      [44, 30],
      [26, 36],
    ],
    HULL_Y[2],
    FROST,
  ],
  [
    [
      [-22, 50],
      [-36, 44],
      [-48, 34],
      [-30, 36],
    ],
    HULL_Y[2],
    FROST,
  ],
  [
    [
      [-50, 6],
      [-58, -6],
      [-56, -30],
      [-50, -24],
    ],
    HULL_Y[2],
    FROST,
  ],
  [
    [
      [48, -46],
      [56, -44],
      [54, -58],
      [48, -60],
    ],
    HULL_Y[2],
    FROST,
  ],
  [
    [
      [-12, 10],
      [12, 10],
      [10, 18],
      [-8, 20],
    ],
    TOWER_Y[2],
    FROST,
  ],
  [
    [
      [10, -30],
      [26, -28],
      [24, -48],
      [12, -50],
    ],
    UPPER_Y[2],
    PACKED,
  ],
];
/** A weathered patch welded on the upper deck's right. */
const PATCH = [
  [-26, -20],
  [-18, -20],
  [-18, -6],
  [-27, -8],
] as const;

/** The hull, its neon band, the upper deck and the bridge tower. */
function drawHull(p: EnemyParts): void {
  const { hull, neon } = p;
  hull.bevelSlab(HULL, HULL_Y, [3, 2.5], H.base, {}, H.panel);
  neonBand(neon, HULL, [-3.6, -1.2], [0.985, 1.015], N);
  hull.bevelSlab(UPPER, UPPER_Y, [0, 1.6], H.panel, {}, H.base);
  hull.bevelSlab(TOWER, TOWER_Y, [0, 1.4], H.base, {}, H.panel);
  // The bridge's windows: a dark band round the tower, a red-orange light above it.
  neonBand(hull, TOWER, [22, 24.5], [1.02, 1.02], H.dark);
  neonBand(neon, TOWER, [25, 25.8], [1.02, 1.02], N);
  for (const tip of COLOSSUS_CORE_GUNS) barrelTo(p, tip, [2, 8]);
  for (const s of SIDES) {
    // The pylons out to the cutters (they stay when a cutter is gone).
    hull.box([16, 5, 12], H.panel, { at: [s * 64, 1, 10] }, H.base);
    p.reactor([s * 16, 2, -78], 5);
    p.reactor([s * 38, 2, -70], 4.5);
  }
}

/** The heat stack behind the tower, glowing at its top: the core's rings leave from there. */
function drawStack(p: EnemyParts): void {
  const [ring] = COLOSSUS_STACK;
  if (!ring) return;
  const top = bossPoint(...ring);
  const foot = offset(top, 0, -16, 0);
  p.hull.cylinder(9, 13, 8, H.panel, { at: foot, yaw: Math.PI / 8 }, 7.5);
  p.neon.ring(7.8, 1.2, 8, N, { at: offset(foot, 0, 10.5, 0), yaw: Math.PI / 8 });
  p.charge.cylinder(5.5, 3, 8, WHITE, { at: offset(top, 0, -3, 0) }, 2.5);
  p.muzzle(top, 'ring');
  for (const s of SIDES) {
    p.hull.cylinder(3, 9, 6, H.dark, { at: offset(foot, s * 12, 0, -4) }, 2.6);
    p.hull.cylinder(2.7, 1, 6, SHADE.soot, { at: offset(foot, s * 12, 9, -4) });
  }
}

/** The heat vents along the deck: dark grilles glowing red-orange between their slats. */
function drawVents({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    // Seams between the deck's armour plates, out from the upper deck to the rim.
    for (const [z0, z1] of [
      [20, 24],
      [-48, -54],
    ] as const) {
      seam(hull, [s * 32, z0], [s * 58, z1], [HULL_Y[2] - 0.2, 1, 0.6], H.dark);
    }
    for (const z of VENTS_Z) {
      const at: Vec3 = [s * VENT_X, HULL_Y[2] - 0.2, z];
      neon.box([8, 0.5, 8.5], N, { at: offset(at, 0, 0.1, 0) });
      vent(hull, at, [10, 10], 4);
    }
  }
}

/** The frost: snow caps on the decks and the tower's roof, icicles under the hull's rim. */
function drawFrost({ hull }: EnemyParts): void {
  for (const [outline, y, color] of SNOW) snowCap(hull, outline, y, 1.2, color);
  const rim = scaled(HULL, 0.95);
  icicles(
    hull,
    rim.map(([x, z]): Vec3 => [x, HULL_Y[0] + 1.5, z]),
    6,
  );
}

/** Ore bins heaped with rock and snow on the stern, and wear: hazard paint, a patch, masts. */
function drawWear(p: EnemyParts): void {
  const { hull } = p;
  for (const s of SIDES) {
    hull.box([16, 5, 12], H.dark, { at: [s * 38, HULL_Y[2], -57] }, H.panel);
    hull.box([12, 3, 8], s > 0 ? FROST : PACKED, { at: [s * 38, HULL_Y[2] + 5, -57], yaw: 0.3 });
    hull.box([7, 3, 6], PACKED, { at: [s * 35, HULL_Y[2] + 6.5, -55], yaw: 1.1 });
    seam(hull, [s * 30, 26], [s * 30, -28], [UPPER_Y[2] - 0.2, 0.8, 0.6], SHADE.edge);
    lamps(p.neon, [[s * 60, HULL_Y[2], -8]], 1.8, N);
  }
  hazard(hull, [0, HULL_Y[2] - 0.2, 33], [18, 4], 6);
  plate(hull, PATCH, [UPPER_Y[2], 0.6], SHADE.patch);
  mast(p, [8, TOWER_Y[2], 12], 8, N);
  mast(p, [-24, UPPER_Y[2], -54], 6, N);
}

/**
 * P08-R10: the Glacier Colossus, a giant mining ship 5.5 L across, red-orange neon, glowing heat
 * vents along its deck, crusted with snow and hung with icicles; its cutters out on its beam,
 * its ore cannons and heat sink at its bow, its missile pod on its stern.
 */
export function buildGlacierColossus(scene: Scene): EnemyModel {
  return buildBossModel(GLACIER_COLOSSUS, scene, N, {
    core: (p) => {
      drawHull(p);
      drawStack(p);
      drawVents(p);
      drawFrost(p);
      drawWear(p);
    },
    parts: {
      'cutter-left': cutter,
      'cutter-right': cutter,
      'ore-left': oreCannon,
      'ore-right': oreCannon,
      'heat-sink': heatSink,
      'missile-pod': missilePod,
    },
  });
}
