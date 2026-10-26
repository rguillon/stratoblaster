import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { windowBands } from './city-props';
import { crown } from './jungle-parts';

// P09-R06: the canopy city's towers and blocks, assembled from lots (a stepped tower with trees
// on its terraces, a round "tree" tower crowned with a canopy, a stack of shifted terraces, a
// glass slab with a neon spine), each with a roof garden of small crowns, so the city reads as
// grown into the jungle. Everything stays within X, Z ∈ [-half, half], on Y = 0; the front -Z.

type Rgb = readonly [number, number, number];

/** A lot: its centre and its size along X and Z. */
type Lot = readonly [x: number, z: number, w: number, d: number];

/** The structure and lights a lot is drawn into, with its facade, window and neon colours. */
interface CanopyKit {
  readonly s: SolidBuilder;
  readonly l: SolidBuilder;
  readonly facade: Rgb;
  readonly windows: Rgb;
  readonly neon: Rgb;
  readonly random: Random;
}

const FACADES: readonly Rgb[] = [
  C.glassGreen,
  C.glassDark,
  C.mossStoneDark,
  C.concreteDark,
  C.jungleMetal,
];
const WINDOWS: readonly Rgb[] = [L.windowDim, L.yellowDim, L.whiteDim, L.cyanDim];
const NEONS: readonly Rgb[] = [L.cyanDim, L.pinkDim, L.toxicDim, L.pink];
const GREENS: readonly Rgb[] = [C.canopy, C.canopyLight, C.canopyDark, C.canopyBlue];
/** Space left between the lots of a building. */
const LOT_GAP = 1.5;
/** Canopy towers below this half side stand on one lot or two. */
const TOWER_HALF = 12;

/** A box with rows of lit windows and moss on its roof, from `y` up to `y + h`. */
function block(kit: CanopyKit, [x, z, w, d]: Lot, y: number, h: number, facade = kit.facade): void {
  kit.s.box([w, h, d], facade, { at: [x, y, z] }, C.moss);
  if (h >= 8) windowBands(kit.l, [w, d], [y + 3, y + h - 2], 9, 1.6, kit.windows, [x, z]);
}

/** A roof garden on a `w × d` roof at height `y`: one to three small crowns in its corners. */
function garden(kit: CanopyKit, [x, z, w, d]: Lot, y: number): void {
  const { random } = kit;
  const r = Math.min(w, d) / 4;
  const count = 1 + Math.floor(random() * 3);
  const spots = [
    [-1, -1],
    [1, 1],
    [1, -1],
  ] as const;
  for (const [i, j] of spots.slice(0, count)) {
    const size = r * randomIn(random, [0.7, 1]);
    const at = [x + (i * w) / 4, y, z + (j * d) / 4] as const;
    crown(kit.s, { at, r: size, h: size * 1.3 }, pick(random, GREENS), 5);
  }
}

/** A vertical neon strip up the front (-Z) of a `w × d` block, from `y0` to `y1`. */
function neonSpine(kit: CanopyKit, [x, z, w, d]: Lot, [y0, y1]: readonly [number, number]): void {
  const off = w * randomIn(kit.random, [-0.3, 0.3]);
  kit.l.box([0.5, y1 - y0, 0.3], kit.neon, { at: [x + off, y0, z - d / 2 - 0.15] });
}

/** A tower stepping back in 2 or 3 tiers, trees on each terrace, a garden on its roof. */
function terracedTower(kit: CanopyKit, lot: Lot): void {
  const { random } = kit;
  const [x, z, w, d] = lot;
  let y = randomIn(random, [3, 6]);
  block(kit, lot, 0, y, C.mossStoneDark);
  let [tw, td] = [w * randomIn(random, [0.75, 0.9]), d * randomIn(random, [0.75, 0.9])];
  const tiers = 2 + Math.floor(random() * 2);
  for (let t = 0; t < tiers; t++) {
    const h = randomIn(random, [10, 20]);
    block(kit, [x, z, tw, td], y, h);
    if (t === 0) neonSpine(kit, [x, z, tw, td], [y + 2, y + h - 1]);
    y += h;
    if (t < tiers - 1) {
      crown(kit.s, { at: [x - tw * 0.3, y, z - td * 0.3], r: tw * 0.16, h: 3 }, C.canopy, 5);
      [tw, td] = [tw * 0.75, td * 0.75];
    }
  }
  garden(kit, [x, z, tw, td], y);
}

