/** Numbers taken out smallest first (a binary heap). */
export class MinHeap {
  readonly #items: number[];

  /** Starts with `sorted`, which must be in increasing order. */
  constructor(sorted: readonly number[] = []) {
    this.#items = [...sorted];
  }

  get size(): number {
    return this.#items.length;
  }

  push(value: number): void {
    const items = this.#items;
    let i = items.length;
    items.push(value);
    while (i > 0) {
      const parent = (i - 1) >> 1;
      const above = items[parent] ?? -Infinity;
      if (above <= value) break;
      items[i] = above;
      i = parent;
    }
    items[i] = value;
  }

  /** The smallest number, taken out; undefined when empty. */
  pop(): number | undefined {
    const items = this.#items;
    const top = items[0];
    const last = items.pop();
    if (last !== undefined && items.length > 0) this.#sink(last);
    return top;
  }

  /** Puts `value` at the top, then moves it down below its smaller children. */
  #sink(value: number): void {
    const items = this.#items;
    let i = 0;
    for (let child = this.#smallerChild(i); child !== undefined; child = this.#smallerChild(i)) {
      const below = items[child] ?? Infinity;
      if (below >= value) break;
      items[i] = below;
      i = child;
    }
    items[i] = value;
  }

  /** The index of the smaller child of `i`, if it has one. */
  #smallerChild(i: number): number | undefined {
    const items = this.#items;
    const [l, r] = [2 * i + 1, 2 * i + 2];
    if (l >= items.length) return undefined;
    return r < items.length && (items[r] ?? Infinity) < (items[l] ?? Infinity) ? r : l;
  }
}
