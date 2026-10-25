import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { windowBands } from './city-props';

// P08-R07: polar city towers and blocks assembled from lots (a stepped glass tower with snow on
// its ledges, a round tower with neon bands, a cluster of heated domes on a podium, an insulated
// panel slab), each crowned with heated domes or masts, so the polar city does not look like the
// World 1 city. Everything stays within X, Z ∈ [-half, half], on Y = 0; the front faces -Z.

type Rgb = readonly [number, number, number];

/** A lot: its centre and its size along X and Z. */
type Lot = readonly [x: number, z: number, w: number, d: number];

/** The structure and lights a lot is drawn into, with its facade, window and neon colours. */
interface PolarKit {
  readonly s: SolidBuilder;
  readonly l: SolidBuilder;
  readonly facade: Rgb;
  readonly windows: Rgb;
  readonly neon: Rgb;
  readonly random: Random;
}

const FACADES: readonly Rgb[] = [C.panel, C.panelDark, C.glassBlue, C.glassDark, C.silver];
const WINDOWS: readonly Rgb[] = [L.windowDim, L.whiteDim, L.yellowDim, L.cyanDim];
const NEONS: readonly Rgb[] = [L.cyanDim, L.pinkDim, L.cyan];
/** Space left between the lots of a building. */
const LOT_GAP = 1.5;
/** Polar towers below this half side stand on one lot or two. */
const TOWER_HALF = 12;

/** A box with rows of lit windows and snow on its roof, from `y` up to `y + h`. */
function block(kit: PolarKit, [x, z, w, d]: Lot, y: number, h: number, facade = kit.facade): void {
  kit.s.box([w, h, d], facade, { at: [x, y, z] }, C.snow);
  if (h >= 8) windowBands(kit.l, [w, d], [y + 3, y + h - 2], 9, 1.6, kit.windows, [x, z]);
}

/** A neon band right round a `w × d` block at height `y`, just off its walls (8 triangles). */
function neonBand(kit: PolarKit, [x, z, w, d]: Lot, y: number): void {
  const [x0, x1, z0, z1] = [x - w / 2 - 0.15, x + w / 2 + 0.15, z - d / 2 - 0.15, z + d / 2 + 0.15];
  // The bottom edge of each face, counter-clockwise seen from outside.
  const edges = [
    [x0, z0, x1, z0],
    [x1, z1, x0, z1],
    [x0, z1, x0, z0],
    [x1, z0, x1, z1],
  ] as const;
  for (const [ax, az, bx, bz] of edges) {
    kit.l.face(
      [
        [ax, y, az],
        [ax, y + 0.5, az],
        [bx, y + 0.5, bz],
        [bx, y, bz],
      ],
      kit.neon,
    );
  }
}

/** A heated dome of radius `r` on a roof at (x, y, z): snow banked low, bare glass on top. */
function heatedDome(kit: PolarKit, [x, y, z]: readonly [number, number, number], r: number): void {
  const at = [x, 0, z] as const;
  kit.s.lathe(
    [
      [r, y],
      [r * 0.92, y + r * 0.35],
    ],
    8,
    C.snow,
    { at },
    false,
  );
  kit.s.lathe(
    [
      [r * 0.92, y + r * 0.35],
      [r * 0.6, y + r * 0.75],
      [0, y + r * 0.9],
    ],
    8,
    C.glassBlue,
    { at },
    false,
  );
  kit.l.ring(r * 0.94, 0.4, 8, kit.windows, { at: [x, y + r * 0.3, z] });
}

/** Something on top of a tower: a heated dome, or a mast with a red light. */
function crown(kit: PolarKit, top: readonly [number, number, number], size: number): void {
  const [x, y, z] = top;
  if (kit.random() < 0.6) {
    heatedDome(kit, top, size * 0.4);
    return;
  }
  const h = randomIn(kit.random, [6, 12]);
  kit.s.cylinder(0.35, h, 4, C.metal, { at: top });
  kit.l.box([0.8, 0.8, 0.8], L.red, { at: [x, y + h, z] });
}

/** A glass tower stepping back in 2 or 3 tiers, snow on each ledge, on an insulated plinth. */
function steppedTower(kit: PolarKit, lot: Lot): void {
  const { random } = kit;
  const [x, z, w, d] = lot;
  let y = randomIn(random, [3, 5]);
  block(kit, lot, 0, y, C.panelDark);
  let [tw, td] = [w * randomIn(random, [0.7, 0.9]), d * randomIn(random, [0.7, 0.9])];
  const tiers = 2 + Math.floor(random() * 2);
  for (let t = 0; t < tiers; t++) {
    const h = randomIn(random, [10, 22]);
    block(kit, [x, z, tw, td], y, h);
    if (t === 0) neonBand(kit, [x, z, tw, td], y + h - 1);
    y += h;
    if (t < tiers - 1) [tw, td] = [tw * 0.75, td * 0.75];
  }
  crown(kit, [x, y, z], Math.min(tw, td));
}

