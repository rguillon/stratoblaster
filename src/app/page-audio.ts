import type { GameDefinition } from '../core/content/game-definition';
import { AUDIO_CONFIG } from '../config/audio';
import type { GamepadSource } from '../input/gamepad-menu-input';
import type { GameView } from '../render/game-view';
import { GameAudio, type GameAudioOptions } from './game-audio';
import type { MenuController } from './menu-controller';

type ListenTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

/** The app's options about the page around it (`AppOptions`). */
export interface PageOptions {
  /** Audio (P12-R05): how to create the Web Audio context. Silent when omitted. */
  readonly audio?: Omit<GameAudioOptions, 'screenWidth' | 'clock'>;
  /** Connected gamepads. No gamepad when omitted. */
  readonly gamepads?: GamepadSource;
  /**
   * Where key presses, taps and clicks are heard to unlock the audio (P12-R05). The gamepads'
   * buttons unlock it too. None when omitted.
   */
  readonly gestureTarget?: ListenTarget;
  /** The page's visibility (P12-R03, P12-R11): the level pauses and the audio goes quiet. */
  readonly visibility?: { readonly target: ListenTarget; readonly hidden: () => boolean };
  /** Runs `tick` every `seconds` until the returned function is called (the music scheduler). */
  readonly every?: (tick: () => void, seconds: number) => () => void;
}

/** A frame split in two, as `start-app` runs it. */
interface Ticker {
  readonly simulate: (dtSeconds: number) => void;
  readonly render: () => void;
}

/** Any button down on any gamepad: a user gesture. */
function gamepadPressed(gamepads: GamepadSource | undefined): boolean {
  return (gamepads?.() ?? []).some((pad) => pad?.buttons.some((b) => b.pressed) === true);
}

/**
 * The browser around the game (P12-R03, P12-R05, P12-R11): the first gesture unlocks the audio,
 * a hidden page pauses the level and silences the audio, and a timer schedules the music. Returns
 * a function that stops listening.
 */
export function listenToPage(
  options: PageOptions,
  menu: MenuController,
  audio: GameAudio,
): () => void {
  const stops: (() => void)[] = [];
  const unlock = (): void => {
    audio.unlock();
  };
  const gestures = options.gestureTarget;
  for (const type of ['keydown', 'pointerdown', 'pointerup', 'touchend']) {
    gestures?.addEventListener(type, unlock);
    stops.push(() => gestures?.removeEventListener(type, unlock));
  }
  const { visibility } = options;
  if (visibility) {
    const onVisibility = (): void => {
      const hidden = visibility.hidden();
      if (hidden) menu.pause();
      audio.setHidden(hidden);
    };
    visibility.target.addEventListener('visibilitychange', onVisibility);
    stops.push(() => {
      visibility.target.removeEventListener('visibilitychange', onVisibility);
    });
  }
  if (options.every) {
    stops.push(
      options.every(() => {
        audio.update();
      }, AUDIO_CONFIG.scheduleIntervalSeconds),
    );
  }
  return () => {
    for (const stop of stops) stop();
  };
}

/**
 * The game's audio (P12-R05), on the app's own clock (the sound effect limits count in game
 * time, P12-R10), and the frame wrapper that unlocks it on a gamepad button and schedules the
 * music after each frame.
 */
export function createAppAudio(
  game: GameDefinition<GameView>,
  options: PageOptions,
): { audio: GameAudio; withAudio: (ticker: Ticker) => Ticker } {
  let elapsed = 0;
  const audio = new GameAudio(game.view.audio, {
    ...options.audio,
    clock: () => elapsed,
    screenWidth: game.screen.width,
  });
  const withAudio = (ticker: Ticker): Ticker => ({
    simulate: (dt) => {
      elapsed += Math.max(0, dt);
      if (gamepadPressed(options.gamepads)) audio.unlock();
      ticker.simulate(dt);
      audio.update();
    },
    render: ticker.render,
  });
  return { audio, withAudio };
}
