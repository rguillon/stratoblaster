import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import { ENGINE_CONFIG } from '../config/engine';
import { MENU_CONFIG } from '../config/menu';
import { MENU_INPUT_CONFIG } from '../config/menu-input';
import { GAME_PLAY_CONFIG } from '../config/game-play';
import type { GameControls } from '../input/game-controls';
import { runLoadingTasks } from '../assets/loading-tasks';
import { KeyboardMenuInput } from '../input/keyboard-menu-input';
import { GamepadMenuInput, type GamepadSource } from '../input/gamepad-menu-input';
import { MenuInput } from '../input/menu-input';
import type { MenuCommand } from '../input/menu-action';
import type { KeyValueStorage } from '../platform/key-value-storage';
import type { GameView } from '../render/game-view';
import { MenuOverlay } from '../ui/menu-overlay';
import type { MenuDocument } from '../ui/screens/elements';
import type { GameAudio } from './game-audio';
import type { GamePlay } from './game-play';
import { GameSession, type GameDebugOptions } from './game-session';
import { MenuController } from './menu-controller';
import type { MenuState } from './menu-flow';
import { prepareMenuScenes, renderMenuScenes, type MenuScenes } from './menu-scenes';
import { createAppAudio, listenToPage, type PageOptions } from './page-audio';

type ListenTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

/** Browser pieces the app runs on, injected so tests can use fakes. */
export interface AppOptions extends PageOptions {
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
  /**
   * Starts Babylon's render loop. Unit tests leave it off and call `tick` themselves; e2e builds
   * leave it off and step the app through the test API (ENG-52).
   */
  readonly renderLoop: boolean;
  /** Debug options (P06-R09); none when omitted. */
  readonly debug?: GameDebugOptions;
  /** Where the debug FPS / polygons tile goes. */
  readonly statsParent?: HTMLElement;
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
  /** The level being played, on the game screen. */
  game(): GamePlay | undefined;
  /** The player's in-game controls. */
  readonly controls: GameControls;
  /** The game's music and sounds (P12-R05). */
  readonly audio: GameAudio;
  /** Sends a menu command, as any input device would. */
  command(command: MenuCommand): void;
  /** Runs one frame: input, menus, animations, rendering. */
  tick(dtSeconds: number): void;
  /**
   * Runs `frames` frames of one simulation step each, then renders once (unless `render` is
   * false): the e2e tests' clock (ENG-52), so they never wait on frames that software WebGL draws
   * slowly.
   */
  step(frames: number, render?: boolean): void;
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
  input: { menu: MenuInput; controls: GameControls; audio: GameAudio },
  onChange: (state: MenuState) => void,
): { menu: MenuController; overlay: MenuOverlay } {
  const { controls } = input;
  const overlay = new MenuOverlay(
    options.doc,
    options.overlay,
    (c) => {
      menu.command(c);
    },
    MENU_CONFIG,
    {
      fire: (held) => {
        controls.setTouchFire(held);
      },
      drag: (dx, dy) => {
        controls.drag(dx, dy);
      },
    },
  );
  const menu: MenuController = new MenuController(game, {
    display: overlay,
    input: input.menu,
    storage: options.storage,
    transitionSeconds: MENU_CONFIG.transitionSeconds,
    resultDelaySeconds: GAME_PLAY_CONFIG.completeDelay,
    cardsWidthPercent: 100 / MENU_CONFIG.shipSelect.camera.framingMargin,
    version: __APP_VERSION__,
    commit: __APP_COMMIT__,
    onChange,
    onFeedback: (command, feedback) => {
      input.audio.menuFeedback(command, feedback, menu.flow.state.volumes);
    },
  });
  return { menu, overlay };
}

/** One frame, split in two: the simulation, then the drawing of what it left. */
interface FrameTicker {
  /** Clock, menu input and state, then the level being played or the menu scenes' animations. */
  readonly simulate: (dtSeconds: number) => void;
  /** Renders the level being played, or the menu scenes once loaded. */
  readonly render: () => void;
}

