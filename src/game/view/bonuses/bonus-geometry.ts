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
