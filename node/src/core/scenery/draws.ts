/** The item at `r` (0..1) of `items`, each taking a share of the draw as big as its weight. */
export function weighted<T extends { readonly weight: number }>(
  items: readonly T[],
  r: number,
): T | undefined {
  const total = items.reduce((sum, item) => sum + item.weight, 0);
  let left = r * total;
  for (const item of items) {
    left -= item.weight;
    if (left < 0) return item;
  }
  return items.at(-1);
}

/** The `items` whose id is in `ids` (all of them when `ids` is undefined). */
export function allowed<T extends { readonly id: string }>(
  items: readonly T[],
  ids?: readonly string[],
): T[] {
  return ids ? items.filter((item) => ids.includes(item.id)) : [...items];
}

/** A value in `range` for a draw `r` in [0, 1). */
export function between([min, max]: readonly [number, number], r: number): number {
  return min + (max - min) * r;
}
