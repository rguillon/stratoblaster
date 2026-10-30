/** `items[i]`, failing the test instead of returning `undefined` when out of range. */
export function at<T>(items: ArrayLike<T>, i: number): T {
  const item = items[i];
  if (item === undefined) throw new RangeError(`No item at index ${String(i)}`);
  return item;
}
