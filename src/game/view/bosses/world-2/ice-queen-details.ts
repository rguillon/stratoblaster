import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { CANOPY_SECTION, flipX, POD_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { lamps, plate } from '../mini-boss-greebles';
import { H, QUARTER } from '../mini-boss-shapes';
import { gland, glowVein, ICE_FLESH } from './w2-organic';
import { crystal, FROST, icicles, PALE_BLUE, VIOLET } from './ice-queen-shards';

// P08-R10, 2-5: the Ice Queen's details: its crystal canopy, its engine nacelles, the crystal
// fins at its tail, frosted plates and lights on its wings. Logical pixels, nose +Z, Y up.
type Vec3 = [number, number, number];

/** The crystal canopy on the fuselage's back (loft stations), closing to a point at the front. */
const CANOPY = [
  [14, 3.6, 6.5, 11.4],
  [27, 3.4, 5, 10.8],
  [37, 2.2, 4.3, 8.4],
  [44, 0, 5.8, 5.8],
] as const;
/** An engine nacelle on a wing root (loft stations), its back snowed over. */
const NACELLE = [
  [-53, 2.4, 0.4, 5],
  [-44, 3.2, 0, 5.6],
  [-26, 2.8, 0.4, 5],
  [-14, 0, 2.6, 2.6],
] as const;
const NACELLE_X = 12.5;
const NACELLE_BACK = 2;

/** The frosted armour plates on the right wing (+X), and its underwing crystal pod. */
const WING_PLATES: readonly OutlinePoint[][] = [
  [
    [10, 8],
    [22, -6],
    [22, -16],
    [10, -10],
  ],
  [
    [26, -10],
    [38, -22],
    [38, -28],
    [26, -22],
  ],
];
const POD = [
  [0, -7],
  [1.6, -3],
  [1.8, 3],
  [0, 8],
] as const;

/** The crystal canopy and the nose's sensor crystal. */
function drawCanopy({ hull, neon }: EnemyParts): void {
  hull.loft(
    CANOPY_SECTION,
    CANOPY,
    FROST.ice,
    {},
    { paint: (side) => (side === 1 || side === 2 ? FROST.pale : undefined) },
  );
  neon.box([0.4, 0.4, 20], VIOLET, { at: [0, 11.3, 22], pitch: -0.03 });
  crystal(hull, [0, 2.6, 56], [QUARTER, 0, 0], [1.1, 6]);
}

/** The engine nacelles on the wing roots: snowed backs, pale blue strips along their sides. */
function drawNacelles(p: EnemyParts): void {
  const { flesh, neon } = p;
  for (const s of SIDES) {
    const at: Vec3 = [s * NACELLE_X, 0, 0];
    // P16-R05: swollen engine sacs of flesh on the wing roots.
    flesh.loft(
      POD_SECTION,
      NACELLE,
      ICE_FLESH.teal,
      { at },
      {
        paint: (side) => (side === NACELLE_BACK ? ICE_FLESH.rime : undefined),
      },
    );
    neon.box([0.4, 0.6, 20], PALE_BLUE, { at: [s * (NACELLE_X + 3.3), 2.4, -36] });
    glowVein(p, [s * NACELLE_X, 5.6, -46], [s * NACELLE_X, 5.4, -22], 0.7, VIOLET);
  }
}

/**
 * The crystal fins leaning back at the tail, and low crystals along the spine (under the crown
 * ring and its spokes as they turn).
 */
function drawCrystals({ flesh: hull }: EnemyParts): void {
  for (const s of SIDES) {
    crystal(hull, [s * 4.5, 7, -44], [-0.8, -0.35 * s, 0], [2.2, 13]);
    crystal(hull, [s * 3, 8.4, -26], [-0.5, -0.6 * s, 0], [1.3, 3.5]);
    crystal(hull, [s * 6.5, 8.6, -6], [-0.3, -0.9 * s, 0], [1.2, 3.2]);
  }
  crystal(hull, [0, 6.2, -50], [-0.6, 0, 0], [1.6, 8]);
}

/** Frosted plates, seams and a vent on the wings, lights at their tips, crystal pods under them. */
function drawWingDetail(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  for (const s of SIDES) {
    for (const outline of WING_PLATES) {
      plate(hull, s > 0 ? outline : flipX(outline), [2.4, 0.5], FROST.frosted);
    }
    gland(p, [s * 18, 2.6, -22], 1, PALE_BLUE);
    lamps(neon, [[s * 47, 2.6, -32]], 1.4, VIOLET);
    lamps(neon, [[s * 14.5, 3.6, 24]], 1, PALE_BLUE);
    flesh.lathe(POD, 6, ICE_FLESH.membrane, { at: [s * 30, -0.6, -14], pitch: QUARTER });
    hull.box([1.2, 1.4, 6], H.dark, { at: [s * 30, -0.2, -14] });
    icicles(flesh, s, [
      [6, 24],
      [10, 23],
    ]);
  }
}

/** The Ice Queen's details (P08-R10), on its core body. */
export function drawDetails(p: EnemyParts): void {
  drawCanopy(p);
  drawNacelles(p);
  drawCrystals(p);
  drawWingDetail(p);
}
