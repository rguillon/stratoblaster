import { Engine } from '@babylonjs/core/Engines/engine';
import { startApp } from './app/start-app';
import { resolveRoute } from './app/route';
import { startShipViewer } from './app/start-ship-viewer';
import { ENGINE_CONFIG } from './config/engine';
import { MENU_CONFIG } from './config/menu';
import { hasWebGL2 } from './platform/webgl-support';
import { CookieStorage } from './platform/cookie-storage';
import { browserGamepads } from './input/gamepad-menu-input';
import { applyStageFit, fitStage } from './ui/stage-fit';
import { installTestApi } from './debug/test-api';
import { GAME } from './game/index';

// Bootstrap only: create the engine and start the app (ENG-10).
function showFatal(message: string): void {
  const el = document.getElementById('fatal');
  if (el) {
    el.textContent = message;
    el.hidden = false;
  }
}

function element(id: string): HTMLElement {
  const el = document.getElementById(id);
  if (!el) throw new Error(`#${id} not found`);
  return el;
}

const nextFrame = (): Promise<void> =>
  new Promise((resolve) => {
    requestAnimationFrame(() => {
      resolve();
    });
  });

function startGame(engine: Engine): void {
  const stage = element('stage');
  const overlay = element('menu');
  const fit = (): void => {
    applyStageFit(stage, overlay, fitStage(innerWidth, innerHeight, GAME.screen), GAME.screen);
    engine.resize();
  };
  window.addEventListener('resize', fit);
  fit();
  const app = startApp(engine, GAME, {
    environment: true,
    doc: document,
    overlay,
    storage: new CookieStorage(document, MENU_CONFIG.cookieMaxAgeDays),
    keyboardTarget: window,
    gamepads: browserGamepads(navigator),
    yieldToBrowser: nextFrame,
    renderLoop: true,
  });
  if (__E2E__) {
    installTestApi(window, {
      state: () => app.menu.flow.state,
      loadingProgress: () => app.loadingProgress,
      send: (action) => {
        app.command(action);
      },
    });
  }
}

function boot(): void {
  const canvas = document.getElementById('game-canvas');
  if (!(canvas instanceof HTMLCanvasElement)) throw new Error('#game-canvas not found');

  if (!hasWebGL2(() => document.createElement('canvas'))) {
    showFatal(GAME.texts.unsupported);
    return;
  }

  const engine = new Engine(canvas, true, { adaptToDeviceRatio: false, stencil: true });
  engine.setHardwareScalingLevel(
    1 / Math.min(window.devicePixelRatio, ENGINE_CONFIG.maxDevicePixelRatio),
  );
  engine.onContextLostObservable.add(() => {
    showFatal('The graphics context was lost. Please reload the page.');
  });

  if (resolveRoute(window.location.pathname) === 'player-ship-viewer') {
    window.addEventListener('resize', () => {
      engine.resize();
    });
    startShipViewer(engine, GAME, {
      environment: true,
      captions: { doc: document, parent: document.body },
    });
  } else {
    document.title = GAME.title;
    startGame(engine);
  }
}

boot();
