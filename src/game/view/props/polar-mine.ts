import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { cone, pane, snowyGable } from './polar-parts';

// P08-R07: the big mining complex of 2-4, assembled from plots of mining equipment (a drill rig,
// ore silos, a snowy shed, ore heaps, fuel tanks) joined by a conveyor, laid out in one of three
// ways. Everything stays within X, Z ∈ [-half, half], standing on Y = 0; the front faces -Z.

type Rgb = readonly [number, number, number];

/** A plot: its centre and its size along X and Z. */
type Plot = readonly [x: number, z: number, w: number, d: number];

interface MineKit {
  readonly s: SolidBuilder;
  readonly l: SolidBuilder;
  readonly random: Random;
}

/** Space left between the plots of a complex. */
const GAP = 1.5;
const PAINTS: readonly Rgb[] = [C.mineYellow, C.polarRed, C.metal];
const SHED_WALLS: readonly Rgb[] = [C.polarRed, C.metal, C.containerBlue, C.panelDark];

/** A drill rig: a tapering derrick over a platform, a red light at the top. */
function drillRig({ s, l, random }: MineKit, [x, z, w, d]: Plot): void {
  const size = Math.min(w, d);
  s.box([w * 0.9, 1.6, d * 0.9], C.metalDark, { at: [x, 0, z] }, C.snowShade);
  const r = Math.min(size * 0.35, 4.5);
  const h = randomIn(random, [18, 30]);
  s.cylinder(r, h, 4, pick(random, PAINTS), { at: [x, 1.6, z], yaw: Math.PI / 4 }, r * 0.3);
  s.box([r * 0.9, 1.4, r * 0.9], C.metal, { at: [x, h + 1.6, z] }, C.snow);
  l.box([0.7, 0.7, 0.7], L.red, { at: [x, h + 3, z] });
  l.box([size * 0.5, 0.3, 0.3], L.yellow, { at: [x, 1.2, z - d * 0.45 - 0.2] });
}

/** A row of tall ore silos under snowy cone roofs, with a lit ring. */
function silos({ s, l, random }: MineKit, [x, z, w, d]: Plot): void {
  const along = w >= d;
  const r = Math.min(along ? d : w, 8) / 2 - 0.3;
  const count = Math.min(3, Math.max(1, Math.floor((along ? w : d) / (2 * r + 0.6))));
  const h = randomIn(random, [12, 22]);
  const color = pick(random, [C.silver, C.mineYellow, C.metal]);
  for (let i = 0; i < count; i++) {
    const t = -0.5 + (i + 0.5) / count;
    const [sx, sz] = along ? [x + t * w, z] : [x, z + t * d];
    s.cylinder(r, h, 6, color, { at: [sx, 0, sz] });
    cone(s, r * 1.05, [h, r * 0.6], 6, C.snow, { at: [sx, 0, sz] });
    l.ring(r * 1.03, 0.5, 6, L.cyanDim, { at: [sx, h * 0.7, sz] });
  }
}

/** A shed of painted metal under a snowy gable roof, with a lit loading door. */
function shed({ s, l, random }: MineKit, [x, z, w, d]: Plot): void {
  const h = randomIn(random, [5, 9]);
  const wall = pick(random, SHED_WALLS);
  s.box([w * 0.92, h, d * 0.92], wall, { at: [x, 0, z] });
  snowyGable(s, { size: [w * 0.96, d * 0.96], y: h, rise: Math.min(w, d) * 0.25 }, wall, {
    at: [x, 0, z],
  });
  pane(l, [Math.min(4, w * 0.4), 0.6], [x, h * 0.55, z - d * 0.46 - 0.05], L.yellow);
}

/** One or two heaps of dark ore, dusted with snow on top. */
function heaps({ s, random }: MineKit, [x, z, w, d]: Plot): void {
  const r = Math.min(w, d) / 2 - 0.4;
  const h = r * randomIn(random, [0.6, 0.9]);
  cone(s, r, [0, h], 7, C.ore, { at: [x, 0, z] });
  cone(s, r * 0.38, [h * 0.65, h * 0.35 + 0.15], 7, C.snow, { at: [x, 0, z] });
  if (Math.max(w, d) > 2.5 * Math.min(w, d)) {
    const [ox, oz] = w > d ? [w / 3, 0] : [0, d / 3];
    cone(s, r * 0.8, [0, h * 0.6], 6, C.ore, { at: [x + ox, 0, z + oz] });
  }
}

