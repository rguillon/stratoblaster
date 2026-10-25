import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';

// P08-R10, 2-5: the Boreal Citadel's polar city: its colours, the towers and heated domes on its
// deck, the icicles under its edges. Model space: logical pixels, nose +Z (down the screen), Y up
// towards the camera; +X is the screen's left.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

const H = ENEMY_LOOK.hull;

/** Aurora green: the boss's registered neon (GD-61), and violet, its second neon colour. */
export const AURORA = BOSS_LOOK.neon['boreal-citadel'] ?? ([1, 1, 1] as Rgb);
export const VIOLET: Rgb = [0.62, 0.28, 1];

/** World 2 frost (P08-R10): snow on top faces, pale ice, and frosted (snow-dusted) panels. */
export const FROST = {
  snow: [0.75, 0.82, 0.9] as Rgb,
  ice: [0.56, 0.7, 0.92] as Rgb,
  frosted: [0.36, 0.4, 0.47] as Rgb,
};

/** Heights of the deck's top and of the raised avenue down its middle. */
export const CITADEL_DECK = { top: 6, avenue: 12 } as const;

/** A rectangle `w` wide and `d` long around (x, z). */
export function rect(w: number, d: number, [x, z]: OutlinePoint = [0, 0]): OutlinePoint[] {
  return [
    [x - w / 2, z - d / 2],
    [x + w / 2, z - d / 2],
    [x + w / 2, z + d / 2],
    [x - w / 2, z + d / 2],
  ];
}

/** A tower of the city: where, its footprint and height, a setback tier on top, its windows' colour. */
interface Tower {
  readonly x: number;
  readonly z: number;
  readonly w: number;
  readonly d: number;
  readonly h: number;
  readonly tier?: readonly [number, number, number];
  readonly lit: Rgb;
}

/** The towers of the right half of the deck (+X), mirrored on the left (some swapped in colour). */
const TOWERS: readonly Tower[] = [
  { x: 12, z: 66, w: 9, d: 8, h: 11, lit: VIOLET },
  { x: 26, z: 60, w: 7, d: 7, h: 16, tier: [4.5, 4.5, 5], lit: AURORA },
  { x: 50, z: 12, w: 8, d: 10, h: 13, tier: [5, 6, 4], lit: AURORA },
  { x: 52, z: -6, w: 7, d: 8, h: 9, lit: VIOLET },
  { x: 24, z: -24, w: 8, d: 9, h: 19, tier: [5, 6, 6], lit: VIOLET },
  { x: 26, z: -62, w: 10, d: 8, h: 12, lit: AURORA },
  { x: 42, z: -60, w: 7, d: 7, h: 8, lit: VIOLET },
  { x: 40, z: 20, w: 6, d: 6, h: 10, lit: VIOLET },
  { x: 36, z: 2, w: 6, d: 7, h: 15, tier: [4, 4, 4], lit: AURORA },
  { x: 36, z: -12, w: 6, d: 6, h: 7, lit: VIOLET },
  { x: 10, z: -72, w: 6, d: 6, h: 9, lit: AURORA },
];

/** Lit window bands on a block's front (+Z) face, `w` wide, from `y0` up `h`, at `front`. */
function windows(
  neon: SolidBuilder,
  [x, y0, front]: Vec3,
  [w, h]: readonly [number, number],
  lit: Rgb,
): void {
  const rows = Math.floor((h - 1.5) / 3);
  for (let r = 0; r < rows; r++) {
    const y = y0 + 1.6 + r * 3;
    const [a, b] = [x - w / 2 + 1, x + w / 2 - 1];
    neon.face(
      [
        [a, y, front],
        [b, y, front],
        [b, y + 1.1, front],
        [a, y + 1.1, front],
      ],
      lit,
    );
  }
}

/** A tower on the deck: a dark block, its snowed roof, lit windows, a setback tier. */
function drawTower({ hull, neon }: EnemyParts, t: Tower, s: number): void {
  const base = CITADEL_DECK.top;
  const x = s * t.x;
  hull.bevelSlab(
    rect(t.w, t.d, [x, t.z]),
    [base, base, base + t.h],
    [0, 0.7],
    H.base,
    {},
    FROST.snow,
  );
  // The left half's towers have the other colour, so the city is not a mirror image.
  const lit = s > 0 ? t.lit : t.lit === AURORA ? VIOLET : AURORA;
  windows(neon, [x, base, t.z + t.d / 2 + 0.1], [t.w, t.h], lit);
  if (!t.tier) return;
  const [w, d, h] = t.tier;
  const top = base + t.h;
  hull.bevelSlab(
    rect(w, d, [x, t.z - 0.5]),
    [top, top, top + h],
    [0, 0.5],
    H.panel,
    {},
    FROST.snow,
  );
  windows(neon, [x, top - 1, t.z - 0.5 + d / 2 + 0.1], [w, h + 1], lit);
}

/** A small heated dome of the city (lathe profile): glass glowing warm through the frost. */
const CITY_DOME = [
  [5, 0],
  [4.4, 2.4],
  [2.6, 4.2],
  [0, 5],
] as const;

/** The city on the deck: its towers, two small heated domes, a few roof masts. */
export function drawCity(p: EnemyParts): void {
  for (const s of SIDES) {
    for (const t of TOWERS) drawTower(p, t, s);
    const at: Vec3 = [s * 15, CITADEL_DECK.top, 77];
    p.hull.cylinder(5.6, 1.2, 8, H.panel, { at });
    p.neon.lathe(CITY_DOME, 8, s > 0 ? AURORA : VIOLET, { at: [at[0], at[1] + 1.2, at[2]] });
    p.hull.ring(5.2, 0.6, 8, FROST.snow, { at: [at[0], at[1] + 1.2, at[2]] });
    p.hull.cylinder(0.4, 9, 4, H.dark, { at: [s * 26, CITADEL_DECK.top + 21, 60] }, 0.2);
    p.neon.box([0.8, 0.8, 0.8], VIOLET, { at: [s * 26, CITADEL_DECK.top + 30, 60] });
  }
}

/**
 * Icicles hanging under the deck's edge between `a` and `b` (seen from above, at height `y`),
 * `count` of them, a little longer and shorter by turns.
 */
export function icicles(
  hull: SolidBuilder,
  [a, b]: readonly [OutlinePoint, OutlinePoint],
  y: number,
  count: number,
): void {
  for (let i = 0; i < count; i++) {
    const t = (i + 0.5) / count;
    const at: Vec3 = [a[0] + (b[0] - a[0]) * t, y, a[1] + (b[1] - a[1]) * t];
    hull.cylinder(0.9, 3 + (i % 3) * 1.6, 4, FROST.ice, { at, pitch: Math.PI }, 0);
  }
}
