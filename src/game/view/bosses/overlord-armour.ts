import type { OutlinePoint } from '../../../render/geometry/outline';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { radial } from '../enemies/enemy-shapes';
import { box2d, OVERLORD_DECK, OVERLORD_NEON } from './overlord-city';

// P07-R05 (phase 7 review: fat armour over complex machinery): thick armour blocks around the
// Overlord's citadel and over its wing roots; between them, darker gears, rams, cables and lit
// conduits show. Model space: logical pixels, nose +Z, Y up; +X is the screen's left.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;
const DEG = Math.PI / 180;
const N = OVERLORD_NEON;

/** A cog lying flat (lathe profile, bottom to top): a low-sided rim, its hub. */
const COG = [
  [3.6, 0],
  [3.6, 1.2],
  [1.8, 1.8],
  [0, 1.8],
] as const;

/** The collar's armour blocks around the citadel (from, to, degrees from the nose towards +X). */
const COLLAR = [
  [40, 86],
  [100, 160],
  [200, 264],
  [278, 320],
] as const;
/** The collar's radii and heights. */
const RING = { inner: 21.5, outer: 28.5, y0: 12, waist: 16.5, top: 19.5 } as const;

/** An annular sector around the citadel, from `a0` to `a1` (radians), as an outline. */
function sector(a0: number, a1: number, r0: number, r1: number): OutlinePoint[] {
  const steps = Math.max(1, Math.round((a1 - a0) / (24 * DEG)));
  const arc = (r: number): OutlinePoint[] =>
    Array.from({ length: steps + 1 }, (_, i) => {
      const [x, , z] = radial(a0 + ((a1 - a0) * i) / steps, r, 0);
      return [x, z];
    });
  return [...arc(r1), ...arc(r0).reverse()];
}

/** The works in the collar's gap at angle `a`: a cog, a ram out to the deck, a cable. */
function collarWorks({ hull, neon, charge }: EnemyParts, a: number): void {
  const deck = OVERLORD_DECK.top;
  const [cx, , cz] = radial(a, 27, 0);
  hull.lathe(COG, 8, H.panel, { at: [cx, OVERLORD_DECK.boulevard + 0.2, cz] });
  charge.cylinder(1, 0.4, 6, WHITE, { at: [cx, OVERLORD_DECK.boulevard + 2, cz] });
  // A conduit glowing along the citadel's wall.
  const [wx, , wz] = radial(a, 24.2, 0);
  neon.box([5, 1.2, 0.6], N, { at: [wx, deck + 3.6, wz], yaw: a });
  // A ram from the citadel out to the deck: a fat barrel, a bright rod.
  const ram = (r: number): [number, number, number] => {
    const [x, , z] = radial(a, r, 0);
    return [x, deck + 4, z];
  };
  hull.cylinder(1.3, 6, 6, H.base, { at: ram(22), pitch: QUARTER, yaw: a });
  hull.cylinder(0.65, 6, 6, H.panel, { at: ram(28), pitch: QUARTER, yaw: a });
  const side = a + 0.12;
  const [kx, , kz] = radial(side, 23, 0);
  hull.cylinder(0.7, 11, 5, H.panel, { at: [kx, deck + 2.5, kz], pitch: QUARTER, yaw: side });
}

/** The armoured collar around the citadel's foot, the machinery showing in its gaps. */
function drawCollar(parts: EnemyParts): void {
  const { inner, outer, y0, waist, top } = RING;
  COLLAR.forEach(([from, to], i) => {
    const block = sector(from * DEG, to * DEG, inner, outer);
    const shade = i % 2 === 0 ? H.panel : H.base;
    parts.hull.bevelSlab(block, [y0, waist, top], [1, 1.6], shade, {}, H.base);
    const mid = ((from + to) / 2) * DEG;
    const [lx, , lz] = radial(mid, outer - 2.5, 0);
    parts.neon.box([1.2, 0.4, 1.2], N, { at: [lx, top, lz] });
    const next = COLLAR[(i + 1) % COLLAR.length];
    if (next && next[0] > to) {
      // The machinery's dark bed in the gap, then the machinery on it.
      const bed = sector((to - 2) * DEG, (next[0] + 2) * DEG, inner, outer - 0.5);
      parts.hull.slab(bed, [OVERLORD_DECK.top, OVERLORD_DECK.boulevard + 0.2], H.dark);
      collarWorks(parts, ((to + next[0]) / 2) * DEG);
    }
  });
}

/** The wing roots' armour plates (z ranges, by side), over the joint between deck and wing. */
const ROOT_PLATES: readonly (readonly [1 | -1, number, number])[] = [
  [1, -31, -19],
  [1, -11, 2],
  [1, 9, 19],
  // The right one has lost a plate: a wide gap with more machinery.
  [-1, -31, -19],
  [-1, 7, 19],
];
const ROOT = { x0: 55, x1: 70, y0: 0, waist: 6, top: 9 } as const;

/** The works in a wing root's gap at `z`: rams across the joint, a cog, a lit conduit. */
function rootWorks({ hull, neon, charge }: EnemyParts, s: 1 | -1, z: number, wide: boolean): void {
  // Rolled a quarter turn, a cylinder runs along +X (rolled the other way, along -X).
  const along = { roll: -s * QUARTER };
  for (const dz of wide ? [-5, 0, 5] : [-1.5, 1.5]) {
    hull.cylinder(1.2, 7, 6, H.base, { ...along, at: [s * 54, 4, z + dz] });
    hull.cylinder(0.6, 8, 6, H.panel, { ...along, at: [s * 61, 4, z + dz] });
  }
  hull.lathe(COG, 8, H.panel, { at: [s * 64, 2.4, z] });
  charge.cylinder(1, 0.4, 6, WHITE, { at: [s * 64, 4.2, z] });
  neon.box([12, 0.6, 1], N, { at: [s * 62, 2.4, z + (wide ? 8 : 2.6)] });
}

/** The armour over the wing roots, plates proud of deck and wing, machinery in the gaps. */
function drawWingRoots(parts: EnemyParts): void {
  const { x0, x1, y0, waist, top } = ROOT;
  ROOT_PLATES.forEach(([s, z0, z1], i) => {
    const plate = box2d(x1 - x0, z1 - z0, [(s * (x0 + x1)) / 2, (z0 + z1) / 2]);
    parts.hull.bevelSlab(plate, [y0, waist, top], [0, 2], H.panel, {}, H.base);
    parts.neon.box([0.8, 0.5, z1 - z0 - 4], N, { at: [s * (x1 - 2.4), top - 0.6, (z0 + z1) / 2] });
    const next = ROOT_PLATES[i + 1];
    if (next?.[0] === s) {
      const gap = next[1] - z1;
      const bed = box2d(x1 - x0, gap + 2, [(s * (x0 + x1)) / 2, (z1 + next[1]) / 2]);
      parts.hull.slab(bed, [y0, 2.4], H.dark);
      rootWorks(parts, s, (z1 + next[1]) / 2, gap > 10);
    }
  });
}

/** P07-R05 (phase 7 review): the Overlord's armour, and the machinery under it. */
export function drawOverlordArmour(parts: EnemyParts): void {
  drawCollar(parts);
  drawWingRoots(parts);
}
