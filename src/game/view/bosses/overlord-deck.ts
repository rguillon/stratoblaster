import type { OutlinePoint } from '../../../render/geometry/outline';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { around, decal, radial, SIDES } from '../enemies/enemy-shapes';
import { box2d, edgeLights, OVERLORD_DECK, OVERLORD_NEON } from './overlord-city';
import { WING_TOP } from './overlord-parts';

// P07-R05 (phase 7 review: more detail): the Overlord's streets and street lights, lit strips on
// the boulevard, grilles on its engine block, panels and hazard paint on its wings, and a landing
// pad off its right wing. Model space: logical pixels, nose +Z, Y up; +X is the screen's left.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const N = OVERLORD_NEON;
/** Faded hazard paint. */
const HAZARD = [0.4, 0.3, 0.07] as const;

/** Streets on the deck between the towers (x, z, width, length): dark lanes with lights. */
const STREETS: readonly (readonly [number, number, number, number])[] = [
  [40, 0, 3, 40],
  [-40, 22, 18, 2.6],
  [42, -18, 24, 3],
  [-44, -20, 22, 3],
  [44, 18, 16, 2.6],
];

/** The streets, lights along them, and lit strips down the boulevard. */
function drawStreets({ hull, neon }: EnemyParts): void {
  const deck = OVERLORD_DECK.top;
  for (const [x, z, w, d] of STREETS) {
    decal(hull, box2d(w, d, [x, z]), deck + 0.03, H.dark);
    const long = d > w;
    const count = Math.floor(Math.max(w, d) / 7);
    for (let k = 0; k < count; k++) {
      const t = (k + 0.5) / count - 0.5;
      const at: OutlinePoint = long ? [x + w / 2 + 0.6, z + t * d] : [x + t * w, z - d / 2 - 0.6];
      decal(neon, box2d(0.8, 0.8, at), deck + 0.06, k % 3 === 2 ? WHITE : N);
    }
  }
  const y = OVERLORD_DECK.boulevard + 0.04;
  for (const [x, z, d] of [
    [8, 42, 12],
    [13, -40, 22],
    [-13, -40, 22],
    [-20, -36, 18],
    [-8, 44, 8],
  ] as const) {
    decal(neon, box2d(1.2, d, [x, z]), y, N);
  }
}

/** Grilles across the engine block's top, between the reactors. */
function drawEngineGrilles({ hull }: EnemyParts): void {
  for (const x of [-20, 0, 20]) {
    decal(hull, box2d(8, 6, [x, -62]), 5.03, H.dark);
    for (const dz of [-2, 0, 2]) decal(hull, box2d(7, 0.7, [x, -62 + dz]), 5.06, H.panel);
  }
}

/** Panel lines and rivets on both wings; hazard paint on the left one's tip. */
function drawWingPanels({ hull }: EnemyParts): void {
  const y = WING_TOP + 0.03;
  for (const s of SIDES) {
    decal(hull, box2d(0.6, 28, [s * 90, -5]), y, H.dark);
    decal(hull, box2d(24, 0.6, [s * 80, -24]), y, H.dark);
    for (let k = 0; k < 7; k++)
      decal(hull, box2d(0.8, 0.8, [s * (64 + k * 4), 19 - k * 1.5]), y, H.dark);
  }
  for (let k = 0; k < 4; k++) {
    const z = -12 + k * 4;
    const stripe: OutlinePoint[] = [
      [94, z],
      [99, z + 2.5],
      [99, z + 4.3],
      [94, z + 1.8],
    ];
    decal(hull, stripe, y + 0.02, HAZARD);
  }
}

/** The landing pad off the right wing's trailing edge: a hexagon on struts, lit, marked. */
const PAD = { x: -80, z: -30, r: 9.5 } as const;

/** A landing pad on the right wing (-X): lit edges, an H, lights at its corners. */
function drawLandingPad({ hull, neon, charge }: EnemyParts): void {
  const { x, z, r } = PAD;
  const hex = around(6).map((a): OutlinePoint => {
    const [px, , pz] = radial(a + Math.PI / 6, r, 0);
    return [x + px, z + pz];
  });
  for (const dx of [-4, 4]) hull.box([1.6, 3, 1.6], H.dark, { at: [x + dx, -1, z + 4] });
  hull.bevelSlab(hex, [0, 2, 3.4], [1.5, 0.8], H.base, {}, H.panel);
  edgeLights(neon, hex, [0, 1, 2, 3, 4, 5], [1.6, 2.4], N);
  const top = 3.45;
  decal(hull, box2d(10, 10, [x, z]), top, H.dark);
  for (const dx of [-2.2, 2.2]) decal(neon, box2d(1, 6, [x + dx, z]), top + 0.03, WHITE);
  decal(neon, box2d(3.4, 1, [x, z]), top + 0.03, WHITE);
  for (const [px, pz] of hex) {
    charge.box([0.8, 0.8, 0.8], WHITE, { at: [x + (px - x) * 0.82, top, z + (pz - z) * 0.82] });
  }
}

/** P07-R05 (phase 7 review): the details of the Overlord's deck, engines and wings. */
export function drawDeck(parts: EnemyParts): void {
  drawStreets(parts);
  drawEngineGrilles(parts);
  drawWingPanels(parts);
  drawLandingPad(parts);
}
