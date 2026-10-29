import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import {
  MOSQUITO,
  MOSQUITO_MANDIBLES,
  MOSQUITO_SAC,
} from '../../../config/bosses/world-3/mosquito';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { reactorSac } from '../../enemies/organic-parts';
import { ROUND_SECTION, tendril } from '../../../../render/geometry/organic';
import { F, sinew, veinTo } from './jungle-flesh';
import { bossPoint, buildBossModel } from '../boss-model';
import { rod } from '../final-boss-greebles';
import { lamps, seam } from '../mini-boss-greebles';
import { H, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { MOSQUITO_PINK, MOSS, moss, needle, proboscis, wing } from './mosquito-parts';

// P09-R09, 3-4: the Mosquito. Logical pixels, nose +Z, Y up (towards the camera). A thin
// bio-drone: a small armoured thorax, a big-eyed head, a long segmented abdomen behind, six
// thin legs hanging under it, moss grown over its back.
type Vec3 = [number, number, number];

/** The thorax along the centre line (loft stations: z, half width, bottom, top). */
const THORAX = [
  [-9, 5, -2, 6],
  [0, 9, -3, 9],
  [10, 8, -3, 8],
  [16, 5, -1, 5],
] as const;
/** The abdomen, tail to waist: long and segmented. */
const ABDOMEN = [
  [-44, 1.2, 1, 2.6],
  [-38, 4.5, -1, 5.5],
  [-26, 6.5, -2, 7.5],
  [-14, 6.5, -2, 7.5],
  [-8, 4, -1, 5],
] as const;
/** Where the abdomen's segments meet: a pink band across its back at each. */
const SEGMENTS = [
  [-20, 6.4, 7.8],
  [-27, 6.2, 7.6],
  [-34, 5, 6.6],
] as const;
/** The head: a rounded capsule (a lathe profile along its axis, Y up). */
const HEAD = [
  [0, -4.5],
  [4, -3.8],
  [6, -1],
  [5.6, 2],
  [3.6, 4.4],
  [0, 5.2],
] as const;
const HEAD_AT: Vec3 = [0, 2.5, 21];
/** A compound eye: a low neon dome, turned to face its side. */
const EYE = [
  [3.2, 0],
  [2.7, 1.6],
  [1.4, 2.5],
  [0, 2.8],
] as const;
/** The legs, front to back (left side, +X): hip, knee and foot. */
const LEGS: readonly (readonly [Vec3, Vec3, Vec3])[] = [
  [
    [6, 0, 9],
    [19, 5, 15],
    [25, -7, 22],
  ],
  [
    [7, 0, 3],
    [22, 5, 2],
    [29, -8, 0],
  ],
  [
    [6, 0, -4],
    [20, 5, -12],
    [26, -8, -20],
  ],
];
/** The blood sac on its back (a lathe dome), lighting up as its next ring charges. */
const SAC = [
  [3.6, 0],
  [3.1, 1.5],
  [1.6, 2.3],
  [0, 2.5],
] as const;

/** The thorax and the segmented abdomen, pink bands between the segments, moss on its back. */
function drawBody(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R05: a living insect: a purple flesh thorax, a swollen, blood-filled abdomen ringed by
  // grafted metal bands, a vein pulsing down its back.
  flesh.loft(ROUND_SECTION, THORAX, F.purple);
  flesh.loft(ROUND_SECTION, ABDOMEN, F.crimson);
  veinTo(
    p,
    [
      [0, 6.4, 12],
      [0, 4.2, -40],
    ],
    [0, 2, 0],
    MOSQUITO_PINK,
    1,
  );
  for (const [z, w, y] of SEGMENTS) {
    neon.box([w * 1.6, 0.4, 0.8], MOSQUITO_PINK, { at: [0, y, z] });
    hull.box([w * 2.1, 1, 1.4], H.dark, { at: [0, y - 2.4, z] });
  }
  seam(hull, [0, 14], [0, -6], [8.6, 1.2, 0.6], SHADE.edge);
  moss(hull, [
    [3.5, 8.4, 4],
    [-4, 8.2, -3],
    [2, 7.2, -24],
    [-2.5, 6.6, -33],
  ]);
  // A strand of vine trailing from its side.
  rod(hull, [-6, 1, -22], [-10, -6, -30], 0.5, MOSS);
  reactorSac(p, [0, 1.8, -44.4], 1.6, MOSQUITO_PINK, { flesh: F.purple });
  for (const s of SIDES) p.reactor([s * 5, 2, -9.2], 1.6);
}

/** The head: big pink compound eyes and the mandible guns under them (the core's bursts). */
function drawHead(p: EnemyParts): void {
  const { hull, flesh, neon, charge, muzzle } = p;
  flesh.lathe(HEAD, 7, F.purple, { at: HEAD_AT, pitch: QUARTER });
  for (const s of SIDES) {
    neon.lathe(EYE, 6, MOSQUITO_PINK, { at: [s * 4.6, 3.4, 22.5], roll: -s * QUARTER });
    // P16-R05: feathery antennae of sinew, tipped with a lit gland.
    sinew(
      p,
      [
        [s * 2, 7, 22],
        [s * 6, 12, 15],
      ],
      [s * 0.6, 1, 0],
      0.45,
    );
    lamps(neon, [[s * 6, 12, 15]], 0.9, MOSQUITO_PINK);
  }
  for (const tip of MOSQUITO_MANDIBLES.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.box([2.6, 2.6, 4], H.panel, { at: [x, y - 1.4, z - 6] }, SHADE.edge);
    hull.cylinder(0.9, 5.4, 6, H.dark, { at: [x, y, z - 6], pitch: QUARTER });
    charge.cylinder(0.95, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/** Six thin legs hanging under the thorax, bent at the knee. */
function drawLegs(p: EnemyParts): void {
  for (const s of SIDES) {
    for (const [hip, knee, foot] of LEGS) {
      const side = (v: Vec3): Vec3 => [s * v[0], v[1], v[2]];
      // P16-R05: thin legs of sinew, a metal knee joint grafted where they bend.
      tendril(p.flesh, [side(hip), side(knee)], [0.8, 0.6], 4, F.sinew);
      tendril(p.flesh, [side(knee), side(foot)], [0.55, 0.15], 3, F.bone);
      p.hull.box([1.4, 1.4, 1.4], H.panel, { at: side(knee) });
    }
  }
}

/** The blood sac on its back, where its last-stage rings leave from. */
function drawSac({ flesh, neon, charge, muzzle }: EnemyParts): void {
  const [top] = MOSQUITO_SAC.map((m) => bossPoint(...m));
  if (!top) return;
  const [x, y, z] = top;
  // P16-R05: the blood sac swelling out of the abdomen's flesh.
  flesh.cylinder(4.4, 1.6, 7, F.wound, { at: [x, y - 4.2, z] });
  neon.ring(4.5, 0.4, 8, MOSQUITO_PINK, { at: [x, y - 3, z] });
  charge.lathe(SAC, 8, WHITE, { at: [x, y - 2.5, z] });
  muzzle(top, 'ring');
}

/**
 * P09-R09: the Mosquito, a thin, fast bio-drone with pink neon: long buzzing wings with a fan
 * pod under each, a big-eyed head and a needle-like proboscis that aims its laser.
 */
export function buildMosquito(scene: Scene): EnemyModel {
  return buildBossModel(MOSQUITO, scene, MOSQUITO_PINK, {
    core: (p) => {
      drawBody(p);
      drawHead(p);
      drawLegs(p);
      drawSac(p);
    },
    parts: { 'wing-left': wing, 'wing-right': wing, proboscis },
    turrets: { proboscis: needle },
  });
}
