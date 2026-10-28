import { Engine } from '@babylonjs/core/Engines/engine';
import { startApp } from './app/start-app';
import { parseDebugOptions } from './app/debug-options';
import { redirectOf, resolveRoute, type AppRoute } from './app/route';
import { startShipViewer } from './app/start-ship-viewer';
import { startShotViewer } from './app/start-shot-viewer';
import { startSceneryViewer } from './app/start-scenery-viewer';
import { startEnemyViewer } from './app/start-enemy-viewer';
import { startPropViewer } from './app/start-prop-viewer';
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
import { installViewerTestApi } from './debug/viewer-test-api';
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

/**
 * Web Audio, if the browser has it (P12-R05): the context is only created during a user
 * gesture that lets audio start, so no autoplay warning is shown.
 */
function browserAudio(): { createContext?: () => AudioContext; canStart?: () => boolean } {
  if (typeof AudioContext !== 'function') return {};
  const activation = (navigator as Partial<Navigator>).userActivation;
  return {
    createContext: () => new AudioContext(),
    canStart: () => activation?.isActive ?? true,
  };
}

/** Runs `tick` every `seconds` (the music scheduler, P12-R05). */
function every(tick: () => void, seconds: number): () => void {
  const id = setInterval(tick, seconds * 1000);
  return () => {
    clearInterval(id);
  };
}

const nextFrame = (): Promise<void> =>
  new Promise((resolve) => {
    requestAnimationFrame(() => {
      resolve();
    });
  });

/** Keeps the stage and the menu overlay fitted to the window. */
function fitToWindow(engine: Engine, stage: HTMLElement, overlay: HTMLElement): void {
  const fit = (): void => {
    applyStageFit(stage, overlay, fitStage(innerWidth, innerHeight, GAME.screen), GAME.screen);
    engine.resize();
  };
  window.addEventListener('resize', fit);
  fit();
}

function startGame(engine: Engine): void {
  const overlay = element('menu');
  fitToWindow(engine, element('stage'), overlay);
  const debug = parseDebugOptions(window.location.search);
  const app = startApp(engine, GAME, {
    environment: true,
    doc: document,
    overlay,
    storage: new CookieStorage(document, MENU_CONFIG.cookieMaxAgeDays),
    keyboardTarget: window,
    gamepads: browserGamepads(navigator),
    yieldToBrowser: nextFrame,
    // e2e builds have no render loop: the tests step the app (ENG-52).
    renderLoop: !__E2E__,
    ...(debug ? { debug, statsParent: document.body } : {}),
    // P13-R03: levels load in steps, behind a loading screen.
    steppedLoading: true,
    // P13-R04: shaders compiled while a level loads; not in e2e builds (software WebGL, ENG-52).
    precompileShaders: !__E2E__,
    // P13-R03: the highlighted level is prepared in a worker, and built ahead (not in e2e builds:
    // software WebGL would build a level for every highlighted cell, ENG-52).
    backgroundLoading: true,
    prebuildLevels: !__E2E__,
    // P13-R01: the perf overlay (F3) in dev and e2e builds only (ENG-111).
    ...(import.meta.env.DEV || __E2E__ ? { perfParent: document.body } : {}),
    audio: browserAudio(),
    gestureTarget: window,
    visibility: { target: document, hidden: () => document.visibilityState === 'hidden' },
    every,
  });
  if (__E2E__) {
    installTestApi(window, {
      state: () => app.menu.flow.state,
      audio: () => app.audio.state,
      highScore: () => app.menu.highScore,
      loadingProgress: () => app.loadingProgress,
      game: () => app.game()?.state,
      send: (action) => {
        app.command(action);
      },
      bomb: () => {
        app.controls.bomb();
      },
      step: (frames, render) => {
        app.step(frames, render);
      },
      stepHz: 1 / app.clock.stepSeconds,
      perf: () => app.perf.numbers,
      readability: (share) => app.game()?.readability(share) ?? Promise.resolve(null),
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
  const viewer = startShotViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    statsParent: document.body,
    keyboardTarget: window,
    renderLoop: !__E2E__,
  });
  if (__E2E__) {
    installViewerTestApi(window, '__SHOTS_TEST__', {
      frame: (dt) => {
        viewer.frame(dt);
      },
      render: () => {
        viewer.scene.render();
      },
    });
  }
}

function startScenery(engine: Engine): void {
  fitCanvasStage(engine);
  const viewer = startSceneryViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    statsParent: document.body,
    keyboardTarget: window,
    renderLoop: !__E2E__,
  });
  if (__E2E__) {
    installViewerTestApi(window, '__SCENERY_TEST__', {
      frame: (dt) => {
        viewer.frame(dt);
      },
      render: () => {
        viewer.scene.render();
      },
    });
  }
}

function startEnemies(engine: Engine): void {
  fitCanvasStage(engine);
  const viewer = startEnemyViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    statsParent: document.body,
    keyboardTarget: window,
    renderLoop: !__E2E__,
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
      render: () => {
        viewer.activeScene.render();
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
    renderLoop: !__E2E__,
  });
  if (__E2E__) {
    installBossViewerTestApi(window, {
      state: () => viewer.state(),
      frame: (dt) => {
        viewer.frame(dt);
      },
      render: () => {
        viewer.activeScene.render();
      },
    });
  }
}

function startProps(engine: Engine): void {
  window.addEventListener('resize', () => {
    engine.resize();
  });
  const viewer = startPropViewer(engine, GAME, {
    environment: true,
    doc: document,
    panelParent: element('panel'),
    keyboardTarget: window,
    renderLoop: !__E2E__,
  });
  if (__E2E__) {
    installViewerTestApi(window, '__PROPS_TEST__', {
      frame: () => undefined,
      render: () => {
        viewer.scene.render();
      },
    });
  }
}

function boot(): void {
  const redirect = redirectOf(window.location.pathname);
  if (redirect) {
    window.location.replace(redirect + window.location.search);
    return;
  }
  const canvas = document.getElementById('game-canvas');
  if (!(canvas instanceof HTMLCanvasElement)) throw new Error('#game-canvas not found');

  if (!hasWebGL2(() => document.createElement('canvas'))) {
    showFatal(GAME.texts.unsupported);
    return;
  }

  const { e2e } = ENGINE_CONFIG;
  const antialias = __E2E__ ? e2e.antialias : true;
  const engine = new Engine(canvas, antialias, { adaptToDeviceRatio: false, stencil: true });
  const pixelRatio = Math.min(window.devicePixelRatio, ENGINE_CONFIG.maxDevicePixelRatio);
  engine.setHardwareScalingLevel(1 / (pixelRatio * (__E2E__ ? e2e.renderScale : 1)));
  engine.onContextLostObservable.add(() => {
    showFatal('The graphics context was lost. Please reload the page.');
  });

  START[resolveRoute(window.location.pathname)](engine);
}

function startPlayerShips(engine: Engine): void {
  window.addEventListener('resize', () => {
    engine.resize();
  });
  startShipViewer(engine, GAME, {
    environment: true,
    captions: { doc: document, parent: document.body },
  });
}

/** What each page starts. */
const START: Record<AppRoute, (engine: Engine) => void> = {
  game: (engine) => {
    document.title = GAME.title;
    startGame(engine);
  },
  'player-ship-viewer': startPlayerShips,
  'player-shots-viewer': startShots,
  'scenery-viewer': startScenery,
  'enemy-viewer': startEnemies,
  'boss-viewer': startBosses,
  'prop-viewer': startProps,
};

boot();
