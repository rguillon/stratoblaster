/**
 * How far a scrolling level has gone (P04-R06): the ground scrolls at `speed` world units per
 * second from distance 0 to `length`, then the level has ended and the track stops.
 */
export class ScrollTrack {
  #time = 0;
  /** Simulated seconds per real second (e.g. 4 to fast-forward); 0 pauses. */
  timeScale = 1;

  constructor(
    readonly speed: number,
    readonly length: number,
  ) {
    if (!(speed > 0)) throw new RangeError('The scroll speed must be positive');
    if (!(length >= 0)) throw new RangeError('The level length cannot be negative');
  }

  /** Seconds the whole level takes at speed × 1. */
  get duration(): number {
    return this.length / this.speed;
  }

  /** Seconds since the start of the level. */
  get time(): number {
    return this.#time;
  }

  /** Distance flown, i.e. Z of the bottom of the playfield. */
  get distance(): number {
    return this.#time * this.speed;
  }

  get ended(): boolean {
    return this.#time >= this.duration;
  }

  /** Advances by `dt` real seconds (times {@link timeScale}), stopping at the end. */
  step(dt: number): void {
    this.seek(this.#time + Math.max(0, dt) * this.timeScale);
  }

  /** Jumps to `time` seconds, kept within the level. */
  seek(time: number): void {
    this.#time = Math.min(this.duration, Math.max(0, time));
  }

  restart(): void {
    this.#time = 0;
  }
}
