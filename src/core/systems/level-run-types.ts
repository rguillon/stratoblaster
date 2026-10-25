import type { LogicalScreen } from '../content/game-definition';
import type { GameLevel } from '../content/game-level';
import type { EnemyKindDefinition } from '../entities/enemy';
import type { PlayfieldEye } from '../entities/muzzle';
import type { WeaponDefinition } from '../entities/weapon';
import type { BonusRules } from './bonus-world';
import type { BossFightRules, BossKindDefinition } from './boss-fights';
import type { FlightBounds, FlightInput } from './player-flight';
import type { PlayerHitKind } from './player-hits';
import type { HullEvent, HullRules } from './player-hull';
import type { WeaponLevels } from './run-arsenal';

/** Where a level stands (P06-R03); `over` once the player has lost every life (GD-20). */
export type LevelPhase = 'playing' | 'clearing' | 'complete' | 'over';

/**
 * Where a level can start again once its mini boss is destroyed (P07-R08, GD-42): the level's
 * progress just after it, the bosses passed, and the player's weapons at that moment.
 */
export interface LevelCheckpoint {
  readonly progress: number;
  readonly bossesPassed: number;
  readonly weapons: WeaponLevels;
}

/** What the "Level complete" (or "Game over") overlay shows (P06-R03). */
export interface LevelResult {
  readonly levelId: string;
  readonly destroyed: number;
  readonly spawned: number;
  /** Whether the level was completed, or the game is over (phase 6 review). */
  readonly outcome: 'complete' | 'over';
  /** When the game is over after the mini boss: where it can go on from (P07-R08). */
  readonly checkpoint?: LevelCheckpoint;
}

/** A hit that landed on the player during a step, and what it did. */
export interface LandedHit {
  readonly kind: PlayerHitKind;
  readonly x: number;
  readonly y: number;
  readonly event: HullEvent;
}

/** The player's controls for one step. */
export interface LevelControls {
  readonly move: FlightInput;
  readonly fire: boolean;
  /** Switch to the next weapon of `LevelRunOptions.weapons` (phase 6 review). */
  readonly switchWeapon?: boolean;
}

/** The player ship of a run. */
export interface RunShip {
  readonly start: { readonly x: number; readonly y: number };
  readonly maxSpeed: number;
  readonly accelerationSeconds: number;
  /** Shots leave this far above the ship's centre (its nose). */
  readonly muzzleOffset: number;
  /** Its health (GD-20); 100 when omitted. */
  readonly maxHealth?: number;
}

export interface LevelRunOptions {
  readonly screen: LogicalScreen;
  readonly level: GameLevel;
  readonly kinds: readonly EnemyKindDefinition[];
  /** The weapon and its level the ship starts with. */
  readonly weapon: WeaponDefinition;
  readonly weaponLevel: number;
  /**
   * The weapons the player can switch between, in order (`LevelControls.switchWeapon`), each
   * starting at `weaponLevel` and keeping its own level. Only `weapon` when omitted.
   */
  readonly weapons?: readonly WeaponDefinition[];
  readonly ship: RunShip;
  readonly bounds: FlightBounds;
  /** Enemies and shots this far outside the playfield are removed. */
  readonly cullMargin: number;
  /** The camera's eye, from which enemy shots are seen leaving their raised muzzles. */
  readonly eye?: PlayfieldEye;
  readonly maxEnemyAge: number;
  /** Longest wait for the last enemies once the scroll has ended (P06-R03). */
  readonly endWait: number;
  readonly seed: number;
  /**
   * Whether a point of the playfield is on screen. Only enemies (and missiles) whose centre is
   * on screen can be hit, so nothing blows up where the player cannot see it. Defaults to the
   * playfield's rectangle.
   */
  readonly inView?: (x: number, y: number) => boolean;
  /**
   * Weapon bonuses (phase 6 review): some destroyed enemies drop one, and picking it up raises
   * the weapon in use by a level. None when omitted.
   */
  readonly bonuses?: BonusRules;
  /**
   * What hurts the player, and its lives (GD-20..GD-22, phase 6 review). The player cannot be
   * hurt when omitted.
   */
  readonly hull?: HullRules;
  /** The boss kinds the level's bosses are taken from, and how fights go (P07). */
  readonly bossKinds?: readonly BossKindDefinition[];
  readonly bossRules?: BossFightRules;
  /** Starts from this checkpoint instead of the level's start (P07-R08). */
  readonly checkpoint?: LevelCheckpoint;
}
