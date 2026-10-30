import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { SCORPION } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { carapace, ROUND_SECTION, vein } from '../../../render/geometry/organic';
import { SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { armLimbs, claw } from './scorpion-arms';
import { YELLOW } from './scorpion-look';
import { mast } from './mini-boss-greebles';
import { offset, QUARTER, WHITE } from './mini-boss-shapes';
import { F, graft, hide, M, scaleOutline, spine, tentacle } from './world-1-organic-kit';

// P07-R05, P16-R05, 1-4: the Scorpion. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/** The head plate seen from above. */
const HEAD = [
  [0, 24],
  [11, 20],
  [17, 10],
  [16, 0],
  [-16, 0],
  [-17, 10],
  [-11, 20],
] as const;
/** Where the right legs grow from under the body (mirrored on the left). */
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
  { flesh, neon }: { flesh: SolidBuilder; neon: SolidBuilder },
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
  carapace(flesh, beadBody(bead), [F.crimson, F.membrane], { at, pitch });
  // The light along the segment's upper side: the section's top, or its bottom where the
  // segment runs backwards (pitched over, the section is upside down).
  const up = Math.cos(pitch) < 0 ? -1 : 1;
  neon.box([1, 0.4, length * 0.5], YELLOW, {
    at: along(at, pitch, w * 0.9 * up, length * 0.5),
    pitch,
  });
}

/** A tail bead as a ridged shell along its length (P16-R05). */
function beadBody(bead: readonly (readonly [number, number, number, number])[]) {
  const [first, mid, last] = [bead[0], bead[1], bead[2]];
  const w = mid?.[1] ?? 4;
  return {
    tail: (first?.[0] ?? 0) - w * 0.4,
    nose: (last?.[0] ?? 0) + w * 0.4,
    segments: 1,
    width: w,
    bottom: -w * 0.9,
    top: w * 0.9,
  };
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

/**
 * The body (P16-R05): a swollen, segmented abdomen under a ridged shell, the head plated with
 * grafted armour, bone legs, glowing eyes, and the tail of shelled beads.
 */
function drawBody(p: EnemyParts): void {
  const { flesh, neon } = p;
  hide(p, {
    tail: -31,
    nose: 6,
    width: 18,
    bottom: -3,
    top: 8,
    segments: 4,
    shell: [F.crimson, F.membrane],
    belly: F.sinew,
  });
  flesh.bevelSlab(HEAD, [-3, 0, 6], [1.5, 3], F.sinew, {}, F.crimson);
  graft(p, scaleOutline(HEAD, 0.7, 0, 5), [6, 7], [0, 0, 0]);
  eyes(p, [0, 7, 19], { count: 4, size: 0.8, spacing: 2.2 }, YELLOW);
  for (const s of SIDES) {
    for (const [x, z] of s > 0 ? LEG_ROOTS : LEG_ROOTS.slice(0, 2)) {
      const knee: Vec3 = [s * (x + 6), 3, z - 1];
      tentacle(p, [s * x, 0, z], knee, [0, 1, 0], [1.6, 1.1], F.sinew, 4);
      tentacle(p, knee, [s * (x + 10), -2, z - 4], [0, 0.5, 0], [1.1, 0.15], F.bone, 3);
    }
  }
  TAIL.slice(1).forEach((b, i) => {
    const a = TAIL[i];
    if (a) segment({ flesh, neon }, a, b, TAIL_WIDTH[i] ?? 4);
  });
}

/**
 * The living works (P16-R05): sinew rings at the tail's joints, a yellow vein along the tail's
 * left, the torn stump of the missing right hind leg, a plate grafted on the abdomen.
 */
function drawMachinery(p: EnemyParts): void {
  TAIL.slice(1, -1).forEach(([z, y], i) => {
    const w = (TAIL_WIDTH[i] ?? 5) * 0.8;
    p.flesh.cylinder(w, w * 2, 6, F.sinew, { at: [w, y, z], roll: QUARTER });
    p.vein.cylinder(w * 1.04, 0.8, 6, YELLOW, { at: [0.4, y, z], roll: QUARTER });
  });
  const path = TAIL.slice(0, -1).map(([z, y], i): Vec3 => [(TAIL_WIDTH[i] ?? 5) + 0.6, y, z]);
  vein(p.vein, path, 1.2, YELLOW);
  // The missing right hind leg: a torn stump.
  p.flesh.cylinder(1.6, 2.4, 6, F.wound, { at: [-15, -0.5, -13], roll: QUARTER });
  graft(p, PATCH, [5.5, 6.6], [0, 0, 0], { color: M.base });
  spine(p, [0, 8.5, -26], [0, 8.5, 0], { color: YELLOW, width: 1 });
}

/**
 * P07-R05, P16-R05: the Scorpion, a living desert scorpion with yellow veins: a segmented shell, two arms out to its
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
      for (const s of SIDES) reactorSac(p, [s * 9, 2, -28], 2.8, YELLOW);
    },
    parts: { 'claw-left': claw, 'claw-right': claw, stinger },
    limbs: { ...armLimbs('left'), ...armLimbs('right') },
  });
}

/** The stinger (P07-R05, P16-R05): a venom bulb hanging from the tail's tip, its emitter in front. */
function stinger({ flesh, vein: glow, charge, muzzle }: EnemyParts, at: Vec3): void {
  const place = { at: offset(at, 0, STINGER_Y, 0), pitch: STINGER_TILT };
  flesh.loft(ROUND_SECTION, STINGER, F.purple, place);
  glow.box([7.5, 0.6, 1], YELLOW, {
    at: along(place.at, STINGER_TILT, 6, -1),
    pitch: STINGER_TILT,
  });
  // Brightens through the laser's warning, full while it fires.
  const tip = along(place.at, STINGER_TILT, -0.5, 11);
  charge.lathe(STINGER_EMITTER, 6, WHITE, { at: tip, pitch: QUARTER + STINGER_TILT });
  muzzle(along(tip, QUARTER + STINGER_TILT, 5.5, 0), 'laser');
}
