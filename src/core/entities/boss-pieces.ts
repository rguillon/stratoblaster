import type { Boss, BossPartSpec } from './boss';
import { BossTurret } from './boss-turret';
import type { DropSource, LaserOwner } from './enemy';
import { muzzlePoint, type Muzzle, type RaisedPoint } from './muzzle';
import type { ShotTarget } from './shot-target';

// The pieces of a boss (P07-R01): its destroyable parts and its core, as shots and weapons see
// them.

/** Something of a boss that shots hit and its weapons fire from: a part or the core. */
export interface BossPiece extends ShotTarget, Omit<LaserOwner, 'health'> {
  /** Seconds since it last took damage (for the hit flash); Infinity before. */
  readonly sinceHit: number;
  /** The turret its guns are on, if any (phase 7 review): its weapons turn it. */
  readonly turret: BossTurret | undefined;
  /**
   * Where one of its guns' muzzles is now, `muzzle` given from the boss's centre (as the boss
   * is drawn, its orbiting parts at a spin of 0, its joints at rest): it rolls with the boss,
   * turns with it, moves with the joint its piece hangs on, and with its turret when `onTurret`.
   */
  place(muzzle: Muzzle, onTurret?: boolean): RaisedPoint;
}

/** The turret of the piece `id` of `boss`, if it has one. */
function turretOf(boss: Boss, id: string): BossTurret | undefined {
  const spec = boss.stats.turrets?.[id];
  return spec && new BossTurret(spec);
}

/** Laser owners fire along their heading from one radius ahead of their centre. */
function emitterOf(piece: { x: number; y: number; radius: number; heading: number }) {
  return {
    x: piece.x + Math.sin(piece.heading) * piece.radius,
    y: piece.y + Math.cos(piece.heading) * piece.radius,
  };
}

/** A destroyable part of a {@link Boss}, at its offset from the boss's centre. */
export class BossPart implements BossPiece, DropSource {
  x = 0;
  y = 0;
  /** Lasers fired from it go this way (straight down). */
  heading = Math.PI;
  sinceHit = Infinity;
  /** Set once the boss has taken its destruction into account (its stage went up). */
  broken = false;
  readonly radius: number;
  readonly maxHealth: number;
  readonly dropChance: number;
  readonly shieldsCore: boolean;
  readonly turret: BossTurret | undefined;
  #health: number;

  constructor(
    readonly spec: BossPartSpec,
    readonly index: number,
    private readonly boss: Boss,
  ) {
    this.radius = spec.radius;
    this.maxHealth = spec.health;
    this.#health = spec.health;
    this.dropChance = spec.dropChance;
    this.shieldsCore = spec.shieldsCore;
    this.turret = turretOf(boss, spec.id);
  }

  /** Unique among the boss's pieces (the core is the boss's id). */
  get id(): number {
    return -(this.boss.id * 64 + this.index + 1);
  }

  get health(): number {
    return this.#health;
  }

  /** Damage only counts once the boss is in place (P07-R05). */
  set health(value: number) {
    if (!this.boss.vulnerable) return;
    const next = Math.max(0, value);
    if (next < this.#health) this.sinceHit = 0;
    this.#health = next;
  }

  get destroyed(): boolean {
    return this.#health <= 0;
  }

  get gone(): boolean {
    return this.boss.gone || this.destroyed;
  }

  get emitter(): { readonly x: number; readonly y: number } {
    return emitterOf(this);
  }

  place(muzzle: Muzzle, onTurret = false): RaisedPoint {
    const [x, y, height] = onTurret && this.turret ? this.turret.turned(muzzle) : muzzle;
    const moved: Muzzle = [...this.boss.joints.move(this.spec.joint, x, y), height];
    return muzzlePoint(this.boss, moved, this.spec.orbits ? this.boss.spin : 0);
  }

  /** Destroys it at once, whatever the boss is doing (its death, a debug key). */
  destroy(): void {
    this.#health = 0;
  }
}

/** The core of a {@link Boss} as its shots see it: shielded while its shielding parts stand. */
export class BossCore implements BossPiece {
  heading = Math.PI;
  sinceHit = Infinity;
  readonly radius: number;
  readonly maxHealth: number;
  readonly turret: BossTurret | undefined;

  constructor(private readonly boss: Boss) {
    this.radius = boss.stats.coreRadius;
    this.maxHealth = boss.stats.health;
    this.turret = turretOf(boss, 'core');
  }

  get id(): number {
    return this.boss.id;
  }

  get x(): number {
    return this.boss.x;
  }

  get y(): number {
    return this.boss.y;
  }

  get health(): number {
    return this.boss.coreHealth;
  }

  /** Shots that hit a shielded core (or one coming in) spark but do no damage (P07-R01). */
  set health(value: number) {
    if (!this.boss.vulnerable || this.boss.coreShielded) return;
    if (value < this.boss.coreHealth) this.sinceHit = 0;
    this.boss.hurtCore(value);
  }

  get gone(): boolean {
    return this.boss.gone || this.boss.state === 'dying';
  }

  get emitter(): { readonly x: number; readonly y: number } {
    return emitterOf(this);
  }

  place(muzzle: Muzzle, onTurret = false): RaisedPoint {
    return muzzlePoint(this.boss, onTurret && this.turret ? this.turret.turned(muzzle) : muzzle);
  }
}
