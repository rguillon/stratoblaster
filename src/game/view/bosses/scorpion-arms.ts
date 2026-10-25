import type { OutlinePoint } from '../../../render/geometry/outline';
import { SCORPION } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { flipX } from '../enemies/enemy-shapes';
import { bossPoint, type LimbDrawing } from './boss-limbs';
import { cog, GEAR, glowLine, ram } from './mini-boss-mechanism';
import { H, offset, QUARTER, scaled, socket, WHITE } from './mini-boss-shapes';
import { YELLOW } from './scorpion-look';

// P07-R05, 1-4: the Scorpion's arms and claws, moving on their joints (phase 7 review). Logical
// pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

/**
 * The left (+X) arm from the head out to the claw's socket (mirrored on the right): a dark bed of
 * machinery, under two fat armour plates with a gap between them over the elbow. The upper arm
 * and the forearm are drawn on their own joints (phase 7 review), their beds overlapping under
 * the elbow so that it does not open as the arm bends.
 */
const UPPER_ARM = [
  [12, 16],
  [29, 26.8],
  [29, 11.2],
  [16, 4],
] as const;
const FOREARM = [
  [26, 24.9],
  [34, 30],
  [44, 27],
  [44, 17],
  [36, 15],
  [26, 9.5],
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

/** `outline` on the arm of side `s` (+1 left, at +X; -1 right). */
const onSide = (s: number, outline: readonly OutlinePoint[]): readonly OutlinePoint[] =>
  s > 0 ? outline : flipX(outline);

/**
 * An upper arm (side `s`), on its shoulder joint: its bed and armour plate, its light, and the
 * machinery seen at the elbow (its cog, a ram and a lit conduit).
 */
function upperArm(s: number) {
  return ({ hull, neon }: EnemyParts): void => {
    hull.bevelSlab(onSide(s, UPPER_ARM), [-1.5, -0.5, 1.5], [0.8, 1.2], GEAR);
    hull.bevelSlab(onSide(s, ARM_ARMOUR[0]), [-1, 0.5, 6], [0.8, 1.8], H.base, {}, H.panel);
    const [x, z] = ARM_LIGHTS[0];
    neon.box([1, 0.3, 7], YELLOW, { at: [s * x, 6, z], yaw: s * ARM_YAW });
    cog(hull, [s * 27.5, 1.2, 18], 3.4, 8, s * 0.3);
    ram(hull, [s * 19, 2.6, 11.5], [s * 27, 2.8, 15.5], 1.2);
    glowLine(neon, [s * 25, 1.4, 12], [s * 29.5, 1.4, 24], 1.2, YELLOW);
  };
}

/** A forearm (side `s`), on its elbow joint: its bed, armour plate, light, ram and claw socket. */
function forearm(s: number) {
  return ({ hull, neon }: EnemyParts): void => {
    hull.bevelSlab(onSide(s, FOREARM), [-1.5, -0.5, 1.5], [0.8, 1.2], GEAR);
    hull.bevelSlab(onSide(s, ARM_ARMOUR[1]), [-1, 0.5, 6], [0.8, 1.8], H.base, {}, H.panel);
    const [x, z] = ARM_LIGHTS[1];
    neon.box([1, 0.3, 7], YELLOW, { at: [s * x, 6, z], yaw: s * ARM_YAW });
    ram(hull, [s * 29, 2.8, 16], [s * 35, 3, 19.5], 1.2);
    socket(hull, [s * 40, 3.5, 22], 7, 1);
  };
}

/**
 * The limbs of the arm on `side` (phase 7 review): the upper arm on the shoulder, the forearm on
 * the elbow, and the claw's jaws on their hinges, going with the claw.
 */
export function armLimbs(side: 'left' | 'right'): Record<string, LimbDrawing> {
  const s = side === 'left' ? 1 : -1;
  const claw = `claw-${side}`;
  const spec = SCORPION.stats.parts.find((p) => p.id === claw);
  const at = bossPoint(spec?.x ?? 0, spec?.y ?? 0);
  // The jaw on the claw's +X is its outer one on the left, its inner one on the right.
  const [plusX, minusX] = s > 0 ? ['outer', 'inner'] : ['inner', 'outer'];
  return {
    [`shoulder-${side}`]: { draw: upperArm(s) },
    [`elbow-${side}`]: { draw: forearm(s) },
    [`jaw-${side}-${plusX}`]: {
      draw: (p) => {
        drawJaw(p, at, JAW);
      },
      part: claw,
    },
    [`jaw-${side}-${minusX}`]: {
      draw: (p) => {
        drawJaw(p, at, flipX(JAW));
      },
      part: claw,
    },
  };
}

/** How a claw centred on `at` (side from its X) is drawn: scaled, and turned towards the head. */
function clawPlace(at: Vec3) {
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
  return { k, place, put };
}

/** One jaw of the claw at `at`, from its outline (on its hinge's joint). */
function drawJaw({ hull }: EnemyParts, at: Vec3, jaw: readonly OutlinePoint[]): void {
  const { k, place } = clawPlace(at);
  hull.bevelSlab(scaled(jaw, k), [-1, 1, 4.5], [0.6, 1.4], H.base, place, H.panel);
}

/**
 * A claw cannon (P07-R05), on its wrist joint: a knuckle, a cannon between its two jaws (drawn on
 * their own hinges, {@link drawJaw}), and the rams that work the jaws. The left (+X) claw is the
 * bigger one, a fiddler crab's.
 */
export function claw({ hull, neon, charge, muzzle }: EnemyParts, at: Vec3): void {
  const { k, place, put } = clawPlace(at);
  hull.bevelSlab(scaled(KNUCKLE, k), [-2, 1, 3], [1, 1.2], GEAR, place);
  hull.bevelSlab(scaled(KNUCKLE_CAP, k), [2, 3, 8], [0, 2.2], H.panel, place, H.base);
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
  muzzle(put(0, 2.5, length + 1.6));
}
