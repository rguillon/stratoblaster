import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import type { GameView } from '../render/game-view';
import { ENEMY_VIEWER_CONFIG as CFG } from '../config/enemy-viewer';
import { buildLevelScene, type LevelScene } from './level-scene';

/** The Level Zero view of the enemies page, with a layer for everything on the playfield. */
export type EnemyViewerScene = LevelScene;

/**
 * Builds the scene of the enemies page (P05-R11): the game's first scenery level under the
 * tilted playfield camera (as on `level_zero/`), and the playfield layer above it.
 */
export function buildEnemyViewerScene(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: {
    readonly environment: boolean;
    readonly glow: { intensity: number; blurKernelSize: number };
  },
): EnemyViewerScene {
  const level = game.sceneryLevels[0];
  if (!level) throw new Error('The game has no scenery level');
  return buildLevelScene(engine, game, {
    level,
    environment: options.environment,
    glow: options.glow,
    environmentCubeSize: CFG.environmentCubeSize,
    stage: CFG.stage,
  });
}
