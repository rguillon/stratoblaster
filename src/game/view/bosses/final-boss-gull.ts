import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal } from '../enemies/enemy-shapes';
import { edgeStrips } from './final-boss-shapes';
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
import { armour, cables, cog, glowLine, ram } from './final-boss-mechanism';

// P07-R05 (phase 7 review: more detail, not symmetrical, fat armour over a mechanism): the Gull
// Mothership's deck details. Like a real carrier, its island stands on one side of the deck
// (the right, -X), while the left side (+X) is the runway: launch arrows on a catapult track,
// cargo containers and a deck crane by the hangar. Armour segments along the hull's back, in
// front of the bridge, leave gaps on the cogs, cables and lit conduit under them.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

const DECK = 4;
/** The armour segments on the hull's back: centre z, the hull's top there. */
const SPINE = [
  [12, 17],
  [22, 16.5],
  [32, 15.8],
  [42, 14.4],
] as const;

/** The armour segments along the hull's back and the machinery in the gaps between them. */
export function gullSpine(p: EnemyParts, neon: Rgb): void {
  for (const [z, top] of SPINE) {
    armour(p.hull, rect([0, z], [15, 7]), [top - 1.5, top + 2.6], SHADE.panel, 1.2, SHADE.mid);
    decals(p.hull, [rect([0, z - 0.5], [5, 3])], top + 2.63, SHADE.dark);
  }
  SPINE.slice(1).forEach(([z, top], i) => {
    const gap = z - 5;
    cog(p.hull, [i % 2 === 0 ? 4 : -4, top + 0.1, gap], [2.6, 0.8], 7, { yaw: i });
    p.charge.box([2.2, 0.4, 1.2], [1, 1, 1], { at: [i % 2 === 0 ? -3.5 : 3.5, top, gap] });
  });
  for (const x of [-6, 6]) {
    cables(p.hull, [x, 17.6, 8], [x, 16.6, 30], [2, 1, 0.45]);
    cables(p.hull, [x, 16.6, 30], [x, 13.8, 46], [2, 1, 0.45]);
  }
  glowLine(
    p.neon,
    [
      [0, 8],
      [0, 30],
    ],
    16.9,
    neon,
  );
  glowLine(
    p.neon,
    [
      [0, 30],
      [0, 45],
    ],
    15.2,
    neon,
  );
  ram(p.hull, [-6, 16.4, 17], [-7, 18.4, 20.5], 0.7);
  ram(p.hull, [6, 15.7, 37], [7, 17.4, 39.6], 0.7);
  // A vent block on the hull's back, behind the bridge.
  armour(p.hull, rect([0, -35], [10, 12]), [14.5, 17.5], SHADE.panel, 1, SHADE.mid);
  grille(p.hull, [0, -35], [6, 8], [5, 17.53]);
}

/** The island on the right of the deck: an armoured block, the bridge, a funnel, a radar mast. */
export function gullIsland(p: EnemyParts, neon: Rgb): void {
  armour(p.hull, rect([-30, -6], [13, 24]), [DECK - 0.5, 15], SHADE.mid, 1.6, SHADE.light);
  armour(p.hull, rect([-30.5, -1], [15, 12]), [15, 20], SHADE.panel, 1, SHADE.pale);
  p.hull.box([15.6, 1.6, 12.6], SHADE.dark, { at: [-30.5, 17, -1] });
  for (const x of [-37.5, -23.5]) p.neon.box([0.9, 0.9, 0.9], neon, { at: [x, 17.3, 5.4] });
  p.neon.box([12, 0.5, 0.6], neon, { at: [-30, 14.4, 6.2] });
  p.hull.box([5, 6, 6.5], SHADE.panel, { at: [-30, 15, -13.5] }, SHADE.dark);
  grille(p.hull, [-30, -13.5], [4, 5.5], [4, 21.05]);
  mast(p, [-31, 20, -3], 10, neon);
  p.hull.box([10, 0.8, 1.6], SHADE.pale, { at: [-31, 27.5, -3] });
  dish(p, [-25.5, 20, 2], 2.8, [0.7, 0.3]);
  rod(p.hull, [-36.5, 20, 3], [-38, 27, 1], 0.2);
  hazard(p.hull, [-30, 7.5], [11, 2.4], 4, DECK + 0.03);
  studs(
    p.neon,
    [
      [-35.5, -18.5],
      [-24.5, -18.5],
    ],
    [4, 0.8],
    DECK + 0.05,
    neon,
  );
}

/** The runway on the left of the deck: the catapult track and its arrows, cargo, a crane. */
export function gullRunway(p: EnemyParts, neon: Rgb): void {
  edgeStrips(
    p.hull,
    [
      [24, -24],
      [24, 18],
    ],
    1.6,
    [DECK - 0.2, DECK + 0.04],
    SHADE.dark,
  );
  for (let k = 0; k < 6; k++) {
    const z = -20 + k * 7;
    const arrow: OutlinePoint[] = [
      [21.8, z],
      [24, z + 2.6],
      [26.2, z],
    ];
    decal(p.neon, arrow, DECK + 0.08, neon);
  }
  hazard(p.hull, [24, -26.5], [8, 2.4], 3, DECK + 0.03);
  greebles(
    p.hull,
    [36.5, DECK, 0],
    [
      [0, -16, 5, 3.2, 7],
      [0, -8, 5, 3.2, 7],
      [0.3, 0, 4.6, 2.6, 6],
    ],
    SHADE.light,
  );
  p.hull.box([4.6, 3, 6.6], SHADE.mid, { at: [36.3, DECK + 3.2, -16] }, SHADE.pale);
  for (const z of [-16, -8]) p.neon.box([5.2, 0.4, 0.4], neon, { at: [36.5, DECK + 1.4, z + 3.4] });
  // The deck crane: a post, its boom over the containers, the hook line.
  p.hull.cylinder(1.4, 10, 6, SHADE.dark, { at: [34, DECK, 8] }, 1);
  rod(p.hull, [34, DECK + 9.5, 8], [37, DECK + 11, -12], 0.5, SHADE.light);
  rod(p.hull, [37, DECK + 11, -12], [37, DECK + 6.4, -12], 0.15);
  p.neon.box([0.9, 0.9, 0.9], neon, { at: [34, DECK + 10, 8] });
}

