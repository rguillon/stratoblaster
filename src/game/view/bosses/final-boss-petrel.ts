import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { FIGHTER_SECTION, POD_SECTION } from '../enemies/enemy-shapes';
import { edgeStrips, shift, sided } from './final-boss-shapes';
import { cog } from './final-boss-mechanism';
import {
  decals,
  dish,
  greebles,
  grille,
  hazard,
  mast,
  plate,
  rect,
  rod,
  SHADE,
  studs,
} from './final-boss-greebles';

// P07-R05 (phase 7 review: more detail, not symmetrical): the Storm Petrel's surface details.
// Left and right as seen on the screen (left is +X). Its left wing was patched after a hit, its
// left engine replaced; its right wing carries a sensor blister and a whip antenna, its right
// engine has a hatch left open; a dorsal mast strings a wire antenna to the right fin.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

const WING_TOP = 9.5;
/** The hull paint by loft band, then by section side (see {@link petrelHullPaint}). */
const HULL_PAINT: Readonly<Record<number, Readonly<Record<number, Rgb>>>> = {
  0: { 3: SHADE.dark, 4: SHADE.dark },
  2: { 3: SHADE.panel, 4: SHADE.panel },
  3: { 2: SHADE.light },
  4: { 1: SHADE.dark, 6: SHADE.dark },
  5: { 3: SHADE.panel, 4: SHADE.panel },
  7: { 2: SHADE.dark, 3: SHADE.dark, 4: SHADE.dark, 5: SHADE.dark },
};
const QUARTER = Math.PI / 2;

/**
 * The paint of the hull's loft (stations of `storm-petrel-model.ts`): darker plates along its
 * back, a vent band on its flanks, the cockpit windows under the nose armour, and a lighter
 * replacement panel on its left shoulder.
 */
export function petrelHullPaint(side: number, band: number): Rgb | undefined {
  return HULL_PAINT[band]?.[side];
}

/** The back of the hull: a dorsal spine, an off-centre astrodome, the mast and its wire. */
export function petrelBack(p: EnemyParts, neon: Rgb): void {
  const spine = [
    [-26, 2.4, 12.2, 14.2],
    [-6, 2.4, 14.2, 16],
  ] as const;
  p.hull.loft(POD_SECTION, spine, SHADE.panel);
  for (let k = 0; k < 4; k++)
    p.neon.box([1.2, 0.3, 1.2], neon, { at: [0, 14.25 + k * 0.45, -24 + k * 5] });
  // The navigator's astrodome, on the left of the back only.
  p.hull.cylinder(3.2, 1, 6, SHADE.panel, { at: [4.6, 10.2, -12] });
  p.hull.lathe(
    [
      [2.6, 0],
      [2, 1.6],
      [0, 2.3],
    ],
    6,
    SHADE.dark,
    { at: [4.6, 11.2, -12] },
  );
  p.neon.ring(2.75, 0.4, 6, neon, { at: [4.6, 11.1, -12] });
  // The dorsal mast on the right, its wire antenna running back to the right fin's tip.
  mast(p, [-4.5, 10, -21], 9, neon);
  rod(p.hull, [-4.5, 18.4, -21], [-28, 19.6, -60.5], 0.18);
  // A hatch on the tail cone, the tail light at its tip.
  decals(p.hull, [rect([0, -59], [4, 5])], 8, SHADE.light);
  p.neon.box([2, 1.2, 1], neon, { at: [0, 4.4, -64.4] });
}

