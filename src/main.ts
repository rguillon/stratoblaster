import { Engine } from '@babylonjs/core/Engines/engine';
import { startApp } from './app/start-app';
import { ENGINE_CONFIG } from './config/engine';
import { hasWebGL2 } from './platform/webgl-support';
import { GAME } from './game/index';

// Bootstrap only: create the engine and start the app (ENG-10).
function showFatal(message: string): void {
  const el = document.getElementById('fatal');
  if (el) {
    el.textContent = message;
    el.hidden = false;
  }
}

function boot(): void {
  document.title = GAME.title;
  const canvas = document.getElementById('game-canvas');
  if (!(canvas instanceof HTMLCanvasElement)) throw new Error('#game-canvas not found');

  if (!hasWebGL2(() => document.createElement('canvas'))) {
    showFatal('Your browser does not support WebGL2, which this game requires.');
    return;
  }

  const engine = new Engine(canvas, true, { adaptToDeviceRatio: false, stencil: true });
  engine.setHardwareScalingLevel(
    1 / Math.min(window.devicePixelRatio, ENGINE_CONFIG.maxDevicePixelRatio),
  );
  engine.onContextLostObservable.add(() => {
    showFatal('The graphics context was lost. Please reload the page.');
  });
  window.addEventListener('resize', () => {
    engine.resize();
  });

  startApp(engine, GAME);
}

boot();
