import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { ArcRotateCamera } from '@babylonjs/core/Cameras/arcRotateCamera';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { Color4 } from '@babylonjs/core/Maths/math.color';
import type { GameDefinition } from '../core/content/game-definition';
import type { GameView, ModelFactory } from '../render/game-view';
import { ModelShowcase } from '../render/model-showcase';
import { countTriangles } from '../render/mesh-stats';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import { renderCaptionRow } from '../ui/caption-row';
import { shipCaption } from '../ui/ship-caption';
import { SHIP_VIEWER_CONFIG as CFG } from '../config/ship-viewer';

/** Options of {@link startShipViewer}. */
export interface ShipViewerOptions {
  /** Procedural image-based lighting and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  /** Where to show each ship's name, stats and polygon count. No captions when omitted. */
  readonly captions?: {
    readonly doc: Pick<Document, 'createElement'>;
    readonly parent: HTMLElement;
  };
  /** Seconds elapsed since the previous frame. Defaults to the engine's frame time. */
  readonly frameSeconds?: () => number;
}

/** Handle on a running ship viewer. */
export interface RunningShipViewer {
  readonly scene: Scene;
  readonly camera: ArcRotateCamera;
  readonly showcase: ModelShowcase;
  dispose(): void;
}

function shipModels(game: GameDefinition<GameView>): ModelFactory[] {
  return game.playerShips.ships.map(({ id }) => {
    const factory = game.view.playerShipModels[id];
    if (!factory) throw new Error(`No model for player ship "${id}"`);
    return factory;
  });
}

function createCamera(scene: Scene, rowWidth: number): ArcRotateCamera {
  const { alpha, beta, horizontalFov, framingMargin, minZoomFactor, maxZoomFactor } = CFG.camera;
  const radius = ((rowWidth / 2) * framingMargin) / Math.tan(horizontalFov / 2);
  const camera = new ArcRotateCamera('viewer-camera', alpha, beta, radius, Vector3.Zero(), scene);
  camera.fovMode = Camera.FOVMODE_HORIZONTAL_FIXED;
  camera.fov = horizontalFov;
  camera.lowerRadiusLimit = radius * minZoomFactor;
  camera.upperRadiusLimit = radius * maxZoomFactor;
  const canvas = scene.getEngine().getRenderingCanvas();
  if (canvas) camera.attachControl(true);
  return camera;
}

function addLights(scene: Scene): void {
  const { lights } = CFG;
  new HemisphericLight('viewer-ambient', Vector3.Up(), scene).intensity = lights.ambientIntensity;
  const key = new DirectionalLight('viewer-key', new Vector3(...lights.keyDirection), scene);
  key.intensity = lights.keyIntensity;
  const rim = new DirectionalLight('viewer-rim', new Vector3(...lights.rimDirection), scene);
  rim.intensity = lights.rimIntensity;
}

/** Starts the player ship viewer: every player ship of the game, side by side, rotating. */
export function startShipViewer(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: ShipViewerOptions,
): RunningShipViewer {
  const models = shipModels(game);
  const scene = new Scene(engine);
  scene.clearColor = new Color4(...CFG.clearColor);
  const showcase = new ModelShowcase(scene, models, CFG);
  const camera = createCamera(scene, showcase.width);
  addLights(scene);
  if (options.environment) applyShowcaseEnvironment(scene, { ...CFG.environment, glow: CFG.glow });

  const captions = options.captions;
  const row = captions
    ? renderCaptionRow(
        captions.doc,
        captions.parent,
        game.playerShips.ships.map(({ id }, i) => {
          const pivot = showcase.pivots[i];
          return shipCaption(game.playerShips, id, pivot && countTriangles(pivot));
        }),
        100 / CFG.camera.framingMargin,
      )
    : undefined;

  const frameSeconds = options.frameSeconds ?? (() => engine.getDeltaTime() / 1000);
  scene.onBeforeRenderObservable.add(() => {
    showcase.update(frameSeconds());
  });
  engine.runRenderLoop(() => {
    scene.render();
  });

  return {
    scene,
    camera,
    showcase,
    dispose: () => {
      engine.stopRenderLoop();
      row?.remove();
      scene.dispose();
    },
  };
}