/** A round tower like a giant trunk, banded with lit rings, under a big canopy crown. */
function treeTower(kit: CanopyKit, lot: Lot): void {
  const { s, l, random } = kit;
  const [x, z, w, d] = lot;
  const r = (Math.min(w, d) / 2) * randomIn(random, [0.45, 0.6]);
  const h = randomIn(random, [22, 40]);
  const base = randomIn(random, [2, 4]);
  s.box([w, base, d], C.mossStoneDark, { at: [x, 0, z] }, C.moss);
  s.cylinder(r * 1.25, h, 7, C.jungleBark, { at: [x, base, z] }, r);
  for (let i = 0, y = 7; y < h - 2; i++, y += 8) {
    l.ring(r * 1.25 - (r * 0.25 * y) / h + 0.12, 1.2, 7, i % 2 === 0 ? kit.windows : kit.neon, {
      at: [x, y, z],
    });
  }
  const top = (Math.min(w, d) / 2) * 0.95;
  crown(s, { at: [x, h + 1, z], r: top, h: top * 0.9 }, pick(random, GREENS), 7, true);
}

/** A stack of two or three terraces shifted from one another, each with its garden. */
function terraceStack(kit: CanopyKit, lot: Lot): void {
  const { random } = kit;
  const [x, z, w, d] = lot;
  let y = 0;
  const levels = 2 + Math.floor(random() * 2);
  for (let i = 0; i < levels; i++) {
    const [lw, ld] = [w * randomIn(random, [0.6, 0.8]), d * randomIn(random, [0.6, 0.8])];
    const lx = x + ((w - lw) / 2) * (i % 2 === 0 ? -1 : 1) * randomIn(random, [0.4, 1]);
    const lz = z + ((d - ld) / 2) * randomIn(random, [-1, 1]);
    const h = randomIn(random, [6, 11]);
    block(kit, [lx, lz, lw, ld], y, h);
    y += h;
    garden(kit, [lx, lz, lw, ld], y);
  }
}

/** A glass slab with a neon spine up its front, roof units and a roof garden. */
function glassSlab(kit: CanopyKit, lot: Lot): void {
  const { s, random } = kit;
  const [x, z, w, d] = lot;
  const h = randomIn(random, [14, 30]);
  block(kit, lot, 0, h, pick(random, [C.glassGreen, C.glassBlue, C.glassDark]));
  neonSpine(kit, lot, [2, h - 1]);
  s.box([w * 0.3, 1.6, d * 0.3], C.metalDark, { at: [x + w * 0.25, h, z + d * 0.2] }, C.moss);
  garden(kit, [x - w * 0.15, z - d * 0.1, w * 0.65, d * 0.75], h);
}

const KINDS = [terracedTower, treeTower, terraceStack, glassSlab] as const;
const TOWERS = [terracedTower, treeTower] as const;

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
 * One of the canopy city's buildings, decided by `seed`, fitting in a square of half side
 * `half`: terraced towers, tree towers, terrace stacks and glass slabs, with moss on every roof,
 * roof gardens of small crowns, lit windows and neon.
 */
export function buildCanopyBuilding(seed: number, half = TOWER_HALF): PropGeometry {
  const random = createRng(seed * 32452843 + half * 131 + 7);
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  const windows = pick(random, WINDOWS);
  const neon = pick(random, NEONS);
  lots(half, random).forEach((lot, i) => {
    const facade = pick(random, FACADES);
    // A canopy tower always has a tower on its first lot.
    const kinds = half <= TOWER_HALF && i === 0 ? TOWERS : KINDS;
    pick(random, kinds)({ s, l, facade, windows, neon, random }, lot);
  });
  return { structure: s.geometry, lights: l.geometry };
}
