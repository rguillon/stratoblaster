/** A 2D point `[x, z]` of a planform outline (seen from above, X right, Z forward). */
export type OutlinePoint = readonly [x: number, z: number];

/** Element `i` of a closed ring (indices wrap around), e.g. the vertices of an outline. */
export function ringAt<T>(ring: readonly T[], i: number): T {
  const n = ring.length;
  const item = ring[((i % n) + n) % n];
  if (item === undefined) throw new RangeError('Empty ring');
  return item;
}

/**
 * The outline moved inwards by `distance` (a counter-clockwise outline in (x, z)), each corner
 * along its bisector. Sharp corners move at most `maxMiter` times `distance`, so thin tips stay
 * close to where they were instead of shooting through the outline.
 */
export function insetOutline(
  outline: readonly OutlinePoint[],
  distance: number,
  maxMiter = 3,
): OutlinePoint[] {
  const normal = ([x1, z1]: OutlinePoint, [x2, z2]: OutlinePoint): OutlinePoint => {
    const length = Math.hypot(x2 - x1, z2 - z1) || 1;
    // Left of the edge: inwards for a counter-clockwise outline.
    return [-(z2 - z1) / length, (x2 - x1) / length];
  };
  return outline.map((p, i): OutlinePoint => {
    const [ax, az] = normal(ringAt(outline, i - 1), p);
    const [bx, bz] = normal(p, ringAt(outline, i + 1));
    const k = Math.min(1 / Math.max(1 + ax * bx + az * bz, 1e-6), (maxMiter * maxMiter) / 2);
    // (a + b) / (1 + a·b) is `distance` away from both edges; |a + b|² = 2 (1 + a·b).
    return [p[0] + (ax + bx) * k * distance, p[1] + (az + bz) * k * distance];
  });
}