/** A round tower in octagonal facets with neon bands, a heated dome or mast on top. */
function roundTower(kit: PolarKit, lot: Lot): void {
  const { s, l, random } = kit;
  const [x, z, w, d] = lot;
  const r = (Math.min(w, d) / 2) * randomIn(random, [0.65, 0.9]);
  const base = randomIn(random, [2, 4]);
  s.box([w, base, d], C.panelDark, { at: [x, 0, z] }, C.snow);
  const h = randomIn(random, [22, 44]);
  s.cylinder(r, h, 8, kit.facade, { at: [x, base, z] }, r * 0.9);
  s.cylinder(r * 0.92, 0.6, 8, C.snow, { at: [x, base + h, z] });
  for (let i = 0, y = base + 5; y < base + h - 3; i++, y += 9) {
    const ring = r * (1.02 - ((y - base) / h) * 0.1);
    l.ring(ring, 1.2, 8, i % 2 === 0 ? kit.neon : kit.windows, { at: [x, y, z] });
  }
  crown(kit, [x, base + h + 0.6, z], r * 2);
}

/** A podium with one to three heated domes of different sizes on it. */
function domeCluster(kit: PolarKit, lot: Lot): void {
  const { random } = kit;
  const [x, z, w, d] = lot;
  const h = randomIn(random, [3, 7]);
  block(kit, lot, 0, h, pick(random, [C.panel, C.panelDark, C.silver]));
  neonBand(kit, lot, h - 1.2);
  const r = Math.min(w, d) / 2 - 0.5;
  if (Math.max(w, d) < 1.6 * Math.min(w, d)) {
    heatedDome(kit, [x, h, z], r);
    return;
  }
  const along = w > d;
  for (const k of [-1, 1]) {
    const off = (k * Math.max(w, d)) / 4;
    const size = Math.min(r, Math.max(w, d) / 4 - 0.3) * (k < 0 ? 1 : 0.8);
    heatedDome(kit, [along ? x + off : x, h, along ? z : z + off], size);
  }
}

/** A slab of insulated panels with rows of windows, snow on its roof and roof units. */
function panelSlab(kit: PolarKit, lot: Lot): void {
  const { s, random } = kit;
  const [x, z, w, d] = lot;
  const h = randomIn(random, [8, 18]);
  block(kit, lot, 0, h, pick(random, [C.panel, C.panelDark, C.white]));
  neonBand(kit, lot, 2.4);
  s.box([w * 0.3, 1.6, d * 0.3], C.metalDark, { at: [x - w * 0.2, h, z + d * 0.1] }, C.snow);
  heatedDome(kit, [x + w * 0.22, h, z - d * 0.15], Math.min(w, d) * 0.22);
}

const KINDS = [steppedTower, roundTower, domeCluster, panelSlab] as const;
const TOWERS = [steppedTower, roundTower] as const;

/** Cuts `[-half, half]` in one or two spans at a random point. */
function spans(half: number, split: boolean, random: Random): (readonly [number, number])[] {
  if (!split) return [[-half, half]];
  const cut = randomIn(random, [-0.3, 0.3]) * half;
  return [
    [-half, cut],
    [cut, half],
  ];
}

/** The lots of a building: one or two for towers, two to four for the larger blocks. */
function lots(half: number, random: Random): Lot[] {
  const large = half > TOWER_HALF;
  const xs = spans(half, large || random() < 0.4, random);
  const zs = spans(half, large && random() < 0.6, random);
  return xs.flatMap(([x0, x1]) =>
    zs.map(([z0, z1]): Lot => [(x0 + x1) / 2, (z0 + z1) / 2, x1 - x0 - LOT_GAP, z1 - z0 - LOT_GAP]),
  );
}

/**
 * One of the polar city buildings, decided by `seed`, fitting in a square of half side `half`:
 * stepped glass towers, round towers, dome clusters and panel slabs, with snow on every roof and
 * ledge, heated domes and neon bands.
 */
export function buildPolarBuilding(seed: number, half = TOWER_HALF): PropGeometry {
  const random = createRng(seed * 15485863 + half * 97 + 3);
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  const windows = pick(random, WINDOWS);
  const neon = pick(random, NEONS);
  lots(half, random).forEach((lot, i) => {
    const facade = pick(random, FACADES);
    // A polar tower always has a tower on its first lot.
    const kinds = half <= TOWER_HALF && i === 0 ? TOWERS : KINDS;
    pick(random, kinds)({ s, l, facade, windows, neon, random }, lot);
  });
  return { structure: s.geometry, lights: l.geometry };
}
