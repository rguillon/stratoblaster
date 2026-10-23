import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// Phase 4 review: industrial complexes assembled from parts (a hall with one of four roofs,
// chimneys, tanks, an annex, a pipe rack, roof units, lit doors), so the industrial zone shows
// many different buildings. Everything stays within X, Z ∈ [-HALF, HALF], standing on Y = 0;
// the front faces -Z.

/** Half the side of the square every complex fits in. */
export const INDUSTRIAL_HALF = 12;

type Rgb = readonly [number, number, number];

interface Hall {
  readonly x: number;
  readonly z: number;
  readonly w: number;
  readonly d: number;
  readonly h: number;
}

const WALLS: readonly Rgb[] = [C.concrete, C.metal, C.rust, C.concreteDark, C.containerBlue];
const DOOR_LIGHTS: readonly Rgb[] = [L.yellow, L.cyan, L.pink];

function roof(s: SolidBuilder, hall: Hall, random: Random): void {
  const { x, z, w, d, h } = hall;
  const style = Math.floor(random() * 4);
  if (style === 1) {
    // Sawtooth: slanted strips across the hall.
    const strips = Math.max(2, Math.round(d / 4));
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

/** Tanks, an annex or a pipe rack in the strip left beside the hall. */
function sideStrip(s: SolidBuilder, l: SolidBuilder, hall: Hall, random: Random): void {
  const x0 = hall.x + hall.w / 2 + 1;
  const width = INDUSTRIAL_HALF - x0;
  if (width < 2.5) return;
  const kind = Math.floor(random() * 3);
  const xc = x0 + width / 2;
  if (kind === 0) {
    const r = Math.min(width / 2, 3.5);
    for (let zc = -INDUSTRIAL_HALF + r; zc + r <= INDUSTRIAL_HALF; zc += 2 * r + 0.8) {
      s.lathe(
        [
          [r, 0],
          [r, 6],
          [r * 0.7, 7.5],
          [0, 8.2],
        ],
        8,
        C.white,
        { at: [xc, 0, zc] },
      );
    }
  } else if (kind === 1) {
    s.box(
      [width, randomIn(random, [3, 6]), hall.d * 0.8],
      pick(random, WALLS),
      { at: [xc, 0, hall.z] },
      C.roof,
    );
    l.box([0.3, 1, hall.d * 0.5], pick(random, DOOR_LIGHTS), {
      at: [INDUSTRIAL_HALF + 0.05, 2, hall.z],
    });
  } else {
    for (const zc of [-8, 0, 8]) s.box([0.6, 7, 0.6], C.metalDark, { at: [xc, 0, zc] });
    for (const y of [6, 7.2])
      s.box([0.8, 0.8, 18], pick(random, [C.rust, C.metal]), { at: [xc, y, 0] });
  }
}

/** One of the industrial complexes, decided by `seed`. */
export function buildIndustrialComplex(seed: number): PropGeometry {
  const random = createRng(seed * 7919 + 13);
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  const w = randomIn(random, [12, 20]);
  const d = randomIn(random, [10, 2 * INDUSTRIAL_HALF - 2]);
  const hall: Hall = {
    x: -INDUSTRIAL_HALF + w / 2,
    z: randomIn(random, [-INDUSTRIAL_HALF + d / 2, INDUSTRIAL_HALF - d / 2]),
    w,
    d,
    h: randomIn(random, [6, 12]),
  };
  s.box([hall.w, hall.h, hall.d], pick(random, WALLS), { at: [hall.x, 0, hall.z] }, C.roof);
  roof(s, hall, random);
  chimneys(s, l, hall, random);
  sideStrip(s, l, hall, random);
  // Lit loading doors along the front.
  const doors = 1 + Math.floor(random() * 3);
  const light = pick(random, DOOR_LIGHTS);
  for (let i = 0; i < doors; i++) {
    const dx = hall.x - hall.w / 2 + (hall.w * (i + 0.5)) / doors;
    l.box([3, 0.5, 0.3], light, { at: [dx, 4, hall.z - hall.d / 2 - 0.2] });
  }
  return { structure: s.geometry, lights: l.geometry };
}
