import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { GlowLayer } from '@babylonjs/core/Layers/glowLayer';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { GameDefinition } from '../core/content/game-definition';
import type { Weather } from '../core/scenery/atmosphere';
import type { GamePlaySky } from './game-play-state';
import { levelLength, type SceneryLevel } from '../core/scenery/scenery-level';
import { ScrollTrack } from '../core/scenery/scroll-track';
import type { GameView } from '../render/game-view';
import {
  applyShowcaseEnvironment,
  updateSkyEnvironment,
} from '../render/environment/showcase-environment.visual';
import type { AtmosphereOptions } from '../render/scenery/atmosphere-of';
import { NodeAdopter } from '../render/node-adopter';
import { OutlineLayer, type OutlineLook } from '../render/outline';
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
  /** The level's look (phase 10: its shot style, P10-R07). */
  readonly look: SceneryLook;
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
  /** Phase 14 (P14-R03, R04): rim glows round the playfield meshes that ask for one. */
  readonly outline?: OutlineLook;
}

/** Compiles the shaders of `meshes` (in parallel where WebGL can, P13-R04). */
export function compileShaders(meshes: readonly AbstractMesh[]): void {
  for (const mesh of meshes) {
    const { material } = mesh;
    if (material && mesh.subMeshes.length > 0) material.forceCompilation(mesh);
  }
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

/** Babylon's default resolution of a glow image, as a share of the screen's. */
const DEFAULT_GLOW_RATIO = 0.5;

/** Samples per pixel of the ground's glow image (antialiased: thin lights do not flicker). */
const GROUND_GLOW_SAMPLES = 4;

/**
 * The ground's glow drawn at full resolution and antialiased (reviewer, 2026-10-28: small lights
 * blinked as the ground scrolled), its blur as wide on screen as before.
 */
export function groundGlowLook(glow: SceneryLook['glow']) {
  const ratio = 1;
  return {
    ...glow,
    ratio,
    samples: GROUND_GLOW_SAMPLES,
    blurKernelSize: (glow.blurKernelSize * ratio) / DEFAULT_GLOW_RATIO,
  };
}

/**
 * Phase 10 (P10-R05): the lava blooms in the ground's glow layer with its own material, the
 * terrain drawn there too, black, so hills hide the lava under them.
 */
function glowLava(glow: GlowLayer, stage: SceneryStage): void {
  const { lava } = stage;
  if (!lava) return;
  glow.addIncludedOnlyMesh(lava);
  glow.referenceMeshToUseItsOwnMaterial(lava);
}

/**
 * The ground's glow (reviewer, 2026-10-28): the lights, and the props, cars and terrain, drawn
 * black there, so a light behind a building or a hill does not glow through it.
 */
function glowGround(glow: GlowLayer, stage: SceneryStage): void {
  for (const mesh of [...stage.glowingMeshes, ...stage.glowOccluders]) {
    glow.addIncludedOnlyMesh(mesh);
  }
  stage.watchTerrain((mesh) => {
    glow.addIncludedOnlyMesh(mesh);
  });
  glowLava(glow, stage);
}

/**
 * How the level looks where the view is, for the test API (P08 … P10): its weathers, lightning,
 * aurora, light and fog, and (phase 10) whether its liquid (`sea`) is lava, how deep it is under
 * the playfield at `middle` (≤ 0: ground), the plumes drawn and the shot style.
 */
export function skyState(
  view: LevelScene,
  sea: { readonly level: number } | undefined,
  middle: number,
): GamePlaySky {
  const { stage, look } = view;
  const { aurora, groundLights, sun, fog, weather, lightning, secondWeather } = stage.atmosphere;
  const kind = (w: Weather | undefined) => (w && w.strength > 0 ? w.kind : 'none');
  return {
    weather: kind(weather),
    secondWeather: kind(secondWeather),
    weatherParticles: stage.weatherParticles,
    rainRings: stage.rainRings,
    lightning,
    flash: stage.lightningFlash,
    aurora,
    groundLights,
    sunIntensity: sun.intensity,
    fogEnd: fog.end,
    lava: stage.lava !== undefined,
    liquidDepth: sea ? sea.level - stage.field.height(0, middle) : 0,
    plumes: stage.plumes,
    shotStyle: look.shotStyle ?? 'default',
  };
}

/** The sky lighting of `stage`'s scene, as its look is now (P08-R04). */
function followSky(stage: SceneryStage, cubeSize: number): void {
  const { sky } = stage.atmosphere;
  updateSkyEnvironment(stage.scene, cubeSize, sky.stops, sky.environmentIntensity);
}

/**
 * The playfield layer of a level: what is created through it is drawn above the clouds, with
 * the playfield's glow and (phase 14) the rims meshes ask for.
 */
function playfieldLayer(scene: Scene, options: LevelSceneOptions): NodeAdopter {
  const glow = options.environment ? playfieldGlow(scene, options.glow) : undefined;
  const outline = options.outline ? new OutlineLayer(options.outline) : undefined;
  const root = new TransformNode('playfield', scene);
  // The playfield's XY plane onto the flight plane: Y along the level (+Z), -Z up (+Y).
  root.rotation.x = Math.PI / 2;
  // Shots are additive and bright enough already: only the ships' neon lights glow. Nor do soft,
  // see-through particles (vertex alpha: the blasts' fire and smoke), which the glow layer would
  // draw white, without their tints.
  return new NodeAdopter(scene, root, ABOVE_CLOUDS_GROUP, (mesh) => {
    const additive = mesh.material?.alphaMode === Constants.ALPHA_ADD;
    if (mesh instanceof Mesh && !additive && !mesh.hasVertexAlpha) glow?.addIncludedOnlyMesh(mesh);
    outline?.add(mesh);
  });
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
        glow: groundGlowLook(look.glow),
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
  if (groundGlow) glowGround(groundGlow, stage);
  if (groundGlow) groundGlow.renderingGroupId = BELOW_CLOUDS_GROUP;
  const playfield = playfieldLayer(scene, options);
  const root = playfield.root;
  return {
    scene,
    look,
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
