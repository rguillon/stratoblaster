import { randomIn, type Random } from '../../../core/math/rng';
import type { EnemyBlast } from '../../../core/systems/enemy-world';
import { ENEMY_LOOK } from '../../config/enemy-look';

const LOOK = ENEMY_LOOK.blasts;

type Rgb = readonly [number, number, number];
type Range = readonly [number, number];

/** The layers of an explosion, each drawn in one go. */
export type BlastLayer = 'smoke' | 'rings' | 'fireballs' | 'debris' | 'embers' | 'flashes';

export const BLAST_LAYERS: readonly BlastLayer[] = [
  'smoke',
  'rings',
  'fireballs',
  'debris',
  'embers',
  'flashes',
];

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  /** Negative until the particle appears. */
  age: number;
  readonly life: number;
  readonly size: number;
  /** Size at the end of its life, relative to `size`. */
  readonly growth: number;
  readonly drag: number;
  /** Debris only: time to the next ember and smoke wisp. */
  ember: number;
  wisp: number;
}

/** A disc to draw: centre, radius, and the colour it is tinted with (alpha for smoke). */
export interface BlastSpot {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
  readonly r: number;
  readonly g: number;
  readonly b: number;
  readonly a: number;
}

/** What to draw on one frame, per layer. */
export type BlastSpots = Readonly<Record<BlastLayer, readonly BlastSpot[]>>;

/** The colour at `t` (0..1) along `colors`. */
export function ramp(colors: readonly Rgb[], t: number): Rgb {
  const last = colors.length - 1;
  const at = Math.min(Math.max(t, 0), 1) * last;
  const i = Math.min(Math.floor(at), last - 1);
  const [a, b] = [colors[i] ?? [0, 0, 0], colors[i + 1] ?? [0, 0, 0]];
  const k = at - i;
  return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
}

const spot = (p: Particle, radius: number, [r, g, b]: Rgb, a = 1): BlastSpot => ({
  x: p.x,
  y: p.y,
  radius,
  r,
  g,
  b,
  a,
});

/** How each layer looks at `t` (0..1) of a particle's life. */
const LOOKS: Readonly<Record<BlastLayer, (p: Particle, t: number) => BlastSpot>> = {
  flashes: (p, t) => {
    const [r, g, b] = ramp(LOOK.heat, t * 0.6);
    const k = LOOK.flash.brightness * (1 - t);
    return spot(p, p.size * (0.6 + 0.4 * Math.sqrt(t)), [r * k, g * k, b * k]);
  },
  rings: (p, t) => {
    const fade = (1 - t) ** 2;
    const [r, g, b] = LOOK.ring.color;
    return spot(p, p.size * Math.sqrt(t), [r * fade, g * fade, b * fade]);
  },
  fireballs: (p, t) => {
    const f = LOOK.fireball;
    const alpha = f.alpha * Math.min(1, (1 - t) / (1 - f.opaque));
    return spot(p, grown(p, Math.sqrt(t)), ramp(f.colors, t), alpha);
  },
  smoke: (p, t) => {
    // Thickens fast, then thins out as it spreads.
    const alpha = LOOK.smoke.alpha * Math.min(1, t / 0.12) * (1 - t);
    return spot(p, grown(p, Math.sqrt(t)), ramp(LOOK.smoke.colors, t * 2), alpha);
  },
  debris: (p, t) => spot(p, p.size * (1 - 0.5 * t), ramp(LOOK.heat, 0.15 + 0.75 * t)),
  embers: (p, t) => spot(p, p.size * (1 - t), ramp(LOOK.heat, 0.25 + 0.75 * t)),
};

function grown(p: Particle, k: number): number {
  return p.size * (1 + (p.growth - 1) * k);
}

/**
 * Explosions where enemies and missiles were destroyed (GD-62; phase 5 review: bigger, more
 * realistic): a white flash and a shock ring, a cluster of fireballs going off one after the
 * other and cooling from white to deep red, dark smoke that lingers, and burning debris thrown
 * out in every direction, trailing embers and smoke. Bigger enemies blow up bigger.
 */
