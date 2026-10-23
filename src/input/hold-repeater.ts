/**
 * Turns held keys into repeated presses: a press is emitted at once, then again after
 * `delaySeconds`, then every `intervalSeconds` while the key stays held.
 */
export class HoldRepeater<K extends string> {
  readonly #timers = new Map<K, number>();

  constructor(
    private readonly delaySeconds: number,
    private readonly intervalSeconds: number,
  ) {
    if (!(intervalSeconds > 0) || delaySeconds < 0) {
      throw new RangeError('intervalSeconds must be > 0 and delaySeconds >= 0');
    }
  }

  /** Starts holding `key`. Returns true when this is a new press (to be emitted at once). */
  press(key: K): boolean {
    if (this.#timers.has(key)) return false;
    this.#timers.set(key, this.delaySeconds);
    return true;
  }

  release(key: K): void {
    this.#timers.delete(key);
  }

  releaseAll(): void {
    this.#timers.clear();
  }

  /** Keys currently held. */
  get held(): readonly K[] {
    return [...this.#timers.keys()];
  }

  /** Advances time and returns the repeats due, in order. */
  update(dtSeconds: number): K[] {
    const repeats: K[] = [];
    for (const [key, timer] of this.#timers) {
      let left = timer - dtSeconds;
      while (left <= 0) {
        repeats.push(key);
        left += this.intervalSeconds;
      }
      this.#timers.set(key, left);
    }
    return repeats;
  }
}
