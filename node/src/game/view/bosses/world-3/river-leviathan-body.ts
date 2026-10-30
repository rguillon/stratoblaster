import type { OutlinePoint } from '../../../../render/geometry/outline';
import {
  LEVIATHAN_BODY,
  LEVIATHAN_JOINTS,
  LEVIATHAN_RACK,
  SEGMENTS,
  TURRET_EMITTER_HEIGHT,
  type Segment,
} from '../../../config/bosses/world-3/river-leviathan';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, radial, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, type LimbDrawing } from '../boss-limbs';
import type { PartDrawing } from '../boss-model';
import { GEAR } from '../mini-boss-mechanism';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { moss, scutes, SWAMP, vine } from './mangrove-croc-jungle';
import { reactorSac } from '../../enemies/organic-parts';
import { ribs, ROUND_SECTION } from '../../../../render/geometry/organic';
import { F, gland, veinTo } from './jungle-flesh';

// P09-R09, 3-1: the River Leviathan's body: its four segments and its tail, each drawn on its
// hinge (D-061) so that they sway one after the other, the segments' ring turrets on their
// sponsons and the tail's missile rack. Logical pixels, nose +Z, Y up: the playfield's +Y (the
// tail) is the model's -Z, and its -X (the screen's left) the model's +X.
type Vec3 = [number, number, number];

/** The River Leviathan's teal neon (P09-R09). */
export const LEVIATHAN_TEAL = BOSS_LOOK.neon['river-leviathan'] ?? [0.05, 0.9, 0.8];
const N = LEVIATHAN_TEAL;

/** The segments' half widths and their heights (bottom, top), head to tail. */
const SEGMENT_WIDTH = [15, 14, 13, 12] as const;
const SEGMENT_Y = [-3, 10] as const;
/** The tail (loft stations from its hinge, along -Z: z, half width, bottom, top). */
const TAIL = [
  [2, 11, -2.5, 8.5],
  [-14, 10, -2, 8],
  [-26, 7, -1, 6.5],
  [-36, 2.5, 1, 4],
] as const;
/** A tail fluke (the left one at +X), seen from above, from the tail's tip. */
const FLUKE: readonly OutlinePoint[] = [
  [1, 2],
  [12, -4],
  [14, -9],
  [9, -7],
  [1, -4],
];
/** The ring turret's dome (a lathe profile above its mount). */
const DOME = [
  [8, 0],
  [8.2, 1.2],
  [6.6, 4.2],
  [3.2, 6],
  [0, 6.4],
] as const;
/** Height of the turret's mount (where its dome stands) and of the sponson's deck. */
const MOUNT = 7.5;

/** The model z of the hinge `i` (0 = the neck). */
const hingeZ = (i: number): number => -(LEVIATHAN_BODY.hinges[i] ?? 0);

/**
 * A ball joint at hinge `i`: a round collar standing on the pivot, so that the bend between two
 * segments never opens a gap whichever way they turn.
 */
function collar({ hull, neon }: EnemyParts, i: number, radius: number): void {
  const at: Vec3 = [0, SEGMENT_Y[0] + 0.5, hingeZ(i)];
  hull.cylinder(radius, SEGMENT_Y[1] - SEGMENT_Y[0] - 1.5, 8, GEAR, { at }, radius * 0.9);
  neon.ring(radius * 0.92, 0.6, 8, N, { at: offset(at, 0, SEGMENT_Y[1] - SEGMENT_Y[0] - 2.4, 0) });
}

/**
 * Segment `k`, on its hinge: its collar, an armoured hull plate along the spine with scutes and
 * a teal light down its back, its turret's sponson out to one side, moss and a hanging vine.
 */
