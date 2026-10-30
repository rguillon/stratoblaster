/** Result of advancing the clock by one rendered frame. */
export interface ClockAdvance {
  /** Number of fixed simulation steps to run this frame. */
  readonly steps: number;
  /** Interpolation factor in [0, 1) between the previous and current simulation states. */
  readonly alpha: number;
}

/**
 * Fixed-timestep accumulator (ENG-100): converts variable frame times into a whole number
 * of fixed simulation steps plus an interpolation factor for rendering.
 */
export class FixedStepClock {
  /** Duration of one simulation step, in seconds. */
  readonly stepSeconds: number;
  private accumulator = 0;

  constructor(
    hz: number,
    private readonly maxStepsPerFrame: number,
  ) {
    if (hz <= 0 || maxStepsPerFrame < 1) {
      throw new RangeError('hz must be > 0 and maxStepsPerFrame >= 1');
    }
    this.stepSeconds = 1 / hz;
  }

  /** Advances by `frameSeconds` of real time. Excess time beyond the step cap is dropped. */
  advance(frameSeconds: number): ClockAdvance {
    this.accumulator += Math.max(0, frameSeconds);
    let steps = Math.floor(this.accumulator / this.stepSeconds);
    if (steps > this.maxStepsPerFrame) {
      steps = this.maxStepsPerFrame;
      this.accumulator = 0;
      return { steps, alpha: 0 };
    }
    this.accumulator -= steps * this.stepSeconds;
    return { steps, alpha: this.accumulator / this.stepSeconds };
  }
}
