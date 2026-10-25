import type { SceneryLevel } from '../scenery/scenery-level';
import type { LevelBoss } from '../systems/boss-fights';
import type { EnemyDifficulty } from '../systems/enemy-world';
import type { WaveScript } from '../systems/wave-runner';

/**
 * A level the player can fly (P06): its ground, its wave script and how hard its enemies are.
 * `id` is the id of its entry on the level select screen (`LevelEntry.id`).
 */
export interface GameLevel {
  readonly id: string;
  readonly scenery: SceneryLevel;
  readonly waves: WaveScript;
  readonly difficulty: EnemyDifficulty;
  /**
   * Its bosses (GD-41, P07-R06): a mini boss and a final boss. With a final boss, the level
   * ends when it is destroyed; without one, at the end of its scroll (P06-R03).
   */
  readonly bosses?: readonly LevelBoss[];
  /**
   * Seconds (at the level's ground speed) of extra ground drawn after the level's end, like
   * its last section, for a final boss fight that keeps the ground scrolling (P07-R03). Past
   * it, the terrain still goes on.
   */
  readonly runout?: number;
}

/** The level with id `id`, or undefined. */
export function findGameLevel(levels: readonly GameLevel[], id: string): GameLevel | undefined {
  return levels.find((level) => level.id === id);
}
