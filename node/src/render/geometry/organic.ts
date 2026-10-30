import type { Random } from '../../core/math/rng';
import type { OutlinePoint } from './outline';
import type { LoftStation, Placement, SectionPoint, SolidBuilder } from './solids';

// Builders of living shapes (bodies of segments, shells, ribs, tendrils, membrane wings, organs,
// veins, armour plates grafted on) for low-poly, flat-shaded models. Game-agnostic: they draw
// into a SolidBuilder and know nothing of what they are used for.

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** A rounded cross-section (counter-clockwise seen from the nose): a soft, swollen body. */
export const ROUND_SECTION: readonly SectionPoint[] = [
  [0.4, 0],
  [0.9, 0.25],
  [1, 0.55],
  [0.65, 0.9],
  [0, 1],
  [-0.65, 0.9],
  [-1, 0.55],
  [-0.9, 0.25],
  [-0.4, 0],
];

/** A shell's cross-section: low flanks rising to a ridge along its back. */
export const SHELL_SECTION: readonly SectionPoint[] = [
  [0.7, 0],
  [1, 0.2],
  [0.75, 0.6],
  [0.3, 0.88],
  [0, 1],
  [-0.3, 0.88],
  [-0.75, 0.6],
  [-1, 0.2],
  [-0.7, 0],
];

/** A body of segments along Z, from its tail to its nose. */
export interface SegmentedBody {
  /** Z of the tail end. */
  readonly tail: number;
  /** Z of the nose end. */
  readonly nose: number;
  /** Number of swollen segments. */
  readonly segments: number;
  /** Half width at the widest segment. */
  readonly width: number;
  /** Height of its bottom and top at the widest segment. */
  readonly bottom: number;
  readonly top: number;
  /** How much thinner it is between two segments (0: not at all, 1: to nothing). */
  readonly pinch?: number;
  /** Its girth along the body, from tail (t = 0) to nose (t = 1): a swollen middle by default. */
  readonly girth?: (t: number) => number;
  /** Whether the tail and nose close to a point (both by default). */
  readonly closed?: readonly [tail: boolean, nose: boolean];
}

const swollen = (t: number): number => 0.35 + 0.65 * Math.sin(Math.PI * t);

/** The loft stations of a {@link SegmentedBody}: a bulge at each segment, a waist between. */
export function segmentStations(body: SegmentedBody): LoftStation[] {
  const { tail, nose, segments, width, bottom, top, pinch = 0.3, girth = swollen } = body;
  const [closeTail, closeNose] = body.closed ?? [true, true];
  const mid = (bottom + top) / 2;
  const station = (t: number, k: number): LoftStation => {
    const g = girth(t) * k;
    return [tail + (nose - tail) * t, width * g, mid - (mid - bottom) * g, mid + (top - mid) * g];
  };
  const stations: LoftStation[] = [];
  for (let i = 0; i <= 2 * segments; i++) {
    const t = i / (2 * segments);
    // Even stations are the waists between segments, odd ones their swollen middles.
    stations.push(station(t, i % 2 === 0 ? 1 - pinch : 1));
  }
  const ends: [number, boolean][] = [
    [0, closeTail],
    [stations.length - 1, closeNose],
  ];
  for (const [i, close] of ends) {
    const s = stations[i];
    if (close && s) stations[i] = [s[0], 0, mid, mid];
  }
  return stations;
}

/** Draws a {@link SegmentedBody} with `section` ({@link ROUND_SECTION} by default). */
export function segmentedBody(
  b: SolidBuilder,
  body: SegmentedBody,
  color: Rgb,
  place: Placement = {},
  section: readonly SectionPoint[] = ROUND_SECTION,
): SolidBuilder {
  return b.loft(section, segmentStations(body), color, place);
}

/** A shell over a body: plates along Z, alternately `color` and `seam`, on a ridged section. */
export function carapace(
  b: SolidBuilder,
  body: SegmentedBody,
  [color, seam]: readonly [Rgb, Rgb],
  place: Placement = {},
): SolidBuilder {
  const paint = (_side: number, band: number): Rgb | undefined =>
    band % 2 === 1 ? seam : undefined;
  return b.loft(SHELL_SECTION, segmentStations({ pinch: 0.12, ...body }), color, place, { paint });
}

