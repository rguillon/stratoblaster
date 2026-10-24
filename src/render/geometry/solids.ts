import type { ColoredGeometry } from './gradient-shapes';
import { insetOutline, ringAt, type OutlinePoint } from './outline';
import { triangulatePolygon } from './triangulate';

type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Where a solid goes: a position, then turns around X (pitch), Z (roll) and Y (yaw), radians. */
export interface Placement {
  readonly at?: Vec3;
  readonly yaw?: number;
  readonly pitch?: number;
  readonly roll?: number;
}

/** A profile point of a body of revolution: radius at a height. */
export type ProfilePoint = readonly [radius: number, y: number];

/** A point of a loft cross-section: `u` across (-1 to 1, +X), `v` up (0 to 1, +Y). */
export type SectionPoint = readonly [u: number, v: number];

/** A loft station: where along Z, its half width, and the heights of its bottom and top. */
export type LoftStation = readonly [z: number, halfWidth: number, bottom: number, top: number];

export interface LoftOptions {
  /** Leaves the section's closing side and the end caps out, e.g. a canopy sitting on a hull. */
  readonly open?: boolean;
  /**
   * Another colour for some faces: side `side` of the section (from point `side` to the next)
   * between stations `band` and `band + 1`, e.g. a canopy painted on a fuselage's back.
   */
  readonly paint?: (side: number, band: number) => Rgb | undefined;
}

/** A loft station of no width and no height: the body closes to a point there. */
function isPoint([, halfWidth, bottom, top]: LoftStation): boolean {
  return halfWidth === 0 && bottom === top;
}

function rotate([x, y, z]: Vec3, { yaw = 0, pitch = 0, roll = 0 }: Placement): Vec3 {
  // Pitch (around X), then roll (around Z), then yaw (around Y).
  const y1 = y * Math.cos(pitch) - z * Math.sin(pitch);
  const z1 = y * Math.sin(pitch) + z * Math.cos(pitch);
  const x2 = x * Math.cos(roll) - y1 * Math.sin(roll);
  const y2 = x * Math.sin(roll) + y1 * Math.cos(roll);
  const x3 = x2 * Math.cos(yaw) + z1 * Math.sin(yaw);
  const z3 = -x2 * Math.sin(yaw) + z1 * Math.cos(yaw);
  return [x3, y2, z3];
}

/** Twice the signed area of an outline in the XZ plane: positive when counter-clockwise. */
function doubleArea(outline: readonly OutlinePoint[]): number {
  return outline.reduce((sum, [x1, z1], i) => {
    const [x2, z2] = ringAt(outline, i + 1);
    return sum + x1 * z2 - x2 * z1;
  }, 0);
}

/** A side facet of a body of revolution, a triangle where a ring closes to a point. */
function sideFace(a0: Vec3, a1: Vec3, b1: Vec3, b0: Vec3, rA: number, rB: number): Vec3[] {
  if (rA === 0) return [a1, b1, b0];
  if (rB === 0) return [a0, a1, b1];
  return [a0, a1, b1, b0];
}

/**
 * Builds low-poly, flat-shaded, vertex-coloured solids into one {@link ColoredGeometry}: every
 * face has its own vertices, so computed normals are per face. Used for props (P04-R04).
 */
export class SolidBuilder {
  readonly geometry: ColoredGeometry = { positions: [], indices: [], colors: [] };

  /**
   * With `openBottoms`, upright boxes and bodies of revolution get no bottom face: for buildings
   * seen from above, standing on the ground or on another solid, it would never show.
   */
  constructor(private readonly options: { readonly openBottoms?: boolean } = {}) {}

