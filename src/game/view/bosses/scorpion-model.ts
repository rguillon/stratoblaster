import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { BOSS_LOOK } from '../../config/boss-look';
import { SCORPION } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { angryEyes, decal, flipX, POD_SECTION, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { mast, plate, seam } from './mini-boss-greebles';
import { cog, conduit, GEAR, glowLine, ram } from './mini-boss-mechanism';
import { H, offset, QUARTER, scaled, SHADE, socket, WHITE } from './mini-boss-shapes';

// P07-R05, 1-4: the Scorpion. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

const YELLOW = BOSS_LOOK.neon.scorpion ?? [1, 0.9, 0.1];

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
/**
 * The left (+X) arm from the head out to the claw's socket (mirrored on the right): a dark bed of
 * machinery, under two fat armour plates with a gap between them over the elbow.
 */
const ARM = [
  [12, 16],
  [34, 30],
  [44, 27],
  [44, 17],
  [36, 15],
  [16, 4],
] as const;
const ARM_ARMOUR = [
  [
    [12, 16],
    [22.5, 22.7],
    [26.5, 10],
    [16, 4],
  ],
  [
    [28.5, 26.5],
    [34, 30],
    [44, 27],
    [44, 17],
    [36, 15],
    [32.5, 13],
  ],
] as const;
/** Direction of the arm seen from above (a yaw), and its lights' centres on the armour. */
const ARM_YAW = Math.atan2(26, 12);
const ARM_LIGHTS = [
  [19.5, 13.5],
  [37, 21.5],
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
/** A claw around its centre, its jaws open to the front (+Z), and its knuckle. */
const JAW = [
  [3, -6],
  [10, -2],
  [11, 6],
  [7, 14],
  [4.5, 12.5],
  [6.5, 6],
  [5, 0],
  [2, -1],
] as const;
/** The armour cap over the back of a knuckle, leaving its front machinery bare. */
const KNUCKLE_CAP = [
  [-8.5, -2.5],
  [8.5, -2.5],
  [9.5, -6.5],
  [6, -11.5],
  [-6, -11.5],
  [-9.5, -6.5],
] as const;
/** The claws are drawn this much bigger than their outlines: the left (+X) one is oversized. */
const CLAW_SCALE = { left: 1.45, right: 1.22 } as const;
/** Length of the cannon between the jaws. */
const CLAW_BARREL = 13;
const KNUCKLE = Array.from({ length: 8 }, (_, k) => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a) * 9, Math.cos(a) * 8 - 4] as const;
});

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

/** The carapace, the arms out to the claw sockets, the legs and the tail. */
function drawBody({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(ABDOMEN, [-3, 0, 6], [1.5, 2.5], H.base, {}, H.panel);
  hull.bevelSlab(THORAX, [-3, 0, 8], [1.5, 3], H.panel, {}, H.base);
  hull.bevelSlab(HEAD, [-3, 0, 7], [1.5, 3], H.base, {}, H.panel);
  for (const eye of angryEyes([0, 17], 2, [7, 1.4], 0.35)) decal(neon, eye, 7.05, YELLOW);
  for (const s of SIDES) {
    const side = (o: readonly OutlinePoint[]): readonly OutlinePoint[] => (s > 0 ? o : flipX(o));
    hull.bevelSlab(side(ARM), [-1.5, -0.5, 1.5], [0.8, 1.2], GEAR);
    for (const armour of ARM_ARMOUR) {
      hull.bevelSlab(side(armour), [-1, 0.5, 6], [0.8, 1.8], H.base, {}, H.panel);
    }
    for (const [x, z] of ARM_LIGHTS) {
      neon.box([1, 0.3, 7], YELLOW, { at: [s * x, 6, z], yaw: s * ARM_YAW });
    }
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
 * The machinery under the armour (phase 7 review): the elbows' cogs, rams and lit conduits seen
 * between the arms' plates, the tail's joint drums, and a cable bundle along the tail's left.
 */
function drawMachinery({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    cog(hull, [s * 27.5, 1.2, 18], 3.4, 8, s * 0.3);
    ram(hull, [s * 19, 2.6, 11.5], [s * 35, 3, 19.5], 1.2);
    glowLine(neon, [s * 25, 1.4, 12], [s * 29.5, 1.4, 24], 1.2, YELLOW);
  }
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
      for (const s of SIDES) {
        socket(p.hull, [s * 40, 3.5, 22], 7, 1);
        p.reactor([s * 9, 2, -28], 2.8);
      }
    },
    parts: { 'claw-left': claw, 'claw-right': claw, stinger },
  });
}

/**
 * A claw cannon (P07-R05): a knuckle, two jaws open to the front, a cannon between them, and the
 * rams that work the jaws. The left (+X) claw is the bigger one, a fiddler crab's.
 */
function claw({ hull, neon, charge }: EnemyParts, at: Vec3): void {
  const s = Math.sign(at[0]);
  const k = s > 0 ? CLAW_SCALE.left : CLAW_SCALE.right;
  // Turned a little towards the centre line, so the claws close in front of the head.
  const place = { at: offset(at, 0, 3, 0), yaw: -s * 0.18 };
  const put = (x: number, y: number, z: number): Vec3 =>
    offset(
      place.at,
      x * Math.cos(place.yaw) + z * Math.sin(place.yaw),
      y,
      -x * Math.sin(place.yaw) + z * Math.cos(place.yaw),
    );
  hull.bevelSlab(scaled(KNUCKLE, k), [-2, 1, 3], [1, 1.2], GEAR, place);
  hull.bevelSlab(scaled(KNUCKLE_CAP, k), [2, 3, 8], [0, 2.2], H.panel, place, H.base);
  for (const jaw of [JAW, flipX(JAW)]) {
    hull.bevelSlab(scaled(jaw, k), [-1, 1, 4.5], [0.6, 1.4], H.base, place, H.panel);
  }
  for (const x of [-1, 1]) {
    ram(hull, put(x * 4 * k, 5, -5 * k), put(x * 8 * k, 4.6, 5 * k), 0.9);
    cog(hull, put(x * 6 * k, 3.6, 0), 1.8 * k, 6);
  }
  neon.box([5 * k, 0.4, 0.8], YELLOW, { at: put(0, 8, -6.5 * k), yaw: place.yaw });
  glowLine(neon, put(-5 * k, 3.4, -0.5 * k), put(5 * k, 3.4, -0.5 * k), 1, YELLOW);
  const length = CLAW_BARREL * k * 0.85;
  const barrel = { at: put(0, 2.5, 0), pitch: QUARTER, yaw: place.yaw };
  hull.cylinder(2.4, length, 6, H.dark, barrel, 2);
  charge.cylinder(2.2, 1.6, 6, WHITE, { ...barrel, at: put(0, 2.5, length) }, 1.4);
}

/** The stinger (P07-R05): a bulb hanging from the tail's tip, its laser emitter at the front. */
function stinger({ hull, neon, charge }: EnemyParts, at: Vec3): void {
  const place = { at: offset(at, 0, STINGER_Y, 0), pitch: STINGER_TILT };
  hull.loft(POD_SECTION, STINGER, H.panel, place);
  neon.box([7.5, 0.6, 1], YELLOW, {
    at: along(place.at, STINGER_TILT, 6, -1),
    pitch: STINGER_TILT,
  });
  // Brightens through the laser's warning, full while it fires.
  const tip = along(place.at, STINGER_TILT, -0.5, 11);
  charge.lathe(STINGER_EMITTER, 6, WHITE, { at: tip, pitch: QUARTER + STINGER_TILT });
}
