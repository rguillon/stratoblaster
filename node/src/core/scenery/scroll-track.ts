/** Smooth 0..1 ease of `t` in 0..1 (zero slope at both ends). */
const smooth = (t: number): number => t * t * (3 - 2 * t);

/**
 * How far a scrolling level has gone (P04-R06): the ground scrolls at `speed` world units per
 * second from distance 0 to `length`, then the level has ended and the track stops.
 *
 * Two distances are kept (P07-R03): {@link distance}, the ground flown over (what the scenery
 * shows), and {@link progress}, how far the level has got (what its waves and bosses are
 * placed by). They move together, except while the track is {@link held} (a boss fight): the
 * ground goes on, the level does not. The ground's speed is `speed` times a factor that eases
 * from one value to another ({@link setSpeedFactor}).
 */
export class ScrollTrack {
  #progress = 0;
  #distance = 0;
  #factor = 1;
  #ease: { from: number; to: number; seconds: number; done: number } | undefined;
  /** Simulated seconds per real second (e.g. 4 to fast-forward); 0 pauses. */
  timeScale = 1;
  /** While held, the ground scrolls but the level's progress stays where it is. */
  held = false;

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

  /** Seconds of the level flown at speed × 1 (its progress, in time). */
  get time(): number {
    return this.#progress / this.speed;
  }

  /** How far the level has got, from 0 to `length`. */
  get progress(): number {
    return this.#progress;
  }

  /** Ground flown over, i.e. Z of the bottom of the playfield. */
  get distance(): number {
    return this.#distance;
  }

  /** The factor on `speed` the ground scrolls at now. */
  get speedFactor(): number {
    return this.#factor;
  }

  get ended(): boolean {
    return this.#progress >= this.length;
  }

  /** Eases the ground's speed factor from where it is to `factor` over `seconds`. */
  setSpeedFactor(factor: number, seconds: number): void {
    if (!(factor >= 0)) throw new RangeError('The speed factor cannot be negative');
    if (seconds <= 0) {
      this.#factor = factor;
      this.#ease = undefined;
      return;
    }
    this.#ease = { from: this.#factor, to: factor, seconds, done: 0 };
  }

  /** Advances by `dt` real seconds (times {@link timeScale}), stopping at the end unless held. */
  step(dt: number): void {
    const seconds = Math.max(0, dt) * this.timeScale;
    this.#stepEase(seconds);
    let run = this.speed * this.#factor * seconds;
    if (!this.held) {
      run = Math.min(run, Math.max(0, this.length - this.#progress));
      this.#progress += run;
    }
    this.#distance += run;
  }

  #stepEase(seconds: number): void {
    const ease = this.#ease;
    if (!ease) return;
    ease.done = Math.min(ease.seconds, ease.done + seconds);
    const t = smooth(ease.done / ease.seconds);
    this.#factor = ease.from + (ease.to - ease.from) * t;
    if (ease.done >= ease.seconds) this.#ease = undefined;
  }

  /**
   * Jumps to `time` seconds of the level, kept within it. The ground keeps the lead it took
   * during held stretches, so the scenery does not jump back.
   */
  seek(time: number): void {
    const lead = this.#distance - this.#progress;
    this.#progress = Math.min(this.length, Math.max(0, time * this.speed));
    this.#distance = this.#progress + lead;
  }

  restart(): void {
    this.#progress = 0;
    this.#distance = 0;
    this.#factor = 1;
    this.#ease = undefined;
    this.held = false;
  }
}