/** Two unit vectors across `t` (a unit tangent), for the rings of a tube along it. */
function across([tx, ty, tz]: Vec3): [Vec3, Vec3] {
  // Any vector not along t, crossed with it.
  const up: Vec3 = Math.abs(ty) < 0.9 ? [0, 1, 0] : [1, 0, 0];
  const nx = up[1] * tz - up[2] * ty;
  const ny = up[2] * tx - up[0] * tz;
  const nz = up[0] * ty - up[1] * tx;
  const n = Math.hypot(nx, ny, nz) || 1;
  const a: Vec3 = [nx / n, ny / n, nz / n];
  const c: Vec3 = [ty * a[2] - tz * a[1], tz * a[0] - tx * a[2], tx * a[1] - ty * a[0]];
  return [a, c];
}

function unit([x, y, z]: Vec3): Vec3 {
  const n = Math.hypot(x, y, z) || 1;
  return [x / n, y / n, z / n];
}

/**
 * A tube along the polyline `path`, its radius going from `r0` at the first point to `r1` at the
 * last (0 closes it to a point): a tendril, a sinew, a strut, a vein. `sides` facets round.
 */
export function tendril(
  b: SolidBuilder,
  path: readonly Vec3[],
  [r0, r1]: readonly [number, number],
  sides: number,
  color: Rgb,
  place: Placement = {},
): SolidBuilder {
  if (path.length < 2) throw new RangeError('A tendril needs 2 points');
  const rings = path.map((p, i) => {
    const prev = path[Math.max(0, i - 1)] ?? p;
    const next = path[Math.min(path.length - 1, i + 1)] ?? p;
    const [a, c] = across(unit([next[0] - prev[0], next[1] - prev[1], next[2] - prev[2]]));
    const r = r0 + ((r1 - r0) * i) / (path.length - 1);
    return Array.from({ length: sides }, (_, k): Vec3 => {
      const angle = (2 * Math.PI * k) / sides;
      const [cos, sin] = [Math.cos(angle) * r, Math.sin(angle) * r];
      return [
        p[0] + a[0] * cos + c[0] * sin,
        p[1] + a[1] * cos + c[1] * sin,
        p[2] + a[2] * cos + c[2] * sin,
      ];
    });
  });
  rings.slice(1).forEach((ring, i) => {
    const prev = rings[i] ?? ring;
    for (let k = 0; k < sides; k++) {
      const k1 = (k + 1) % sides;
      const [a0, a1, b0, b1] = [prev[k], prev[k1], ring[k], ring[k1]] as Vec3[];
      if (!a0 || !a1 || !b0 || !b1) continue;
      if (i + 1 === rings.length - 1 && r1 === 0) b.face([a0, a1, b0], color, place);
      else b.face([a0, a1, b1, b0], color, place);
    }
  });
  if (r0 > 0) b.face([...(rings[0] ?? [])].reverse(), color, place);
  if (r1 > 0) b.face(rings.at(-1) ?? [], color, place);
  return b;
}

/** Points along a curve from `from` to `to`, bowed by `bow` (an offset at its middle). */
export function curve(from: Vec3, to: Vec3, bow: Vec3, points = 4): Vec3[] {
  return Array.from({ length: points + 1 }, (_, i): Vec3 => {
    const t = i / points;
    const k = 4 * t * (1 - t);
    return [
      from[0] + (to[0] - from[0]) * t + bow[0] * k,
      from[1] + (to[1] - from[1]) * t + bow[1] * k,
      from[2] + (to[2] - from[2]) * t + bow[2] * k,
    ];
  });
}

/**
 * Ribs across a body: at each Z of `at`, an arch over its back from one flank to the other,
 * `halfWidth` out and `height` up from `y`.
 */
