import type { LevelPhase, LevelRun } from '../core/systems/level-run';

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
  };
}

function bonusState({ bonuses }: LevelRun): { bonuses: number; bonusesDropped: number } {
  return { bonuses: bonuses?.bonuses.length ?? 0, bonusesDropped: bonuses?.dropped ?? 0 };
}
