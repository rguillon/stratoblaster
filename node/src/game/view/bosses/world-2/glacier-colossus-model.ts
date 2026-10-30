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
import { lamps, mast, plate, rect, vent } from '../mini-boss-greebles';
import { ribs } from '../../../../render/geometry/organic';
import { eyes, reactorSac } from '../../enemies/organic-parts';
import { crystals, glowVein, ICE_FLESH, shell, spineRow } from './w2-organic';
import { H, neonBand, offset, scaled, SHADE, WHITE } from '../mini-boss-shapes';
import { barrelTo, FROST, icicles, PACKED, snowCap } from './avalanche-frost';
import {
  COLOSSUS_NEON as N,
  cutter,
  cutterMount,
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
  const { hull, flesh, neon } = p;
  // P16-R06: a glacier titan, a vast body of cold flesh under a ridged shell, its brain hump
  // where the bridge tower was, eyes round it.
  flesh.bevelSlab(HULL, HULL_Y, [3, 2.5], ICE_FLESH.sinew, {}, ICE_FLESH.teal);
  neonBand(neon, HULL, [-3.6, -1.2], [0.985, 1.015], N);
  flesh.bevelSlab(UPPER, UPPER_Y, [0, 1.6], ICE_FLESH.teal, {}, ICE_FLESH.purple);
  shell(flesh, { tail: -58, nose: 6, segments: 5, width: 26, bottom: UPPER_Y[2] - 1, top: 24 });
  flesh.bevelSlab(TOWER, TOWER_Y, [0, 4], ICE_FLESH.purple, {}, ICE_FLESH.rime);
  neonBand(flesh, TOWER, [22, 24.5], [1.02, 1.02], ICE_FLESH.seam);
  eyes(p, [0, 23, 28.4], { count: 4, size: 1.2, spacing: 5 }, N);
  neonBand(neon, TOWER, [25, 25.8], [1.02, 1.02], N);
  for (const tip of COLOSSUS_CORE_GUNS) barrelTo(p, tip, [2, 8]);
  for (const s of SIDES) {
    // The pylons out to the cutters (they stay when a cutter is gone).
    flesh.box([16, 5, 12], ICE_FLESH.sinew, { at: [s * 64, 1, 10] }, ICE_FLESH.rime);
    hull.box([6, 6, 13], H.panel, { at: [s * 60, 1, 10] }, H.base);
    reactorSac(p, [s * 16, 2, -78], 5, N, { flesh: ICE_FLESH.purple });
    p.reactor([s * 38, 2, -70], 4.5);
  }
}

/** The heat stack behind the tower, glowing at its top: the core's rings leave from there. */
function drawStack(p: EnemyParts): void {
  const [ring] = COLOSSUS_STACK;
  if (!ring) return;
  const top = bossPoint(...ring);
  const foot = offset(top, 0, -16, 0);
  // A spiracle of flesh breathing heat, a metal ring grafted round its mouth.
  p.flesh.cylinder(9, 13, 7, ICE_FLESH.crimson, { at: foot, yaw: Math.PI / 8 }, 7);
  p.hull.ring(7.9, 2, 8, H.panel, { at: offset(foot, 0, 12, 0), yaw: Math.PI / 8 });
  p.neon.ring(7.8, 1.2, 8, N, { at: offset(foot, 0, 10.5, 0), yaw: Math.PI / 8 });
  p.charge.cylinder(5.5, 3, 8, WHITE, { at: offset(top, 0, -3, 0) }, 2.5);
  p.muzzle(top, 'ring');
  for (const s of SIDES) {
    p.flesh.cylinder(3, 9, 5, ICE_FLESH.sinew, { at: offset(foot, s * 12, 0, -4) }, 2.4);
    p.hull.cylinder(2.7, 1, 6, SHADE.soot, { at: offset(foot, s * 12, 9, -4) });
  }
}

/** The heat vents along the deck: dark grilles glowing red-orange between their slats. */
function drawVents(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    // Veins out from the shell to the rim; the vents are gill slits glowing between metal grilles.
    for (const [z0, z1] of [
      [20, 24],
      [-48, -54],
    ] as const) {
      glowVein(p, [s * 30, HULL_Y[2] + 2, z0], [s * 58, HULL_Y[2], z1], 1.3, N);
    }
    for (const z of VENTS_Z) {
      const at: Vec3 = [s * VENT_X, HULL_Y[2] - 0.2, z];
      neon.box([8, 0.5, 8.5], N, { at: offset(at, 0, 0.1, 0) });
      vent(hull, at, [10, 10], 4);
    }
  }
}

/** The frost: snow caps on the decks and the tower's roof, icicles under the hull's rim. */
function drawFrost({ flesh: hull }: EnemyParts): void {
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
  const { hull, flesh } = p;
  for (const s of SIDES) {
    // Glacier ice grown through the flesh on the stern, crystals over the shell.
    crystals(flesh, [s * 38, HULL_Y[2], -57], 9, 4);
    crystals(flesh, [s * 20, UPPER_Y[2] + 4, -20], 5);
    ribs(
      flesh,
      [s * 46],
      { halfWidth: 4, y: HULL_Y[2], height: 3, thickness: 0.8 },
      ICE_FLESH.bone,
    );
    lamps(p.neon, [[s * 60, HULL_Y[2], -8]], 1.8, N);
  }
  plate(hull, rect(18, 8), [HULL_Y[2], 1], H.panel, { at: [0, 0, 33] });
  plate(hull, PATCH, [UPPER_Y[2], 0.6], SHADE.patch);
  spineRow(flesh, [0, 24, -6], [0, 22, -50], 5, 5);
  mast(p, [8, TOWER_Y[2], 12], 8, N);
  mast(p, [-24, UPPER_Y[2], -54], 6, N);
}

/**
 * P08-R10: the Glacier Colossus, a giant mining ship 5.5 L across, red-orange neon, glowing heat
 * vents along its deck, crusted with snow and hung with icicles; its cutters out on its beam,
 * its ore cannons and heat sink at its bow, its missile pod on its stern.
 * P16-R06: now a living glacier titan, a vast shelled body of cold flesh with glacier ice grown
 * through it, gills glowing down its back; its parts armoured organs and fleshy gun limbs.
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
      'cutter-left': cutterMount,
      'cutter-right': cutterMount,
      'ore-left': oreCannon,
      'ore-right': oreCannon,
      'heat-sink': heatSink,
      'missile-pod': missilePod,
    },
    turrets: { 'cutter-left': cutter, 'cutter-right': cutter },
  });
}
