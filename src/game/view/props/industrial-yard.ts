import { pick, randomIn, type Random } from '../../../core/math/rng';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// Phase 4 review: the equipment that fills the ground around industrial halls (tanks, silos, a
// gas sphere, container stacks, a pipe rack, an annex, a flare stack, a conveyor, a crane), so
// industrial complexes vary much more. Each one fills a rectangle of ground, a "plot".

type Rgb = readonly [number, number, number];

/** A plot: its centre and its size along X and Z. */
export type Plot = readonly [x: number, z: number, w: number, d: number];

export interface YardKit {
  readonly s: SolidBuilder;
  readonly l: SolidBuilder;
  readonly random: Random;
}

export const WALLS: readonly Rgb[] = [C.concrete, C.metal, C.rust, C.concreteDark, C.containerBlue];
const CONTAINERS: readonly Rgb[] = [C.containerBlue, C.containerGreen, C.containerRed, C.rust];
const DOOR_LIGHTS: readonly Rgb[] = [L.yellow, L.cyan, L.pink];

/** Positions of `count` items spread evenly across `size` around `centre`. */
function spread(centre: number, size: number, count: number): number[] {
  return Array.from({ length: count }, (_, i) => centre - size / 2 + (size * (i + 0.5)) / count);
}

/** Rows of round tanks with domed tops. */
function tanks({ s, random }: YardKit, [x, z, w, d]: Plot): void {
  // At most 3 × 3 tanks, bigger on bigger plots.
  const [nx, nz] = [w, d].map((size) => Math.min(3, Math.max(1, Math.round(size / 9)))) as [
    number,
    number,
  ];
  const r = Math.min(w / nx, d / nz) / 2 - 0.5;
  const h = randomIn(random, [4, 8]);
  const color = pick(random, [C.white, C.metal, C.concrete]);
  for (const tx of spread(x, w, nx)) {
    for (const tz of spread(z, d, nz)) {
      s.lathe(
        [
          [r, 0],
          [r, h],
          [0, h + r * 0.5],
        ],
        6,
        color,
        { at: [tx, 0, tz] },
      );
    }
  }
}

/** A row of tall silos with cone tops, joined by a walkway. */
function silos({ s, random }: YardKit, [x, z, w, d]: Plot): void {
  const long = w >= d;
  const r = Math.min(long ? d : w, 6) / 2 - 0.3;
  const count = Math.min(5, Math.max(1, Math.floor((long ? w : d) / (2 * r + 0.5))));
  const h = randomIn(random, [12, 22]);
  const color = pick(random, [C.white, C.concrete, C.metal]);
  for (const t of spread(long ? x : z, long ? w : d, count)) {
    const [sx, sz] = long ? [t, z] : [x, t];
    s.lathe(
      [
        [r, 0],
        [r, h],
        [0, h + r],
      ],
      8,
      color,
      { at: [sx, 0, sz] },
    );
  }
  s.box(long ? [w * 0.9, 0.6, 0.8] : [0.8, 0.6, d * 0.9], C.metalDark, { at: [x, h + 0.5, z] });
}

/** A gas holder sphere on legs. */
function sphere({ s, l }: YardKit, [x, z, w, d]: Plot): void {
  const r = Math.min(w, d, 12) / 2 - 0.5;
  const y = r * 0.5;
  for (const [lx, lz] of [
    [-1, -1],
    [1, -1],
    [-1, 1],
    [1, 1],
  ] as const) {
    s.box([0.5, y + r * 0.3, 0.5], C.metalDark, { at: [x + lx * r * 0.6, 0, z + lz * r * 0.6] });
  }
  const ring = (k: number): [number, number] => [
    r * Math.sin((Math.PI * k) / 6),
    y + r - r * Math.cos((Math.PI * k) / 6),
  ];
  s.lathe([[0, y], ring(1), ring(2), ring(3), ring(4), ring(5), [0, y + 2 * r]], 8, C.white, {
    at: [x, 0, z],
  });
  l.box([0.6, 0.6, 0.6], L.red, { at: [x, y + 2 * r, z] });
}

/** Stacks of shipping containers in rows. */
function containers({ s, random }: YardKit, [x, z, w, d]: Plot): void {
  // At most 3 rows of 3 stacks of up to 3, shorter in narrow plots; a stack is one box.
  const rows = Math.min(3, Math.max(1, Math.floor(d / 3.4)));
  const cols = Math.min(3, Math.max(1, Math.floor(w / 7)));
  const length = Math.min(6, w / cols - 0.5);
  for (const cz of spread(z, d, rows)) {
    for (const cx of spread(x, w, cols)) {
      const high = 1 + Math.floor(random() * 3);
      s.box([length, high * 2.4, 2.8], pick(random, CONTAINERS), { at: [cx, 0, cz] });
    }
  }
}

