import type {
  EnemyBulletSpec,
  EnemyLaserSpec,
  EnemyMissileSpec,
  LaserOwner,
} from '../entities/enemy';
import { seenOnPlayfield, type PlayfieldEye } from '../entities/muzzle';
import type { ShotTarget } from '../entities/shot-target';
import { headingTo, turnTowards } from './projectile-motion';

const DEG = Math.PI / 180;

/** An enemy bullet in flight (GD-43): straight, at constant speed. */
export interface EnemyBullet {
  alive: boolean;
  x: number;
  y: number;
  heading: number;
  speed: number;
  radius: number;
  style: string;
}

/** An enemy missile in flight: it homes on the player for a while, and can be shot down. */
export interface EnemyMissile extends ShotTarget {
  alive: boolean;
  id: number;
  radius: number;
  maxHealth: number;
  heading: number;
  speed: number;
  turnRate: number;
  /** Seconds of homing left. */
  homing: number;
  style: string;
  /** Seconds since launch. */
  age: number;
}

/** A laser: a warning line first, then the beam, along its owner's heading from its emitter. */
export interface EnemyLaser {
  readonly owner: LaserOwner;
  readonly spec: EnemyLaserSpec;
  /** Seconds since it started (warning included). */
  age: number;
  /** Start and direction, updated from the owner every step. */
  x: number;
  y: number;
  heading: number;
  /** Length to the edge of the playfield. */
  length: number;
  readonly phase: 'warning' | 'firing';
}

interface LaserState {
  owner: LaserOwner;
  spec: EnemyLaserSpec;
  age: number;
  x: number;
  y: number;
  heading: number;
  length: number;
  phase: 'warning' | 'firing';
}

export interface EnemyShotsOptions {
  readonly width: number;
  readonly height: number;
  /** Shots this far outside the playfield are removed. */
  readonly cullMargin: number;
  /**
   * The camera's eye, from which lasers are seen leaving their raised emitters
   * (`LaserOwner.emitter`); straight below them when omitted.
   */
  readonly eye?: PlayfieldEye | undefined;
}

/** Length of a ray from (x, y) along `heading` to the edge of the playfield grown by `margin`. */
export function rayToEdge(
  x: number,
  y: number,
  heading: number,
  box: { readonly width: number; readonly height: number },
  margin: number,
): number {
  const [dx, dy] = [Math.sin(heading), Math.cos(heading)];
  const along = (p: number, d: number, size: number): number => {
    if (d > 1e-9) return (size + margin - p) / d;
    if (d < -1e-9) return (-margin - p) / d;
    return Infinity;
  };
  return Math.max(0, Math.min(along(x, dx, box.width), along(y, dy, box.height)));
}

/**
 * The shots of all the enemies (GD-43, GD-44): bullets, homing missiles the player can shoot
 * down, and lasers with a warning line. Pure and deterministic, stepped with a fixed `dt`.
 */
export class EnemyShots {
  /** Pools: entries with `alive` false are free for reuse. */
  readonly bullets: EnemyBullet[] = [];
  readonly missiles: EnemyMissile[] = [];
  readonly #lasers: LaserState[] = [];
  #nextMissileId = 1;

  constructor(readonly options: EnemyShotsOptions) {}

  get lasers(): readonly EnemyLaser[] {
    return this.#lasers;
  }

  fireBullet(x: number, y: number, heading: number, spec: EnemyBulletSpec): void {
    let bullet = this.bullets.find((b) => !b.alive);
    if (!bullet) {
      bullet = { alive: true, x, y, heading, speed: 0, radius: 0, style: '' };
      this.bullets.push(bullet);
    }
    Object.assign(bullet, { alive: true, x, y, heading, ...spec });
  }

