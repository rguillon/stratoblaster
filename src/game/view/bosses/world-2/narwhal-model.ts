import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import { BOSS_LOOK } from '../../../config/boss-look';
import { NARWHAL, NARWHAL_EMITTER } from '../../../config/bosses/world-2/narwhal';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { flipX, sideStripe, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { edgeStrips, shift, turret } from '../final-boss-shapes';
import { plate, rect } from '../mini-boss-greebles';
import { organ, ribs } from '../../../../render/geometry/organic';
import { FROST } from './floe-breaker-frost';
import { crystals, gland, glowVein, ICE_FLESH, spineRow } from './w2-organic';
import { deckDressing, hullDressing } from './narwhal-details';
import { ballastPod, hornLance, SUB_SECTION, torpedoTube } from './narwhal-parts';

// P08-R10, 2-1: the Narwhal, the final boss of the Ice floes level. Logical pixels, nose +Z,
// Y up (towards the camera). A long flying submarine: a round hull with a sail on its back,
// cruciform tail planes and a shrouded propeller, teal neon along its back; its spiral horn,
// torpedo tubes and ballast pods are its parts.
const H = ENEMY_LOOK.hull;
const N = BOSS_LOOK.neon.narwhal ?? [0.05, 0.95, 0.75];
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** The pressure hull (loft stations, tail to nose): round, its widest just behind the sail. */
const HULL = [
  [-66, 4, 2, 9],
  [-56, 9, -2, 12],
  [-40, 14, -5, 15],
  [-16, 17, -7, 17],
  [10, 18, -7, 17.5],
  [30, 16.5, -6, 16.5],
  [42, 13, -4, 14],
  [50, 8, -1, 10],
  [56, 0, 4.5, 4.5],
] as const;
/** The flat back of {@link SUB_SECTION}, and its shoulders either side. */
const BACK = 4;
/** Snow lies in patches along its back, between the neon lines. */
const hullPaint = (side: number, band: number) =>
  side === BACK && band % 2 === 1 ? ICE_FLESH.rime : band === 0 ? ICE_FLESH.bone : undefined;
/** The sail (conning tower) on its back (loft stations, aft to front). */
const SAIL = [
  [-8, 3, 15, 22],
  [-2, 5, 15, 27],
  [16, 5, 15, 27],
  [22, 3, 15, 23],
] as const;
/** The sail's flat top under its snow cap. */
const sailPaint = (side: number) => (side === BACK ? ICE_FLESH.rime : undefined);
/** The right sail plane (the screen's left: +X is the model's left side, mirrored for the other). */
const SAIL_PLANE = [
  [4.5, 15],
  [14, 11],
  [14, 8],
  [4.5, 7],
] as const;
/** The right stern plane, and the upper and lower rudders (in their own plane, rolled upright). */
const STERN_PLANE = [
  [6, -50],
  [24, -59],
  [25, -65],
  [5, -63],
] as const;
const RUDDER = [
  [0, -48],
  [13, -58],
  [13, -64],
  [0, -64],
] as const;
/** The propeller shroud: a lathe profile out along its outer wall and back along its inner one. */
const SHROUD = [
  [6.4, 0],
  [7, 0.5],
  [7, 6],
  [6.2, 6],
  [6.2, 0.5],
] as const;
/** The emitter on the sail's top: a lathe profile (the core's spiral gun). */
const EMITTER = [
  [3, 0],
  [3.2, 1.2],
  [2, 2.6],
  [0, 3],
] as const;

/** The pressure hull, its teal neon along the back, and the ballast pods' pylons. */
function drawHull({ hull, flesh, neon }: EnemyParts): void {
  // P16-R06: a whale's body of cold teal flesh, ribbed, metal bands grafted round it.
  flesh.loft(SUB_SECTION, HULL, ICE_FLESH.teal, {}, { paint: hullPaint });
  ribs(
    flesh,
    [-36, -28, 28, 36],
    { halfWidth: 15.5, y: 3, height: 13, thickness: 0.8 },
    ICE_FLESH.bone,
  );
  for (const side of [BACK - 1, BACK + 1]) {
    const stripe = sideStripe(SUB_SECTION, side, [0.1, 0.35], 1.03);
    neon.loft(stripe, HULL.slice(1, 7), N, {}, { open: true });
  }
  // A neon line under its chin and along its keel lamps.
  neon.box([1, 0.5, 30], N, { at: [0, -7.2, 0] });
  for (const s of SIDES) {
    const pylon = [
      [s * 15, -28],
      [s * 33, -24],
      [s * 33, -12],
      [s * 15, -6],
    ] as const;
    flesh.bevelSlab(pylon, [3, 5, 7], [0.5, 1], ICE_FLESH.sinew, {}, ICE_FLESH.rime);
    hull.ring(17.8, 1.4, 8, H.panel, { at: [0, 5, s * 6 - 10], pitch: QUARTER });
  }
}

/** The sail, its planes and the spiral emitter on its top. */
function drawSail(p: EnemyParts): void {
  const { hull, flesh, neon, charge, muzzle } = p;
  // The dorsal hump where the sail was, its planes now fins.
  flesh.loft(SUB_SECTION, SAIL, ICE_FLESH.purple, {}, { paint: sailPaint });
  edgeStrips(
    neon,
    [
      [0, -7.6],
      [0, 21.6],
    ],
    0.8,
    [26.9, 27.5],
    N,
  );
  for (const s of SIDES) {
    const plane = s > 0 ? SAIL_PLANE : flipX(SAIL_PLANE);
    flesh.bevelSlab(plane, [21, 22, 23], [0.3, 0.6], ICE_FLESH.membrane, {}, ICE_FLESH.purple);
    crystals(flesh, [s * 12, 22, 9], 2.6, 2);
    // Feelers on the hump, of different heights.
    flesh.cylinder(0.8, 4 + s * 1.5, 4, ICE_FLESH.sinew, { at: [s * 2.2, 27, 2] }, 0.2);
  }
  hull.lathe(EMITTER, 8, H.dark, { at: [0, 27, 10] });
  neon.ring(3.3, 0.5, 8, N, { at: [0, 27.4, 10] });
  charge.cylinder(1.3, 1.6, 6, WHITE, { at: [0, 29.4, 10] }, 0.4);
  for (const at of NARWHAL_EMITTER) muzzle(bossPoint(...at), 'ring');
}

/** The cruciform tail: stern planes, rudders, the propeller shroud and its reactor. */
function drawTail(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  for (const s of SIDES) {
    // The tail flukes, flesh where the stern planes were.
    const plane = s > 0 ? STERN_PLANE : flipX(STERN_PLANE);
    flesh.bevelSlab(plane, [4, 5, 6.5], [0.4, 0.8], ICE_FLESH.teal, {}, ICE_FLESH.rime);
    edgeStrips(
      neon,
      s > 0 ? STERN_PLANE.slice(0, 2) : flipX(STERN_PLANE.slice(0, 2)),
      0.8,
      [5.6, 6.6],
      N,
    );
    crystals(flesh, [s * 22, 6, -60], 3, 2);
  }
  flesh.bevelSlab(RUDDER, [-0.8, 0, 0.8], [0.2, 0.4], ICE_FLESH.sinew, {
    at: [0, 9, 0],
    roll: QUARTER,
  });
  flesh.bevelSlab(RUDDER, [-0.8, 0, 0.8], [0.2, 0.4], ICE_FLESH.sinew, {
    at: [0, 1, 0],
    roll: -QUARTER,
  });
  organ(flesh, 6.5, 7, ICE_FLESH.purple, { at: [0, 5, -72], pitch: QUARTER }, 0.6);
  hull.lathe(SHROUD, 8, H.dark, { at: [0, 5, -73], pitch: QUARTER }, false);
  neon.ring(7.2, 0.8, 8, N, { at: [0, 5, -70], pitch: QUARTER });
  p.reactor([0, 5, -67], 3.6);
  glowVein(p, [0, 10, -66], [0, 14, -44], 1.2, N);
}

/** Deck details: hatches, vents, frost, ice chunks, hazard paint. */
function drawDeck(p: EnemyParts): void {
  const { hull, flesh } = p;
  plate(hull, rect(5, 7), [17.6, 0.5], FROST.panel, { at: [0, 0, -18] });
  plate(hull, rect(4, 4), [15.6, 0.5], H.panel, { at: [0, 0, -38] });
  gland(p, [0, 17, -26], 1.6, N);
  spineRow(flesh, [0, 16, -50], [0, 17, -30], 4, 3.5);
  crystals(flesh, [6, 16.6, -32], 3.4);
  crystals(flesh, [-7, 16.6, 24], 2.6);
  crystals(flesh, [-9, 12, -48], 3);
  for (const s of SIDES) {
    glowVein(p, [s * 5, 17, 20], [s * 14, 10, 44], 1, N);
    glowVein(p, [s * 5, 16, -14], [s * 15, 8, -48], 1, N);
  }
}

/** The deck gun on the forward deck (the core's turret), around its pivot `at`. */
function deckGun(p: EnemyParts, at: Vec3): void {
  p.hull.cylinder(6.5, 2, 8, H.dark, { at: shift(at, [0, 15, 0]) });
  turret(p, shift(at, [0, 16.5, 0]), 7, [2, N]);
}

/**
 * P08-R10: the Narwhal, a long flying submarine 5 L from its tail to the tip of its spiral horn,
 * teal neon along its back; its horn lance, two torpedo tubes on its flanks and two ballast
 * pods on pylons are its parts, its deck gun and the emitter on its sail the core's guns.
 * P16-R06: now a living cyber-narwhal, a whale of cold flesh, ribbed, with fins and flukes, its
 * horn of bone; its torpedo tubes and ballast sacs swell from its flanks, metal grafted on.
 */
export function buildNarwhal(scene: Scene): EnemyModel {
  return buildBossModel(NARWHAL, scene, N, {
    core: (p) => {
      drawHull(p);
      drawSail(p);
      drawTail(p);
      drawDeck(p);
      hullDressing(p, N);
      deckDressing(p, N);
    },
    parts: {
      lance: (p, at) => {
        hornLance(p, at, N);
      },
      'tube-left': (p, at) => {
        torpedoTube(p, at, N);
      },
      'tube-right': (p, at) => {
        torpedoTube(p, at, N);
      },
      'pod-left': (p, at) => {
        ballastPod(p, at, N);
      },
      'pod-right': (p, at) => {
        ballastPod(p, at, N);
      },
    },
    turrets: { core: deckGun },
  });
}
