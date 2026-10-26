import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  EMBER_CROWN,
  EMBER_GUNS,
  EMBER_HERALD,
  EMBER_LANCE,
} from '../../../config/bosses/world-4/ember-herald';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, canopyPaint, FIGHTER_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { seam, vent } from '../mini-boss-greebles';
import { H, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { edgeLights, symmetric } from '../overlord-city';
import { emberLance, embers, GOLD, HEAT, spike } from './ember-herald-parts';

// P10-R11, 4-5: the Ember Herald, the mini boss of the Caldera. Model space: logical pixels,
// nose +Z (down the screen), Y up towards the camera; +X is the screen's left.
type Vec3 = [number, number, number];

/** The fuselage (loft stations, tail to nose): a long, hard-edged body closing to a needle nose. */
const FUSELAGE = [
  [-54, 6, 0, 6],
  [-40, 9, 0, 9.5],
  [-14, 11, 0, 11],
  [14, 9.5, 0, 10],
  [36, 6.5, 0.5, 7.5],
  [50, 3.5, 1.5, 4.5],
  [60, 0, 2.6, 2.6],
] as const;
/** The fuselage's back (sides of its section), sooted behind the canopy. */
const BACK = new Set([2, 3, 4, 5]);

/**
 * The spiky wings seen from above (right half, front to tail): a forward spike off the wing
 * root, a long spike at the tip, a sawtooth trailing edge and a spike at the tail.
 */
const WING = symmetric([
  [6, 34],
  [14, 16],
  [28, 7],
  [50, 14],
  [38, -2],
  [57, -24],
  [45, -24],
  [36, -33],
  [30, -46],
  [20, -36],
  [8, -40],
]);
/** Heights of the wing: belly, edge, top. */
const WING_Y = [-2.5, 0, 2.5] as const;
/** Its leading edges, lit gold (edges of {@link WING}, from point i to the next). */
const LEADING = [0, 1, 2, 4, 16, 18, 19, 20];
/** The molten seams cracking across the right wing's top, `[x, z]` from and to. */
const SEAMS = [
  [
    [12, 8],
    [30, 1],
  ],
  [
    [30, 1],
    [44, -16],
  ],
  [
    [22, -6],
    [26, -30],
  ],
  [
    [30, 1],
    [40, 6],
  ],
] as const satisfies readonly (readonly [OutlinePoint, OutlinePoint])[];

/** The spire over the core (lathe profile), rising through the ring's hub to its lit crown. */
const SPIRE = [
  [6, 0],
  [5, 6],
  [2.6, 12],
] as const;
const SPIRE_BASE = 9;
const CROWN = [
  [2.4, 0],
  [0, EMBER_CROWN[2] - SPIRE_BASE - 12],
] as const;

/** The ring: its rim (lathe profile), the hub round the spire and its spokes. */
const RIM = [
  [EMBER_LANCE.orbit - 2.6, 8.6],
  [EMBER_LANCE.orbit + 2.6, 8.6],
  [EMBER_LANCE.orbit + 3.2, 9.6],
  [EMBER_LANCE.orbit + 2, 10.4],
  [EMBER_LANCE.orbit - 2, 10.4],
  [EMBER_LANCE.orbit - 2.6, 8.6],
] as const;
const HUB = [
  [6.5, 11],
  [8.6, 11],
  [9, 12.6],
  [6.5, 13.2],
  [6.5, 11],
] as const;
const SPOKE: OutlinePoint[] = [
  [-1.8, 8],
  [1.8, 8],
  [1.2, EMBER_LANCE.orbit - 2],
  [-1.2, EMBER_LANCE.orbit - 2],
];

/** The fuselage, soot-black behind its canopy, gold strips down its flanks, reactors aft. */
function drawFuselage({ hull, neon, reactor }: EnemyParts): void {
  const canopy = canopyPaint([3, 4], H.dark);
  // Soot over its back behind the canopy, from the reactors' heat.
  const paint = (side: number, band: number) =>
    canopy(side, band) ?? (band < 2 && BACK.has(side) ? HEAT.soot : undefined);
  hull.loft(FIGHTER_SECTION, FUSELAGE, H.base, {}, { paint });
  for (const s of SIDES) {
    neon.box([0.5, 0.5, 34], GOLD, { at: [s * 9.4, 4, 4], yaw: s * 0.07 });
    neon.box([0.5, 0.4, 16], HEAT.molten, { at: [s * 4.6, 7.4, 38], yaw: -s * 0.1 });
    reactor([s * 4, 3.6, -55], 3);
    reactor([s * 11, 2.4, -50], 2.2);
    vent(hull, [s * 5.5, 9, -32], [4, 8], 3, 0);
  }
  seam(hull, [0, -50], [0, -16], [11.05, 0.8, 0.4], H.dark);
}

/** The spiky wings: soot-dark tops cracked with molten seams, gold leading edges, spikes. */
function drawWings(p: EnemyParts): void {
  const { hull, neon } = p;
  hull.bevelSlab(WING, WING_Y, [0.6, 0.8], H.base, {}, HEAT.blued);
  edgeLights(neon, WING, LEADING, [-1.2, -0.2], GOLD);
  for (const s of SIDES) {
    for (const [[ax, az], [bx, bz]] of SEAMS) {
      const [dx, dz] = [s * (bx - ax), bz - az];
      neon.box([0.7, 0.3, Math.hypot(dx, dz)], HEAT.molten, {
        at: [(s * (ax + bx)) / 2, WING_Y[2], (az + bz) / 2],
        yaw: Math.atan2(dx, dz),
      });
    }
    spike(p, [s * 52, WING_Y[2] - 0.5, -21], [QUARTER + 0.15, 0, Math.PI - s * 0.6], [1.6, 9]);
    spike(p, [s * 46, WING_Y[2] - 0.5, 11], [QUARTER - 0.1, 0, s * 0.9], [1.4, 7]);
    spike(p, [s * 28, WING_Y[2] - 0.5, -42], [QUARTER, 0, Math.PI - s * 0.25], [1.3, 6]);
    hull.box([1, 7, 12], H.panel, { at: [s * 12, 4, -36], roll: s * 0.45 }, HEAT.soot);
    neon.box([0.5, 0.5, 10], GOLD, { at: [s * 15, 10.2, -36], roll: s * 0.45 });
  }
}

/** The dorsal spikes down its back, leaning aft. */
function drawSpikes(p: EnemyParts): void {
  [
    [-22, 3],
    [-30, 3.6],
    [-38, 3],
  ].forEach(([z = 0, size = 3], i) => {
    spike(p, [0, 9.8 - i * 0.6, z], [-0.7, 0, 0], [size * 0.5, size * 2.6]);
  });
}

/** The twin ember cannons under the nose, their tips at the design's muzzles. */
function drawNoseGuns({ hull, charge, muzzle }: EnemyParts): void {
  for (const m of EMBER_GUNS) {
    const [x, y, z]: Vec3 = bossPoint(...m);
    const along = (dz: number): Placement => ({ at: [x, y, z - dz], pitch: QUARTER });
    hull.cylinder(1.5, 15, 6, H.dark, along(18), 1.1);
    hull.cylinder(2.3, 5, 6, SHADE.edge, along(20));
    charge.cylinder(1.2, 3, 6, WHITE, along(3), 0.5);
    muzzle([x, y, z]);
  }
}

/** The spire over the core, its crown glowing where its spirals leave from. */
function drawSpire({ hull, neon, charge, muzzle }: EnemyParts): void {
  hull.lathe(SPIRE, 6, H.panel, { at: [0, SPIRE_BASE, 0] });
  neon.ring(5.4, 0.8, 6, GOLD, { at: [0, SPIRE_BASE + 5, 0] });
  charge.lathe(CROWN, 6, WHITE, { at: [0, SPIRE_BASE + 12, 0] });
  muzzle(bossPoint(...EMBER_CROWN), 'ring');
}

/** The core body: fuselage, wings, spikes, nose guns, spire and the embers round it. */
function drawCore(p: EnemyParts): void {
  drawFuselage(p);
  drawWings(p);
  drawSpikes(p);
  drawNoseGuns(p);
  drawSpire(p);
  embers(p.neon);
}

/** The turning ring (P10-R11): a soot-black rim lit gold, held by three spokes from the hub. */
function drawRing({ hull, neon }: EnemyParts): void {
  const r = EMBER_LANCE.orbit;
  hull.lathe(RIM, 18, H.base, {}, false);
  hull.ring(r + 1.6, 0.3, 18, HEAT.soot, { at: [0, 10.4, 0] });
  neon.ring(r + 3.3, 0.7, 18, GOLD, { at: [0, 8.8, 0] });
  neon.ring(r - 2.7, 0.5, 18, HEAT.molten, { at: [0, 9, 0] });
  hull.lathe(HUB, 8, H.panel, {}, false);
  neon.ring(9.1, 0.5, 8, GOLD, { at: [0, 11.6, 0] });
  for (const a of around(3)) {
    const yaw = a + Math.PI / 3;
    hull.bevelSlab(SPOKE, [10, 10.6, 11.4], [0.2, 0.5], H.panel, { yaw }, HEAT.soot);
  }
}

/**
 * P10-R11: the Ember Herald, a fast, spiky interceptor (3.5 L) wreathed in embers, gold neon:
 * spiked wings cracked with molten seams, a spire over the core, and a ring turning over it
 * carrying three ember lances.
 */
export function buildEmberHerald(scene: Scene): EnemyModel {
  const lances = Object.fromEntries(
    EMBER_HERALD.stats.parts.map((part) => [
      part.id,
      (parts: EnemyParts, at: Vec3) => {
        emberLance(parts, EMBER_HERALD.guns[part.id]?.gun ?? [], at);
      },
    ]),
  );
  return buildBossModel(EMBER_HERALD, scene, GOLD, {
    core: drawCore,
    ring: drawRing,
    parts: lances,
  });
}