  fireMissile(x: number, y: number, heading: number, spec: EnemyMissileSpec): void {
    let missile = this.missiles.find((m) => !m.alive);
    if (!missile) {
      missile = {
        alive: true,
        id: 0,
        x,
        y,
        radius: 0,
        health: 0,
        maxHealth: 0,
        heading,
        speed: 0,
        turnRate: 0,
        homing: 0,
        style: '',
        age: 0,
      };
      this.missiles.push(missile);
    }
    Object.assign(missile, {
      alive: true,
      id: this.#nextMissileId++,
      x,
      y,
      heading,
      radius: spec.radius,
      health: spec.health,
      maxHealth: spec.health,
      speed: spec.speed,
      turnRate: spec.turnRateDeg * DEG,
      homing: spec.homingSeconds,
      style: spec.style,
      age: 0,
    });
  }

  fireLaser(owner: LaserOwner, spec: EnemyLaserSpec): void {
    this.#lasers.push({ owner, spec, age: 0, x: 0, y: 0, heading: 0, length: 0, phase: 'warning' });
    this.#aim(this.#lasers.at(-1));
  }

  /** Number of bullets and missiles in flight, and lasers shown. */
  get count(): number {
    const alive = (list: readonly { alive: boolean }[]): number =>
      list.reduce((n, s) => n + (s.alive ? 1 : 0), 0);
    return alive(this.bullets) + alive(this.missiles) + this.#lasers.length;
  }

  /** Removes every shot. */
  clear(): void {
    for (const shot of [...this.bullets, ...this.missiles]) shot.alive = false;
    this.#lasers.length = 0;
  }

  /** Moves the shots by `dt`; missiles home on (playerX, playerY). */
  step(dt: number, playerX: number, playerY: number): void {
    for (const b of this.bullets) {
      if (!b.alive) continue;
      b.x += Math.sin(b.heading) * b.speed * dt;
      b.y += Math.cos(b.heading) * b.speed * dt;
      if (this.#isOut(b.x, b.y)) b.alive = false;
    }
    for (const m of this.missiles) {
      if (m.alive) this.#moveMissile(m, dt, playerX, playerY);
    }
    for (let i = this.#lasers.length - 1; i >= 0; i--) {
      const laser = this.#lasers[i];
      if (laser && !this.#stepLaser(laser, dt)) this.#lasers.splice(i, 1);
    }
  }

  #moveMissile(m: EnemyMissile, dt: number, playerX: number, playerY: number): void {
    if (m.health <= 0) {
      m.alive = false;
      return;
    }
    if (m.homing > 0) {
      m.heading = turnTowards(m.heading, headingTo(m.x, m.y, playerX, playerY), m.turnRate * dt);
      m.homing -= dt;
    }
    m.x += Math.sin(m.heading) * m.speed * dt;
    m.y += Math.cos(m.heading) * m.speed * dt;
    m.age += dt;
    if (this.#isOut(m.x, m.y)) m.alive = false;
  }

  /** Advances a laser; returns false once it is over (or its owner is gone). */
  #stepLaser(laser: LaserState, dt: number): boolean {
    laser.age += dt;
    const { warningSeconds, firingSeconds } = laser.spec;
    const owner = laser.owner;
    if (owner.gone || owner.health <= 0 || laser.age >= warningSeconds + firingSeconds) {
      return false;
    }
    laser.phase = laser.age < warningSeconds ? 'warning' : 'firing';
    this.#aim(laser);
    return true;
  }

  #aim(laser: LaserState | undefined): void {
    if (!laser) return;
    const { x: ex, y: ey, height = 0 } = laser.owner.emitter;
    const { x, y } = seenOnPlayfield(this.options.eye, { x: ex, y: ey, height });
    laser.x = x;
    laser.y = y;
    laser.heading = laser.owner.heading;
    laser.length = rayToEdge(x, y, laser.heading, this.options, this.options.cullMargin);
  }

  #isOut(x: number, y: number): boolean {
    const { width, height, cullMargin: m } = this.options;
    return x < -m || x > width + m || y < -m || y > height + m;
  }
}
