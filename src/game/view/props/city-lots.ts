import { pick, randomIn, type Random } from '../../../core/math/rng';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { windowBands } from './city-props';

// Phase 4 review: the lots a city building is made of, each one a different kind of volume (a
// stepped tower, a round tower, a low slab, a courtyard block or an L-shaped block; more in
// `city-landmarks.ts`), so the city centre reads as varied as the industrial zone.

type Rgb = readonly [number, number, number];

/** A lot: its centre and its size along X and Z. */
export type Lot = readonly [x: number, z: number, w: number, d: number];

/** The structure and lights a lot is drawn into, with its facade and window colours. */
export interface LotKit {
  readonly s: SolidBuilder;
  readonly l: SolidBuilder;
  readonly facade: Rgb;
  readonly windows: Rgb;
  /** Colour of the flat roofs. */
  readonly roof: Rgb;
  readonly random: Random;
}

/** A box with rows of lit windows, from `y` up to `y + h`. */
export function volume(
  kit: LotKit,
  [x, z, w, d]: Lot,
  y: number,
  h: number,
  facade = kit.facade,
): void {
  kit.s.box([w, h, d], facade, { at: [x, y, z] }, kit.roof);
  // Few rows, and none on low volumes, to keep the triangle count down (review).
  if (h >= 8) windowBands(kit.l, [w, d], [y + 3, y + h - 2], 10, 2, kit.windows, [x, z]);
}

/** Something on top of a tower at (x, y, z): a spire, a mast, a pyramid or roof units. */
export function crown(
  kit: LotKit,
  [x, y, z]: readonly [number, number, number],
  size: number,
): void {
  const { s, l, random } = kit;
  const style = Math.floor(random() * 4);
  if (style === 0) {
    s.lathe(
      [
        [size * 0.25, y],
        [0, y + randomIn(random, [8, 16])],
      ],
      4,
      C.metal,
      { at: [x, 0, z] },
    );
  } else if (style === 1) {
    const h = randomIn(random, [8, 14]);
    s.cylinder(0.4, h, 4, C.metal, { at: [x, y, z] });
    l.box([1, 1, 1], L.red, { at: [x, y + h, z] });
  } else if (style === 2) {
    s.lathe(
      [
        [size * 0.6, y],
        [0, y + size * 0.4],
      ],
      4,
      C.roof,
      { at: [x, 0, z], yaw: Math.PI / 4 },
    );
  } else {
    s.box([size * 0.4, 2, size * 0.3], C.metalDark, { at: [x - size * 0.2, y, z] });
    s.box([size * 0.2, 1.4, size * 0.2], C.metal, { at: [x + size * 0.25, y, z + size * 0.2] });
  }
}

/** A low base covering the whole lot, so no bare ground shows around a tower; its height. */
export function plinth(kit: LotKit, [x, z, w, d]: Lot): number {
  // At least 3 high, so the uneven ground of a block never shows through it (review).
  const h = randomIn(kit.random, [3, 6]);
  kit.s.box(
    [w, h, d],
    pick(kit.random, [C.concreteDark, C.brick, C.concrete]),
    { at: [x, 0, z] },
    kit.roof,
  );
  return h;
}

/** A tower in 1 to 3 tiers stepping back, on a base covering its lot. */
function steppedTower(kit: LotKit, lot: Lot): void {
  const { random } = kit;
  const [x, z, w, d] = lot;
  const tiers = 1 + Math.floor(random() * 3);
  let [tw, td] = [w * randomIn(random, [0.55, 0.9]), d * randomIn(random, [0.55, 0.9])];
  let y = plinth(kit, lot);
  for (let t = 0; t < tiers; t++) {
    const h = randomIn(random, [12, 30]);
    volume(kit, [x, z, tw, td], y, h);
    y += h;
    const shrink = randomIn(random, [0.6, 0.8]);
    if (t < tiers - 1) [tw, td] = [tw * shrink, td * shrink];
  }
  crown(kit, [x, y, z], Math.min(tw, td));
}

/** A round tower in octagonal facets, with lit rings around it. */
function roundTower(kit: LotKit, lot: Lot): void {
  const { s, l, random } = kit;
  const [x, z, w, d] = lot;
  const r = (Math.min(w, d) / 2) * randomIn(random, [0.6, 0.85]);
  const base = plinth(kit, lot);
  const h = base + randomIn(random, [25, 60]);
  s.cylinder(r, h - base, 6, kit.facade, { at: [x, base, z] }, r * randomIn(random, [0.7, 1]));
  for (let y = base + 4; y + 2 < h - 4; y += 12) {
    l.ring(r * 1.02, 2, 6, kit.windows, { at: [x, y, z] });
  }
  crown(kit, [x, h, z], r);
}

/** A low slab filling its lot, with roof units and now and then a neon sign. */
function slab(kit: LotKit, lot: Lot): void {
  const { s, l, random } = kit;
  const [x, z, w, d] = lot;
  const h = randomIn(random, [6, 14]);
  volume(kit, lot, 0, h, pick(random, [C.concrete, C.concreteDark, C.brick]));
  s.box([w * 0.3, 1.5, d * 0.25], C.metalDark, { at: [x - w * 0.15, h, z + d * 0.1] });
  if (random() < 0.5) l.box([w * 0.5, 1.4, 0.3], L.pinkDim, { at: [x, 3, z - d / 2 - 0.3] });
}

/** A block of four wings around a courtyard. */
function courtyard(kit: LotKit, [x, z, w, d]: Lot): void {
  const t = Math.min(w, d) * randomIn(kit.random, [0.25, 0.35]);
  const h = randomIn(kit.random, [10, 24]);
  volume(kit, [x, z - d / 2 + t / 2, w, t], 0, h);
  volume(kit, [x, z + d / 2 - t / 2, w, t], 0, h);
  volume(kit, [x - w / 2 + t / 2, z, t, d - 2 * t], 0, h);
  volume(kit, [x + w / 2 - t / 2, z, t, d - 2 * t], 0, h);
}

/** An L-shaped block along two sides of its lot, with a taller wing at the corner. */
function lBlock(kit: LotKit, [x, z, w, d]: Lot): void {
  const { random } = kit;
  const t = Math.min(w, d) * randomIn(random, [0.35, 0.5]);
  const h = randomIn(random, [10, 20]);
  volume(kit, [x, z + d / 2 - t / 2, w, t], 0, h);
  volume(kit, [x - w / 2 + t / 2, z - t / 2, t, d - t], 0, h);
  volume(kit, [x - w / 2 + t / 2, z + d / 2 - t / 2, t, t], h, randomIn(random, [10, 30]));
}

/** The plain kinds of lots; courtyards and L-shaped blocks need room for their wings. */
export const LOTS = [steppedTower, roundTower, slab, courtyard, lBlock] as const;
export const WIDE_LOTS: readonly ((kit: LotKit, lot: Lot) => void)[] = [courtyard, lBlock];