/** Fuel tanks lying on cradles, side by side. */
function tanks({ s, random }: MineKit, [x, z, w, d]: Plot): void {
  const r = Math.min(d / 4, 2.2);
  const color = pick(random, [C.white, C.silver, C.polarRed]);
  for (const t of [-0.25, 0.25]) {
    const tz = z + t * d;
    s.box([w * 0.7, 1, r * 1.4], C.metalDark, { at: [x, 0, tz] });
    s.cylinder(r, w * 0.85, 6, color, { at: [x - w * 0.425, r + 0.6, tz], roll: -Math.PI / 2 });
    s.box([w * 0.85, 0.3, r * 0.8], C.snowShade, { at: [x, 2 * r + 0.45, tz] }, C.snow);
  }
}

const PARTS = [drillRig, silos, shed, heaps, tanks] as const;

/** Splits `plot` across X at a share `t` of its width, leaving a gap between the two. */
function splitX([x, z, w, d]: Plot, t: number): [Plot, Plot] {
  const cut = x - w / 2 + w * t;
  return [
    [(x - w / 2 + cut - GAP / 2) / 2, z, cut - (x - w / 2) - GAP / 2, d],
    [(cut + GAP / 2 + x + w / 2) / 2, z, x + w / 2 - cut - GAP / 2, d],
  ];
}

/** Splits `plot` across Z, as {@link splitX}. */
function splitZ([x, z, w, d]: Plot, t: number): [Plot, Plot] {
  const [a, b] = splitX([z, x, d, w], t);
  return [
    [a[1], a[0], a[3], a[2]],
    [b[1], b[0], b[3], b[2]],
  ];
}

/** Ways of cutting the square of a complex into three or four plots. */
const LAYOUTS = [
  (square: Plot, random: Random): Plot[] => {
    const [left, right] = splitX(square, randomIn(random, [0.4, 0.6]));
    return [...splitZ(left, randomIn(random, [0.35, 0.65])), right];
  },
  (square: Plot, random: Random): Plot[] => {
    const [front, back] = splitZ(square, randomIn(random, [0.35, 0.55]));
    return [front, ...splitX(back, randomIn(random, [0.35, 0.65]))];
  },
  (square: Plot, random: Random): Plot[] => {
    const [left, right] = splitX(square, randomIn(random, [0.4, 0.6]));
    return [left, right].flatMap((column) => splitZ(column, randomIn(random, [0.4, 0.6])));
  },
] as const;

/** A copy of `items` in a random order (Fisher-Yates). */
function shuffle<T>(items: readonly T[], random: Random): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [out[i], out[j]] = [out[j] as T, out[i] as T];
  }
  return out;
}

/** A conveyor belt rising on two trestles from the middle of plot `a` to that of plot `b`. */
function conveyor({ s }: MineKit, [ax, az]: Plot, [bx, bz]: Plot, top: number): void {
  const length = Math.hypot(bx - ax, bz - az);
  const run = Math.atan2(top - 1, length);
  const yaw = Math.atan2(az - bz, bx - ax);
  const mid = [(ax + bx) / 2, (top + 1) / 2 - 0.4, (az + bz) / 2] as const;
  s.box([Math.hypot(length, top - 1), 0.8, 1.8], C.mineYellow, { at: mid, roll: run, yaw }, C.ore);
  s.box([0.5, mid[1], 0.5], C.metalDark, { at: [mid[0], 0, mid[2]] });
}

/**
 * The big mining complex of 2-4, decided by `seed`, fitting in a square of half side `half`:
 * three or four plots of mining equipment, always with a drill rig and a shed, joined by a
 * conveyor.
 */
export function buildMiningComplex(seed: number, half = 18): PropGeometry {
  const random = createRng(seed * 32452843 + half * 59 + 11);
  const kit: MineKit = {
    s: new SolidBuilder({ openBottoms: true }),
    l: new SolidBuilder({ openBottoms: true }),
    random,
  };
  const plots = pick(random, LAYOUTS)([0, 0, 2 * half, 2 * half], random);
  // A drill rig and a shed in every complex, then the other parts in a random order.
  const others = shuffle(
    PARTS.filter((p) => p !== drillRig && p !== shed),
    random,
  );
  const parts = [drillRig, ...others.slice(0, plots.length - 2), shed];
  plots.forEach((plot, i) => {
    parts[(i + seed) % parts.length]?.(kit, plot);
  });
  const [a, b] = plots;
  if (a && b) conveyor(kit, a, b, randomIn(random, [8, 14]));
  return { structure: kit.s.geometry, lights: kit.l.geometry };
}