/** A wing's plates, rivet lines, flap fairings, and what only that side has. */
export function petrelWing(p: EnemyParts, s: number, neon: Rgb): void {
  const spar: [OutlinePoint, OutlinePoint] = [
    [s * 31, 9.6],
    [s * 41, 7.2],
  ];
  studs(p.hull, spar, [6, 0.7], WING_TOP + 0.05, SHADE.light);
  greebles(
    p.hull,
    [0, 7.5, 0],
    [
      [s * 20, -17.6, 1.6, 2.6, 5],
      [s * 34, -13.6, 1.6, 2.6, 5],
    ],
    SHADE.dark,
  );
  // A nav light on the wing tip, a hazard band where the crew steps onto the wing root.
  p.neon.box([1.4, 0.8, 2.2], neon, { at: [s * 76.6, 8.6, -3.5] });
  hazard(p.hull, [s * 33, 10.5], [6, 2.4], 3, WING_TOP + 0.05);
  // The inner wing, between the hull and the nacelle: an access plate, a vent and a cable run.
  plate(p.hull, rect([s * 14.5, 2], [4.6, 13]), WING_TOP, SHADE.panel, 0.5);
  studs(
    p.hull,
    [
      [s * 14.5, -2.2],
      [s * 14.5, 6.2],
    ],
    [4, 0.6],
    WING_TOP + 0.52,
    SHADE.light,
  );
  grille(p.hull, [s * 14.6, -11.5], [4, 6], [4, WING_TOP + 0.05]);
  edgeStrips(
    p.hull,
    sided(
      [
        [13, 11.5],
        [19, 10.5],
      ],
      s,
    ),
    0.9,
    [WING_TOP, WING_TOP + 0.5],
    SHADE.dark,
  );
  // A lamp on the fin's tip.
  p.neon.box([1, 1, 3], neon, { at: [s * 28, 20, -61.5] });
  if (s > 0) patchedWing(p);
  else sensorWing(p, neon);
}

/** The left wing, patched after a hit: mismatched plates, rivets around them, a scorch mark. */
function patchedWing(p: EnemyParts): void {
  plate(p.hull, rect([35, 3], [8, 9], 0.12), WING_TOP, SHADE.light, 0.6);
  plate(p.hull, rect([36.5, -6.5], [6, 6], -0.2), WING_TOP, SHADE.mid, 0.5);
  studs(
    p.hull,
    [
      [31.6, -0.1],
      [37.6, -0.8],
    ],
    [5, 0.6],
    WING_TOP + 0.62,
    SHADE.dark,
  );
  studs(
    p.hull,
    [
      [32.4, 6.8],
      [38.4, 6.1],
    ],
    [5, 0.6],
    WING_TOP + 0.62,
    SHADE.dark,
  );
  const scorch: OutlinePoint[] = [
    [30, -10],
    [33, -12.5],
    [38, -11.5],
    [41, -9],
    [37, -8.4],
    [32, -8.6],
  ];
  decals(p.hull, [scorch], WING_TOP + 0.04, SHADE.scorch);
}

/** The right wing: a neat plate, a sensor blister with its light, and a whip antenna. */
function sensorWing(p: EnemyParts, neon: Rgb): void {
  plate(p.hull, rect([-35.5, -5], [8, 10]), WING_TOP, SHADE.panel, 0.5);
  const blister: Vec3 = [-36, WING_TOP, 4.5];
  p.hull.lathe(
    [
      [3.4, 0],
      [3, 1.8],
      [1.4, 3],
      [0, 3.2],
    ],
    6,
    SHADE.panel,
    { at: blister },
  );
  p.neon.box([1.2, 0.6, 1.2], neon, { at: shift(blister, [0, 3, 1.4]) });
  rod(p.hull, [-40, WING_TOP, -2], [-43, WING_TOP + 9, -9], 0.2);
}

/**
 * A nacelle's details: an exhaust collar, and on the left a replacement engine with cooling
 * fins across its back and a darker cowl.
 */
export function petrelNacelle(p: EnemyParts, at: Vec3, s: number): void {
  p.hull.ring(5, 1.6, 6, SHADE.dark, { at: shift(at, [0, 3.5, -18]), pitch: QUARTER });
  decals(p.hull, [rect([at[0], at[2] + 4], [4.5, 6])], at[1] + 8.8, SHADE.dark);
  for (const dz of [-13, 13]) {
    p.hull.ring(5.9, 1.2, 6, SHADE.mid, { at: shift(at, [0, 4.5, dz]), pitch: QUARTER });
  }
  if (s < 0) {
    // The right engine's maintenance hatch, left open on its gears.
    cog(p.hull, shift(at, [0, 8.4, 4]), [2, 0.8], 6);
    p.hull.box([0.4, 3.6, 5.6], SHADE.light, { at: shift(at, [2.7, 8.8, 4]), roll: -0.5 });
    return;
  }
  for (let k = 0; k < 4; k++) {
    p.hull.box([7, 1, 0.8], SHADE.light, { at: shift(at, [0, 8.6, -10 + k * 2.4]) });
  }
  p.hull.cylinder(3, 3.5, 6, SHADE.panel, { at: shift(at, [s * 5, 6, -6]), pitch: QUARTER });
}

