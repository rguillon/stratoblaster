import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { GlowLayer } from '@babylonjs/core/Layers/glowLayer';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { GameDefinition } from '../core/content/game-definition';
import { levelLength, type SceneryLevel } from '../core/scenery/scenery-level';
import { ScrollTrack } from '../core/scenery/scroll-track';
import type { GameView } from '../render/game-view';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import { NodeAdopter } from '../render/node-adopter';
import { createPlainSceneryKit } from '../render/scenery/scenery-kit';
import { createSceneryKit } from '../render/scenery/scenery-kit.visual';
import type { SceneryLook } from '../render/scenery/scenery-look';
import {
  ABOVE_CLOUDS_GROUP,
  BELOW_CLOUDS_GROUP,
  SceneryStage,
} from '../render/scenery/scenery-stage';
import { ENEMY_VIEWER_CONFIG as CFG } from '../config/enemy-viewer';

/** The Level Zero view of the enemies page, with a layer for everything on the playfield. */
export interface EnemyViewerScene {
  readonly scene: Scene;
  readonly stage: SceneryStage;
  readonly track: ScrollTrack;
  /**
   * The playfield plane: X right, Y up the screen, -Z towards the camera, one unit per logical
   * pixel, origin at its bottom left (the space of `ShotFrame`). Code run through it draws there,
   * above the clouds.
   */
  readonly playfield: NodeAdopter;
  /** Moves the scenery and the playfield to `distance` along the level. */
  update(distance: number, dt: number): void;
}

function firstLevel(game: GameDefinition<GameView>): { level: SceneryLevel; look: SceneryLook } {
  const level = game.sceneryLevels[0];
  if (!level) throw new Error('The game has no scenery level');
  const look = game.view.scenery.looks[level.id];
  if (!look) throw new Error(`No look for scenery level "${level.id}"`);
  return { level, look };
}

/** A glow layer for the playfield's self-lit parts (enemy neon, shots), drawn above the clouds. */
function playfieldGlow(scene: Scene, look: { intensity: number; blurKernelSize: number }) {
  const glow = new GlowLayer('playfield-glow', scene, { blurKernelSize: look.blurKernelSize });
  glow.intensity = look.intensity;
  glow.renderingGroupId = ABOVE_CLOUDS_GROUP;
  return glow;
}

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
  const { level, look } = firstLevel(game);
  const scene = new Scene(engine);
  const groundGlow = options.environment
    ? applyShowcaseEnvironment(scene, {
        cubeSize: CFG.environmentCubeSize,
        intensity: look.sky.environmentIntensity,
        stops: look.sky.stops,
        glow: look.glow,
      })
    : undefined;
  const stage = new SceneryStage(scene, {
    screen: game.screen,
    camera: game.view.scenery.camera,
    level,
    look,
    propModels: game.view.scenery.propModels,
    kit: options.environment ? createSceneryKit : createPlainSceneryKit,
    config: CFG.stage,
  });
  for (const mesh of stage.glowingMeshes) groundGlow?.addIncludedOnlyMesh(mesh);
  if (groundGlow) groundGlow.renderingGroupId = BELOW_CLOUDS_GROUP;
  const glow = options.environment ? playfieldGlow(scene, options.glow) : undefined;
  const root = new TransformNode('playfield', scene);
  // The playfield's XY plane onto the flight plane: Y along the level (+Z), -Z up (+Y).
  root.rotation.x = Math.PI / 2;
  // Shots are additive and bright enough already: only the ships' neon lights glow.
  const playfield = new NodeAdopter(scene, root, ABOVE_CLOUDS_GROUP, (mesh) => {
    const additive = mesh.material?.alphaMode === Constants.ALPHA_ADD;
    if (mesh instanceof Mesh && !additive) glow?.addIncludedOnlyMesh(mesh);
  });
  return {
    scene,
    stage,
    track: new ScrollTrack(level.scrollSpeed, levelLength(level)),
    playfield,
    update: (distance, dt) => {
      stage.update(distance, dt);
      root.position = stage.playfieldPoint(0, 0, distance);
    },
  };
}
