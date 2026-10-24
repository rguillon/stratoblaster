import { randomIn, type Random } from '../../../core/math/rng';
import type { EnemyBlast } from '../../../core/systems/enemy-world';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { flashScale } from '../shots/impact-flashes';

const LOOK = ENEMY_LOOK.blasts;

interface Fireball {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
  age: number;
}

interface Debris {
  x: number;
  y: number;
  vx: number;
  vy: number;
  age: number;
  readonly life: number;
  readonly size: number;
}

/** A disc to draw: centre and radius. */
export interface BlastSpot {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
}

/** What to draw on one frame. */
export interface BlastSpots {
  readonly fireballs: readonly BlastSpot[];
  readonly debris: readonly BlastSpot[];
}

/**
 * Explosions where enemies and missiles were destroyed (GD-62): a fireball that swells and
 * fades, and hot debris thrown out in every direction, more for bigger enemies.
 */
export class BlastParticles {
  readonly #fireballs: Fireball[] = [];
  readonly #debris: Debris[] = [];

  constructor(private readonly random: Random) {}

  get count(): number {
    return this.#fireballs.length + this.#debris.length;
  }

  emit(blast: EnemyBlast): void {
    const scale = blast.kind === 'missile' ? LOOK.missileScale : 1;
    const radius = blast.radius * scale;
    this.#fireballs.push({
      x: blast.x,
      y: blast.y,
      radius: radius * LOOK.fireball.radiusFactor,
      age: 0,
    });
    const d = LOOK.debris;
    const count = Math.round(Math.min(d.max, Math.max(d.min, radius * d.perRadius)) * scale);
    for (let i = 0; i < count; i++) {
      const angle = this.random() * 2 * Math.PI;
      const speed = randomIn(this.random, d.speed) * (0.5 + radius / 40);
      this.#debris.push({
        x: blast.x,
        y: blast.y,
        vx: Math.sin(angle) * speed,
        vy: Math.cos(angle) * speed,
        age: 0,
        life: randomIn(this.random, d.life),
        size: randomIn(this.random, d.size),
      });
    }
  }

  /** Ages everything by `dt`, drops what is over, and returns where to draw. */
  step(dt: number): BlastSpots {
    const duration = LOOK.fireball.duration;
    const fireballs: BlastSpot[] = [];
    for (let i = this.#fireballs.length - 1; i >= 0; i--) {
      const f = this.#fireballs[i];
      if (!f) continue;
      f.age += dt;
      if (f.age >= duration) this.#fireballs.splice(i, 1);
      else fireballs.push({ x: f.x, y: f.y, radius: f.radius * flashScale(f.age, duration) });
    }
    const slow = Math.exp(-LOOK.debris.drag * dt);
    const debris: BlastSpot[] = [];
    for (let i = this.#debris.length - 1; i >= 0; i--) {
      const p = this.#debris[i];
      if (!p) continue;
      p.age += dt;
      if (p.age >= p.life) {
        this.#debris.splice(i, 1);
        continue;
      }
      p.vx *= slow;
      p.vy *= slow;
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      debris.push({ x: p.x, y: p.y, radius: p.size * (1 - p.age / p.life) });
    }
    return { fireballs, debris };
  }
}
