import { randomIn, type Random } from '../../../core/math/rng';

type Range = readonly [number, number];

export interface SparkOptions {
  /** Sparks per burst. */
  readonly count: number;
  readonly speed: Range;
  /** Half-angle of the spray around straight back (down), in degrees. */
  readonly spreadDeg: number;
  readonly drag: number;
  readonly life: Range;
  readonly length: Range;
  readonly twinkle: number;
  readonly twinkleHz: Range;
}

interface Spark {
  x: number;
  y: number;
  vx: number;
  vy: number;
  age: number;
  readonly life: number;
  readonly length: number;
  readonly twinkleHz: number;
  readonly phase: number;
}

/** A spark to draw: a streak along its motion, `length` long, at `brightness` (0..1). */
export interface SparkSpot {
  readonly x: number;
  readonly y: number;
  /** Direction of motion, radians from +Y, positive to the right. */
  readonly heading: number;
  readonly length: number;
  readonly brightness: number;
}

/**
 * Bursts of metal sparks where bullets hit (P03-R01, phase 3 review): each burst throws
 * `count` sparks back from the hit, spread around straight down; they slow down with drag,
 * twinkle, and shrink to nothing over their life.
 */
export class SparkBursts {
  readonly #sparks: Spark[] = [];

  constructor(
    private readonly options: SparkOptions,
    private readonly random: Random,
  ) {}

  /** Number of sparks alive. */
  get count(): number {
    return this.#sparks.length;
  }

  /** Throws a burst of sparks from (x, y). */
  emit(x: number, y: number): void {
    const { options: o, random } = this;
    const spread = (o.spreadDeg * Math.PI) / 180;
    for (let i = 0; i < o.count; i++) {
      const heading = Math.PI + randomIn(random, [-spread, spread]);
      const speed = randomIn(random, o.speed);
      this.#sparks.push({
        x,
        y,
        vx: Math.sin(heading) * speed,
        vy: Math.cos(heading) * speed,
        age: 0,
        life: randomIn(random, o.life),
        length: randomIn(random, o.length),
        twinkleHz: randomIn(random, o.twinkleHz),
        phase: random() * 2 * Math.PI,
      });
    }
  }

  /** Moves and ages the sparks by `dt`, drops the dead ones, and returns where to draw them. */
  step(dt: number): SparkSpot[] {
    const slow = Math.exp(-this.options.drag * dt);
    const spots: SparkSpot[] = [];
    for (let i = this.#sparks.length - 1; i >= 0; i--) {
      const s = this.#sparks[i];
      if (!s) continue;
      s.age += dt;
      if (s.age >= s.life) {
        this.#sparks.splice(i, 1);
        continue;
      }
      s.vx *= slow;
      s.vy *= slow;
      s.x += s.vx * dt;
      s.y += s.vy * dt;
      const fade = 1 - s.age / s.life;
      const twinkle =
        1 -
        this.options.twinkle * (0.5 + 0.5 * Math.sin(s.phase + 2 * Math.PI * s.twinkleHz * s.age));
      spots.push({
        x: s.x,
        y: s.y,
        heading: Math.atan2(s.vx, s.vy),
        length: s.length * fade,
        brightness: fade * twinkle,
      });
    }
    return spots;
  }
}
