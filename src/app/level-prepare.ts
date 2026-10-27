import type { GameDefinition } from '../core/content/game-definition';
import { findGameLevel, type GameLevel } from '../core/content/game-level';
import { withRunout, type SceneryLevel } from '../core/scenery/scenery-level';
import { prepareLevelGround, prepareLevelRoads } from '../render/scenery/level-ground';

/** Each level's scenery with its runout, made once, so its generated ground is reused (P13-R03). */
const runouts = new WeakMap<GameLevel, SceneryLevel>();

export function sceneryWithRunout(level: GameLevel): SceneryLevel {
  let scenery = runouts.get(level);
  if (!scenery) {
    scenery = withRunout(level.scenery, level.runout ?? 0);
    runouts.set(level, scenery);
  }
  return scenery;
}

export function levelOf(game: GameDefinition, id: string): GameLevel {
  const level = findGameLevel(game.gameLevels, id);
  if (!level) throw new Error(`Level "${id}" cannot be played`);
  return level;
}

/**
 * Generates the ground of level `levelId` ahead of its {@link GamePlay} (P13-R03): its roads
 * (`roads`), then the rest.
 */
export function prepareLevel(game: GameDefinition, levelId: string, part: 'roads' | 'all'): void {
  const scenery = sceneryWithRunout(levelOf(game, levelId));
  if (part === 'roads') prepareLevelRoads(scenery);
  else prepareLevelGround(scenery);
}
