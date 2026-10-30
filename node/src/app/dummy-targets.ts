import type { ShotTarget } from '../core/entities/shot-target';

export interface DummyTargetOptions {
  readonly radius: number;
  readonly maxHealth: number;
  readonly anchors: readonly { readonly x: number; readonly y: number }[];
  readonly swayAmplitude: number;
  readonly swayHz: number;
  readonly respawnSeconds: number;
}

/**
 * Targets for the shots viewer (P03-R10): they sway left and right together around their
 * anchors and come back with full health some time after being destroyed. When disabled, they
 * are all dead and stay dead.
 */
export class DummyTargets {
  readonly targets: ShotTarget[];
  /** Destroyed targets since creation. */
  kills = 0;
  #time = 0;
  #enabled = true;
  readonly #deadFor: number[];

  constructor(private readonly options: DummyTargetOptions) {
    this.targets = options.anchors.map((anchor, id) => ({
      id,
      x: anchor.x,
      y: anchor.y,
      radius: options.radius,
      health: options.maxHealth,
      maxHealth: options.maxHealth,
    }));
    this.#deadFor = this.targets.map(() => 0);
  }

  get enabled(): boolean {
    return this.#enabled;
  }

  /** Shows (full health) or removes all targets. */
  setEnabled(enabled: boolean): void {
    this.#enabled = enabled;
    for (const target of this.targets) target.health = enabled ? target.maxHealth : 0;
    this.#deadFor.fill(0);
  }

  /** Moves the targets, counts the newly destroyed ones and brings back the old ones. */
  update(dt: number): void {
    this.#time += dt;
    const { anchors, swayAmplitude, swayHz, respawnSeconds } = this.options;
    const sway = swayAmplitude * Math.sin(2 * Math.PI * swayHz * this.#time);
    this.targets.forEach((target, i) => {
      target.x = (anchors[i]?.x ?? target.x) + sway;
      if (!this.#enabled || target.health > 0) return;
      const deadFor = this.#deadFor[i] ?? 0;
      if (deadFor === 0) this.kills++;
      this.#deadFor[i] = deadFor + dt;
      if (deadFor + dt >= respawnSeconds) {
        target.health = target.maxHealth;
        this.#deadFor[i] = 0;
      }
    });
  }
}
