import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { buildYard, WALLS, type Plot, type YardKit } from './industrial-yard';

// Phase 4 review: industrial complexes assembled from parts (halls with one of four roofs,
// chimneys and lit doors, and plots of equipment, see `industrial-yard.ts`), laid out in one of
// five ways, so the industrial zone shows many different buildings. Everything stays within X, Z ∈ [-HALF, HALF], standing on Y = 0;
// the front faces -Z.

/** Half the side of the square every complex fits in. */
export const INDUSTRIAL_HALF = 12;

type Rgb = readonly [number, number, number];

interface Hall {
  /** Half the side of the square the whole complex fits in. */
  readonly half: number;
  readonly x: number;
  readonly z: number;
  readonly w: number;
  readonly d: number;
  readonly h: number;
}

// Weathered greys and rust only: green roofs stood out from the rest of the zone (review).
const ROOFS: readonly Rgb[] = [C.roof, C.rust, C.metal, C.concreteDark, C.metalDark];
/** Space left between the parts of a complex. */
const GAP = 1.5;
const DOOR_LIGHTS: readonly Rgb[] = [L.yellow, L.cyan, L.pink];

function roof(s: SolidBuilder, hall: Hall, random: Random): void {
  const { x, z, w, d, h } = hall;
  const style = Math.floor(random() * 4);
  if (style === 1) {
    // Sawtooth: slanted strips across the hall.
    const strips = Math.min(4, Math.max(2, Math.round(d / 5)));
    for (let i = 0; i < strips; i++) {
      const sz = z - d / 2 + (d * (i + 0.5)) / strips;
      s.box([w, 0.6, d / strips + 0.6], C.metal, { at: [x, h + 1, sz], pitch: -0.45 });
    }
  } else if (style === 2) {
    // Pitched: two slopes meeting along X.
    s.box([w + 1, 0.6, d / 2 + 1], C.rust, { at: [x, h + 0.6, z + d / 4], pitch: 0.4 });
    s.box([w + 1, 0.6, d / 2 + 1], C.rust, { at: [x, h + 0.6, z - d / 4], pitch: -0.4 });
  } else if (style === 3) {
    // Barrel vault: a cylinder lying along X, its lower half inside the hall.
    const r = d / 2;
    s.cylinder(r, w, 8, C.metal, { at: [x - w / 2, h - r * 0.4, z], roll: -Math.PI / 2 });
  } else {
    s.box([w * 0.3, 1.6, d * 0.3], C.metalDark, { at: [x - w / 4, h, z] });
    s.box([w * 0.2, 1.2, d * 0.25], C.metal, { at: [x + w / 4, h, z + d / 5] });
  }
}

function chimneys(s: SolidBuilder, l: SolidBuilder, hall: Hall, random: Random): void {
  const count = Math.floor(random() * 4);
  for (let i = 0; i < count; i++) {
    const cx = hall.x - hall.w / 2 + (hall.w * (i + 0.5)) / count;
    const cz = hall.z + hall.d / 2 - 2;
    const top = hall.h + randomIn(random, [8, 20]);
    const r = randomIn(random, [0.9, 1.6]);
    s.cylinder(
      r,
      top,
      6,
      pick(random, [C.rust, C.metal, C.concreteDark]),
      { at: [cx, 0, cz] },
      r * 0.75,
    );
    l.ring(r * 0.8, 0.6, 6, L.red, { at: [cx, top - 1.4, cz] });
  }
}

/** A hall standing on `plot`: walls, one of four roofs, chimneys and lit loading doors. */
function hall(kit: YardKit, [x, z, w, d]: Plot, half: number): void {
  const { s, l, random } = kit;
  const h = randomIn(random, [6, 6 + half / 2]);
  const building: Hall = { half, x, z, w, d, h };
  s.box([w, h, d], pick(random, WALLS), { at: [x, 0, z] }, pick(random, ROOFS));
  roof(s, building, random);
  chimneys(s, l, building, random);
  const doors = 1 + Math.floor(random() * 3);
  const light = pick(random, DOOR_LIGHTS);
  for (let i = 0; i < doors; i++) {
    const dx = x - w / 2 + (w * (i + 0.5)) / doors;
    l.box([Math.min(3, w / doors - 0.5), 0.5, 0.3], light, { at: [dx, 4, z - d / 2 - 0.2] });
  }
}

