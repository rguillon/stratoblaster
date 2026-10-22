import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { Color4 } from '@babylonjs/core/Maths/math.color';
import type { GameDefinition } from '../core/content/game-definition';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import { ENGINE_CONFIG } from '../config/engine';

/** Handle on a running app, used by main.ts and tests. */
export interface RunningApp {
  readonly scene: Scene;
  readonly clock: FixedStepClock;
  dispose(): void;
}

/** Wires the layers together and starts the render loop with a fixed-step simulation clock. */
export function startApp(engine: AbstractEngine, game: GameDefinition): RunningApp {
  const scene = new Scene(engine);
  scene.metadata = { gameId: game.id };
  scene.clearColor = new Color4(0.05, 0.02, 0.1, 1);
  new FreeCamera('camera', new Vector3(0, 0, -10), scene);
  const clock = new FixedStepClock(ENGINE_CONFIG.simulationHz, ENGINE_CONFIG.maxStepsPerFrame);

  engine.runRenderLoop(() => {
    clock.advance(engine.getDeltaTime() / 1000);
    scene.render();
  });

  return {
    scene,
    clock,
    dispose: () => {
      engine.stopRenderLoop();
      scene.dispose();
    },
  };
}
