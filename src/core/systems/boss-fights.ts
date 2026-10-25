import type { Boss } from '../entities/boss';
import type { EnemySpawnArea } from '../entities/enemy';
import type { ScrollTrack } from '../scenery/scroll-track';

/** The two bosses of a level (GD-41): one around its middle, one at its end. */
export type BossRank = 'mini' | 'final';

/** A boss of a level (P07-R06): its kind, its rank, and how far into the level it comes. */
export interface LevelBoss {
  /** Id of a {@link BossKindDefinition}. */
  readonly kind: string;
  readonly rank: BossRank;
  /** Level progress (world units, `ScrollTrack.progress`) where it arrives. */
  readonly at: number;
}

/** A kind of boss a game offers (P07-R05). */
export interface BossKindDefinition {
  /** Stable identifier. */
  readonly id: string;
  readonly name: string;
  /** Creates the boss just above the playfield. */
  spawn(area: EnemySpawnArea): Boss;
}

/** How fights go (engine timings, given by the game). */
export interface BossFightRules {
  /** Seconds the ground takes to change to the fight's speed, and back (P07-R03). */
  readonly speedEaseSeconds: number;
  /** Seconds the health bar takes to fill up when a boss arrives (P07-R02). */
  readonly barFillSeconds: number;
}

/** What the boss health bar shows (P07-R02). */
export interface BossBar {
  readonly name: string;
  readonly rank: BossRank;
  /** Share of the bar filled, 0..1: the health left over the full health, as it fills up. */
  readonly share: number;
  readonly health: number;
  readonly fullHealth: number;
  /** Where each destroyable part's share ends along the bar, 0..1 from the left. */
  readonly notches: readonly number[];
}

/** Throws a descriptive error for a level boss of an unknown kind. */
export function validateLevelBosses(
  bosses: readonly LevelBoss[],
  kindIds: readonly string[],
): void {
  for (const boss of bosses) {
    if (!kindIds.includes(boss.kind)) throw new Error(`Unknown boss kind "${boss.kind}"`);
    if (!(boss.at >= 0)) throw new Error(`Boss "${boss.kind}": bad distance`);
  }
}

/** A boss being fought. */
interface Fight {
  readonly boss: Boss;
  readonly level: LevelBoss;
  /** Seconds since it arrived. */
  age: number;
}

/** Slack on distances (seeking to a boss's distance in seconds may round). */
const SLACK = 1e-6;

/** What {@link BossFights} needs from the level it runs in. */
export interface BossFightHooks {
  /** Where bosses appear. */
  readonly area: () => EnemySpawnArea;
  /** Adds the boss to the level's enemies. */
  readonly add: (boss: Boss) => void;
}

/**
 * The boss fights of a level (P07-R03, R06): when the level gets to a boss, it comes in, the
 * track is held (the level's progress waits; the ground goes on, eased to the boss's speed),
 * and once the boss has blown up the ground eases back and the level goes on. Pure and
 * deterministic.
 */
export class BossFights {
  /** Bosses destroyed so far, in order. */
  readonly defeated: LevelBoss[] = [];
  /** The boss destroyed during the last step, if any. */
  justDefeated: LevelBoss | undefined;
  readonly #bosses: readonly LevelBoss[];
  #next = 0;
  #fight: Fight | undefined;

  constructor(
    bosses: readonly LevelBoss[],
    private readonly kinds: readonly BossKindDefinition[],
    private readonly rules: BossFightRules,
    private readonly hooks: BossFightHooks,
  ) {
    validateLevelBosses(
      bosses,
      kinds.map((k) => k.id),
    );
    this.#bosses = [...bosses].sort((a, b) => a.at - b.at);
  }

  /** The boss being fought, if any. */
  get boss(): Boss | undefined {
    return this.#fight?.boss;
  }

  get rank(): BossRank | undefined {
    return this.#fight?.level.rank;
  }

  /** Whether a boss is being fought (from its arrival to the end of its death blasts). */
  get active(): boolean {
    return this.#fight !== undefined;
  }

  /** Bosses passed so far: fought, or skipped by a seek. */
  get passed(): number {
    return this.#next;
  }

  get hasFinal(): boolean {
    return this.#bosses.some((b) => b.rank === 'final');
  }

  get finalDefeated(): boolean {
    return this.defeated.some((b) => b.rank === 'final');
  }

  /** The level's bosses, in order. */
  get bosses(): readonly LevelBoss[] {
    return this.#bosses;
  }

  /** Starts the next boss once the level has got to it; ends the fight once it is gone. */
  step(dt: number, track: ScrollTrack): void {
    this.justDefeated = undefined;
    const fight = this.#fight;
    if (fight) {
      fight.age += dt;
      if (fight.boss.gone) this.#end(fight, track);
      return;
    }
    const next = this.#bosses[this.#next];
    if (next && track.progress >= next.at - SLACK) this.#start(next, track);
  }

  /**
   * After a seek or a restart at `progress` (P06-R09, P07-R08): the boss being fought (if any)
   * is dropped, the ground goes back to its speed, and the next boss is the first one at or
   * after `progress`, or the one after the first `passed` when given.
   */
  skipTo(track: ScrollTrack, passed?: number): void {
    this.#fight = undefined;
    track.held = false;
    track.setSpeedFactor(1, 0);
    const next = this.#bosses.findIndex((b) => b.at >= track.progress - SLACK);
    this.#next = passed ?? (next < 0 ? this.#bosses.length : next);
  }

  /** What the health bar shows, while a boss is fought. */
  get bar(): BossBar | undefined {
    const fight = this.#fight;
    if (!fight) return undefined;
    const { boss } = fight;
    const full = boss.fullHealth;
    const fill = Math.min(1, fight.age / this.rules.barFillSeconds);
    let edge = 0;
    const notches = boss.parts.map((part) => (edge += part.maxHealth / full));
    return {
      name: boss.name,
      rank: fight.level.rank,
      share: (boss.remainingHealth / full) * fill,
      health: boss.remainingHealth,
      fullHealth: full,
      notches,
    };
  }

  #start(level: LevelBoss, track: ScrollTrack): void {
    const kind = this.kinds.find((k) => k.id === level.kind);
    this.#next++;
    if (!kind) return;
    const boss = kind.spawn(this.hooks.area());
    this.hooks.add(boss);
    this.#fight = { boss, level, age: 0 };
    track.held = true;
    track.setSpeedFactor(boss.groundSpeed, this.rules.speedEaseSeconds);
  }

  #end(fight: Fight, track: ScrollTrack): void {
    this.#fight = undefined;
    track.held = false;
    track.setSpeedFactor(1, this.rules.speedEaseSeconds);
    this.defeated.push(fight.level);
    this.justDefeated = fight.level;
  }
}
