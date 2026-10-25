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
import {
  applyShowcaseEnvironment,
  updateSkyEnvironment,
} from '../render/environment/showcase-environment.visual';
import type { AtmosphereOptions } from '../render/scenery/atmosphere-of';
import { NodeAdopter } from '../render/node-adopter';
import { createPlainSceneryKit } from '../render/scenery/scenery-kit';
import { createSceneryKit } from '../render/scenery/scenery-kit.visual';
import type { SceneryLook } from '../render/scenery/scenery-look';
import {
  ABOVE_CLOUDS_GROUP,
  BELOW_CLOUDS_GROUP,
  SceneryStage,
  type SceneryStageConfig,
} from '../render/scenery/scenery-stage';

/** A level's scenery under the playfield camera, with a layer for everything on the playfield. */
export interface LevelScene {
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

/** What {@link buildLevelScene} shows and how. */
export interface LevelSceneOptions {
  readonly level: SceneryLevel;
  /** Generated textures, sky lighting, shadows and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  /** Glow of the playfield's self-lit parts (enemy neon, shots). */
  readonly glow: { readonly intensity: number; readonly blurKernelSize: number };
  readonly environmentCubeSize: number;
  readonly stage: SceneryStageConfig;
  /** Debug choices on the level's look (P08-R12). */
  readonly atmosphere?: AtmosphereOptions;
}

/** The look of `level`, or a descriptive error. */
export function sceneryLook(game: GameDefinition<GameView>, level: SceneryLevel): SceneryLook {
  const look = game.view.scenery.looks[level.id];
  if (!look) throw new Error(`No look for scenery level "${level.id}"`);
  return look;
}

/** A glow layer for the playfield's self-lit parts (enemy neon, shots), drawn above the clouds. */
function playfieldGlow(scene: Scene, look: { intensity: number; blurKernelSize: number }) {
  const glow = new GlowLayer('playfield-glow', scene, { blurKernelSize: look.blurKernelSize });
  glow.intensity = look.intensity;
  glow.renderingGroupId = ABOVE_CLOUDS_GROUP;
  return glow;
}

/** The sky lighting of `stage`'s scene, as its look is now (P08-R04). */
function followSky(stage: SceneryStage, cubeSize: number): void {
  const { sky } = stage.atmosphere;
  updateSkyEnvironment(stage.scene, cubeSize, sky.stops, sky.environmentIntensity);
}

/**
 * Builds the scene of a level (P04, P05-R11, P06-R02): its generated ground under the tilted
 * playfield camera, and the playfield layer above it where ships, enemies and shots are drawn.
 */
export function buildLevelScene(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: LevelSceneOptions,
): LevelScene {
  const { level } = options;
  const look = sceneryLook(game, level);
  const scene = new Scene(engine);
  const groundGlow = options.environment
    ? applyShowcaseEnvironment(scene, {
        cubeSize: options.environmentCubeSize,
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
    config: options.stage,
    ...(options.atmosphere ? { atmosphere: options.atmosphere } : {}),
  });
  for (const mesh of stage.glowingMeshes) groundGlow?.addIncludedOnlyMesh(mesh);
  if (groundGlow) groundGlow.renderingGroupId = BELOW_CLOUDS_GROUP;
  const glow = options.environment ? playfieldGlow(scene, options.glow) : undefined;
  const root = new TransformNode('playfield', scene);
  // The playfield's XY plane onto the flight plane: Y along the level (+Z), -Z up (+Y).
  root.rotation.x = Math.PI / 2;
  // Shots are additive and bright enough already: only the ships' neon lights glow. Nor do soft,
  // see-through particles (vertex alpha: the blasts' fire and smoke), which the glow layer would
  // draw white, without their tints.
  const playfield = new NodeAdopter(scene, root, ABOVE_CLOUDS_GROUP, (mesh) => {
    const additive = mesh.material?.alphaMode === Constants.ALPHA_ADD;
    if (mesh instanceof Mesh && !additive && !mesh.hasVertexAlpha) glow?.addIncludedOnlyMesh(mesh);
  });
  return {
    scene,
    stage,
    track: new ScrollTrack(level.scrollSpeed, levelLength(level)),
    playfield,
    update: (distance, dt) => {
      stage.update(distance, dt);
      if (options.environment) followSky(stage, options.environmentCubeSize);
      root.position = stage.playfieldPoint(0, 0, distance);
    },
  };
}