export function ribs(
  b: SolidBuilder,
  at: readonly number[],
  {
    halfWidth,
    y,
    height,
    thickness,
  }: { halfWidth: number; y: number; height: number; thickness: number },
  color: Rgb,
  place: Placement = {},
): SolidBuilder {
  for (const z of at) {
    const arch = Array.from({ length: 7 }, (_, i): Vec3 => {
      const a = Math.PI * (i / 6);
      return [Math.cos(a) * halfWidth, y + Math.sin(a) * height, z];
    });
    tendril(b, arch, [thickness, thickness], 3, color, place);
  }
  return b;
}

/** An organ: a swollen, faceted bulb of `radius`, `stretch` times as tall, standing on `at`. */
export function organ(
  b: SolidBuilder,
  radius: number,
  sides: number,
  color: Rgb,
  place: Placement = {},
  stretch = 1,
): SolidBuilder {
  const h = radius * 2 * stretch;
  return b.lathe(
    [
      [0, 0],
      [radius * 0.75, h * 0.12],
      [radius, h * 0.45],
      [radius * 0.8, h * 0.8],
      [0, h],
    ],
    sides,
    color,
    place,
  );
}

/** A wing: a membrane spread between its root and its tips, and a strut out to each tip. */
export interface MembraneWing {
  /** Where the wing joins the body, and the points of its membrane out to its tips. */
  readonly root: OutlinePoint;
  readonly tips: readonly OutlinePoint[];
  /** Height of the membrane, its thickness and the struts' radius at the root. */
  readonly y: number;
  readonly thickness: number;
  readonly strut: number;
}

/**
 * Draws a {@link MembraneWing}: its membrane in `skin` (from the root along the tips and back),
 * a strut along each tip in `bone`, thinning out to it.
 */
export function membraneWing(
  skin: SolidBuilder,
  bone: SolidBuilder,
  wing: MembraneWing,
  [skinColor, boneColor]: readonly [Rgb, Rgb],
  place: Placement = {},
): void {
  const { root, tips, y, thickness, strut } = wing;
  skin.slab([root, ...tips], [y - thickness / 2, y + thickness / 2], skinColor, place);
  for (const [x, z] of tips) {
    const path = curve([root[0], y, root[1]], [x, y, z], [0, thickness * 2, 0], 3);
    tendril(bone, path, [strut, strut * 0.2], 4, boneColor, place);
  }
}

/** A glowing vein along `path`: a thin three-sided tube, `width` across. */
export function vein(
  b: SolidBuilder,
  path: readonly Vec3[],
  width: number,
  color: Rgb,
  place: Placement = {},
): SolidBuilder {
  return tendril(b, path, [width / 2, width / 4], 3, color, place);
}

/**
 * An armour plate grafted on: a bevelled slab of `outline` from `y0` to `y1`, and a rivet at
 * each of its corners in `rivet`.
 */
export function plate(
  b: SolidBuilder,
  outline: readonly OutlinePoint[],
  [y0, y1]: readonly [number, number],
  [color, rivet]: readonly [Rgb, Rgb],
  place: Placement = {},
): SolidBuilder {
  const t = y1 - y0;
  b.bevelSlab(outline, [y0, y0, y1], [0, t * 0.8], color, place);
  for (const [x, z] of outline) {
    const [cx, cz] = [x * 0.82, z * 0.82];
    b.box([t * 0.6, t * 0.4, t * 0.6], rivet, { ...place, at: offset(place, [cx, y1, cz]) });
  }
  return b;
}

/** `p` moved by the position of `place` (its turns left out: rivets are tiny). */
function offset(place: Placement, [x, y, z]: Vec3): Vec3 {
  const [ax, ay, az] = place.at ?? [0, 0, 0];
  return [ax + x, ay + y, az + z];
}

/**
 * The outline `outline` with each point moved by up to `amount` at random: an uneven, grown edge
 * instead of a drawn one. The same `random` sequence gives the same outline.
 */
export function grown(
  outline: readonly OutlinePoint[],
  amount: number,
  random: Random,
): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [
    x + (random() * 2 - 1) * amount,
    z + (random() * 2 - 1) * amount,
  ]);
}
