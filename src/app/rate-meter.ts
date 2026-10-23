/** Measures how fast a running total grows, over a sliding time window. */
export class RateMeter {
  readonly #samples: { time: number; total: number }[] = [];
  #time = 0;

  constructor(private readonly windowSeconds: number) {}

  /** Records the running `total` after `dt` more seconds. */
  add(dt: number, total: number): void {
    this.#time += dt;
    this.#samples.push({ time: this.#time, total });
    while ((this.#samples[1]?.time ?? Infinity) <= this.#time - this.windowSeconds) {
      this.#samples.shift();
    }
  }

  /** Growth per second over the window (over less time until a full window has passed). */
  get rate(): number {
    const first = this.#samples[0];
    const last = this.#samples[this.#samples.length - 1];
    if (!first || !last || last.time <= first.time) return 0;
    return (last.total - first.total) / (last.time - first.time);
  }
}
