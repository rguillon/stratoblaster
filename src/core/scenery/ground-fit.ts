import type { HeightField } from './height-field';

// How a prop sits on the ground (P04-R04): pure helpers of the prop placement.

/** The lowest ground under a square of half side `half` around (x, z). */
export function lowestUnder(field: HeightField, x: number, z: number, half: number): number {
  const corners = [-half, half].flatMap((dx) => [-half, half].map((dz) => [x + dx, z + dz]));
  return Math.min(field.height(x, z), ...corners.map(([cx = x, cz = z]) => field.height(cx, cz)));
}

/**
 * Lowest ground height under a footprint of radius `radius` around (`x`, `z`), or undefined
 * when the ground there is steeper than `maxSlope` or lower than `minHeight`.
 */
export function standingHeight(
  field: HeightField,
  [x, z, radius]: readonly [number, number, number],
  [maxSlope, minHeight]: readonly [number, number],
): number | undefined {
  const heights = [
    field.height(x, z),
    field.height(x + radius, z),
    field.height(x - radius, z),
    field.height(x, z + radius),
    field.height(x, z - radius),
  ];
  const low = Math.min(...heights);
  const high = Math.max(...heights);
  if (low < minHeight) return undefined;
  return high - low <= maxSlope * radius ? low : undefined;
}