/** A pipe rack on posts, with two pipes along it. */
function pipeRack({ s, random }: YardKit, [x, z, w, d]: Plot): void {
  const long = w >= d;
  const length = (long ? w : d) * 0.9;
  for (const t of spread(long ? x : z, length, 3)) {
    s.box([0.6, 7, 0.6], C.metalDark, { at: long ? [t, 0, z] : [x, 0, t] });
  }
  for (const y of [6, 7.2]) {
    const size = long ? ([length, 0.8, 0.8] as const) : ([0.8, 0.8, length] as const);
    s.box(size, pick(random, [C.rust, C.metal, C.containerGreen]), { at: [x, y, z] });
  }
}

/** A low annex with a lit door. */
function annex({ s, l, random }: YardKit, [x, z, w, d]: Plot): void {
  const h = randomIn(random, [3, 7]);
  s.box(
    [w * 0.85, h, d * 0.85],
    pick(random, WALLS),
    { at: [x, 0, z] },
    pick(random, [C.roof, C.rust]),
  );
  l.box([Math.min(3, w * 0.4), 1, 0.3], pick(random, DOOR_LIGHTS), {
    at: [x, 1.5, z - d * 0.425 - 0.2],
  });
}

/** A tall flare stack with a lit tip, and a small pump house. */
function flare({ s, l, random }: YardKit, [x, z, w, d]: Plot): void {
  const h = randomIn(random, [18, 30]);
  s.cylinder(0.7, h, 6, C.metal, { at: [x, 0, z] }, 0.45);
  l.ring(0.6, 1, 6, L.yellow, { at: [x, h - 1, z] });
  s.box([w * 0.35, 3, d * 0.35], C.concreteDark, { at: [x + w * 0.25, 0, z + d * 0.25] }, C.roof);
}

/** A slanted conveyor from a hopper on the ground up to a tower. */
function conveyor({ s, random }: YardKit, [x, z, w, d]: Plot): void {
  const h = randomIn(random, [10, 16]);
  const long = w >= d;
  const length = (long ? w : d) * 0.8;
  s.box(
    [3, h, 3],
    pick(random, WALLS),
    { at: long ? [x + length / 2 - 1.5, 0, z] : [x, 0, z + length / 2 - 1.5] },
    C.roof,
  );
  const pitch = Math.atan2(h * 0.8, length);
  s.box([1.2, 0.8, Math.hypot(length, h * 0.8)], C.metalDark, {
    at: [x, h * 0.4, z],
    yaw: long ? Math.PI / 2 : 0,
    pitch: -pitch,
  });
}

/** A gantry crane over a strip of ground, with a red warning light. */
function gantry({ s, l, random }: YardKit, [x, z, w, d]: Plot): void {
  const h = randomIn(random, [9, 14]);
  const color = pick(random, [L.yellow, C.containerRed, C.containerBlue]);
  for (const sx of [x - w * 0.42, x + w * 0.42]) s.box([0.8, h, 0.8], color, { at: [sx, 0, z] });
  s.box([w * 0.9, 1.2, 1.4], color, { at: [x, h, z] });
  s.box([1.6, 1.4, 1.6], C.metalDark, { at: [x + randomIn(random, [-0.3, 0.3]) * w, h - 1.4, z] });
  l.box([0.5, 0.5, 0.5], L.red, { at: [x, h + 1.4, z] });
  if (d > 4) containers({ s, l, random }, [x, z + d / 4, w * 0.7, d / 2 - 0.5]);
}

const YARDS = [tanks, silos, sphere, containers, pipeRack, annex, flare, conveyor, gantry] as const;

/** Fills `plot` with one kind of equipment, picked among those that fit it. */
export function buildYard(kit: YardKit, plot: Plot): void {
  const [, , w, d] = plot;
  if (w < 2.5 || d < 2.5) return;
  // Spheres, conveyors and gantries need room; the others fit narrow strips.
  const kinds = Math.min(w, d) < 7 ? YARDS.filter((k) => k !== sphere && k !== gantry) : YARDS;
  pick(kit.random, kinds)(kit, plot);
}
