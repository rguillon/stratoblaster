/** Variants of the industrial complexes and city buildings assembled from parts (review). */
export const INDUSTRIAL_VARIANTS = 8;
export const CITY_VARIANTS = 8;
/**
 * Families of buildings assembled from parts, with the half side of the square their models fit
 * in. The large ones fill the blocks of the industrial zone and the city centre (review).
 */
export const PART_FAMILIES = {
  'industrial-complex': 12,
  'industrial-works': 18,
  'industrial-plant': 30,
  'city-building': 9,
  'city-tower': 14,
  'city-block': 24,
} as const;
export type PartFamily = keyof typeof PART_FAMILIES;
/** Id of variant `n` (1-based) of a building assembled from parts. */
export const variantId = (kind: PartFamily, n: number): string => `${kind}-${String(n)}`;