function drawSegment(k: Segment) {
  const i = k - 1;
  const w = SEGMENT_WIDTH[i] ?? 12;
  const [front, back] = [hingeZ(i) - 2, hingeZ(i + 1) + 1];
  return (p: EnemyParts): void => {
    const { hull, flesh, neon } = p;
    collar(p, i, w * 0.85);
    const [b, t] = SEGMENT_Y;
    // P16-R06: a living serpent's segment: swollen teal flesh, bone ribs over it, a vein along
    // its spine; the scutes and the sponson its grafted armour.
    const stations = [
      [back, w * 0.8, b + 1, t - 1.5],
      [back + 6, w, b, t],
      [front - 6, w, b, t],
      [front, w * 0.85, b + 1, t - 1],
    ] as const;
    flesh.loft(ROUND_SECTION, stations, F.teal);
    ribs(
      flesh,
      [back + 9, front - 9],
      { halfWidth: w * 0.95, y: b + 2, height: t - b - 1.4, thickness: 0.7 },
      F.bone,
    );
    neon.box([1.2, 0.5, front - back - 8], N, { at: [0, t + 0.05, (front + back) / 2] });
    const ridge: Vec3[] = [front - 8, (front + back) / 2, back + 8].map((z) => [0, t - 0.4, z]);
    scutes(hull, ridge.slice(0, 1), 2.2);
    scutes(hull, ridge.slice(2), 2.2);
    for (const s of SIDES) {
      hull.box([2.4, 1.2, front - back - 10], SHADE.edge, {
        at: [s * w * 0.62, t - 0.4, (front + back) / 2],
      });
    }
    sponson(p, k);
    const side = -(LEVIATHAN_BODY.sides[i] ?? 1);
    moss(
      hull,
      [
        [-side * 3, back + 6],
        [-side * 9, back + 7],
        [-side * 8, back + 13],
        [-side * 3, back + 12],
      ],
      t - 0.2,
    );
    vine(hull, [-side * w * 0.9, t - 3, front - 5], [-side * w * 0.9, t - 3, back + 6], 5);
  };
}

/** The sponson carrying segment `k`'s turret: an armoured arm from the spine out to its mount. */
function sponson({ hull, neon }: EnemyParts, k: Segment): void {
  const [x, , z] = turretSpot(k);
  const s = Math.sign(x);
  hull.box([Math.abs(x) - 6, 3, 9], H.dark, { at: [x / 2 + s * 2, MOUNT - 4, z] }, H.panel);
  hull.box([Math.abs(x) - 10, 1, 4], GEAR, { at: [x / 2 + s * 2, MOUNT - 1, z] });
  neon.box([Math.abs(x) - 14, 0.4, 0.8], N, { at: [x / 2 + s * 3, MOUNT - 0.95, z + 2.6] });
}

/** Where segment `k`'s turret stands, in model space (on its mount). */
function turretSpot(k: Segment): Vec3 {
  const i = k - 1;
  return bossPoint(
    (LEVIATHAN_BODY.sides[i] ?? 1) * LEVIATHAN_BODY.turretOut,
    LEVIATHAN_BODY.middles[i] ?? 0,
  );
}

/** The tail, on its hinge: its collar, a tapering hull, two flukes with reactors, moss. */
function drawTail(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  const z0 = hingeZ(4);
  collar(p, 4, 9.5);
  // P16-R06: a tapering flesh tail, membrane flukes on bone, its reactors in flesh sacs.
  flesh.loft(
    ROUND_SECTION,
    [...TAIL].reverse().map(([z, w, b, t]) => [z0 + z, w, b, t] as const),
    F.teal,
  );
  const tip = z0 + (TAIL.at(-1)?.[0] ?? 0);
  for (const s of SIDES) {
    const fluke = FLUKE.map(([x, z]): OutlinePoint => [s * x, tip + 4 + z]);
    flesh.bevelSlab(fluke, [1.5, 2.5, 3.5], [0.4, 0.8], F.membrane, {}, F.teal);
    neon.box([0.8, 0.5, 8], N, { at: [s * 8, 3.6, tip - 2], yaw: s * 0.9 });
    reactorSac(p, [s * 4.5, 3, tip + 2], 1.8, N, { flesh: F.teal });
  }
  neon.box([1, 0.5, 20], N, { at: [0, 8.55, z0 - 4] });
  moss(
    hull,
    [
      [-2, z0 - 28],
      [4, z0 - 26],
      [3, z0 - 20],
      [-3, z0 - 22],
    ],
    6.8,
  );
}

/** The body (D-061): each segment, and the tail, drawn on its hinge; they go with the core. */
export function leviathanBody(): Record<string, LimbDrawing> {
  const limbs: Record<string, LimbDrawing> = {};
  for (const k of SEGMENTS) limbs[LEVIATHAN_JOINTS[k - 1] ?? 'neck'] = { draw: drawSegment(k) };
  limbs.tail = { draw: drawTail };
  return limbs;
}

