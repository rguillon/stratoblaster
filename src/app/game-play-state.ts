import type { BossState } from '../core/entities/boss';
import type { BossRank } from '../core/systems/boss-fights';
import type { LevelPhase, LevelRun } from '../core/systems/level-run';

/** The boss being fought (P07), for the test API. */
export interface GamePlayBoss {
  readonly name: string;
  readonly rank: BossRank;
  readonly state: BossState;
  readonly stage: number;
  /** Parts not destroyed yet, out of all its parts. */
  readonly partsLeft: number;
  readonly parts: number;
  readonly health: number;
  readonly fullHealth: number;
}

/** A snapshot of a running level, for the test API. */
export interface GamePlayState {
  readonly levelId: string;
  readonly phase: LevelPhase;
  /** Seconds since the start of the level, and its whole duration. */
  readonly time: number;
  readonly duration: number;
  readonly timeScale: number;
  readonly enemies: number;
  readonly destroyed: number;
  readonly spawned: number;
  readonly wavesTriggered: number;
  readonly player: { readonly x: number; readonly y: number };
  readonly firing: boolean;
  readonly shots: number;
  /** Level of the weapon in use, and weapon bonuses falling / dropped (phase 6 review). */
  readonly weaponLevel: number;
  readonly bonuses: number;
  readonly bonusesDropped: number;
  /** The ship's health, lives left and seconds of invincibility left (GD-20, GD-22). */
  readonly health: number;
  readonly lives: number;
  readonly invincible: number;
  /** The boss being fought, if any; bosses destroyed; the ground's speed factor (P07). */
  readonly boss: GamePlayBoss | null;
  readonly bossesDefeated: number;
  readonly groundSpeed: number;
  /** Whether the mini boss's checkpoint is saved (P07-R08). */
  readonly checkpoint: boolean;
  /**
   * How the level looks where the view is (P08-R04, R05): snowflakes drawn, the aurora's and the
   * ground lights' strength, and the sun's (or moon's) light. Set by the game screen.
   */
  readonly sky?: GamePlaySky;
}

/** The look of the level where the view is, for the test API (P08). */
export interface GamePlaySky {
  /** Kind of the weather falling (`none` when there is none; P08-R05, P09-R05). */
  readonly weather: string;
  /** Kind of the second weather (phase 10: embers with ash), `none` when there is none. */
  readonly secondWeather: string;
  readonly weatherParticles: number;
  /** Strength of the rain rings on the water, and of the storm's lightning (P09-R05). */
  readonly rainRings: number;
  readonly lightning: number;
  /** How bright the lightning flash is on this frame (0..1). */
  readonly flash: number;
  readonly aurora: number;
  readonly groundLights: number;
  readonly sunIntensity: number;
  readonly fogEnd: number;
  /**
   * Phase 10: whether the level's liquid is lava, how deep it is under the middle of the
   * playfield (≤ 0: ground), the plume meshes drawn and the enemy shot style (P10-R05, R07, R08).
   */
  readonly lava: boolean;
  readonly liquidDepth: number;
  readonly plumes: number;
  readonly shotStyle: string;
}

/** The state of `run` for the test API; `maxHealth` stands for the health without a hull. */
export function levelState(run: LevelRun, timeScale: number, maxHealth: number): GamePlayState {
  const { track, enemies, shots, ship, waves, hull } = run;
  return {
    levelId: run.result.levelId,
    phase: run.phase,
    time: track.time,
    duration: track.duration,
    timeScale,
    enemies: enemies.enemies.length,
    destroyed: enemies.kills,
    spawned: enemies.spawned,
    wavesTriggered: waves.triggered,
    player: { x: ship.x, y: ship.y },
    firing: shots.firing,
    shots: shots.activeCount,
    weaponLevel: shots.level,
    ...bonusState(run),
    health: hull?.health ?? maxHealth,
    lives: hull?.lives ?? 0,
    invincible: hull?.invincible ?? 0,
    boss: bossState(run),
    bossesDefeated: run.fights.defeated.length,
    groundSpeed: track.speedFactor,
    checkpoint: run.checkpoint !== undefined,
  };
}

function bossState({ fights }: LevelRun): GamePlayBoss | null {
  const { boss, rank } = fights;
  if (!boss || !rank) return null;
  return {
    name: boss.name,
    rank,
    state: boss.state,
    stage: boss.stage,
    partsLeft: boss.parts.filter((p) => !p.destroyed).length,
    parts: boss.parts.length,
    health: boss.remainingHealth,
    fullHealth: boss.fullHealth,
  };
}

function bonusState({ bonuses }: LevelRun): { bonuses: number; bonusesDropped: number } {
  return { bonuses: bonuses?.bonuses.length ?? 0, bonusesDropped: bonuses?.dropped ?? 0 };
}
