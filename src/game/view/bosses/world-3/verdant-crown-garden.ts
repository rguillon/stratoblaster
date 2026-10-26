import type { Placement, SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { VERDANT_BLOOM } from '../../../config/bosses/world-3/verdant-crown';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, radial } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-limbs';

// P09-R09, 3-5: the Verdant Crown's colours and its glass garden dome over the core: a lattice of
// ribs and glowing mullions, trees inside, the tallest one rising through the oculus at the top.
// Model space: logical pixels, nose +Z (down the screen), Y up towards the camera.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

const H = ENEMY_LOOK.hull;
const WHITE: Rgb = [1, 1, 1];

/** Emerald, its registered neon (GD-61), and magenta, its second neon colour (P09-R09). */
export const EMERALD: Rgb = BOSS_LOOK.neon['verdant-crown'] ?? [0.1, 1, 0.45];
export const MAGENTA: Rgb = [1, 0.15, 0.75];
/** The World 3 jungle over the dark metal: moss, bark, leaves, old stone. */
export const JUNGLE = {
  moss: [0.1, 0.19, 0.07] as Rgb,
  bark: [0.13, 0.085, 0.05] as Rgb,
  leaf: [0.07, 0.24, 0.09] as Rgb,
  stone: [0.2, 0.2, 0.17] as Rgb,
};

/** Height of the deck's top, which the dome, the city and the parts stand on. */
export const DECK_TOP = 6;
/** The dome: its radius, its ribs, the elevations of its mullions and of its oculus's rim. */
const DOME = { radius: 31, ribs: 8, mullions: [0.42, 0.85], oculus: 1.2, steps: 4 } as const;

/** A cylinder of `radius` (to `end` at `b`) from `a` to `b`, `sides` facets. */
export function strut(
  builder: SolidBuilder,
  [a, b]: readonly [Vec3, Vec3],
  [radius, end]: readonly [number, number],
  color: Rgb,
  sides = 4,
): void {
  const [dx, dy, dz] = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const length = Math.hypot(dx, dy, dz);
  const place: Placement = {
    at: a,
    pitch: Math.acos(dy / length),
    yaw: Math.atan2(dx, dz),
  };
  builder.cylinder(radius, length, sides, color, place, end);
}

/** The point of the dome at the turn `a` (from the nose) and the elevation `e` (radians). */
function onDome(a: number, e: number): Vec3 {
  const r = DOME.radius * Math.cos(e);
  return [Math.sin(a) * r, DECK_TOP + DOME.radius * Math.sin(e), Math.cos(a) * r];
}

/** The dome's lattice: dark ribs up to the oculus, glowing mullions round it, a lit rim. */
function drawLattice({ hull, neon }: EnemyParts): void {
  const { radius, ribs, mullions, oculus, steps } = DOME;
  for (const a of around(ribs)) {
    const turn = a + Math.PI / ribs;
    for (let k = 0; k < steps; k++) {
      const [e0, e1] = [(oculus * k) / steps, (oculus * (k + 1)) / steps];
      strut(hull, [onDome(turn, e0), onDome(turn, e1)], [1, 1], H.panel);
    }
  }
  for (const e of mullions) {
    const [, y] = onDome(0, e);
    neon.ring(radius * Math.cos(e), 0.4, ribs * 2, EMERALD, { at: [0, y, 0] });
  }
  const [, top] = onDome(0, oculus);
  const rim = radius * Math.cos(oculus);
  hull.cylinder(rim + 1.5, 1.6, ribs * 2, H.base, { at: [0, top - 0.8, 0] }, rim + 1);
  neon.ring(rim + 1.6, 0.6, ribs * 2, MAGENTA, { at: [0, top - 0.4, 0] });
  hull.cylinder(radius + 2, 3, ribs * 2, H.panel, { at: [0, DECK_TOP - 1, 0] }, radius + 1);
  neon.ring(radius + 2.1, 0.8, ribs * 2, EMERALD, { at: [0, DECK_TOP + 0.6, 0] });
}

/** A tree of the garden: where (model x, z), how tall, how wide its crown. */
const TREES = [
  [14, 10, 18, 7],
  [-15, 8, 16, 6.5],
  [10, -15, 15, 7],
  [-12, -14, 19, 6],
  [0, 18, 13, 5.5],
  [21, -4, 12, 5],
  [-21, -2, 13, 5],
] as const;
/** A crown of leaves (a lathe profile in units of its radius): a squat, faceted ball. */
const CROWN = [
  [0.4, 0],
  [1, 0.35],
  [0.85, 0.8],
  [0, 1.1],
] as const;

/** A tree: a trunk and a faceted crown of leaves, a magenta flower or two in it. */
function tree(
  { hull, neon }: EnemyParts,
  [tx, tz, th, tr]: readonly [number, number, number, number],
  i: number,
): void {
  hull.cylinder(1.2, th - tr * 0.4, 5, JUNGLE.bark, { at: [tx, DECK_TOP, tz] }, 0.7);
  const crown = CROWN.map(([u, v]) => [u * tr, v * tr] as const);
  hull.lathe(crown, 6, JUNGLE.leaf, { at: [tx, DECK_TOP + th - tr * 0.6, tz], yaw: i });
  const [fx, , fz] = radial(i * 2.1, tr * 0.8, 0);
  neon.box([1.2, 1.2, 1.2], MAGENTA, { at: [tx + fx, DECK_TOP + th - tr * 0.2, tz + fz] });
}

/** The tallest tree, rising through the oculus, its bloom the core's ring emitter. */
function greatTree(p: EnemyParts): void {
  const { hull, charge, muzzle } = p;
  const bloom = bossPoint(...VERDANT_BLOOM);
  hull.cylinder(2.6, bloom[1] - DECK_TOP - 9, 6, JUNGLE.bark, { at: [0, DECK_TOP, 0] }, 1.4);
  const crown = CROWN.map(([u, v]) => [u * 10, v * 6] as const);
  hull.lathe(crown, 7, JUNGLE.leaf, { at: [0, bloom[1] - 8.6, 0] });
  hull.lathe(
    [
      [3.6, 0],
      [2.2, 1.6],
    ],
    6,
    JUNGLE.moss,
    { at: [0, bloom[1] - 2.6, 0] },
  );
  charge.lathe(
    [
      [2.4, 0],
      [1.2, 0.8],
      [0, 1],
    ],
    6,
    WHITE,
    { at: [0, bloom[1] - 1, 0] },
  );
  muzzle(bloom, 'ring');
}

/** The glass garden dome over the core (P09-R09): its lattice, its garden, its great tree. */
export function drawGarden(p: EnemyParts): void {
  p.hull.cylinder(DOME.radius, 0.4, 16, JUNGLE.moss, { at: [0, DECK_TOP, 0] });
  drawLattice(p);
  TREES.forEach((t, i) => {
    tree(p, t, i);
  });
  greatTree(p);
}
