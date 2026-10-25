import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { angryEyes, decal, SIDES } from '../enemies/enemy-shapes';
import { mirrored, sided } from './final-boss-shapes';
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
import { armour, cables, cog, conduit, glowLine, MECH, ram, well } from './final-boss-mechanism';

// P07-R05 (phase 7 review: more detail, not symmetrical, fat armour over a mechanism): the Mesa
// Fortress's upper tier is three chunky armour blocks over its machinery: cogs, rams, cables and
// lit conduits show in the trench and the slot between them. The left block was hit: a corner
// torn off shows the gears under it, a patch is bolted next to it; a comms tower stands on the
// right block, a radar dish on the right of the lower deck, crates on the left (left and right
// as seen on the screen: left is +X).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

const QUARTER = Math.PI / 2;
/** Heights: the lower deck, the machinery floor in the gaps, the front and the side blocks. */
const DECK = 7;
const FLOOR = 10;
const FRONT_TOP = 15;
const SIDE_TOP = 17;

/** The upper tier's outline: the machinery block under the armour. */
const KEEP = mirrored([
  [0, 40],
  [16, 38],
  [28, 26],
  [30, 4],
  [26, -14],
  [14, -20],
  [0, -22],
]);
/** The front armour block (the fan cannon stands on it), ahead of the slot. */
const FRONT = mirrored([
  [0, 40],
  [16, 38],
  [28, 26],
  [29.7, 11.5],
  [0, 11.5],
]);
/** A side block (its +X outline; mirrored, the right block), beside the central trench. */
const SIDE_BLOCK = [
  [9.5, 5],
  [29.9, 5],
  [26.2, -14],
  [14, -20],
  [9.5, -21],
] as const;
/** The left side block (+X side of the model), its inner rear corner torn off. */
const TORN_BLOCK = [
  [9.5, 5],
  [29.9, 5],
  [26.2, -14],
  [17.5, -18.3],
  [18.5, -13],
  [14, -10.5],
  [9.5, -11.5],
] as const;

/** The upper tier: the machinery block, the armour blocks, the trench, the eyes. */
export function mesaKeep(p: EnemyParts, neon: Rgb): void {
  well(p.hull, KEEP, FLOOR);
  p.hull.slab(KEEP, [DECK, FLOOR - 0.4], MECH.metal);
  armour(p.hull, FRONT, [DECK, FRONT_TOP], SHADE.panel, 1.5, SHADE.mid);
  armour(p.hull, sided(SIDE_BLOCK, -1), [DECK, SIDE_TOP], SHADE.panel, 1.6, SHADE.mid);
  armour(p.hull, TORN_BLOCK, [DECK, SIDE_TOP], SHADE.panel, 1.6, SHADE.mid);
  for (const eye of angryEyes([0, 17.5], 2, [9, 1.6], 0.3))
    decal(p.neon, eye, FRONT_TOP + 0.05, neon);
  trench(p, neon);
  slot(p, neon);
  tornCorner(p, neon);
  commsTower(p, neon);
  for (const s of SIDES) {
    // The red gun slits along the side blocks, their seams and rivets.
    for (let k = 0; k < 3; k++) {
      const z = -9 + k * 5.5;
      glowLine(
        p.neon,
        [
          [s * 25.6, z],
          [s * 25.6, z + 3.8],
        ],
        SIDE_TOP - 0.3,
        neon,
      );
    }
    studs(
      p.hull,
      [
        [s * 13, 3],
        [s * 24, 3],
      ],
      [5, 0.7],
      SIDE_TOP + 0.03,
      SHADE.light,
    );
    hazard(p.hull, [s * 19, 34], [8, 2.4], 3, FRONT_TOP + 0.03);
  }
}

/** The trench between the side blocks: two cogs, a cable bundle, a ribbed conduit, rams, lights. */
function trench(p: EnemyParts, neon: Rgb): void {
  cog(p.hull, [0, FLOOR, -5], [6.6, 1.2], 10, { yaw: 0.2 });
  cog(p.hull, [2.5, FLOOR + 0.6, -16], [3.8, 1], 7, { yaw: 0.5 });
  cables(p.hull, [-6.2, FLOOR + 0.5, -21], [-6.2, FLOOR + 0.5, 8], [3, 1.1, 0.45]);
  conduit(p.hull, [6.6, FLOOR + 0.9, -21], [6.6, FLOOR + 0.9, 8], [0.8, 6]);
  for (const s of SIDES) {
    glowLine(
      p.neon,
      [
        [s * 8.6, -20],
        [s * 8.6, 5],
      ],
      FLOOR,
      neon,
    );
    ram(p.hull, [s * 3.5, FLOOR, 1.5], [s * 9.6, SIDE_TOP - 2, 1.5], 0.9);
    ram(p.hull, [s * 4.5, FLOOR, -19], [s * 9.8, SIDE_TOP - 2, -16], 0.9);
  }
}

/** The slot between the front block and the side blocks: upright cog rims and a lit conduit. */
function slot(p: EnemyParts, neon: Rgb): void {
  for (const x of [-21, -12, 12, 21]) {
    cog(p.hull, [x + 0.6, FLOOR - 1, 8.25], [3.8, 1.2], 7, { roll: QUARTER });
  }
  glowLine(
    p.neon,
    [
      [-28, 8.25],
      [28, 8.25],
    ],
    FLOOR,
    neon,
  );
  cables(p.hull, [-27, FLOOR + 0.3, 7.4], [27, FLOOR + 0.3, 7.4], [1, 0, 0.5]);
}

