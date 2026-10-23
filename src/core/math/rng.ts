/** A source of pseudo-random numbers in [0, 1), like `Math.random`. */
export type Random = () => number;

/**
 * Seeded pseudo-random generator (mulberry32): the same seed always gives the same
 * sequence, so generated content looks the same on every run.
 */
export function createRng(seed: number): Random {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** A number in [min, max). */
export function randomIn(random: Random, [min, max]: readonly [number, number]): number {
  return min + (max - min) * random();
}

/** One of `items`, chosen uniformly. */
export function pick<T>(random: Random, items: readonly T[]): T {
  const item = items[Math.floor(random() * items.length)];
  if (item === undefined) throw new RangeError('Cannot pick from an empty list');
  return item;
}
