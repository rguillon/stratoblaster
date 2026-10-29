import { pick, randomIn, type Random } from '../../../core/math/rng';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { PROP_LIGHTS as L } from '../../config/prop-look';
import type { Lot } from './city-lots';
import { NEON } from './tile-kit';

// Phase 15 (reviewer, 2026-10-28: "make all buildings from offices, towers, downtown and
// skyscrapers asymmetrical, with a different light pattern on each side, so turning them makes
// more diversity"): each face of a volume gets its own pattern of lights.

type Rgb = readonly [number, number, number];

/** One face of a box: its middle, the direction along it, and its width. */
interface Face {
  readonly x: number;
  readonly z: number;
  /** Along X (the front and back), else along Z. */
  readonly alongX: boolean;
  readonly len: number;
  /** Outwards, the sign of the face's normal on its axis. */
  readonly out: number;
}

/** What a pattern draws with. */
interface Painter {
  readonly l: SolidBuilder;
  readonly random: Random;
  readonly color: Rgb;
  /** The panels this face may still have. */
  readonly room: { n: number };
}

/** Most lit panels a face may have, and a building, to keep the triangle count down. */
const MAX_PANELS = 30;
const BUILDING_PANELS = 220;
/** The panels each building (by its lights builder) has left. */
const left = new WeakMap<SolidBuilder, number>();
/** How far off its face a lit panel stands. */
const OFF = 0.06;

/** A lit panel on `face`, `a` along it from its middle, from `y`, `w` wide and `h` high. */
function panel(p: Painter, face: Face, [a, y, w, h]: readonly number[], color = p.color): void {
  const [aa, yy, ww, hh] = [a ?? 0, y ?? 0, w ?? 0, h ?? 0];
  if (p.room.n <= 0) return;
  p.room.n--;
  left.set(p.l, (left.get(p.l) ?? BUILDING_PANELS) - 1);
  // One quad facing out (2 triangles, not a box's 12), so a face can have many.
  const s = (face.alongX ? -face.out : face.out) * (ww / 2);
  const point = (along: number, height: number): [number, number, number] =>
    face.alongX
      ? [face.x + aa + along, height, face.z + face.out * OFF]
      : [face.x + face.out * OFF, height, face.z + aa + along];
  p.l.face([point(-s, yy), point(-s, yy + hh), point(s, yy + hh), point(s, yy)], color);
}

/** Thin horizontal bands across the face, every few floors. */
function rows(p: Painter, f: Face, [y0, y1]: readonly [number, number]): void {
  // Spread over the whole height, however few the panels.
  const gap = Math.max(pick(p.random, [2.5, 3, 3.5]), (y1 - y0) / p.room.n);
  for (let y = y0 + 1; y < y1; y += gap) panel(p, f, [0, y, f.len * 0.85, 0.35]);
}

/** Short horizontal ribbons, staggered from floor to floor. */
function ribbons(p: Painter, f: Face, [y0, y1]: readonly [number, number]): void {
  const gap = Math.max(2.5, (y1 - y0) / p.room.n);
  let i = 0;
  for (let y = y0 + 1.5; y < y1; y += gap, i++)
    panel(p, f, [(i % 2 === 0 ? -0.2 : 0.2) * f.len, y, f.len * 0.4, 0.3]);
}

/** A loose grid of small lit windows, some dark. */
function grid(p: Painter, f: Face, [y0, y1]: readonly [number, number]): void {
  const [cw, ch] = [Math.max(2.5, f.len / 8), 2.5];
  // Spread over the whole height, a floor every so often, so every face is lit.
  const gap = Math.max(ch, (y1 - y0) / Math.max(1, Math.ceil(p.room.n / 2)));
  for (let y = y0 + 1; y + 1 < y1; y += gap) {
    let lit = false;
    for (let a = -f.len / 2 + cw / 2; a < f.len / 2; a += cw)
      if (p.random() < 0.55 || (!lit && a + cw >= f.len / 2)) {
        panel(p, f, [a, y, cw * 0.6, 0.6]);
        lit = true;
      }
  }
}

/** A thin neon band at the top, a lit one at the bottom, dim rows between. */
function bands(p: Painter, f: Face, [y0, y1]: readonly [number, number]): void {
  panel(p, f, [0, y1 - 2, f.len * 0.9, 0.5], pick(p.random, NEON));
  panel(p, f, [0, y0 + 0.5, f.len * 0.9, 0.4]);
  const gap = Math.max(3, (y1 - y0) / p.room.n);
  for (let y = y0 + 3; y < y1 - 4; y += gap) panel(p, f, [0, y, f.len * 0.7, 0.3], L.windowDim);
}

/** A neon sign high up the face, thin rows under it. */
function sign(p: Painter, f: Face, [y0, y1]: readonly [number, number]): void {
  const h = Math.min(4, (y1 - y0) * 0.12);
  panel(
    p,
    f,
    [randomIn(p.random, [-0.2, 0.2]) * f.len, y1 - h - 2, f.len * 0.5, h],
    pick(p.random, NEON),
  );
  for (let y = y0 + 1; y < y1 - h - 4; y += Math.max(3, (y1 - y0) / p.room.n))
    panel(p, f, [0, y, f.len * 0.75, 0.3], L.windowDim);
}

type Pattern = (p: Painter, f: Face, span: readonly [number, number]) => void;

const PATTERNS: readonly Pattern[] = [rows, ribbons, grid, bands, sign];

/**
 * The lights of a `w` × `d` volume at (x, z), from `y0` to `y1`: each face its own pattern, no
 * two of the four the same, so the building looks different from each side.
 */
export function faceLights(
  { l, random, color }: Omit<Painter, 'room'>,
  [x, z, w, d]: Lot,
  [y0, y1]: readonly [number, number],
): void {
  const faces: Face[] = [
    { x, z: z - d / 2, alongX: true, len: w, out: -1 },
    { x: x + w / 2, z, alongX: false, len: d, out: 1 },
    { x, z: z + d / 2, alongX: true, len: w, out: 1 },
    { x: x - w / 2, z, alongX: false, len: d, out: -1 },
  ];
  // The patterns shuffled, so the four faces all differ.
  const order: Pattern[] = [...PATTERNS];
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [order[i], order[j]] = [order[j] ?? rows, order[i] ?? rows];
  }
  // Each face its share of what the building has left, a few panels at least, so none is dark.
  const share = Math.min(MAX_PANELS, Math.max(6, Math.floor((left.get(l) ?? BUILDING_PANELS) / 8)));
  faces.forEach((face, i) => {
    const pattern = order[i] ?? rows;
    pattern({ l, random, color, room: { n: share } }, face, [y0, y1]);
  });
}
