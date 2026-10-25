import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import type { OutlinePoint } from '../../../render/geometry/outline';
import { BOSS_LOOK } from '../../config/boss-look';
import { REEF_WARDEN } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import {
  canopyPaint,
  decal,
  FIGHTER_SECTION,
  flipX,
  POD_SECTION,
  sideStripe,
  SIDES,
} from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { cable, dish, hazard, lamps, mast, plate, seam, vent } from './mini-boss-greebles';
import { H, neonBand, offset, scaled, SHADE, socket, turret } from './mini-boss-shapes';

// P07-R05, 1-1: the Reef Warden. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];
type Rgb = readonly [number, number, number];

const CYAN = BOSS_LOOK.neon['reef-warden'] ?? [0.1, 0.9, 1];
/** Navigation lights: red to port (+X, the screen's left), green to starboard. */
const PORT_RED = [1, 0.1, 0.12] as const;
const STARBOARD_GREEN = [0.2, 1, 0.35] as const;

/** The hover skirt seen from above: a wide hull, pointed at the prow, the cannons on its beam. */
const REEF_HULL = [
  [0, 38],
  [12, 34],
  [24, 23],
  [35, 11],
  [40, 1],
  [38, -10],
  [28, -22],
  [14, -30],
  [-14, -30],
  [-28, -22],
  [-38, -10],
  [-40, 1],
  [-35, 11],
  [-24, 23],
  [-12, 34],
] as const;
/** Heights of the skirt: its bottom, its rim (the widest), its deck. */
const SKIRT = [-5, -1, 3] as const;
/** The raised deck on the skirt: the hull's outline scaled down and moved back. */
const DECK = scaled(REEF_HULL, 0.66, 0, -3);
/** The bridge along the centre line (loft stations: z, half width, bottom, top). */
const BRIDGE = [
  [-24, 7, 5, 9],
  [-14, 10, 5, 13],
  [2, 10, 5, 14],
  [12, 7, 5, 11],
  [18, 3, 5, 7],
] as const;
/** The engine nacelles on the aft deck, either side of the bridge (loft stations). */
const NACELLE = [
  [-31, 4.5, 1.5, 8.5],
  [-22, 5.5, 1.5, 10],
  [-12, 4, 2.5, 7.5],
  [-6, 0, 5, 5],
] as const;
/** The radar mast on the bridge: a lathe profile. */
const MAST = [
  [1.6, 0],
  [1.2, 3],
  [3.4, 3.6],
  [3.4, 4.2],
  [0, 4.6],
] as const;
/** The right prow light, along the skirt's front edge, on its deck (mirrored for the left). */
const PROW_LIGHT = [
  [4, 32.5],
  [21, 18.5],
  [19.5, 17],
  [3, 30.5],
] as const;
/** The left prow light, broken off where a hit scarred the skirt, and the scar. */
const BROKEN_LIGHT = [
  [-4, 32.5],
  [-12, 25.9],
  [-10.5, 24.4],
  [-3, 30.5],
] as const;
const SCAR = [
  [-13, 24],
  [-17, 27],
  [-21, 23],
  [-23, 18],
  [-19, 16],
  [-15, 19],
] as const;
/** The front deck plates either side of the bridge (the right one; mirrored, a patch on the left). */
const DECK_PLATE = [
  [10, 4],
  [19, 4],
  [15, 13],
  [8.5, 13],
] as const;
/** The cannons' mounting plate (an octagon, in units of the part's radius). */
const MOUNT = Array.from({ length: 8 }, (_, k) => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a), Math.cos(a)] as const;
});

