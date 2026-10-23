import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import { ENGINE_CONFIG } from '../config/engine';
import { MENU_CONFIG } from '../config/menu';
import { MENU_INPUT_CONFIG } from '../config/menu-input';
import { runLoadingTasks } from '../assets/loading-tasks';
import { KeyboardMenuInput } from '../input/keyboard-menu-input';
import { GamepadMenuInput, type GamepadSource } from '../input/gamepad-menu-input';
import { MenuInput } from '../input/menu-input';
import type { MenuCommand } from '../input/menu-action';
import type { KeyValueStorage } from '../platform/key-value-storage';
import type { GameView } from '../render/game-view';
import { MenuOverlay } from '../ui/menu-overlay';
import type { MenuDocument } from '../ui/screens/elements';
import { MenuController } from './menu-controller';
import type { MenuState } from './menu-flow';
import { prepareMenuScenes, renderMenuScenes, type MenuScenes } from './menu-scenes';

type ListenTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

/** Browser pieces the app runs on, injected so tests can use fakes. */
export interface AppOptions {
  /** Image-based lighting and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  readonly doc: MenuDocument;
  /** Element the menu overlay renders into. */
  readonly overlay: HTMLElement;
  /** Persistent storage (cookies in the browser). */
  readonly storage: KeyValueStorage;
  /** Where keyboard events are listened to. No keyboard when omitted. */
  readonly keyboardTarget?: ListenTarget;
  /** Connected gamepads. No gamepad when omitted. */
  readonly gamepads?: GamepadSource;
  /** Lets the browser paint between loading steps. */
  readonly yieldToBrowser: () => Promise<void>;
  /** Starts Babylon's render loop. Tests leave it off and call `tick` themselves. */
  readonly renderLoop: boolean;
}

/** Handle on a running app, used by main.ts, the test API and tests. */
export interface RunningApp {
  readonly clock: FixedStepClock;
  readonly menu: MenuController;
  /** Resolves when loading is over and the title screen is shown. */
  readonly loaded: Promise<void>;
  /** Every progress value the loading screen showed, in order. */
  readonly loadingProgress: readonly number[];
  /** The menu scenes, once loaded. */
  scenes(): MenuScenes | undefined;
  /** Sends a menu command, as any input device would. */
  command(command: MenuCommand): void;
  /** Runs one frame: input, menus, animations, rendering. */
  tick(dtSeconds: number): void;
  dispose(): void;
}

function createInput(options: AppOptions): { input: MenuInput; stop: () => void } {
  const keyboard = new KeyboardMenuInput(MENU_INPUT_CONFIG.keyboard, MENU_INPUT_CONFIG);
  const stop = options.keyboardTarget ? keyboard.listen(options.keyboardTarget) : () => undefined;
  const sources = [keyboard];
  const gamepad = options.gamepads && new GamepadMenuInput(options.gamepads, MENU_INPUT_CONFIG);
  return { input: new MenuInput(gamepad ? [...sources, gamepad] : sources), stop };
}

function syncScenes(scenes: MenuScenes | undefined, state: MenuState, shipIds: string[]): void {
  if (!scenes) return;
  scenes.backdrop.showScreen(state.screen);
  scenes.stage.select(Math.max(0, shipIds.indexOf(state.highlightedShipId)));
}

function loadMenuScenes(
  prepared: ReturnType<typeof prepareMenuScenes>,
  menu: MenuController,
  options: Pick<AppOptions, 'yieldToBrowser'>,
  onLoaded: (scenes: MenuScenes) => void,
): { loaded: Promise<void>; progress: readonly number[] } {
  const progress: number[] = [];
  const loaded = runLoadingTasks(
    prepared.tasks,
    (p) => {
      progress.push(p);
      menu.setProgress(p);
    },
    options.yieldToBrowser,
  ).then(() => {
    const scenes = prepared.result();
    menu.finishLoading();
    onLoaded(scenes);
  });
  return { loaded, progress };
}

function createMenu(
  game: GameDefinition<GameView>,
  options: AppOptions,
  input: MenuInput,
  onChange: (state: MenuState) => void,
): { menu: MenuController; overlay: MenuOverlay } {
  const overlay = new MenuOverlay(
    options.doc,
    options.overlay,
    (c) => {
      menu.command(c);
    },
    MENU_CONFIG,
  );
  const menu: MenuController = new MenuController(game, {
    display: overlay,
    input,
    storage: options.storage,
    transitionSeconds: MENU_CONFIG.transitionSeconds,
    cardsWidthPercent: 100 / MENU_CONFIG.shipSelect.camera.framingMargin,
    version: __APP_VERSION__,
    commit: __APP_COMMIT__,
    onChange,
  });
  return { menu, overlay };
}

/** One frame: clock, menu input and state, scene animations, rendering. */
function frameTicker(
  clock: FixedStepClock,
  menu: MenuController,
  scenes: () => MenuScenes | undefined,
): (dtSeconds: number) => void {
  return (dtSeconds) => {
    const dt = Math.min(Math.max(0, dtSeconds), MENU_CONFIG.maxFrameSeconds);
    clock.advance(dt);
    menu.tick(dt);
    const loaded = scenes();
    if (!loaded) return;
    loaded.backdrop.update(dt);
    loaded.stage.update(dt);
    renderMenuScenes(loaded, menu.flow.state.screen);
  };
}

/**
 * Wires the layers together (ENG-11): loads the menu scenes behind a loading screen, then
 * runs the menus (P01-R01..R15) in Babylon's render loop with a fixed-step clock (ENG-100).
 */
export function startApp(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: AppOptions,
): RunningApp {
  const clock = new FixedStepClock(ENGINE_CONFIG.simulationHz, ENGINE_CONFIG.maxStepsPerFrame);
  const shipIds = game.playerShips.ships.map((s) => s.id);
  const { input, stop } = createInput(options);
  let scenes: MenuScenes | undefined;
  const { menu, overlay } = createMenu(game, options, input, (state) => {
    syncScenes(scenes, state, shipIds);
  });
  const prepared = prepareMenuScenes(engine, game, options.environment);
  const loading = loadMenuScenes(prepared, menu, options, (loadedScenes) => {
    scenes = loadedScenes;
    syncScenes(scenes, menu.flow.state, shipIds);
  });

  const tick = frameTicker(clock, menu, () => scenes);
  if (options.renderLoop) {
    engine.runRenderLoop(() => {
      tick(engine.getDeltaTime() / 1000);
    });
  }

  return {
    clock,
    menu,
    loaded: loading.loaded,
    loadingProgress: loading.progress,
    scenes: () => scenes,
    command: (c) => {
      menu.command(c);
    },
    tick,
    dispose: () => {
      engine.stopRenderLoop();
      stop();
      overlay.dispose();
      scenes?.backdropScene.dispose();
      scenes?.shipScene.dispose();
    },
  };
}
