import { Engine } from '@babylonjs/core/Engines/engine';
import { startApp } from './app/start-app';
import { parseDebugOptions } from './app/debug-options';
import { resolveRoute } from './app/route';
import { startShipViewer } from './app/start-ship-viewer';
import { startShotViewer } from './app/start-shot-viewer';
import { startSceneryViewer } from './app/start-scenery-viewer';
import { startEnemyViewer } from './app/start-enemy-viewer';
import { startBossViewer } from './app/start-boss-viewer';
import { ENGINE_CONFIG } from './config/engine';
import { MENU_CONFIG } from './config/menu';
import { hasWebGL2 } from './platform/webgl-support';
import { CookieStorage } from './platform/cookie-storage';
import { browserGamepads } from './input/gamepad-menu-input';
import { applyStageFit, fitStage } from './ui/stage-fit';
import { installTestApi } from './debug/test-api';
import { installEnemyViewerTestApi } from './debug/enemy-viewer-test-api';
import { installBossViewerTestApi } from './debug/boss-viewer-test-api';
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
  const debug = parseDebugOptions(window.location.search);
  const app = startApp(engine, GAME, {
    environment: true,
    doc: document,
    overlay,
    storage: new CookieStorage(document, MENU_CONFIG.cookieMaxAgeDays),
    keyboardTarget: window,
    gamepads: browserGamepads(navigator),
    yieldToBrowser: nextFrame,
    renderLoop: true,
    ...(debug ? { debug, statsParent: document.body } : {}),
  });
  if (__E2E__) {
    installTestApi(window, {
      state: () => app.menu.flow.state,
      loadingProgress: () => app.loadingProgress,
      game: () => app.game()?.state,
      send: (action) => {
        app.command(action);
      },
    });
  }
}

/** Keeps the canvas box at the game's aspect ratio, centred in the window. */
function fitCanvasStage(engine: Engine): void {
  const stage = element('stage');
  const fit = (): void => {
    const { left, top, width, height } = fitStage(innerWidth, innerHeight, GAME.screen);
    Object.assign(stage.style, {
      left: `${String(left)}px`,
      top: `${String(top)}px`,
      width: `${String(width)}px`,
      height: `${String(height)}px`,
    });
    engine.resize();
  };
  window.addEventListener('resize', fit);
  fit();
}

function startShots(engine: Engine): void {
  fitCanvasStage(engine);
  startShotViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    statsParent: document.body,
    keyboardTarget: window,
    renderLoop: true,
  });
}

function startScenery(engine: Engine): void {
  fitCanvasStage(engine);
  startSceneryViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    statsParent: document.body,
    keyboardTarget: window,
    renderLoop: true,
  });
}

function startEnemies(engine: Engine): void {
  fitCanvasStage(engine);
  const viewer = startEnemyViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    statsParent: document.body,
    keyboardTarget: window,
    renderLoop: true,
  });
  if (__E2E__) {
    installEnemyViewerTestApi(window, {
      state: () => {
        const { enemies, player } = viewer;
        return {
          enemies: enemies.enemies.map(({ model, x, y, health }) => ({ model, x, y, health })),
          bullets: enemies.shots.bullets.filter((b) => b.alive).length,
          missiles: enemies.shots.missiles.filter((m) => m.alive).length,
          lasers: enemies.shots.lasers.map((l) => l.phase),
          kills: enemies.kills,
          score: enemies.score,
          player: { x: player.x, y: player.y },
        };
      },
      frame: (dt) => {
        viewer.frame(dt);
      },
    });
  }
}

function startBosses(engine: Engine): void {
  fitCanvasStage(engine);
  const viewer = startBossViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    statsParent: document.body,
    keyboardTarget: window,
    renderLoop: true,
  });
  if (__E2E__) {
    installBossViewerTestApi(window, {
      state: () => viewer.state(),
      frame: (dt) => {
        viewer.frame(dt);
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

  const route = resolveRoute(window.location.pathname);
  if (route === 'player-ship-viewer') {
    window.addEventListener('resize', () => {
      engine.resize();
    });
    startShipViewer(engine, GAME, {
      environment: true,
      captions: { doc: document, parent: document.body },
    });
  } else if (route === 'player-shots-viewer') {
    startShots(engine);
  } else if (route === 'scenery-viewer') {
    startScenery(engine);
  } else if (route === 'enemy-viewer') {
    startEnemies(engine);
  } else if (route === 'boss-viewer') {
    startBosses(engine);
  } else {
    document.title = GAME.title;
    startGame(engine);
  }
}

boot();