/** The tailplanes: elevators along their trailing edges, a plate at their root. */
export function petrelTail(p: EnemyParts, s: number): void {
  const elevator: OutlinePoint[] = [
    [13, -60],
    [27, -61.4],
    [27, -62.4],
    [13, -61.8],
  ];
  decals(p.hull, [sided(elevator, s)], 9.55, SHADE.dark);
  plate(p.hull, sided(rect([20, -57], [7, 3.5], -0.3), s), 9.5, SHADE.panel, 0.4);
}

/** Gun pod details: a grille on its back, hazard corners, an ammo drum or a targeting eye. */
export function podDetails(p: EnemyParts, at: Vec3, neon: Rgb): void {
  const s = Math.sign(at[0]) || 1;
  const [x, , z] = at;
  grille(p.hull, [x, z - 5], [4.4, 7], [4, 19.05]);
  hazard(p.hull, [x - 10.5, z + 11.2], [4, 2.6], 2, 11.55);
  hazard(p.hull, [x + 10.5, z + 11.2], [4, 2.6], 2, 11.55);
  p.hull.ring(4.6, 1.4, 6, SHADE.dark, { at: shift(at, [0, 14.5, -16.5]), pitch: QUARTER });
  if (s > 0) {
    // The left pod's targeting eye, outboard.
    const eye = shift(at, [10.5, 11.5, 2]);
    p.hull.cylinder(2.4, 2.6, 6, SHADE.panel, { at: eye });
    p.neon.cylinder(1.2, 1, 6, neon, { at: shift(eye, [0, 2.6, 0]) });
  } else {
    // The right pod's ammo drum, outboard, its feed chute into the pod.
    p.hull.cylinder(3.2, 4, 8, SHADE.panel, { at: shift(at, [-10.5, 11.5, -4]) }, 3);
    p.hull.box([4, 1.4, 2], SHADE.dark, { at: shift(at, [-7.5, 14, -4]) });
  }
}

/** The missile rack's details: an exhaust grille at its back, a hazard band, a mast on one side. */
export function rackDetails(p: EnemyParts, at: Vec3, neon: Rgb): void {
  const [x, , z] = at;
  grille(p.hull, [x, z - 8.6], [3.6, 15], [7, 13.05], QUARTER);
  hazard(p.hull, [x, z + 8.4], [17, 2.6], 6, 13.05);
  mast(p, shift(at, [8.4, 13, -9.6]), 5, neon);
  greebles(p.hull, shift(at, [0, 13, 0]), [
    [-9.6, -9.4, 1.6, 1, 2],
    [-9.6, 0, 1.4, 0.8, 7],
  ]);
}

/** The nose armour's details: a raised seam rib across it and a searchlight on its left. */
export function plateDetails(p: EnemyParts, at: Vec3, neon: Rgb): void {
  const z = at[2];
  const rib = [
    [z - 3.2, 13.4, -1.1, 14.5],
    [z - 1, 13, -1.1, 14.2],
  ] as const;
  p.hull.loft(FIGHTER_SECTION, rib, SHADE.light, { at: [at[0], 0, 0] });
  const lamp: Vec3 = [at[0] + 6.4, 6.8, z + 6];
  p.hull.box([3, 1.6, 3], SHADE.dark, { at: lamp });
  p.neon.box([2, 0.4, 0.5], neon, { at: shift(lamp, [0, 0.6, 1.5]) });
  dish(p, [at[0] - 7, 7.6, z + 1], 2.2, [0.6, -0.8]);
}
