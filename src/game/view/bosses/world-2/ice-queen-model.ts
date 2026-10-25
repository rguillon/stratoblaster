import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyModel } from '../../../../render/game-view';
import {
  ICE_QUEEN,
  ICE_QUEEN_NOSE_GUNS,
  ICE_QUEEN_SHARD,
  ICE_QUEEN_SPIRE,
} from '../../../config/bosses/world-2/ice-queen';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, FIGHTER_SECTION, flipX, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { seam, vent } from '../mini-boss-greebles';
import { H, QUARTER, WHITE } from '../mini-boss-shapes';
import { edgeLights } from '../overlord-city';
import { drawDetails } from './ice-queen-details';
import { crystal, FROST, iceShard, icicles, PALE_BLUE, VIOLET } from './ice-queen-shards';

// P08-R10, 2-5: the Ice Queen. Logical pixels, nose +Z (down the screen), Y up (towards the
// camera); +X is the screen's left.
type Vec3 = [number, number, number];

/** The fuselage (loft stations, tail to nose): long and slender, closing to a needle nose. */
const FUSELAGE = [
  [-56, 5, 0, 5],
  [-40, 8, -0.5, 8],
  [-10, 10, -1, 10],
  [20, 8, -0.5, 8.5],
  [42, 4.5, 0, 6],
  [58, 0, 2.5, 2.5],
] as const;
/** The fuselage's back (sides of the section), snowed over behind the canopy. */
const BACK = new Set([3, 4]);
const CANOPY = new Set([2, 3, 4, 5]);

/** The right wing (+X), swept far back from the fuselage, and a canard at the nose. */
const WING: OutlinePoint[] = [
  [7, 18],
  [46, -24],
  [47.5, -31],
  [41, -34],
  [7, -27],
];
const CANARD: OutlinePoint[] = [
  [4, 36],
  [15, 25],
  [15.5, 22],
  [4, 26],
];
const WING_TOP = 2.4;

/** The crystal spire over the core (a lathe profile) and the charge light at its tip. */
const SPIRE = [
  [5.5, 0],
  [4.6, 5],
  [2.6, 11],
  [0, 13.6],
] as const;
const SPIRE_BASE = 9;
const SPIRE_TIP = [
  [1.3, 0],
  [0, ICE_QUEEN_SPIRE[2] - SPIRE_BASE - 13.2],
] as const;

/** The crown ring: its rim (lathe profile), the hub round the spire and three spokes. */
const RIM = [
  [39.5, 10],
  [44, 10],
  [44.6, 11],
  [43.2, 12],
  [40.2, 12],
  [39.5, 10],
] as const;
const HUB = [
  [5.5, 12.5],
  [7.5, 12.5],
  [7.8, 14],
  [5.5, 14.6],
  [5.5, 12.5],
] as const;
const SPOKE: OutlinePoint[] = [
  [-1.6, 7],
  [1.6, 7],
  [1, 40],
  [-1, 40],
];

/** The fuselage, its snowed back and canopy, and the reactors at its tail. */
function drawFuselage({ hull, neon, reactor }: EnemyParts): void {
  hull.loft(
    FIGHTER_SECTION,
    FUSELAGE,
    H.base,
    {},
    {
      paint: (side, band) => {
        if (band === 3 && CANOPY.has(side)) return H.dark;
        return band < 3 && BACK.has(side) ? FROST.snow : undefined;
      },
    },
  );
  for (const s of SIDES) {
    neon.box([0.5, 0.5, 30], PALE_BLUE, { at: [s * 8.6, 4.5, 2], yaw: s * 0.06 });
    neon.box([0.5, 0.4, 18], VIOLET, { at: [s * 5.2, 6.4, 33], yaw: -s * 0.12 });
    reactor([s * 3.6, 3.4, -57], 2.8);
    reactor([s * 12.5, 2.6, -53], 2.2);
    vent(hull, [s * 5, 8.4, -30], [4, 7], 3, 0);
  }
  seam(hull, [0, -50], [0, -14], [10.05, 0.8, 0.4], H.dark);
}

