import type { Scene } from '@babylonjs/core/scene';
import type { SectionPoint } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import { BOSS_LOOK } from '../../../config/boss-look';
import { FLOE_BEACON, FLOE_BREAKER } from '../../../config/bosses/world-2/floe-breaker';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { sideStripe, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { barrels } from '../final-boss-shapes';
import { dish, hazard, lamps, mast, plate, rect, seam, vent } from '../mini-boss-greebles';
import { H, neonBand, offset, scaled, SHADE, socket, turret, WHITE } from '../mini-boss-shapes';
import { floeDressing } from './floe-breaker-details';
import { FROST, iceChunk, icicles } from './floe-breaker-frost';

// P08-R10, 2-1: the Floe Breaker. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

const CYAN = BOSS_LOOK.neon['floe-breaker'] ?? [0.1, 0.85, 1];
/** Navigation lights: red to port (+X, the screen's left), green to starboard. */
const PORT_RED = [1, 0.1, 0.12] as const;
const STARBOARD_GREEN = [0.2, 1, 0.35] as const;

/** The hover skirt seen from above: a long hull, sharp at the bow, square at the stern. */
const FLOE_HULL = [
  [0, 54],
  [9, 40],
  [19, 26],
  [29, 13],
  [35, 2],
  [36, -10],
  [35, -26],
  [30, -38],
  [18, -46],
  [-18, -46],
  [-30, -38],
  [-35, -26],
  [-36, -10],
  [-35, 2],
  [-29, 13],
  [-19, 26],
  [-9, 40],
] as const;
/** Heights of the skirt: its bottom, its rim (the widest), its deck. */
const SKIRT = [-5, -1, 3] as const;
/** The raised deck on the skirt: the hull's outline scaled down and moved back. */
const DECK = scaled(FLOE_HULL, 0.72, 0, -4);
/** The armoured bow: a ridged wedge over the front deck, cutting through the floes. */
const BOW_SECTION: readonly SectionPoint[] = [
  [1, 0],
  [0.8, 0.5],
  [0.3, 0.92],
  [0, 1],
  [-0.3, 0.92],
  [-0.8, 0.5],
  [-1, 0],
];
/** Its loft stations (z, half width, bottom, top), aft to the point of the bow. */
const BOW = [
  [6, 21, 3, 9],
  [20, 18, 3, 10],
  [36, 10, 2.5, 8],
  [49, 3, 1.5, 4.5],
  [56, 0, 2.5, 2.5],
] as const;
/** The bow's top facets crusted with ice on its front bands. */
const bowPaint = (side: number, band: number) =>
  (side === 2 || side === 3) && band >= 1 ? FROST.snow : undefined;
/** The sponsons' mounting plate (an octagon, in units of the part's radius). */
const MOUNT = Array.from({ length: 8 }, (_, k) => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a), Math.cos(a)] as const;
});
/** The frost beacon on the bridge roof: a lathe profile (the core's ring gun). */
const BEACON = [
  [3.6, 0],
  [3.8, 1.5],
  [2.6, 3.4],
  [0, 4],
] as const;

