import { damageTarget, isAlive, type ShotTarget } from '../entities/shot-target';
import type {
  BeamWeaponDefinition,
  ProjectileWeaponDefinition,
  WeaponDefinition,
} from '../entities/weapon';
import { traceBeam, type BeamSegment } from './beam';
import { advanceProjectile, type Projectile } from './projectile-motion';

const DEG = Math.PI / 180;

/** Where a projectile hit, for effects. `blastRadius` is 0 for a direct hit. */
export interface ShotImpact {
  readonly weaponId: string;
  readonly x: number;
  readonly y: number;
  readonly blastRadius: number;
  /** True when the hit did no damage, e.g. on a shielded core (a sound of its own, P12-R09). */
  readonly blocked?: boolean;
}

export interface ShotWorldOptions {
  /** The playfield spans X in [0, width] and Y in [0, height]. */
  readonly width: number;
  readonly height: number;
  /** Shots this far outside the playfield are removed. */
  readonly cullMargin: number;
}

/**
 * Player shots of one ship (P03-R01..R03): fires the selected weapon at the selected level
 * from the muzzle, moves the projectiles, applies damage to the targets and reports impacts.
 * Pure and deterministic: everything depends on the `dt` given to {@link step}.
 */
export class ShotWorld {
  /** Pool of projectiles; entries with `alive` false are free for reuse. */
  readonly projectiles: Projectile[] = [];
  targets: ShotTarget[] = [];
  /** Where shots launched from the muzzle start (the ship's nose); beams always start here. */
  muzzleX = 0;
  muzzleY = 0;
  /** Where shots launched from the centre start. */
  centerX = 0;
  centerY = 0;
  /** Beam segments of the last step (empty unless the weapon is a beam). */
  beam: readonly BeamSegment[] = [];
  /** Impacts of the last step. */
  impacts: ShotImpact[] = [];
  /** Total damage dealt since the world was created. */
  totalDamage = 0;
  /** Whether the weapon fires; shots already in flight keep flying either way. */
  firing = true;
  #weapon: WeaponDefinition;
  #level = 1;
  /** Seconds until the next volley. */
  #cooldown = 0;

  constructor(
    readonly options: ShotWorldOptions,
    weapon: WeaponDefinition,
  ) {
    this.#weapon = weapon;
  }

  get weapon(): WeaponDefinition {
    return this.#weapon;
  }

  get level(): number {
    return this.#level;
  }

  /** Selects the weapon and its level (clamped to the weapon's levels). Shots in flight stay. */
  select(weapon: WeaponDefinition, level: number): void {
    this.#weapon = weapon;
    this.#level = Math.min(Math.max(1, Math.round(level)), weapon.levels.length);
    this.#cooldown = 0;
  }

  /** Number of projectiles in flight. */
  get activeCount(): number {
    return this.projectiles.reduce((n, p) => n + (p.alive ? 1 : 0), 0);
  }

  /** Advances the simulation by `dt` seconds. */
  step(dt: number): void {
    this.impacts = [];
    for (const shot of this.projectiles) {
      if (shot.alive) this.#move(shot, dt);
    }
    const weapon = this.#weapon;
    if (!this.firing) {
      this.beam = [];
      this.#cooldown = 0;
    } else if (weapon.kind === 'projectile') {
      this.beam = [];
      this.#fire(weapon, dt);
    } else {
      this.#fireBeam(weapon, dt);
    }
  }

  #move(shot: Projectile, dt: number): void {
    advanceProjectile(shot, this.targets, dt);
    this.#collide(shot);
    if (shot.alive && this.#isOut(shot)) shot.alive = false;
  }

  #fire(weapon: ProjectileWeaponDefinition, dt: number): void {
    this.#cooldown -= dt;
    const streams = weapon.levels[this.#level - 1] ?? [];
    while (this.#cooldown <= 0) {
      // A volley due during this step has been flying for the rest of the step.
      const flown = -this.#cooldown;
      for (const stream of streams) {
        this.#move(this.#spawn(weapon, stream.offsetX, stream.angleDeg * DEG), flown);
      }
      this.#cooldown += 1 / weapon.shotsPerSecond;
    }
  }

  #spawn(weapon: ProjectileWeaponDefinition, offsetX: number, heading: number): Projectile {
    let shot = this.projectiles.find((p) => !p.alive);
    if (!shot) {
      shot = { alive: true, weapon, x: 0, y: 0, heading: 0, speed: 0, age: 0 };
      this.projectiles.push(shot);
    }
    shot.alive = true;
    shot.weapon = weapon;
    const fromCenter = weapon.launchPoint === 'center';
    shot.x = (fromCenter ? this.centerX : this.muzzleX) + offsetX;
    shot.y = fromCenter ? this.centerY : this.muzzleY;
    shot.heading = heading;
    shot.speed = weapon.launchSpeed;
    shot.age = 0;
    return shot;
  }

  #fireBeam(weapon: BeamWeaponDefinition, dt: number): void {
    const trace = traceBeam(
      weapon.levels,
      this.#level,
      this.muzzleX,
      this.muzzleY,
      this.options.height + this.options.cullMargin,
      this.targets,
    );
    this.beam = trace.segments;
    for (const hit of trace.hits) {
      const dps = weapon.levels[hit.level - 1]?.damagePerSecond ?? 0;
      this.totalDamage += damageTarget(hit.target, dps * dt);
    }
  }

  #collide(shot: Projectile): void {
    const hit = this.targets.find(
      (t) =>
        isAlive(t) &&
        (t.x - shot.x) ** 2 + (t.y - shot.y) ** 2 <= (t.radius + shot.weapon.radius) ** 2,
    );
    if (!hit) return;
    const { weapon } = shot;
    shot.alive = false;
    const dealt = this.#damage(shot, hit);
    this.totalDamage += dealt;
    this.impacts.push({
      weaponId: weapon.id,
      x: shot.x,
      y: shot.y,
      blastRadius: weapon.blastRadius,
      blocked: dealt <= 0,
    });
  }

  /** Deals the shot's damage to `hit`, or to everything in its blast. Returns the damage dealt. */
  #damage(shot: Projectile, hit: ShotTarget): number {
    const { weapon } = shot;
    if (weapon.blastRadius <= 0) return damageTarget(hit, weapon.damage);
    let dealt = 0;
    for (const target of this.targets) {
      const reach = weapon.blastRadius + target.radius;
      if (isAlive(target) && (target.x - shot.x) ** 2 + (target.y - shot.y) ** 2 <= reach ** 2) {
        dealt += damageTarget(target, weapon.damage);
      }
    }
    return dealt;
  }

  #isOut(shot: Projectile): boolean {
    const { width, height, cullMargin: m } = this.options;
    return shot.x < -m || shot.x > width + m || shot.y < -m || shot.y > height + m;
  }
}
