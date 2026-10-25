import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { SCORPION } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { angryEyes, decal, POD_SECTION, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { armLimbs, claw } from './scorpion-arms';
import { YELLOW } from './scorpion-look';
import { mast, plate, seam } from './mini-boss-greebles';
import { conduit, GEAR } from './mini-boss-mechanism';
import { H, offset, QUARTER, SHADE, WHITE } from './mini-boss-shapes';

// P07-R05, 1-4: the Scorpion. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** The carapace in three overlapping plates, head to tail: it reads as a segmented body. */
const HEAD = [
  [0, 24],
  [11, 20],
  [17, 10],
  [16, 0],
  [-16, 0],
  [-17, 10],
  [-11, 20],
] as const;
const THORAX = [
  [0, 6],
  [19, 3],
  [20, -10],
  [15, -16],
  [-15, -16],
  [-20, -10],
  [-19, 3],
] as const;
const ABDOMEN = [
  [0, -12],
  [15, -13],
  [12, -26],
  [5, -30],
  [-5, -30],
  [-12, -26],
  [-15, -13],
] as const;
/** The right legs: three short swept vanes under the thorax (mirrored on the left). */
const LEG = [
  [0, 1.6],
  [9, -1],
  [9.5, -3],
  [0, -1.6],
] as const;
const LEG_ROOTS = [
  [17, -1, -0.3],
  [18, -7, -0.6],
  [15, -13, -0.9],
] as const;
/**
 * The tail's spine, from its root on the abdomen (z, y), up and back, then over the body, its
 * last joint above the head, where the stinger hangs: each pair of points is a segment.
 */
const TAIL = [
  [-18, 6],
  [-28, 13],
  [-27, 22],
  [-15, 28],
  [2, 29],
  [16, 26],
  [24, 21],
] as const;
/** A patch welded on the abdomen's left. */
const PATCH = [
  [4, -14],
  [12, -15],
  [10, -22],
  [5, -24],
] as const;
/** Half widths of the segments, root to tip. */
const TAIL_WIDTH = [7, 6.5, 6, 5.5, 5, 4.5] as const;
/** The stinger around its centre: a bulb along +Z (loft stations), its emitter at the tip. */
const STINGER = [
  [-11, 4, -4, 4],
  [-4, 7, -6, 6],
  [4, 6, -5, 4.5],
  [11, 2.5, -2.5, 1.5],
] as const;
const STINGER_EMITTER = [
  [2.4, 0],
  [1.6, 3.5],
  [0, 5.5],
] as const;
/** Height of the stinger, and its downward tilt (it aims at the player). */
const STINGER_Y = 15;
const STINGER_TILT = 0.35;

/** A tail segment from `a` to `b` ((z, y) points), `w` wide, with a yellow light on its back. */
function segment(
  { hull, neon }: { hull: SolidBuilder; neon: SolidBuilder },
  [za, ya]: readonly [number, number],
  [zb, yb]: readonly [number, number],
  w: number,
): void {
  const [dz, dy] = [zb - za, yb - ya];
  const length = Math.hypot(dz, dy);
  const pitch = -Math.atan2(dy, dz);
  const at: Vec3 = [0, ya, za];
  const bead = [
    [length * 0.14, w * 0.75, -w * 0.7, w * 0.7],
    [length * 0.5, w, -w * 0.9, w * 0.9],
    [length * 0.86, w * 0.75, -w * 0.65, w * 0.65],
  ] as const;
  hull.loft(POD_SECTION, bead, H.base, { at, pitch });
  // The light along the segment's upper side: the section's top, or its bottom where the
  // segment runs backwards (pitched over, the section is upside down).
  const up = Math.cos(pitch) < 0 ? -1 : 1;
  neon.box([1, 0.4, length * 0.5], YELLOW, {
    at: along(at, pitch, w * 0.9 * up, length * 0.5),
    pitch,
  });
}

/** The point `[0, y, z]` of a solid at `at`, pitched by `pitch`. */
function along(at: Vec3, pitch: number, y: number, z: number): Vec3 {
  return offset(
    at,
    0,
    y * Math.cos(pitch) - z * Math.sin(pitch),
    y * Math.sin(pitch) + z * Math.cos(pitch),
  );
}

/** The carapace, the legs and the tail. */
function drawBody({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(ABDOMEN, [-3, 0, 6], [1.5, 2.5], H.base, {}, H.panel);
  hull.bevelSlab(THORAX, [-3, 0, 8], [1.5, 3], H.panel, {}, H.base);
  hull.bevelSlab(HEAD, [-3, 0, 7], [1.5, 3], H.base, {}, H.panel);
  for (const eye of angryEyes([0, 17], 2, [7, 1.4], 0.35)) decal(neon, eye, 7.05, YELLOW);
  for (const s of SIDES) {
    for (const [x, z, yaw] of s > 0 ? LEG_ROOTS : LEG_ROOTS.slice(0, 2)) {
      hull.bevelSlab(LEG, [-1, 0, 1], [0.3, 0.6], H.panel, {
        at: [s * x, -0.5, z],
        yaw: s * (QUARTER + yaw),
      });
    }
  }
  TAIL.slice(1).forEach((b, i) => {
    const a = TAIL[i];
    if (a) segment({ hull, neon }, a, b, TAIL_WIDTH[i] ?? 4);
  });
}

/**
 * The machinery under the armour (phase 7 review): the tail's joint drums, and a cable bundle
 * along the tail's left.
 */
function drawMachinery({ hull, neon }: EnemyParts): void {
  TAIL.slice(1, -1).forEach(([z, y], i) => {
    const w = (TAIL_WIDTH[i] ?? 5) * 0.8;
    hull.cylinder(w, w * 2, 8, GEAR, { at: [w, y, z], roll: QUARTER });
    neon.cylinder(w * 1.04, 0.8, 8, YELLOW, { at: [0.4, y, z], roll: QUARTER });
  });
  const cables = TAIL.slice(0, -1).map(([z, y], i): Vec3 => {
    const w = TAIL_WIDTH[i] ?? 5;
    return [w + 0.6, y, z];
  });
  cables.slice(1).forEach((b, i) => {
    const a = cables[i];
    if (a) conduit(hull, a, b, 0.9, 1);
  });
  // The missing right hind leg: a capped stump and its loose cable.
  hull.cylinder(1.6, 2.4, 6, SHADE.soot, { at: [-15, -0.5, -13], roll: QUARTER });
  // A welded patch on the abdomen's left, a sensor mast on the head's right.
  plate(hull, PATCH, [6, 0.6], SHADE.patch);
  seam(hull, [5, -16], [11, -18], [6.6, 0.5, 0.3], SHADE.edge);
}

/**
 * P07-R05: the Scorpion, a gunship with yellow neon: a segmented carapace, two arms out to its
 * claw cannons, and a segmented tail arched over its back, its stinger hanging in front of the
 * head, between the claws.
 */
export function buildScorpion(scene: Scene): EnemyModel {
  return buildBossModel(SCORPION, scene, YELLOW, {
    core: (p) => {
      drawBody(p);
      drawMachinery(p);
      mast(p, [-6, 6, 12], 6, YELLOW);
      // The core's guns: a charge light at the front of the head.
      p.charge.cylinder(1.8, 3, 6, WHITE, { at: [0, 2, 23], pitch: QUARTER }, 0.8);
      p.muzzle([0, 2, 26]);
      for (const s of SIDES) p.reactor([s * 9, 2, -28], 2.8);
    },
    parts: { 'claw-left': claw, 'claw-right': claw, stinger },
    limbs: { ...armLimbs('left'), ...armLimbs('right') },
  });
}

/** The stinger (P07-R05): a bulb hanging from the tail's tip, its laser emitter at the front. */
function stinger({ hull, neon, charge, muzzle }: EnemyParts, at: Vec3): void {
  const place = { at: offset(at, 0, STINGER_Y, 0), pitch: STINGER_TILT };
  hull.loft(POD_SECTION, STINGER, H.panel, place);
  neon.box([7.5, 0.6, 1], YELLOW, {
    at: along(place.at, STINGER_TILT, 6, -1),
    pitch: STINGER_TILT,
  });
  // Brightens through the laser's warning, full while it fires.
  const tip = along(place.at, STINGER_TILT, -0.5, 11);
  charge.lathe(STINGER_EMITTER, 6, WHITE, { at: tip, pitch: QUARTER + STINGER_TILT });
  muzzle(along(tip, QUARTER + STINGER_TILT, 5.5, 0), 'laser');
}