function frameTicker(
  clock: FixedStepClock,
  menu: MenuController,
  scenes: () => MenuScenes | undefined,
  session: Pick<GameSession, 'play' | 'paused' | 'controls'>,
): FrameTicker {
  return {
    simulate: (dtSeconds) => {
      const dt = Math.min(Math.max(0, dtSeconds), MENU_CONFIG.maxFrameSeconds);
      clock.advance(dt);
      menu.tick(dt);
      const { play } = session;
      if (play) {
        // Paused (P12-R01): nothing in the level advances; its last frame is drawn again.
        if (!session.paused) play.frame(dt);
        // The gamepad in use was disconnected (P12-R03).
        if (session.controls.takeDisconnect()) menu.pause();
        return;
      }
      const loaded = scenes();
      loaded?.backdrop.update(dt);
      loaded?.stage.update(dt);
    },
    render: () => {
      const { play } = session;
      if (play) {
        play.view.scene.render();
        return;
      }
      const loaded = scenes();
      if (loaded) renderMenuScenes(loaded, menu.flow.state.screen);
    },
  };
}

/** A frame of real time (the render loop, unit tests), and whole steps (the e2e tests). */
function clockControls(
  clock: FixedStepClock,
  ticker: FrameTicker,
): Pick<RunningApp, 'tick' | 'step'> {
  return {
    tick: (dtSeconds) => {
      ticker.simulate(dtSeconds);
      ticker.render();
    },
    step: (frames, render = true) => {
      for (let i = 0; i < frames; i++) ticker.simulate(clock.stepSeconds);
      if (render) ticker.render();
    },
  };
}

/** Disposes the menu scenes, once loaded. */
function disposeScenes(scenes: MenuScenes | undefined): void {
  scenes?.backdropScene.dispose();
  scenes?.shipScene.dispose();
}

/** Runs `tick` on every frame of Babylon's render loop, with the frame time in seconds. */
function runLoop(engine: AbstractEngine, tick: (dtSeconds: number) => void): void {
  engine.runRenderLoop(() => {
    tick(engine.getDeltaTime() / 1000);
  });
}

/** With debug options (P06-R09), starts their level straight away once loading is over. */
function startDebugLevel(
  menu: MenuController,
  debug: GameDebugOptions | undefined,
  shipIds: readonly string[],
): void {
  if (debug) menu.playDirect(debug.shipId ?? shipIds[0] ?? '', debug.levelId);
}

/**
 * The game session: its levels' results go to the menus, and its scores to the high score
 * (P11-R03). `menu` is read when they come, once it exists.
 */
function createSession(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: AppOptions,
  menu: () => MenuController,
  audio: GameAudio,
): GameSession {
  return new GameSession(
    engine,
    game,
    options,
    (play) => {
      audio.levelEnded(play.run.result);
      menu().completeLevel(play.run.result);
    },
    {
      highScore: () => menu().highScore,
      record: (score) => {
        menu().recordScore(score);
      },
    },
    {
      started: (levelId) => {
        audio.levelStarted(levelId);
      },
      step: (run) => {
        audio.levelStep(run);
      },
    },
  );
}

/**
 * Wires the layers together (ENG-11): loads the menu scenes behind a loading screen, then
 * runs the menus (P01-R01..R15) and the levels (P06) in Babylon's render loop with a
 * fixed-step clock (ENG-100).
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
  const { audio, withAudio } = createAppAudio(game, options);
  const session = createSession(engine, game, options, () => menu, audio);
  const { controls } = session;
  const { menu, overlay } = createMenu(game, options, { menu: input, controls, audio }, (state) => {
    syncScenes(scenes, state, shipIds);
    session.sync(state);
    audio.menuChanged(state);
  });
  const stopPage = listenToPage(options, menu, audio);
  const prepared = prepareMenuScenes(engine, game, options.environment);
  const loading = loadMenuScenes(prepared, menu, options, (loaded) => {
    scenes = loaded;
    syncScenes(scenes, menu.flow.state, shipIds);
    startDebugLevel(menu, options.debug, shipIds);
  });

  const ticker = withAudio(frameTicker(clock, menu, () => scenes, session));
  const { tick, step } = clockControls(clock, ticker);
  if (options.renderLoop) runLoop(engine, tick);
  return {
    clock,
    menu,
    loaded: loading.loaded,
    loadingProgress: loading.progress,
    scenes: () => scenes,
    game: () => session.play,
    controls,
    audio,
    command: menu.command.bind(menu),
    tick,
    step,
    dispose: () => {
      engine.stopRenderLoop();
      stop();
      stopPage();
      session.dispose();
      overlay.dispose();
      disposeScenes(scenes);
    },
  };
}