/** The skirt with its cyan ring under the rim, the deck, the bridge and the engine nacelles. */
function drawBody({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(REEF_HULL, SKIRT, [3, 3], H.base, {}, H.panel);
  // The cyan ring under the rim, standing just out of the skirt's lower slope.
  neonBand(neon, REEF_HULL, [-3.4, -1.1], [0.985, 1.02], CYAN);
  hull.bevelSlab(DECK, [3, 3, 5], [0, 1.6], H.panel, {}, H.base);
  hull.loft(FIGHTER_SECTION, BRIDGE, H.base, {}, { paint: canopyPaint([2, 3], H.dark) });
  for (const side of [1, 6]) {
    const stripe = sideStripe(FIGHTER_SECTION, side, [0.3, 0.75]);
    neon.loft(stripe, BRIDGE.slice(0, 3), CYAN, {}, { open: true });
  }
  decal(neon, PROW_LIGHT, SKIRT[2] + 0.05, CYAN);
  decal(neon, BROKEN_LIGHT, SKIRT[2] + 0.05, CYAN);
  hull.lathe(MAST, 6, H.panel, { at: [2.5, 12.6, -8] });
  for (const s of SIDES) {
    hull.loft(POD_SECTION, NACELLE, H.base, { at: [s * 13, 0, 0] });
    neon.box([0.6, 0.4, 10], CYAN, { at: [s * 13, 10, -23] });
  }
}

/** Where the skirt's armour panels sit: `[first, second]` hull corners, and their shade. */
const SKIRT_PANELS = [
  [2, 3, H.panel],
  [6, 7, SHADE.edge],
  [7, 8, H.panel],
  [14, 13, H.base],
  [10, 9, H.panel],
  [9, 8, SHADE.patch],
] as const;

/** An armour panel on the skirt, between hull corners `i` and `j` and the deck's matching edge. */
function skirtPanel(hull: EnemyParts['hull'], i: number, j: number, color: Rgb): void {
  const corner = (k: number, t: number): OutlinePoint => {
    const [x, z] = REEF_HULL[k] ?? [0, 0];
    const [dx, dz] = [x * 0.66, z * 0.66 - 3];
    return [dx + (x - dx) * t, dz + (z - dz) * t];
  };
  const [a0, a1, b1, b0] = [corner(i, 0.18), corner(i, 0.62), corner(j, 0.62), corner(j, 0.18)];
  const shrink = (p: OutlinePoint, q: OutlinePoint): OutlinePoint => [
    p[0] + (q[0] - p[0]) * 0.08,
    p[1] + (q[1] - p[1]) * 0.08,
  ];
  const quad = [shrink(a0, b0), shrink(a1, b1), shrink(b1, a1), shrink(b0, a0)];
  plate(hull, quad, [SKIRT[2], 0.6], color);
}

/** Details on both sides: hover vents, aft grille, front deck plates, navigation lights. */
function drawDeck({ hull, neon }: EnemyParts): void {
  const deck = 5;
  for (const s of SIDES) {
    vent(hull, [s * 28, SKIRT[2] - 0.2, -15], [4, 10], 4, Math.atan2(s * -10, -12));
    seam(hull, [s * 8, -21], [s * 24.5, -8], [deck - 0.1, 0.7, 0.5], H.dark);
  }
  vent(hull, [0, SKIRT[2] - 0.2, -26.5], [9, 4], 3, Math.PI / 2);
  for (const [i, j, color] of SKIRT_PANELS) skirtPanel(hull, i, j, color);
  hazard(hull, [0, SKIRT[2] - 0.1, 33.6], [9, 2.4], 5, 0);
  // The right plate is clean; the left one (+X) a weathered patch, riveted with lighter seams.
  plate(hull, flipX(DECK_PLATE), [deck, 0.5], H.panel);
  hazard(hull, [-13.5, deck + 0.4, 8.5], [6, 3], 4, 0);
  plate(hull, DECK_PLATE, [deck, 0.7], SHADE.patch);
  seam(hull, [10.5, 5], [17.5, 5], [deck + 1, 0.5, 0.3], SHADE.edge);
  seam(hull, [9.5, 12], [15.5, 12], [deck + 1, 0.5, 0.3], SHADE.edge);
  for (const s of SIDES) {
    vent(hull, [s * 13, 9.2, -19], [4.5, 6], 3);
    cable(
      hull,
      [
        [s * 9, -2],
        [s * 17, 0],
        [s * 22.5, -3],
      ],
      deck,
      1,
    );
  }
  lamps(neon, [[27, SKIRT[2], -19]], 1.6, PORT_RED);
  lamps(neon, [[-27, SKIRT[2], -19]], 1.6, STARBOARD_GREEN);
  // A scorched scar across the left of the prow (the screen's right).
  plate(hull, SCAR, [SKIRT[2], 0.25], SHADE.soot);
}

/**
 * Mismatched aft deck: cargo containers and a loading crane to port (+X), a radar dish to
 * starboard; a whip antenna off-centre on the bridge.
 */
function drawCargo(p: EnemyParts): void {
  const { hull } = p;
  const deck = 5;
  hull.box([5, 3.4, 8], H.panel, { at: [20.5, deck, -9] }, SHADE.edge);
  hull.box([4.4, 2.6, 4.4], SHADE.patch, { at: [20.5, deck + 3.4, -10.5], yaw: 0.12 });
  hazard(hull, [20.5, deck + 3.4, -4.6], [5, 1.4], 4, 0);
  hull.cylinder(1, 9, 6, H.dark, { at: [24, deck, -15] });
  hull.box([1.2, 1.2, 11], H.panel, { at: [24, deck + 8.4, -15], yaw: -0.5, pitch: -0.12 });
  dish(hull, [-20, deck, -10], 4.5, 0.6, -0.6);
  mast(p, [-4, 11.4, -16], 7, CYAN);
}

/**
 * P07-R05: the Reef Warden, a wide hover-gunboat with a cyan neon ring under its rim, a bridge
 * along its deck and a prow cannon; its two side cannons are mounted on its beam.
 */
export function buildReefWarden(scene: Scene): EnemyModel {
  return buildBossModel(REEF_WARDEN, scene, CYAN, {
    core: (p) => {
      drawBody(p);
      drawDeck(p);
      drawCargo(p);
      for (const s of SIDES) {
        socket(p.hull, [s * 34, 3, 2], 8, 1.2);
        p.reactor([s * 13, 5, -31], 3.4);
      }
      p.reactor([0, -1, -30], 3);
    },
    parts: { 'cannon-left': cannon, 'cannon-right': cannon },
    turrets: { core: prowTurret, 'cannon-left': cannonTurret, 'cannon-right': cannonTurret },
  });
}

/** The prow cannon (the core's gun), on the skirt, turning around its pivot `at`. */
function prowTurret(p: EnemyParts, at: Vec3): void {
  turret(p, offset(at, 0, SKIRT[2], 0), {
    radius: 7,
    barrels: 1,
    gap: 0,
    bore: 1.5,
    length: 7,
    neon: CYAN,
  });
}

/**
 * A side cannon (P07-R05): a mounting plate on the beam under its twin-barrelled turret
 * ({@link cannonTurret}); the left one (+X) feeds from an ammunition box, the right one carries a
 * rangefinder.
 */
function cannon(p: EnemyParts, at: Vec3): void {
  const r = REEF_WARDEN.stats.parts[0]?.radius ?? 14;
  p.hull.bevelSlab(scaled(MOUNT, r * 0.92), [1, 2.5, 4], [0.6, 1.4], H.base, { at }, H.panel);
  if (Math.sign(at[0]) > 0) {
    p.hull.box([4, 3.5, 5], SHADE.patch, { at: offset(at, 6.5, 4, -7), yaw: 0.5 }, H.panel);
    hazard(p.hull, offset(at, 6.5, 7.5, -7), [4, 2], 3, 0.5);
  } else {
    p.hull.box([3, 2.6, 6], H.panel, { at: offset(at, -8.5, 6, -1) }, SHADE.edge);
    p.neon.box([2.2, 1.4, 0.4], CYAN, { at: offset(at, -8.5, 6.6, 2) });
  }
}

/** A side cannon's twin-barrelled turret. */
function cannonTurret(p: EnemyParts, at: Vec3): void {
  turret(p, offset(at, 0, 4, 0), {
    radius: REEF_WARDEN.stats.parts[0]?.radius ?? 14,
    barrels: 2,
    gap: 5,
    bore: 1.6,
    length: 9,
    neon: CYAN,
    hatch: -Math.sign(at[0]),
  });
}
