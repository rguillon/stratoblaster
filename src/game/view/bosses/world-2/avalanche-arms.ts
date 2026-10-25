import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { mirror } from '../../../config/bosses/boss-kit';
import { AVALANCHE_DRILL_GUN } from '../../../config/bosses/world-2/avalanche';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import type { LimbDrawing } from '../boss-limbs';
import { hazard } from '../mini-boss-greebles';
import { cog, GEAR, glowLine, ram } from '../mini-boss-mechanism';
import { H, offset, QUARTER, SHADE } from '../mini-boss-shapes';
import { barrelTo, icicles, snowCap } from './avalanche-frost';

// P08-R10, 2-4: the Avalanche's drill arms, moving on their joints (D-061), and its drills.
// Logical pixels, nose +Z, Y up (towards the camera); the left arm is drawn at +X.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];
type Flat = readonly [number, number];

/** The Avalanche's yellow neon (P08-R10). */
export const AVALANCHE_YELLOW = BOSS_LOOK.neon.avalanche ?? [1, 0.85, 0.1];

/** The drill bit along +Z from its root (a lathe profile: radius, distance along). */
const BIT = [
  [7, 0],
  [7.4, 2],
  [5.4, 8],
  [3.2, 14],
  [0, 21],
] as const;
/** The drill's housing: its radius and its length, and the height of its axis. */
const HOUSING = { radius: 8.5, length: 14, axis: 6 } as const;

/** A beam's outline (seen from above) from `a` to `b`, `width` wide, its ends cut square. */
function beamOutline([ax, az]: Flat, [bx, bz]: Flat, width: number): OutlinePoint[] {
  const length = Math.hypot(bx - ax, bz - az) || 1;
  const [nx, nz] = [((az - bz) / length) * (width / 2), ((bx - ax) / length) * (width / 2)];
  return [
    [ax + nx, az + nz],
    [bx + nx, bz + nz],
    [bx - nx, bz - nz],
    [ax - nx, az - nz],
  ];
}

/**
 * One arm segment from `a` to `b` (side `s` applied to X): a dark bed of machinery under a fat
 * armour plate, frost on its top, a yellow light along it and a ram working it.
 */
function segment(
  { hull, neon }: { hull: SolidBuilder; neon: SolidBuilder },
  s: number,
  [a, b]: readonly [Flat, Flat],
  width: number,
): void {
  const [pa, pb]: [Flat, Flat] = [
    [s * a[0], a[1]],
    [s * b[0], b[1]],
  ];
  hull.bevelSlab(beamOutline(pa, pb, width), [0, 1.5, 4], [0.6, 1], GEAR);
  const inset = (t: number): Flat => [pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t];
  const [ia, ib] = [inset(0.12), inset(0.82)];
  hull.bevelSlab(beamOutline(ia, ib, width * 1.15), [3, 5, 9], [0.8, 1.8], H.base, {}, H.panel);
  snowCap(hull, beamOutline(inset(0.2), inset(0.55), width * 0.7), 9, 0.8);
  const [lx, lz] = inset(0.72);
  const [mx, mz] = inset(0.6);
  glowLine(neon, [mx, 9.2, mz], [lx, 9.2, lz], 1, AVALANCHE_YELLOW);
  ram(hull, [pa[0] - s * 3, 2, pa[1] + 2], [ib[0] - s * 2, 2.5, ib[1]], 1.1);
}

/** The upper arm (side `s`, +1 left at +X), on its shoulder: its segment and the elbow's cog. */
function upperArm(s: number) {
  return (p: EnemyParts): void => {
    segment(
      p,
      s,
      [
        [18, 10],
        [36, 26],
      ],
      9,
    );
    cog(p.hull, [s * 34, 1.5, 24], 4, 8, s * 0.2);
  };
}

/** The forearm (side `s`), on its elbow: its segment, out to the drill's housing. */
function forearm(s: number) {
  return (p: EnemyParts): void => {
    segment(
      p,
      s,
      [
        [32, 22],
        [42, 32],
      ],
      8,
    );
    icicles(
      p.hull,
      [
        [s * 37, 3, 25],
        [s * 39.5, 3, 28],
        [s * 34.5, 3, 22.5],
      ],
      3.5,
    );
  };
}

/** The limbs of the arm on `side` (D-061): the upper arm on the shoulder, the forearm on the elbow. */
export function armLimbs(side: 'left' | 'right'): Record<string, LimbDrawing> {
  const s = side === 'left' ? 1 : -1;
  return {
    [`shoulder-${side}`]: { draw: upperArm(s) },
    [`elbow-${side}`]: { draw: forearm(s) },
  };
}

/** Ridges spiralling round the drill bit from `root` (its axis along +Z), `color`. */
function flutes(hull: SolidBuilder, root: Vec3, color: Rgb): void {
  for (let k = 0; k < 6; k++) {
    const along = 3 + k * 2.6;
    const r = 7 - along * 0.32;
    const a = k * 1.9;
    hull.box([1.2, 1.4, 3.2], color, {
      at: offset(root, Math.cos(a) * r, Math.sin(a) * r - 0.7, along),
      yaw: 0.5,
      roll: a,
    });
  }
}

/**
 * A drill (P08-R10), on its arm's elbow joint: a housing with a yellow neon collar, a fluted
 * bit pointing down the screen, its gun along the outer side, frost on top and icicles under it.
 */
export function drill(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  const s = Math.sign(at[0]);
  const axis = offset(at, 0, HOUSING.axis, 0);
  const back = offset(axis, 0, 0, -HOUSING.length / 2);
  hull.cylinder(HOUSING.radius, HOUSING.length, 8, H.panel, { at: back, pitch: QUARTER });
  hull.cylinder(HOUSING.radius * 0.7, 3, 8, GEAR, {
    at: offset(back, 0, 0, -3),
    pitch: QUARTER,
  });
  const front = offset(axis, 0, 0, HOUSING.length / 2);
  neon.ring(HOUSING.radius * 1.03, 1.2, 8, AVALANCHE_YELLOW, {
    at: offset(front, 0, 0, -2.5),
    pitch: QUARTER,
  });
  hull.lathe(BIT, 6, SHADE.edge, { at: front, pitch: QUARTER });
  flutes(hull, front, H.panel);
  // The gun on the outer side, on a bracket; the right one is the mirror image.
  const [tip] = s > 0 ? AVALANCHE_DRILL_GUN : mirror(AVALANCHE_DRILL_GUN);
  if (tip) barrelTo(p, tip, [1.7, 9]);
  hull.box([5, 3, 8], H.dark, { at: offset(at, s * 6.5, 5, 7) }, H.base);
  hazard(hull, offset(axis, 0, HOUSING.radius - 0.6, -3), [6, 5], 4, QUARTER);
  snowCap(
    hull,
    (
      [
        [-4, -6],
        [3, -7],
        [4.5, 0],
        [-2, 2],
      ] as const
    ).map(([x, z]): Flat => [at[0] + x, at[2] + z]),
    HOUSING.axis + HOUSING.radius - 0.3,
    0.9,
  );
  const under = HOUSING.axis - HOUSING.radius + 0.6;
  icicles(hull, [offset(at, -4, under, 4), offset(at, 3, under, 0), offset(at, 0, under, -4)], 4);
}
