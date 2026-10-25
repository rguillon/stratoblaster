import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import { GameControls } from '../input/game-controls';
import type { GamepadSource } from '../input/gamepad-menu-input';
import { GAME_CONTROLS_CONFIG } from '../config/game-controls';
import type { GameView } from '../render/game-view';
import type { MenuDocument } from '../ui/screens/elements';
import { GamePlay } from './game-play';
import type { MenuState } from './menu-flow';

type ListenTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

/**
 * Debug options from the URL (P06-R09), e.g. `?level=1-3&t=120&ship=heavy`: start a level
 * straight away, at a given time, with the playback keys and the FPS / polygons tile.
 */
export interface GameDebugOptions {
  readonly levelId: string;
  /** Seconds into the level to start at. */
  readonly time: number;
  /** The ship to fly; the game's first ship when null. */
  readonly shipId: string | null;
}

/** What a {@link GameSession} needs from the app's options. */
export interface GameSessionOptions {
  readonly environment: boolean;
  readonly doc: MenuDocument;
  readonly debug?: GameDebugOptions;
  readonly statsParent?: HTMLElement;
  /** Where the in-game HUD goes: the overlay, laid out at the logical resolution. */
  readonly overlay?: HTMLElement;
  /** Where keys are listened to. No keyboard when omitted. */
  readonly keyboardTarget?: ListenTarget;
  /** Connected gamepads. No gamepad when omitted. */
  readonly gamepads?: GamepadSource;
}

/** Keys go to the level's debug keys first (when on), then to the in-game controls. */
export function listenControls(
  target: ListenTarget | undefined,
  controls: GameControls,
  game: () => GamePlay | undefined,
): () => void {
  if (!target) return () => undefined;
  const onKey = (event: Event): void => {
    const { code, type } = event as KeyboardEvent;
    const down = type === 'keydown';
    if (!game()?.debugKey(code, down)) controls.key(code, down);
  };
  const onBlur = (): void => {
    controls.clear();
  };
  target.addEventListener('keydown', onKey);
  target.addEventListener('keyup', onKey);
  target.addEventListener('blur', onBlur);
  return () => {
    target.removeEventListener('keydown', onKey);
    target.removeEventListener('keyup', onKey);
    target.removeEventListener('blur', onBlur);
  };
}

/**
 * Starts the level chosen on the game screen, and ends it when the flow leaves it (P06-R02).
 * The debug options' start time applies to the first level played only.
 */
export class GameSession {
  play: GamePlay | undefined;
  /** The player's in-game controls, fed by the keyboard target and the gamepads. */
  readonly controls: GameControls;
  #startTime: number;
  readonly #stopListening: () => void;

  constructor(
    private readonly engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    private readonly options: GameSessionOptions,
    private readonly onComplete: (play: GamePlay) => void,
  ) {
    this.#startTime = options.debug?.time ?? 0;
    this.controls = new GameControls(GAME_CONTROLS_CONFIG, options.gamepads);
    this.#stopListening = listenControls(options.keyboardTarget, this.controls, () => this.play);
  }

  /** Ends the level being played and stops listening to the keys. */
  dispose(): void {
    this.end();
    this.#stopListening();
  }

  sync(state: MenuState): void {
    const levelId = state.screen === 'game' ? state.chosenLevelId : null;
    if (levelId === null) {
      this.end();
      return;
    }
    if (this.play || state.levelResult) return;
    const shipId = state.chosenShipId ?? state.highlightedShipId;
    const play: GamePlay = new GamePlay(
      this.engine,
      this.game,
      { shipId, levelId },
      this.controls,
      {
        environment: this.options.environment,
        debug: this.options.debug !== undefined,
        startTime: this.#startTime,
        doc: this.options.doc,
        ...(this.options.statsParent ? { statsParent: this.options.statsParent } : {}),
        ...(this.options.overlay ? { hudParent: this.options.overlay } : {}),
        onComplete: () => {
          this.onComplete(play);
        },
      },
    );
    this.#startTime = 0;
    this.play = play;
  }

  end(): void {
    this.play?.dispose();
    this.play = undefined;
    this.controls.clear();
  }
}