/** The torn corner of the left block: gears and cut cables in it, scorch, a bolted patch. */
function tornCorner(p: EnemyParts, neon: Rgb): void {
  cog(p.hull, [13.5, FLOOR - 0.6, -16], [3.6, 1.2], 7, { roll: QUARTER });
  cog(p.hull, [15.5, FLOOR, -13.5], [2.4, 1], 6, { yaw: 0.3 });
  rod(p.hull, [10, FLOOR + 0.5, -18], [13, FLOOR + 4, -12.5], 0.35, MECH.bright);
  rod(p.hull, [11, FLOOR + 0.5, -19], [15, FLOOR + 3, -15], 0.35, MECH.metal);
  p.neon.box([0.8, 0.8, 0.8], neon, { at: [13.2, FLOOR + 3.6, -12.8] });
  const scorch: OutlinePoint[] = [
    [14.5, -9.5],
    [19, -12],
    [21, -16],
    [24, -12],
    [22, -6],
    [17, -5.5],
  ];
  decals(p.hull, [scorch], SIDE_TOP + 0.02, SHADE.scorch);
  plate(p.hull, rect([22, -1], [6, 6], 0.15), SIDE_TOP, SHADE.light, 0.5);
  studs(
    p.hull,
    [
      [19.6, 1.4],
      [24.4, 2.1],
    ],
    [4, 0.6],
    SIDE_TOP + 0.52,
    SHADE.dark,
  );
}

/** A comms tower on the right block only: a mast with crossbars, a dish, stays, a beacon. */
function commsTower(p: EnemyParts, neon: Rgb): void {
  const base: Vec3 = [-20, SIDE_TOP, -8];
  p.hull.box([6, 2, 6], SHADE.dark, { at: base }, SHADE.panel);
  mast(p, [-20, SIDE_TOP + 2, -8], 10, neon);
  p.hull.box([5, 0.4, 0.6], SHADE.panel, { at: [-20, SIDE_TOP + 6, -8] });
  dish(p, [-24.5, SIDE_TOP, -3], 3.4, [0.7, -0.6]);
  for (const d of [3, -3]) {
    rod(p.hull, [-20 + d, SIDE_TOP + 0.5, -8 + d], [-20, SIDE_TOP + 9, -8], 0.18);
  }
}

/** An arm's elbow: armour plates over its beam, a gap with a cog, cables and a lit conduit. */
export function mesaArm(p: EnemyParts, s: number, neon: Rgb): void {
  const side = (o: readonly OutlinePoint[]): readonly OutlinePoint[] => sided(o, s);
  armour(p.hull, side(rect([49.5, -15], [10, 16])), [5, 9], SHADE.panel, 1.2, SHADE.mid);
  armour(p.hull, side(rect([72.5, -15], [21, 15])), [5, 9], SHADE.panel, 1.2, SHADE.mid);
  cog(p.hull, [s * 58, 5.4, -15], [3.4, 1], 7, { yaw: 0.3 });
  cables(p.hull, [s * 52, 6.4, -9.5], [s * 64, 6.4, -9.5], [1, 0, 0.5]);
  conduit(p.hull, [s * 52, 6.6, -20.5], [s * 64, 6.6, -20.5], [0.7, 3]);
  glowLine(
    p.neon,
    [
      [s * 54.8, -15],
      [s * 61.2, -15],
    ],
    6,
    neon,
  );
  ram(p.hull, [s * 38, 5, -30], [s * 46, 7.5, -22], 1);
  grille(p.hull, [s * 72.5, -15], [6, 9], [5, 9.03]);
}

/**
 * The lower deck's details: grilles beside the upper tier, a vent bank and hazard band on the
 * rear deck, a radar dish on its right front corner, crates on the left one.
 */
export function mesaDeck(p: EnemyParts): void {
  for (const s of SIDES) {
    grille(p.hull, [s * 35.5, -6], [5, 10], [5, DECK + 0.03]);
    grille(p.hull, [s * 35.5, -26], [5, 10], [5, DECK + 0.03]);
    plate(p.hull, sided(rect([36, 12], [5.5, 10]), s), DECK, SHADE.mid, 0.6);
  }
  grille(p.hull, [0, -36], [5, 22], [8, DECK + 0.03], QUARTER);
  hazard(p.hull, [0, -45.5], [24, 3], 8, DECK + 0.03);
  dish(p, [-34, DECK, 20], 3.6, [0.6, 2.6]);
  greebles(
    p.hull,
    [33, DECK, 21],
    [
      [0, 0, 4, 3, 5],
      [0.5, -5, 3.5, 2, 4],
      [-0.3, 4.6, 3, 1.6, 3],
    ],
  );
}

/** A lance housing's details: vent grilles on its shoulders and a junction box behind. */
export function lanceDetails(p: EnemyParts, at: Vec3): void {
  const [x, , z] = at;
  grille(p.hull, [x - 6, z - 8], [4, 7], [4, 11.03]);
  grille(p.hull, [x + 6, z - 8], [4, 7], [4, 11.03]);
  greebles(p.hull, [x, 11, z - 15], [[0, 0, 6, 1.4, 3]], SHADE.dark);
}

/** A silo's details: bolts round its rim, a pipe stub and a valve box on its side. */
export function siloDetails(p: EnemyParts, at: Vec3): void {
  const [x, , z] = at;
  for (let k = 0; k < 6; k++) {
    const a = (2 * Math.PI * (k + 0.5)) / 6;
    const [dx, dz] = [Math.sin(a) * 11.5, Math.cos(a) * 11.5];
    p.hull.box([1.2, 0.8, 1.2], SHADE.light, { at: [x + dx, DECK + 3.2, z + dz] });
  }
  const s = Math.sign(x) || 1;
  greebles(p.hull, [x + s * 7, DECK + 3, z - 8.5], [[0, 0, 3, 2.2, 3]], SHADE.dark);
}