/** The deck itself: weathered plates, tie-down rows, edge lights, a lift on the rear deck. */
export function gullDeck(p: EnemyParts, neon: Rgb): void {
  plate(p.hull, rect([-19.5, -40], [6, 10]), DECK, SHADE.mid, 0.4);
  plate(p.hull, rect([19.5, 30], [5, 9], 0.1), DECK, SHADE.light, 0.4);
  decals(p.hull, [rect([-20, 12], [5, 7], 0.3)], DECK + 0.02, SHADE.scorch);
  studs(
    p.hull,
    [
      [-20, -30],
      [-20, 0],
    ],
    [7, 0.7],
    DECK + 0.03,
    SHADE.light,
  );
  studs(
    p.neon,
    [
      [-34, -48],
      [-15, -56],
    ],
    [4, 0.8],
    DECK + 0.05,
    neon,
  );
  studs(
    p.neon,
    [
      [34, -48],
      [15, -56],
    ],
    [4, 0.8],
    DECK + 0.05,
    neon,
  );
  for (const s of [-1, 1]) {
    p.hull.ring(4.4, 1.6, 6, SHADE.dark, { at: [s * 30, DECK + 3, -51.5], pitch: Math.PI / 2 });
    greebles(p.hull, [s * 30, DECK + 8.2, -38], [[0, 0, 4, 1.2, 6]], SHADE.dark);
  }
  deckMarkings(p);
}

/** Seams between the deck's plates, a dashed safety line by the runway, worn patches. */
function deckMarkings(p: EnemyParts): void {
  const seams = [-24, 12, 19].map((z) => rect([-30, z], [25, 0.6]));
  seams.push(rect([30, 19], [22, 0.6]), rect([31, -21], [16, 0.6]));
  decals(p.hull, seams, DECK + 0.02, SHADE.dark);
  const dashes = Array.from({ length: 6 }, (_, k) => rect([29.5, -19 + k * 6.6], [0.8, 3.6]));
  decals(p.hull, dashes, DECK + 0.02, SHADE.pale);
  plate(p.hull, rect([-28, 15.5], [10, 5.4]), DECK, SHADE.light, 0.35);
  plate(p.hull, rect([-21, -30], [7, 9], -0.1), DECK, SHADE.panel, 0.35);
  decals(p.hull, [rect([-36, 22], [6, 4], 0.5)], DECK + 0.03, SHADE.scorch);
}

/** A hangar's details: vents on its outer side, a hazard band at its back, a beacon. */
export function hangarDetails(p: EnemyParts, at: Vec3, neon: Rgb): void {
  const s = Math.sign(at[0]) || 1;
  const [x, , z] = at;
  // Armour over the hangar's outer side, a gap on the door gear between its two blocks.
  for (const dz of [-9, 6]) {
    armour(p.hull, rect([x + s * 16.6, z + dz], [3.6, 10]), [9.5, 13], SHADE.mid, 0.9, SHADE.light);
  }
  cog(p.hull, [x + s * 16.2, 9.4, z - 1.5], [2.4, 1.2], 6, { roll: Math.PI / 2 });
  ram(p.hull, [x + s * 15, 10, z - 3], [x + s * 17.8, 11.6, z - 0.4], 0.5);
  glowLine(
    p.neon,
    [
      [x + s * 17.6, z - 3.6],
      [x + s * 17.6, z + 0.6],
    ],
    10,
    neon,
  );
  hazard(p.hull, [x + s * 2, z - 17.3], [18, 1.6], 6, 10.03);
  p.hull.box([2.4, 1.4, 2.4], SHADE.dark, { at: [x + s * 16, 10, z - 16] });
  p.neon.box([1.4, 1, 1.4], neon, { at: [x + s * 16, 11.4, z - 16] });
  mast(p, [x - s * 12.5, 10, z - 16], 5, neon);
  studs(
    p.hull,
    [
      [x - s * 12.5, z - 10],
      [x - s * 12.5, z + 12],
    ],
    [6, 0.7],
    10.03,
    SHADE.light,
  );
}

/** A flak mount's details: ammo boxes behind the turret, a feed chute, warning studs. */
export function flakDetails(p: EnemyParts, at: Vec3, neon: Rgb): void {
  const [x, , z] = at;
  greebles(
    p.hull,
    [x, 6.4, z - 9],
    [
      [-3, 0, 3.6, 1.8, 2.4],
      [3, 0, 3.6, 1.8, 2.4],
    ],
    SHADE.panel,
  );
  p.hull.box([1.6, 1, 2.6], SHADE.dark, { at: [x, 7.4, z - 8.2] });
  studs(
    p.neon,
    [
      [x - 9, z + 4],
      [x - 9, z - 4],
    ],
    [3, 0.7],
    6.45,
    neon,
  );
}
