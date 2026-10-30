import type { GradientStop } from '../environment/gradient-cube';

/** Raw vertex-coloured geometry (XYZ positions, RGBA colours, 4 per vertex). */
export interface ColoredGeometry {
  readonly positions: number[];
  readonly indices: number[];
  readonly colors: number[];
}

function pushRow(geo: ColoredGeometry, halfWidth: number, y: number, rgb: readonly number[]): void {
  geo.positions.push(-halfWidth, y, 0, halfWidth, y, 0);
  geo.colors.push(...rgb, 1, ...rgb, 1);
}

/** Joins row `r` (2 vertices) to the next row with two triangles. */
function joinRows(geo: ColoredGeometry, r: number): void {
  const a = r * 2;
  geo.indices.push(a, a + 1, a + 3, a, a + 3, a + 2);
}

/**
 * A `width × height` rectangle centred on the origin whose colour goes from the bottom to the
 * top through `stops` (`at` -1 = bottom edge, 1 = top edge). One vertex row per stop.
 */
export function buildGradientRect(
  width: number,
  height: number,
  stops: readonly GradientStop[],
): ColoredGeometry {
  if (stops.length < 2) throw new Error('A gradient rectangle needs at least 2 stops');
  const geo: ColoredGeometry = { positions: [], indices: [], colors: [] };
  const sorted = [...stops].sort((a, b) => a.at - b.at);
  sorted.forEach((stop, i) => {
    pushRow(geo, width / 2, (stop.at * height) / 2, stop.color);
    if (i > 0) joinRows(geo, i - 1);
  });
  return geo;
}
