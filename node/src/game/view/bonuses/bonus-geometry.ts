import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';

type Rgb = readonly [number, number, number];
type Point = readonly [number, number];

/** Adds a flat convex polygon (XY plane, at `z`) of one colour to `geo`. */
function polygon(geo: ColoredGeometry, points: readonly Point[], z: number, color: Rgb): void {
  const base = geo.positions.length / 3;
  for (const [x, y] of points) {
    geo.positions.push(x, y, z);
    geo.colors.push(...color, 1);
  }
  for (let i = 1; i + 1 < points.length; i++) geo.indices.push(base, base + i, base + i + 1);
}

/** The corners of a hexagon of radius `r`, flat side down. */
function hexagon(r: number): Point[] {
  return Array.from({ length: 6 }, (_, i): Point => {
    const angle = (Math.PI / 3) * i;
    return [Math.cos(angle) * r, Math.sin(angle) * r];
  });
}

/** One chevron pointing up, its tip at (0, `top`), arms `thick` thick. */
function chevron(top: number, thick: number): Point[][] {
  const [w, drop] = [0.45, 0.42];
  return [
    [
      [-w, top - drop],
      [0, top],
      [0, top - thick],
      [-w, top - drop - thick],
    ],
    [
      [0, top],
      [w, top - drop],
      [w, top - drop - thick],
      [0, top - thick],
    ],
  ];
}

/**
 * The badge of a weapon bonus, radius 1 in the XY plane, facing -Z: a dark hexagon in a
 * coloured frame (inner edge at `inset`), with two chevrons pointing up in front of it.
 */
export function buildBonusBadge(colors: {
  readonly frame: Rgb;
  readonly face: Rgb;
  readonly chevrons: Rgb;
  readonly inset: number;
}): ColoredGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  const [outer, inner] = [hexagon(1), hexagon(colors.inset)];
  polygon(geo, inner, 0, colors.face);
  outer.forEach((corner, i) => {
    const next = (i + 1) % 6;
    const quad = [corner, outer[next], inner[next], inner[i]] as Point[];
    polygon(geo, quad, 0, colors.frame);
  });
  for (const top of [0.48, 0.08]) {
    for (const arm of chevron(top, 0.2)) polygon(geo, arm, -0.02, colors.chevrons);
  }
  return geo;
}

/** The corners of a regular polygon of `sides` around (`cx`, `cy`), radius `r`. */
function circle(cx: number, cy: number, r: number, sides = 14): Point[] {
  return Array.from({ length: sides }, (_, i): Point => {
    const angle = ((2 * Math.PI) / sides) * i;
    return [cx + Math.cos(angle) * r, cy + Math.sin(angle) * r];
  });
}

/** Adds a heart of size `s` (two lobes over a point, within radius `s`) at depth `z`. */
function heart(geo: ColoredGeometry, s: number, z: number, color: Rgb): void {
  const lobe = 0.36 * s;
  polygon(geo, circle(-0.34 * s, 0.24 * s, lobe), z, color);
  polygon(geo, circle(0.34 * s, 0.24 * s, lobe), z, color);
  polygon(
    geo,
    [
      [-0.68 * s, 0.16 * s],
      [0, -0.8 * s],
      [0.68 * s, 0.16 * s],
      [0, 0.3 * s],
    ],
    z,
    color,
  );
}

/**
 * The badge of a life bonus (P11-R07), radius 1 in the XY plane, facing -Z: a heart in a
 * coloured rim, a lighter heart in front of it. A heart, so it reads without colour.
 */
export function buildLifeBadge(colors: {
  readonly rim: Rgb;
  readonly heart: Rgb;
  readonly inset: number;
}): ColoredGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  heart(geo, 1, 0, colors.rim);
  heart(geo, colors.inset, -0.02, colors.heart);
  return geo;
}

/** Axis-aligned rectangle from (`x0`, `y0`) to (`x1`, `y1`). */
function rect(x0: number, y0: number, x1: number, y1: number): Point[] {
  return [
    [x0, y0],
    [x1, y0],
    [x1, y1],
    [x0, y1],
  ];
}

/** The blocky strokes of a letter B, `h` high, centred on the origin. */
function letterB(h: number): Point[][] {
  const [w, t] = [0.62 * h, 0.2 * h];
  const [left, right, top, bottom] = [-w / 2, w / 2, h / 2, -h / 2];
  return [
    rect(left, bottom, left + t, top),
    rect(left, top - t, right - t, top),
    rect(left, -t / 2, right - t, t / 2),
    rect(left, bottom, right - t, bottom + t),
    rect(right - t, t / 2, right, top - t),
    rect(right - t, bottom + t, right, -t / 2),
  ];
}

/**
 * The badge of a bomb bonus (P11-R07), radius 1 in the XY plane, facing -Z: a round shell
 * with a highlight and a letter B in front. Round and lettered, so it reads without colour.
 */
export function buildBombBadge(colors: {
  readonly shell: Rgb;
  readonly highlight: Rgb;
  readonly letter: Rgb;
}): ColoredGeometry {
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  polygon(geo, circle(0, 0, 1, 18), 0, colors.shell);
  polygon(geo, circle(-0.38, 0.4, 0.26, 10), -0.01, colors.highlight);
  for (const stroke of letterB(1)) polygon(geo, stroke, -0.02, colors.letter);
  return geo;
}
