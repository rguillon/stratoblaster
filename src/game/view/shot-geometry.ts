import type { ColoredGeometry } from '../../render/geometry/gradient-shapes';

type Rgb = readonly [number, number, number];

/**
 * A disc of radius 1 in the XY plane, made of `rings` rings of `segments` sides: `colors[0]`
 * at the centre, `colors[i]` on ring `i`. Drawn with additive blending, a black outer ring
 * fades out, which gives the blob its soft edge.
 */
export function buildGlowDisc(segments: number, colors: readonly Rgb[]): ColoredGeometry {
  if (segments < 3 || colors.length < 2) throw new RangeError('Need 3 segments and 2 colours');
  const geo: ColoredGeometry = { positions: [0, 0, 0], indices: [], colors: [] };
  const [center] = colors;
  if (center) geo.colors.push(...center, 1);
  const rings = colors.length - 1;
  for (let ring = 1; ring <= rings; ring++) {
    const radius = ring / rings;
    const rgb = colors[ring] ?? [0, 0, 0];
    for (let i = 0; i < segments; i++) {
      const angle = (2 * Math.PI * i) / segments;
      geo.positions.push(Math.cos(angle) * radius, Math.sin(angle) * radius, 0);
      geo.colors.push(...rgb, 1);
    }
  }
  for (let i = 0; i < segments; i++) {
    const next = (i + 1) % segments;
    geo.indices.push(0, 1 + i, 1 + next);
  }
  for (let ring = 1; ring < rings; ring++) {
    const inner = 1 + (ring - 1) * segments;
    const outer = inner + segments;
    for (let i = 0; i < segments; i++) {
      const next = (i + 1) % segments;
      geo.indices.push(inner + i, outer + i, outer + next, inner + i, outer + next, inner + next);
    }
  }
  return geo;
}

/**
 * A streak along Y, X in [-0.5, 0.5]: across its width `colors` go from the centre line to both
 * edges (like {@link buildGlowBar}); along it, each row at Y = `at` multiplies them by `tint`.
 * With additive blending, a black row fades the streak out there.
 */
export function buildTracer(
  colors: readonly Rgb[],
  rows: readonly { readonly at: number; readonly tint: Rgb }[],
): ColoredGeometry {
  if (colors.length < 2 || rows.length < 2) throw new RangeError('Need 2 colours and 2 rows');
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  const steps = colors.length - 1;
  const columns = [...colors.keys()].reverse().concat([...colors.keys()].slice(1));
  rows.forEach(({ at, tint }, row) => {
    columns.forEach((c, col) => {
      const rgb = colors[c] ?? [0, 0, 0];
      geo.positions.push(col / (2 * steps) - 0.5, at, 0);
      geo.colors.push(rgb[0] * tint[0], rgb[1] * tint[1], rgb[2] * tint[2], 1);
      if (row > 0 && col > 0) {
        const a = (row - 1) * columns.length + col - 1;
        const b = a + columns.length;
        geo.indices.push(a, b, b + 1, a, b + 1, a + 1);
      }
    });
  });
  return geo;
}

/**
 * A bar from Y = 0 to Y = 1, X in [-0.5, 0.5], coloured across its width: `colors[0]` on the
 * centre line out to the last colour on both edges. Scaled in X and Y, it draws a beam.
 */
export function buildGlowBar(colors: readonly Rgb[]): ColoredGeometry {
  if (colors.length < 2) throw new RangeError('Need 2 colours');
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  const steps = colors.length - 1;
  // Columns from the left edge to the right edge, through the centre.
  const columns = [...colors.keys()].reverse().concat([...colors.keys()].slice(1));
  columns.forEach((c, col) => {
    const x = col / (2 * steps) - 0.5;
    const rgb = colors[c] ?? [0, 0, 0];
    geo.positions.push(x, 0, 0, x, 1, 0);
    geo.colors.push(...rgb, 1, ...rgb, 1);
    if (col > 0) {
      const a = (col - 1) * 2;
      geo.indices.push(a, a + 2, a + 3, a, a + 3, a + 1);
    }
  });
  return geo;
}