/** The skirt with its cyan ring under the rim, the deck and the armoured bow. */
function drawHull({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(FLOE_HULL, SKIRT, [3, 3], H.base, {}, H.panel);
  neonBand(neon, FLOE_HULL, [-3.4, -1.1], [0.985, 1.02], CYAN);
  hull.bevelSlab(DECK, [3, 3, 5], [0, 1.4], H.panel, {}, FROST.panel);
  hull.loft(BOW_SECTION, BOW, H.base, {}, { paint: bowPaint });
  for (const side of [0, 5]) {
    const stripe = sideStripe(BOW_SECTION, side, [0.35, 0.8], 1.05);
    neon.loft(stripe, BOW.slice(0, 4), CYAN, {}, { open: true });
  }
  // The ice-breaking teeth along the bow's waterline, dark and worn.
  for (const s of SIDES) {
    for (const [z, w] of [
      [44, 6],
      [33, 12],
      [22, 17],
    ] as const) {
      hull.box([2.2, 2.4, 4], SHADE.edge, { at: [s * w, 1.6, z], yaw: s * 0.6 });
    }
  }
  icicles(hull, FLOE_HULL, SKIRT[1], 3);
}

/** The bridge tiers, the frost beacon on their roof, the stacks and the hover fans aft. */
function drawBridge(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  hull.box([26, 7, 22], H.base, { at: [0, 4, -18] }, FROST.snow);
  hull.box([18, 6, 13], H.panel, { at: [0, 11, -16] }, FROST.snow);
  // The wheelhouse windows across the upper tier's front, lit cyan.
  neon.box([15, 1.4, 0.4], CYAN, { at: [0, 13.4, -9.4] });
  neon.box([22, 1, 0.4], CYAN, { at: [0, 7.6, -6.9] });
  hull.lathe(BEACON, 8, SHADE.edge, { at: [0, 17, -18] });
  neon.ring(3.9, 0.5, 8, CYAN, { at: [0, 17.6, -18] });
  charge.cylinder(1.6, 2.4, 6, WHITE, { at: [0, 20.6, -18] }, 0.6);
  for (const at of FLOE_BEACON) muzzle(bossPoint(...at), 'ring');
  for (const s of SIDES) {
    hull.cylinder(2.6, 9, 6, H.dark, { at: [s * 8, 4, -32] }, 2.2);
    hull.cylinder(2.3, 0.6, 6, SHADE.soot, { at: [s * 8, 13, -32] });
    hull.ring(5.6, 2, 8, H.panel, { at: [s * 21, 3.6, -32] });
    p.rotor([s * 21, 4.4, -32], 4.6);
    p.reactor([s * 13, 0.5, -45], 3.2);
  }
}

/** Deck details: frosted plates, ice chunks, vents, hazard paint, lamps, the bow chasers. */
function drawDeck(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    plate(hull, rect(8, 10), [5, 0.6], FROST.panel, { at: [s * 15, 0, -2] });
    vent(hull, [s * 25, SKIRT[2] - 0.2, -20], [4, 9], 4);
    seam(hull, [s * 6, 4], [s * 20, 14], [5, 0.6, 0.5], H.dark);
    iceChunk(hull, [s * 12, 4.6, 12 + s * 3], 2.6 + s * 0.4);
  }
  iceChunk(hull, [-4, 9.5, 30], 1.8);
  // Mismatched bridge roof: a radar dish to port (+X), a whip antenna to starboard.
  dish(hull, [6.5, 17, -20], 3.2, -0.5, 0.4);
  mast(p, [-6, 17, -21], 6, CYAN);
  iceChunk(hull, [22, 3, -40], 3);
  hazard(hull, [0, 4.8, -35], [12, 2.4], 6, 0);
  lamps(neon, [[30, SKIRT[2], -30]], 1.6, PORT_RED);
  lamps(neon, [[-30, SKIRT[2], -30]], 1.6, STARBOARD_GREEN);
  // The bow chasers: a mount on the bow ridge, two short barrels (the core's fans).
  hull.box([8, 2.4, 6], H.dark, { at: [0, 9.2, 22] }, H.panel);
  barrels(p, [0, 10.4, 25], [2, 6], [1.1, 6]);
}

/**
 * P08-R10: the Floe Breaker, an icebreaker hovership with a sharp armoured bow, cyan neon
 * around its skirt and along its bow; its two harpoon guns sit on sponsons either side.
 */
export function buildFloeBreaker(scene: Scene): EnemyModel {
  return buildBossModel(FLOE_BREAKER, scene, CYAN, {
    core: (p) => {
      drawHull(p);
      drawBridge(p);
      drawDeck(p);
      floeDressing(p, CYAN);
      for (const s of SIDES) socket(p.hull, [s * 30, 3, 4], 8, 1.2);
    },
    parts: { 'harpoon-left': sponson, 'harpoon-right': sponson },
    turrets: { 'harpoon-left': harpoonTurret, 'harpoon-right': harpoonTurret },
  });
}

/** A harpoon gun's sponson (P08-R10): a mounting plate on the beam and a cable reel outboard. */
function sponson(p: EnemyParts, at: Vec3): void {
  const r = FLOE_BREAKER.stats.parts[0]?.radius ?? 13;
  const s = Math.sign(at[0]);
  p.hull.bevelSlab(scaled(MOUNT, r * 0.9), [1, 2.5, 4.5], [0.6, 1.4], H.base, { at }, FROST.snow);
  // A reel lying across (rolled, it runs towards -X from its base).
  const reel = offset(at, s > 0 ? 13 : -7, 5, -6);
  p.hull.cylinder(3, 6, 8, H.panel, { at: reel, roll: Math.PI / 2 });
  p.hull.cylinder(2.4, 6.4, 8, SHADE.patch, { at: offset(reel, 0.2, 0, 0), roll: Math.PI / 2 });
  p.neon.box([0.4, 1.2, 4], CYAN, { at: offset(at, s * 11.6, 2.6, 4) });
}

/** A harpoon gun's turret: one long barrel, barbs near its tip. */
function harpoonTurret(p: EnemyParts, at: Vec3): void {
  const top = offset(at, 0, 4.5, 0);
  turret(p, top, {
    radius: 11,
    barrels: 1,
    gap: 0,
    bore: 1.8,
    length: 10,
    neon: CYAN,
    hatch: -Math.sign(at[0]),
  });
  for (const s of SIDES) {
    p.hull.box([0.5, 2.6, 2.6], SHADE.edge, { at: offset(top, s * 2, 1.8, 15), yaw: s * 0.5 });
  }
}
