import { randomIn, type Random } from '../../../core/math/rng';
import type { BeamSegment } from '../../../core/systems/beam';

type Range = readonly [number, number];

export interface LaserParticleOptions {
  readonly count: number;
  readonly speed: Range;
  readonly radius: Range;
  /** Sideways spread, as a fraction of the local beam width. */
  readonly spread: number;
}

interface Particle {
  /** Distance travelled from the start of the beam. */
  distance: number;
  readonly speed: number;
  readonly radius: number;
  /** Sideways position in [-1, 1]. */
  readonly lateral: number;
}

/** A particle to draw, in logical pixels. */
export interface ParticleSpot {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
}

/**
 * Particles flowing up along a beam (P03-R02). Each particle runs from the start of the beam to
 * its end, then starts again from the start, so the flow follows the beam as it gets shorter
 * or longer.
 */
export class LaserParticles {
  readonly #particles: Particle[];

  constructor(
    private readonly options: LaserParticleOptions,
    random: Random,
    initialLength: number,
  ) {
    this.#particles = Array.from({ length: options.count }, () => ({
      distance: random() * initialLength,
      speed: randomIn(random, options.speed),
      radius: randomIn(random, options.radius),
      lateral: randomIn(random, [-1, 1]),
    }));
  }

  /** Moves the particles along `segments` (bottom first) and returns where to draw them. */
  step(segments: readonly BeamSegment[], dt: number): ParticleSpot[] {
    const first = segments[0];
    const last = segments[segments.length - 1];
    if (!first || !last) return [];
    const length = last.y1 - first.y0;
    if (!(length > 0)) return [];
    return this.#particles.map((p) => {
      p.distance = (p.distance + p.speed * dt) % length;
      const y = first.y0 + p.distance;
      const segment = segments.find((s) => y <= s.y1) ?? last;
      const x = segment.x + (p.lateral * segment.width * this.options.spread) / 2;
      return { x, y, radius: p.radius };
    });
  }
}
