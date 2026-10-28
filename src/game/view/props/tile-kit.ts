import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { windowBands } from './city-props';

// Phase 15 (P15-R07, R09): what the models made for the grid of tiles share. Each one fills a
// plot `w` × `d` world units (its tiles less the margin), centred on the origin, standing on
// Y = 0, its front towards -Z.

export type Rgb = readonly [number, number, number];

/** What a model of the grid is built with. */
export interface TileKit {
  readonly s: SolidBuilder;
  readonly l: SolidBuilder;
  readonly random: Random;
  /** The plot: width (X) and depth (Z). */
  readonly w: number;
  readonly d: number;
  /** Size of a tile, for spacing things out by the tile. */
  readonly tile: number;
  /** The model's seed: some builders pick their shape by it, so a group's models differ. */
  readonly seed: number;
}

export function tileKit(w: number, d: number, tile: number, seed: number): TileKit {
  return {
    s: new SolidBuilder({ openBottoms: true }),
    l: new SolidBuilder({ openBottoms: true }),
    random: createRng(seed * 7919 + Math.round(w * 31 + d * 17)),
    w,
    d,
    tile,
    seed,
  };
}

export function geometryOf(k: TileKit): PropGeometry {
  return { structure: k.s.geometry, lights: k.l.geometry };
}

export const r = (k: TileKit, range: readonly [number, number]): number =>
  randomIn(k.random, range);
export const any = <T>(k: TileKit, items: readonly T[]): T => pick(k.random, items);

/** The ground of the plot, a little above the street: lawn, paving, sand, asphalt. */
export function plot(k: TileKit, color: Rgb, height = 0.2): void {
  k.s.box([k.w, height, k.d], color);
}

/**
 * A gabled roof over a `w` × `d` box at height `y`, its ridge `h` higher along X (along Z with
 * `alongZ`), centred on `at`.
 */
export function gable(
  k: TileKit,
  [w, d]: readonly [number, number],
  y: number,
  h: number,
  color: Rgb,
  at: readonly [number, number] = [0, 0],
  alongZ = false,
): void {
  const [a, b] = alongZ ? [d, w] : [w, d];
  const place = { at: [at[0], 0, at[1]] as const, yaw: alongZ ? Math.PI / 2 : 0 };
  k.s.face(
    [
      [-a / 2, y, -b / 2],
      [-a / 2, y + h, 0],
      [a / 2, y + h, 0],
      [a / 2, y, -b / 2],
    ],
    color,
    place,
  );
  k.s.face(
    [
      [a / 2, y, b / 2],
      [a / 2, y + h, 0],
      [-a / 2, y + h, 0],
      [-a / 2, y, b / 2],
    ],
    color,
    place,
  );
  k.s.face(
    [
      [-a / 2, y, b / 2],
      [-a / 2, y + h, 0],
      [-a / 2, y, -b / 2],
    ],
    C.concreteDark,
    place,
  );
  k.s.face(
    [
      [a / 2, y, -b / 2],
      [a / 2, y + h, 0],
      [a / 2, y, b / 2],
    ],
    C.concreteDark,
    place,
  );
}

/** Lit window rows round a `w` × `d` block at (x, z), from `y0` to `y1`. */
export function windows(
  k: TileKit,
  [w, d]: readonly [number, number],
  [y0, y1]: readonly [number, number],
  color: Rgb,
  [x, z]: readonly [number, number] = [0, 0],
  gap = 3,
): void {
  windowBands(k.l, [w, d], [y0, y1], gap, Math.min(1.2, gap / 2.5), color, [x, z]);
}

/** A round tree: a trunk and a low-poly crown. */
export function tree(k: TileKit, x: number, z: number, size: number): void {
  k.s.cylinder(size * 0.12, size * 0.6, 5, C.bark, { at: [x, 0, z] });
  k.s.lathe(
    [
      [size * 0.45, size * 0.5],
      [size * 0.55, size * 0.9],
      [0, size * 1.4],
    ],
    6,
    any(k, [C.leaf, C.leafDark, C.leafLight]),
    { at: [x, 0, z] },
  );
}

/** A door light and a neon strip on the front of a block `w` wide whose front is at `z`. */
export function frontLights(k: TileKit, w: number, z: number, y: number, neon: Rgb): void {
  k.l.box([Math.min(2, w / 3), 1.4, 0.3], L.window, { at: [0, 0.2, z - 0.2] });
  k.l.box([w * 0.8, 0.3, 0.3], neon, { at: [0, y, z - 0.2] });
}

/** A lamp post at (x, z): a pole and a light on top, so lots and yards are lit at night. */
export function lamp(k: TileKit, x: number, z: number, h = 4): void {
  k.s.box([0.25, h, 0.25], C.metal, { at: [x, 0, z] });
  k.l.box([0.6, 0.4, 0.6], L.yellowDim, { at: [x, h, z] });
}

export const NEON: readonly Rgb[] = [L.cyan, L.pink, L.violet, L.red];
export const NEON_DIM: readonly Rgb[] = [L.cyanDim, L.pinkDim, L.whiteDim, L.yellowDim];