  /** Whether the bottom face of a solid placed by `place` is left out. */
  #openBottom(place: Placement): boolean {
    return this.options.openBottoms === true && !place.pitch && !place.roll;
  }

  #point(p: Vec3, place: Placement): Vec3 {
    const [x, y, z] = rotate(p, place);
    const [ax, ay, az] = place.at ?? [0, 0, 0];
    return [x + ax, y + ay, z + az];
  }

  /**
   * A flat convex polygon. Its outward normal is (c1 - c0) × (c2 - c0): the corners go
   * counter-clockwise seen from outside.
   */
  face(corners: readonly Vec3[], color: Rgb, place: Placement = {}): this {
    const geo = this.geometry;
    const base = geo.positions.length / 3;
    for (const corner of corners) {
      geo.positions.push(...this.#point(corner, place));
      geo.colors.push(...color, 1);
    }
    // Babylon front faces have the normal (c - a) × (b - a), hence the swapped order.
    for (let i = 1; i < corners.length - 1; i++) geo.indices.push(base, base + i + 1, base + i);
    return this;
  }

  /** Flat caps on the ends of a body of revolution that are not closed to a point. */
  #caps(profile: readonly ProfilePoint[], sides: number, color: Rgb, place: Placement): void {
    const ends: [ProfilePoint | undefined, boolean][] = [
      [profile[0], false],
      [profile.at(-1), true],
    ];
    for (const [end, up] of ends) {
      if (!end || end[0] <= 0 || (!up && this.#openBottom(place))) continue;
      const [r, y] = end;
      const corners = Array.from({ length: sides }, (_, i): Vec3 => {
        const a = ((up ? sides - i : i) / sides) * Math.PI * 2;
        return [r * Math.cos(a), y, r * Math.sin(a)];
      });
      this.face(corners, color, place);
    }
  }

  /** A box of size (w, h, d) standing on its base at `at`. */
  box([w, h, d]: Vec3, color: Rgb, place: Placement = {}, top: Rgb = color): this {
    const [x0, x1, z0, z1] = [-w / 2, w / 2, -d / 2, d / 2];
    const c = (x: number, y: number, z: number): Vec3 => [x, y, z];
    this.face([c(x0, h, z0), c(x0, h, z1), c(x1, h, z1), c(x1, h, z0)], top, place);
    if (!this.#openBottom(place)) {
      this.face([c(x0, 0, z0), c(x1, 0, z0), c(x1, 0, z1), c(x0, 0, z1)], color, place);
    }
    this.face([c(x0, 0, z0), c(x0, h, z0), c(x1, h, z0), c(x1, 0, z0)], color, place);
    this.face([c(x1, 0, z1), c(x1, h, z1), c(x0, h, z1), c(x0, 0, z1)], color, place);
    this.face([c(x0, 0, z1), c(x0, h, z1), c(x0, h, z0), c(x0, 0, z0)], color, place);
    this.face([c(x1, 0, z0), c(x1, h, z0), c(x1, h, z1), c(x1, 0, z1)], color, place);
    return this;
  }

  /**
   * A body of revolution around Y with `sides` flat facets: the profile goes from bottom to top.
   * A profile point of radius 0 closes the body there; otherwise the ends are capped, unless
   * `caps` is false.
   */
  lathe(
    profile: readonly ProfilePoint[],
    sides: number,
    color: Rgb,
    place: Placement = {},
    caps = true,
  ): this {
    const ring = (i: number): number => (i / sides) * Math.PI * 2;
    const at = ([r, y]: ProfilePoint, i: number): Vec3 => [
      r * Math.cos(ring(i)),
      y,
      r * Math.sin(ring(i)),
    ];
    for (let k = 0; k < profile.length - 1; k++) {
      const a = profile[k];
      const b = profile[k + 1];
      if (!a || !b) continue;
      for (let i = 0; i < sides; i++) {
        this.face(
          sideFace(at(a, i + 1), at(a, i), at(b, i), at(b, i + 1), a[0], b[0]),
          color,
          place,
        );
      }
    }
    if (caps) this.#caps(profile, sides, color, place);
    return this;
  }

  /**
   * An open band around Y (no caps), e.g. a lit ring around a building: nothing of it hides
   * inside the building, which matters for glow layers that draw lights without occluders.
   */
  ring(radius: number, height: number, sides: number, color: Rgb, place: Placement = {}): this {
    return this.lathe(
      [
        [radius, 0],
        [radius, height],
      ],
      sides,
      color,
      place,
      false,
    );
  }

  /** A straight (or tapered) cylinder of `sides` facets standing on its base. */
  cylinder(
    radius: number,
    height: number,
    sides: number,
    color: Rgb,
    place: Placement = {},
    topRadius = radius,
  ): this {
    return this.lathe(
      [
        [radius, 0],
        [topRadius, height],
      ],
      sides,
      color,
      place,
    );
  }

  /**
   * A flat slab: a simple polygon outline in the XZ plane (concave is fine, either winding),
   * extruded from height `y0` up to `y1`, e.g. a wing seen from above.
   */
  slab(
    outline: readonly OutlinePoint[],
    [y0, y1]: readonly [number, number],
    color: Rgb,
    place: Placement = {},
    top: Rgb = color,
  ): this {
    const ring = doubleArea(outline) > 0 ? [...outline] : [...outline].reverse();
    const at = ([x, z]: OutlinePoint, y: number): Vec3 => [x, y, z];
    for (const [a, b, c] of triangulatePolygon(ring)) {
      const [pa, pb, pc] = [ringAt(ring, a), ringAt(ring, b), ringAt(ring, c)];
      // Counter-clockwise in (x, z) faces down; reversed, it faces up.
      this.face([at(pa, y1), at(pc, y1), at(pb, y1)], top, place);
      this.face([at(pa, y0), at(pb, y0), at(pc, y0)], color, place);
    }
    ring.forEach((p, i) => {
      const q = ringAt(ring, i + 1);
      this.face([at(p, y0), at(p, y1), at(q, y1), at(q, y0)], color, place);
    });
    return this;
  }

  /**
   * A slab with bevelled edges: the outline at height `waist`, narrowing by `inset` (bottom, top)
   * to a smaller bottom face at `y0` and top face at `y1`. Sloped sides instead of walls (a knife
   * edge for wings, a chamfered plate for hulls) for two triangles more per outline side.
   */
  bevelSlab(
    outline: readonly OutlinePoint[],
    [y0, waist, y1]: readonly [number, number, number],
    [insetBottom, insetTop]: readonly [number, number],
    color: Rgb,
    place: Placement = {},
    top: Rgb = color,
  ): this {
    const ring = doubleArea(outline) > 0 ? [...outline] : [...outline].reverse();
    const bottom = insetOutline(ring, insetBottom);
    const upper = insetOutline(ring, insetTop);
    const at = ([x, z]: OutlinePoint, y: number): Vec3 => [x, y, z];
    for (const [a, b, c] of triangulatePolygon(ring)) {
      const [ua, ub, uc] = [ringAt(upper, a), ringAt(upper, b), ringAt(upper, c)];
      const [da, db, dc] = [ringAt(bottom, a), ringAt(bottom, b), ringAt(bottom, c)];
      this.face([at(ua, y1), at(uc, y1), at(ub, y1)], top, place);
      this.face([at(da, y0), at(db, y0), at(dc, y0)], color, place);
    }
    ring.forEach((p, i) => {
      const q = ringAt(ring, i + 1);
      const [pd, qd] = [ringAt(bottom, i), ringAt(bottom, i + 1)];
      const [pu, qu] = [ringAt(upper, i), ringAt(upper, i + 1)];
      if (y0 < waist) this.face([at(pd, y0), at(p, waist), at(q, waist), at(qd, y0)], color, place);
      this.face([at(p, waist), at(pu, y1), at(qu, y1), at(q, waist)], color, place);
    });
    return this;
  }

  /**
   * A fuselage along Z: the `section` (counter-clockwise seen from the nose) stretched to each
   * station, from tail to nose. A station of no width and no height closes the body to a point;
   * other ends are capped, unless `open` (see {@link LoftOptions}).
   */
  loft(
    section: readonly SectionPoint[],
    stations: readonly LoftStation[],
    color: Rgb,
    place: Placement = {},
    { open = false, paint }: LoftOptions = {},
  ): this {
    const ring = (st: LoftStation): Vec3[] =>
      section.map(([u, v]): Vec3 => [u * st[1], st[2] + v * (st[3] - st[2]), st[0]]);
    const sides = open ? section.length - 1 : section.length;
    stations.slice(1).forEach((sb, k) => {
      const sa = stations[k];
      if (!sa) return;
      const colorOf = (side: number): Rgb => paint?.(side, k) ?? color;
      this.#loftBand(ring(sa), ring(sb), [isPoint(sa), isPoint(sb)], sides, colorOf, place);
    });
    if (!open) this.#loftCaps(stations.map(ring), stations.map(isPoint), color, place);
    return this;
  }

  /** Caps on the ends of a loft (its first and last rings) that are not closed to a point. */
  #loftCaps(rings: Vec3[][], points: readonly boolean[], color: Rgb, place: Placement): void {
    const [first, last] = [rings[0], rings.at(-1)];
    if (first && !points[0]) this.face([...first].reverse(), color, place);
    if (last && !points.at(-1)) this.face(last, color, place);
  }

  /** The faces between two loft rings, triangles where one of them is a point. */
  #loftBand(
    a: readonly Vec3[],
    b: readonly Vec3[],
    [aPoint, bPoint]: readonly [boolean, boolean],
    sides: number,
    colorOf: (side: number) => Rgb,
    place: Placement,
  ): void {
    for (let i = 0; i < sides; i++) {
      const [a0, a1, b0, b1] = [ringAt(a, i), ringAt(a, i + 1), ringAt(b, i), ringAt(b, i + 1)];
      const color = colorOf(i);
      if (aPoint) this.face([a0, b1, b0], color, place);
      else if (bPoint) this.face([a0, a1, b1], color, place);
      else this.face([a0, a1, b1, b0], color, place);
    }
  }
}