/** The swept wings and canards: frosted tops, violet leading edges, crystals at the tips. */
function drawWings(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    const [wing, canard] = s > 0 ? [WING, CANARD] : [flipX(WING), flipX(CANARD)];
    hull.bevelSlab(wing, [0, 1.2, WING_TOP], [0.6, 1.4], H.base, {}, FROST.snow);
    edgeLights(neon, wing, [0], [0.6, 1.6], VIOLET);
    edgeLights(neon, wing, [1], [0.6, 1.6], PALE_BLUE);
    hull.bevelSlab(canard, [1.5, 2.4, 3.4], [0.3, 0.8], H.panel, {}, FROST.snow);
    edgeLights(neon, canard, [0], [2, 3], VIOLET);
    crystal(hull, [s * 44, WING_TOP, -29], [0, -0.35 * s, 0], [2.6, 9]);
    crystal(hull, [s * 26, WING_TOP, -20], [0, 0.4 * s, 0.3], [1.6, 5]);
    icicles(hull, s, [
      [12, -27.5],
      [20, -29],
      [28, -30.5],
      [36, -32],
    ]);
  }
}

/** The twin crystal cannons by the nose, their tips at the design's muzzles. */
function drawNoseGuns({ hull, charge, muzzle }: EnemyParts): void {
  for (const m of ICE_QUEEN_NOSE_GUNS) {
    const [x, y, z]: Vec3 = bossPoint(...m);
    const along = (dz: number) => ({ at: [x, y, z - dz] as Vec3, pitch: QUARTER });
    hull.cylinder(1.6, 14, 6, H.dark, along(17), 1.2);
    hull.cylinder(2.2, 5, 6, H.panel, along(19));
    charge.cylinder(1.3, 3, 6, WHITE, along(3), 0.5);
    muzzle([x, y, z]);
  }
}

/** The crystal spire over the core, glowing at its tip where its spiral leaves from. */
function drawSpire({ hull, neon, charge, muzzle }: EnemyParts): void {
  hull.lathe(SPIRE, 6, FROST.ice, { at: [0, SPIRE_BASE, 0] });
  neon.ring(5.7, 0.7, 6, VIOLET, { at: [0, SPIRE_BASE + 0.4, 0] });
  charge.lathe(SPIRE_TIP, 6, WHITE, { at: [0, SPIRE_BASE + 13.2, 0] });
  muzzle(bossPoint(...ICE_QUEEN_SPIRE), 'ring');
}

/** The core body: fuselage, wings, nose guns and spire. */
function drawCore(p: EnemyParts): void {
  drawFuselage(p);
  drawWings(p);
  drawNoseGuns(p);
  drawSpire(p);
  drawDetails(p);
}

/** The crown ring (P08-R10): a frosted rim lit violet, held by three spokes from the hub. */
function drawRing({ hull, neon }: EnemyParts): void {
  hull.lathe(RIM, 18, H.base, {}, false);
  hull.ring(43.4, 0.25, 18, FROST.snow, { at: [0, 12, 0] });
  neon.ring(44.8, 0.7, 18, VIOLET, { at: [0, 10.2, 0] });
  neon.ring(39.3, 0.6, 18, PALE_BLUE, { at: [0, 10.4, 0] });
  hull.lathe(HUB, 8, H.panel, {}, false);
  neon.ring(7.9, 0.5, 8, PALE_BLUE, { at: [0, 13, 0] });
  for (const a of around(3)) {
    const yaw = a + Math.PI / 3;
    hull.bevelSlab(SPOKE, [12, 12.6, 13.4], [0.2, 0.5], H.panel, { yaw }, FROST.snow);
    const [x, z] = [Math.sin(yaw) * 42, Math.cos(yaw) * 42];
    crystal(hull, [x, 11.5, z], [0.5, 0, yaw], [1.8, 7]);
  }
}

/**
 * P08-R10: the Ice Queen, a slender crystal interceptor (3.5 L) with pale blue and violet neon:
 * swept frosted wings, a crystal spire over the core, and a crown ring turning over it carrying
 * three crystal shards.
 */
export function buildIceQueen(scene: Scene): EnemyModel {
  const shards = Object.fromEntries(
    ICE_QUEEN.stats.parts.map((p) => [
      p.id,
      (parts: EnemyParts) => {
        iceShard(parts, ICE_QUEEN.guns[p.id]?.gun ?? [], ICE_QUEEN_SHARD.height);
      },
    ]),
  );
  return buildBossModel(ICE_QUEEN, scene, PALE_BLUE, {
    core: drawCore,
    ring: drawRing,
    parts: shards,
  });
}
