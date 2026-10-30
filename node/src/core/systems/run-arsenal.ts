import type { WeaponDefinition } from '../entities/weapon';
import type { ShotWorld } from './shot-world';

/** The weapon in use and the level of each weapon used so far, by weapon id. */
export interface WeaponLevels {
  readonly weapon: string;
  readonly levels: Readonly<Record<string, number>>;
}

/**
 * The weapons of a run (phase 6 review): the player switches between them in order, each
 * keeping its own level, and bonuses raise the one in use. Its {@link snapshot} is what a
 * checkpoint keeps (P07-R08).
 */
export class RunArsenal {
  /** The level of each weapon used so far. */
  readonly #levels = new Map<WeaponDefinition, number>();

  constructor(
    private readonly shots: ShotWorld,
    private readonly weapons: readonly WeaponDefinition[],
    private readonly startLevel: number,
  ) {}

  /** The next weapon of the list, at its own level; shots in flight keep flying. */
  switchWeapon(): void {
    const index = this.weapons.indexOf(this.shots.weapon);
    const next = this.weapons[(index + 1) % this.weapons.length] ?? this.shots.weapon;
    this.#levels.set(this.shots.weapon, this.shots.level);
    this.shots.select(next, this.#levels.get(next) ?? this.startLevel);
  }

  /** `count` levels more for the weapon in use, up to its last; the new level fires at once. */
  levelUp(count: number): void {
    if (count > 0) this.shots.select(this.shots.weapon, this.shots.level + count);
  }

  snapshot(): WeaponLevels {
    this.#levels.set(this.shots.weapon, this.shots.level);
    const levels: Record<string, number> = {};
    for (const [weapon, level] of this.#levels) levels[weapon.id] = level;
    return { weapon: this.shots.weapon.id, levels };
  }

  /** Back to the weapons of a {@link snapshot}. */
  restore(saved: WeaponLevels): void {
    this.#levels.clear();
    for (const weapon of this.weapons) {
      const level = saved.levels[weapon.id];
      if (level !== undefined) this.#levels.set(weapon, level);
    }
    const weapon = this.weapons.find((w) => w.id === saved.weapon) ?? this.shots.weapon;
    this.shots.select(weapon, this.#levels.get(weapon) ?? this.startLevel);
  }
}
