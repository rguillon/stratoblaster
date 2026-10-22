/** A 2D point `[x, z]` of a planform outline (seen from above, X right, Z forward). */
export type OutlinePoint = readonly [x: number, z: number];

/** Element `i` of a closed ring (indices wrap around), e.g. the vertices of an outline. */
export function ringAt<T>(ring: readonly T[], i: number): T {
  const n = ring.length;
  const item = ring[((i % n) + n) % n];
  if (item === undefined) throw new RangeError('Empty ring');
  return item;
}
