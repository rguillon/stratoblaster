import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import type { GameView } from '../render/game-view';
import { ENEMY_VIEWER_CONFIG as CFG } from '../config/enemy-viewer';
import { buildLevelScene, type LevelScene } from './level-scene';

/** The view of the enemies page, with a layer for everything on the playfield. */
export type EnemyViewerScene = LevelScene;

/**
 * Builds the scene of the enemies page (P05-R11): the ground of the game's first level under
 * the tilted playfield camera, and the playfield layer above it.
 */
export function buildEnemyViewerScene(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: {
    readonly environment: boolean;
    readonly glow: { intensity: number; blurKernelSize: number };
  },
): EnemyViewerScene {
  // The ground of the first playable level.
  const level = game.gameLevels[0]?.scenery;
  if (!level) throw new Error('The game has no level');
  return buildLevelScene(engine, game, {
    level,
    environment: options.environment,
    glow: options.glow,
    environmentCubeSize: CFG.environmentCubeSize,
    stage: CFG.stage,
  });
}