/** A segment's turret mount (the part, P09-R09): a round armoured base with a teal ring. */
export const turretMount: PartDrawing = (p, at) => {
  const { hull, flesh, neon } = p;
  // P16-R06: a swollen gland on the serpent's flank, the turret's metal ring grafted on top.
  flesh.cylinder(10, MOUNT, 7, F.crimson, { at: offset(at, 0, 0, 0), yaw: QUARTER / 4 }, 9);
  hull.cylinder(8.6, 0.6, 8, GEAR, { at: offset(at, 0, MOUNT, 0), yaw: QUARTER / 4 });
  neon.ring(10.1, 0.8, 8, N, { at: offset(at, 0, MOUNT - 2.2, 0), yaw: QUARTER / 4 });
  veinTo(
    p,
    [offset(at, 0, MOUNT * 0.4, -10), offset(at, 0, MOUNT * 0.4, 10)],
    [-Math.sign(at[0]) * 3, 0, 0],
    N,
  );
};

/**
 * A segment's ring turret (P09-R09), turning with its rings (D-060): a dome ringed with four
 * stubby vanes, the ring emitter glowing on its axis at the top, where its rings leave from.
 */
export const ringTurret: PartDrawing = (p, at) => {
  const { hull, neon, charge, muzzle } = p;
  const base = offset(at, 0, MOUNT + 0.6, 0);
  const top = TURRET_EMITTER_HEIGHT - 1.4 - base[1];
  hull.lathe(
    DOME.map(([r, y]) => [r, (y * top) / 6.4] as const),
    8,
    H.base,
    { at: base, yaw: QUARTER / 4 },
  );
  for (const a of around(4)) {
    const foot = radial(a + QUARTER / 2, 6.4, 0);
    hull.box(
      [2.6, 2.6, 6],
      H.dark,
      { at: offset(base, foot[0], 0.6, foot[2]), yaw: a + QUARTER / 2 },
      H.panel,
    );
    const lamp = radial(a + QUARTER / 2, 9.2, 0);
    charge.box([1.8, 1.2, 0.8], WHITE, {
      at: offset(base, lamp[0], 1.3, lamp[2]),
      yaw: a + QUARTER / 2,
    });
  }
  neon.ring(5.2, 0.6, 8, N, { at: offset(base, 0, top * 0.62, 0), yaw: QUARTER / 4 });
  hull.cylinder(1.8, 1.4, 6, H.dark, { at: offset(at, 0, TURRET_EMITTER_HEIGHT - 1.4, 0) });
  charge.cylinder(1.3, 0.3, 6, WHITE, { at: offset(at, 0, TURRET_EMITTER_HEIGHT - 0.3, 0) });
  muzzle(offset(at, 0, TURRET_EMITTER_HEIGHT, 0));
};

/**
 * The tail's missile rack (P09-R09): an armoured box on the tail's back, four cells open at its
 * top, each with a charge light round its mouth, a teal band round it.
 */
export const missileRack: PartDrawing = (p, at) => {
  const { hull, neon, charge, muzzle } = p;
  const height = LEVIATHAN_RACK[0]?.[2] ?? 10;
  // P16-R06: an egg sac swelling on the tail, a grafted rack of missile cells capping it.
  p.flesh.box([16, height - 4, 18], F.crimson, { at: offset(at, 0, 4, 0) }, F.sinew);
  gland(p, offset(at, 0, height - 2, -10), 2, N);
  hull.box([17, 1.4, 19], H.dark, { at: offset(at, 0, 4.5, 0) });
  neon.box([16.4, 0.6, 18.4], N, { at: offset(at, 0, 6.5, 0) });
  for (const cell of LEVIATHAN_RACK) {
    const mouth = bossPoint(...cell);
    hull.cylinder(2.6, 0.5, 6, H.dark, { at: offset(mouth, 0, -0.45, 0) });
    charge.ring(2.8, 0.4, 6, WHITE, { at: offset(mouth, 0, -0.35, 0) });
    muzzle(mouth, 'missile');
  }
  hull.box([3, 1.2, 18], SWAMP.stone, { at: offset(at, 0, height - 0.2, 0) });
};
