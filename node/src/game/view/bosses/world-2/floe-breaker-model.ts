import type { Scene } from '@babylonjs/core/scene';
import type { SectionPoint } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import { BOSS_LOOK } from '../../../config/boss-look';
import { FLOE_BEACON, FLOE_BREAKER } from '../../../config/bosses/world-2/floe-breaker';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { sideStripe, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { barrels } from '../final-boss-shapes';
import { dish, lamps, mast, plate, rect } from '../mini-boss-greebles';
import { H, neonBand, offset, scaled, SHADE, socket, turret, WHITE } from '../mini-boss-shapes';
import { floeDressing } from './floe-breaker-details';
import { organ, ribs } from '../../../../render/geometry/organic';
import { eyes, reactorSac } from '../../enemies/organic-parts';
import {
  crystals,
  fringe,
  gland,
  glowVein,
  ICE_FLESH,
  iceTeeth,
  shell,
  sinew,
  spineRow,
} from './w2-organic';
import { FROST } from './floe-breaker-frost';

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

/** The swollen body: a belly of rimed flesh on the hull's outline, a shelled back, a bone ram. */
function drawHull(p: EnemyParts): void {
  const { flesh, neon } = p;
  // P16-R05: the old skirt is now the creature's belly, its cyan band a line of photophores.
  flesh.bevelSlab(FLOE_HULL, SKIRT, [3, 3], ICE_FLESH.teal, {}, ICE_FLESH.rime);
  neonBand(neon, FLOE_HULL, [-3.4, -1.1], [0.985, 1.02], CYAN);
  shell(flesh, { tail: -44, nose: 18, segments: 5, width: 27, bottom: 2, top: 11 });
  flesh.loft(BOW_SECTION, BOW, ICE_FLESH.bone, {}, { paint: bowPaint });
  for (const side of [0, 5]) {
    const stripe = sideStripe(BOW_SECTION, side, [0.35, 0.8], 1.05);
    neon.loft(stripe, BOW.slice(0, 4), CYAN, {}, { open: true });
  }
  // The ice-breaking teeth: metal blades grafted along the ram's waterline.
  for (const s of SIDES) {
    for (const [z, w] of [
      [44, 6],
      [33, 12],
      [22, 17],
    ] as const) {
      p.hull.box([2.2, 2.4, 4], SHADE.edge, { at: [s * w, 1.6, z], yaw: s * 0.6 });
    }
    fringe(flesh, [s * 33, -2, -8], [s, -0.2], 3, 7);
  }
  iceTeeth(flesh, FLOE_HULL, SKIRT[1], 3);
}

/** The brain hump with its eyes and beacon gland, the spiracles and the hover fans aft. */
function drawBridge(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  organ(p.flesh, 13, 7, ICE_FLESH.purple, { at: [0, 3, -18] }, 0.5);
  ribs(
    p.flesh,
    [-26, -18, -10],
    { halfWidth: 13, y: 4, height: 9, thickness: 0.9 },
    ICE_FLESH.bone,
  );
  // A row of eyes across the hump's brow, where the wheelhouse windows were.
  eyes(p, [0, 11, -7.5], { count: 5, size: 0.9, spacing: 3 }, CYAN);
  neon.box([22, 1, 0.4], CYAN, { at: [0, 7.6, -6.9] });
  hull.lathe(BEACON, 8, SHADE.edge, { at: [0, 17, -18] });
  neon.ring(3.9, 0.5, 8, CYAN, { at: [0, 17.6, -18] });
  charge.cylinder(1.6, 2.4, 6, WHITE, { at: [0, 20.6, -18] }, 0.6);
  for (const at of FLOE_BEACON) muzzle(bossPoint(...at), 'ring');
  for (const s of SIDES) {
    // Spiracles breathing out of the back, a metal valve on each.
    p.flesh.cylinder(2.8, 9, 5, ICE_FLESH.sinew, { at: [s * 8, 4, -32] }, 2);
    hull.cylinder(2.3, 0.6, 6, SHADE.soot, { at: [s * 8, 13, -32] });
    p.flesh.ring(5.6, 2, 7, ICE_FLESH.purple, { at: [s * 21, 3.6, -32] });
    p.rotor([s * 21, 4.4, -32], 4.6);
    reactorSac(p, [s * 13, 0.5, -45], 3.2, CYAN, { flesh: ICE_FLESH.purple, veinLength: 6 });
  }
}

/** Back details: armour plates, crystals, glands, veins, the ram's guns. */
function drawDeck(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    plate(hull, rect(8, 10), [5, 0.6], FROST.panel, { at: [s * 15, 0, -2] });
    glowVein(p, [s * 6, 10, -10], [s * 22, 5, 10], 0.9, CYAN);
    crystals(p.flesh, [s * 12, 4.6, 12 + s * 3], 3.5);
    gland(p, [s * 24, 4, -22], 1.4, CYAN);
  }
  crystals(p.flesh, [-4, 9.5, 30], 2.5, 2);
  // An antenna stalk and a dish grafted on the hump, uneven.
  dish(hull, [6.5, 17, -20], 3.2, -0.5, 0.4);
  mast(p, [-6, 17, -21], 6, CYAN);
  crystals(p.flesh, [22, 3, -40], 4);
  spineRow(p.flesh, [0, 9, -38], [0, 12, -30], 3, 3);
  lamps(neon, [[30, SKIRT[2], -30]], 1.6, PORT_RED);
  lamps(neon, [[-30, SKIRT[2], -30]], 1.6, STARBOARD_GREEN);
  // The ram's guns: a metal mount grafted on the bone, two short barrels (the core's fans).
  hull.box([8, 2.4, 6], H.dark, { at: [0, 9.2, 22] }, H.panel);
  barrels(p, [0, 10.4, 25], [2, 6], [1.1, 6]);
}

/**
 * P08-R10: the Floe Breaker, an icebreaker hovership with a sharp armoured bow, cyan neon
 * around its skirt and along its bow; its two harpoon guns sit on sponsons either side.
 * P16-R05: now a living ice-ram, a shelled sea beast with a bone ram, a brain hump and eyes,
 * frost crystals grown through its flesh; its harpoons sit on muscles bulging from its flanks.
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
  // P16-R05: a muscle bulging out of the flank, a metal mount on top, the reel a gland.
  organ(p.flesh, r * 0.85, 7, ICE_FLESH.purple, { at: offset(at, 0, -2, 0) }, 0.3);
  p.hull.bevelSlab(scaled(MOUNT, r * 0.55), [3, 3.8, 4.5], [0.4, 1], H.base, { at }, FROST.panel);
  const reel = offset(at, s > 0 ? 10 : -10, 2, -6);
  organ(p.flesh, 3.4, 5, ICE_FLESH.sinew, { at: reel, roll: s * 0.8 }, 0.8);
  crystals(p.flesh, offset(at, s * 6, 3, 6), 3, 2);
  sinew(p.flesh, offset(at, -s * 8, 0, -4), offset(at, -s * 14, 1, -10), 1.6);
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
