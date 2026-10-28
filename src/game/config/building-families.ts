/** Variants of the World 2 buildings assembled from parts (P08-R07). */
export const POLAR_VARIANTS = 8;
/** Variants of the World 3 city buildings assembled from parts (P09-R06). */
export const JUNGLE_VARIANTS = 8;
/**
 * Families of buildings assembled from parts, with the half side of the square their models fit
 * in.
 */
export const PART_FAMILIES = {
  // World 2 (P08-R07): polar city towers and blocks, and the big mining complex of 2-4.
  'polar-tower': 12,
  'polar-block': 20,
  'mining-complex': 18,
  // World 3 (P09-R06): the canopy city's towers and blocks, trees on their roofs.
  'canopy-tower': 12,
  'canopy-block': 20,
} as const;
export type PartFamily = keyof typeof PART_FAMILIES;
/** Id of variant `n` (1-based) of a building assembled from parts. */
export const variantId = (kind: PartFamily, n: number): string => `${kind}-${String(n)}`;

/**
 * One rule per variant of a family of buildings assembled from parts, each with the `weight`
 * given: a square plan of the family's half side (`frontage`), and the footprint circle around it
 * (and 1 more, for overhangs) at the largest scale.
 */
export function familyRules(
  family: PartFamily,
  count: number,
  weight: number,
  scale: readonly [number, number],
) {
  const half = PART_FAMILIES[family];
  return Array.from({ length: count }, (_, i) => ({
    id: variantId(family, i + 1),
    weight,
    // Parts may stand out by up to 1 past the square (overhanging roofs, lit doors).
    footprint: Math.ceil((half + 1) * Math.SQRT2 * scale[1] * 10) / 10,
    frontage: half,
    scale,
  }));
}
