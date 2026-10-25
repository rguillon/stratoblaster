import type { SceneryLevel } from '../scenery/scenery-level';
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
}

/** The level with id `id`, or undefined. */
export function findGameLevel(levels: readonly GameLevel[], id: string): GameLevel | undefined {
  return levels.find((level) => level.id === id);
}