/** Splits `plot` across X at a share `t` of its width, leaving a gap between the two. */
function splitX([x, z, w, d]: Plot, t: number): [Plot, Plot] {
  const cut = x - w / 2 + w * t;
  return [
    [(x - w / 2 + cut - GAP / 2) / 2, z, cut - (x - w / 2) - GAP / 2, d],
    [(cut + GAP / 2 + x + w / 2) / 2, z, x + w / 2 - cut - GAP / 2, d],
  ];
}

/** Splits `plot` across Z, as {@link splitX}. */
function splitZ(plot: Plot, t: number): [Plot, Plot] {
  const [x, z, w, d] = plot;
  const [a, b] = splitX([z, x, d, w], t);
  return [
    [a[1], a[0], a[3], a[2]],
    [b[1], b[0], b[3], b[2]],
  ];
}

/** Ways of laying out a complex on its square: halls, yards of equipment, or both. */
const LAYOUTS = [
  // A hall, with equipment beside it.
  (kit: YardKit, square: Plot, half: number) => {
    const [main, side] = splitX(square, randomIn(kit.random, [0.55, 0.75]));
    hall(kit, main, half);
    buildYard(kit, side);
  },
  // Two halls of different sizes.
  (kit: YardKit, square: Plot, half: number) => {
    const [a, b] = splitZ(square, randomIn(kit.random, [0.4, 0.6]));
    hall(kit, a, half);
    const [c, e] = splitX(b, randomIn(kit.random, [0.5, 0.8]));
    hall(kit, c, half);
    buildYard(kit, e);
  },
  // A tank farm: four plots of equipment around a control room.
  (kit: YardKit, square: Plot) => {
    const [left, right] = splitX(square, randomIn(kit.random, [0.4, 0.6]));
    for (const column of [left, right]) {
      for (const plot of splitZ(column, randomIn(kit.random, [0.4, 0.6]))) buildYard(kit, plot);
    }
  },
  // A hall at the back, and a yard in front of it.
  (kit: YardKit, square: Plot, half: number) => {
    const [front, back] = splitZ(square, randomIn(kit.random, [0.3, 0.45]));
    hall(kit, back, half);
    for (const plot of splitX(front, randomIn(kit.random, [0.3, 0.7]))) buildYard(kit, plot);
  },
  // A long works hall across the square, with a strip of equipment at each end.
  (kit: YardKit, square: Plot, half: number) => {
    const [a, rest] = splitX(square, randomIn(kit.random, [0.15, 0.25]));
    const [main, b] = splitX(rest, randomIn(kit.random, [0.7, 0.85]));
    hall(kit, main, half);
    buildYard(kit, a);
    buildYard(kit, b);
  },
] as const;

/**
 * One of the industrial complexes, decided by `seed`, fitting in a square of half side `half`
 * (bigger complexes for the industrial zone's blocks, phase 4 review): one of five layouts of
 * halls and plots of equipment.
 */
export function buildIndustrialComplex(seed: number, half = INDUSTRIAL_HALF): PropGeometry {
  const random = createRng(seed * 7919 + half * 131 + 13);
  const kit: YardKit = {
    s: new SolidBuilder({ openBottoms: true }),
    l: new SolidBuilder({ openBottoms: true }),
    random,
  };
  const size = 2 * half;
  pick(random, LAYOUTS)(kit, [0, 0, size, size], half);
  return { structure: kit.s.geometry, lights: kit.l.geometry };
}