export class BlastParticles {
  #layers: Record<BlastLayer, Particle[]> = {
    smoke: [],
    rings: [],
    fireballs: [],
    debris: [],
    embers: [],
    flashes: [],
  };

  constructor(private readonly random: Random) {}

  get count(): number {
    return BLAST_LAYERS.reduce((n, layer) => n + this.#layers[layer].length, 0);
  }

  emit(blast: EnemyBlast): void {
    const scale = blast.kind === 'missile' ? LOOK.missileScale : 1;
    const radius = Math.max(blast.radius, LOOK.minRadius) * scale;
    const at = { x: blast.x, y: blast.y };
    this.#add('flashes', { ...at, size: radius * LOOK.flash.size, life: LOOK.flash.life });
    this.#add('rings', { ...at, size: radius * LOOK.ring.size, life: LOOK.ring.life });
    const f = LOOK.fireball;
    const fireballs = this.#count(radius * f.perRadius, f.count, scale);
    for (let i = 0; i < fireballs; i++) {
      // The first one at the centre, at once; the others around it, later.
      const k = i === 0 ? 0 : 1;
      const [dx, dy] = this.#direction(this.random() * radius * f.spread * k);
      const fire = {
        x: blast.x + dx,
        y: blast.y + dy,
        delay: this.random() * f.delay * k,
        speed: f.drift,
        dir: [dx, dy] as const,
      };
      this.#fireball(fire, radius);
    }
    const d = LOOK.debris;
    const pieces = this.#count(radius * d.perRadius, [d.min, d.max], scale);
    const fling = 0.5 + radius / 40;
    for (let i = 0; i < pieces; i++) {
      this.#fling('debris', at, d, fling, LOOK.debris.drag);
    }
    const e = LOOK.embers;
    const embers = this.#count(radius, e.count, scale);
    for (let i = 0; i < embers; i++) this.#fling('embers', at, e, fling, e.drag);
  }

  /** Ages everything by `dt`, drops what is over, and returns where to draw. */
  step(dt: number): BlastSpots {
    this.#burn(dt);
    const out = {} as Record<BlastLayer, BlastSpot[]>;
    for (const layer of BLAST_LAYERS) {
      const spots: BlastSpot[] = [];
      this.#layers[layer] = this.#layers[layer].filter((p) => {
        p.age += dt;
        return p.age < p.life;
      });
      for (const p of this.#layers[layer]) {
        if (p.age < 0) continue;
        const slow = Math.exp(-p.drag * dt);
        p.vx *= slow;
        p.vy *= slow;
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        spots.push(LOOKS[layer](p, p.age / p.life));
      }
      out[layer] = spots;
    }
    return out;
  }

  /** Burning debris drops embers and smoke wisps along its way while it is hot. */
  #burn(dt: number): void {
    const d = LOOK.debris;
    for (const p of this.#layers.debris) {
      if (p.age < 0 || p.age / p.life > 0.7) continue;
      p.ember -= dt;
      p.wisp -= dt;
      const at = { x: p.x, y: p.y };
      if (p.ember <= 0) {
        p.ember += d.emberEvery;
        this.#fling('embers', at, { ...LOOK.embers, speed: [5, 30] }, 1, LOOK.embers.drag);
      }
      if (p.wisp <= 0) {
        p.wisp += d.smokeEvery;
        const size = randomIn(this.random, d.smokeSize);
        const life = randomIn(this.random, LOOK.smoke.life) * 0.6;
        this.#add('smoke', { ...at, size, life, growth: LOOK.smoke.growth });
      }
    }
  }

  #fireball(
    fire: { x: number; y: number; delay: number; speed: number; dir: readonly [number, number] },
    radius: number,
  ): void {
    const f = LOOK.fireball;
    const s = LOOK.smoke;
    const len = Math.hypot(...fire.dir) || 1;
    const [vx, vy] = [(fire.dir[0] / len) * fire.speed, (fire.dir[1] / len) * fire.speed];
    const size = radius * randomIn(this.random, f.size);
    const life = randomIn(this.random, f.life);
    this.#add('fireballs', { ...fire, vx, vy, size, life, growth: f.growth });
    // The smoke it leaves, a little behind it.
    this.#add('smoke', {
      ...fire,
      vx: (vx * s.drift) / f.drift,
      vy: (vy * s.drift) / f.drift,
      delay: fire.delay + life * 0.35,
      size: radius * randomIn(this.random, s.size),
      life: randomIn(this.random, s.life),
      growth: s.growth,
    });
  }

  #fling(
    layer: BlastLayer,
    at: { x: number; y: number },
    look: { speed: Range; size: Range; life: Range },
    fling: number,
    drag: number,
  ): void {
    const [vx, vy] = this.#direction(randomIn(this.random, look.speed) * fling);
    this.#add(layer, {
      ...at,
      vx,
      vy,
      size: randomIn(this.random, look.size),
      life: randomIn(this.random, look.life),
      drag,
      ember: this.random() * LOOK.debris.emberEvery,
      wisp: this.random() * LOOK.debris.smokeEvery,
    });
  }

  #add(
    layer: BlastLayer,
    p: { x: number; y: number; size: number; life: number } & Partial<Particle> & {
        delay?: number;
      },
  ): void {
    const list = this.#layers[layer];
    if (list.length >= LOOK.cap) return;
    list.push({
      vx: 0,
      vy: 0,
      growth: 1,
      drag: 0,
      ember: 0,
      wisp: 0,
      ...p,
      age: -(p.delay ?? 0),
    });
  }

  /** A vector `length` long in a random direction. */
  #direction(length: number): [number, number] {
    const angle = this.random() * 2 * Math.PI;
    return [Math.sin(angle) * length, Math.cos(angle) * length];
  }

  #count(n: number, [min, max]: Range, scale: number): number {
    return Math.max(1, Math.round(Math.min(max, Math.max(min, n)) * scale));
  }
}
