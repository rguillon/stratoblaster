import { HoldRepeater } from './hold-repeater';
import { isMenuDirection, type MenuAction, type MenuDirection } from './menu-action';

/** The parts of a keyboard event the menu input reads. */
export interface MenuKeyEvent {
  readonly code: string;
  readonly repeat: boolean;
  preventDefault(): void;
}

/** Key repeat timing. */
export interface RepeatTiming {
  readonly repeatDelaySeconds: number;
  readonly repeatIntervalSeconds: number;
}

/**
 * Keyboard → menu actions (P01-R09). Keys are matched by `KeyboardEvent.code` (physical
 * position), so WASD positions work on AZERTY. Held directions repeat with our own timing;
 * the browser's auto-repeat events are ignored.
 */
export class KeyboardMenuInput {
  readonly #queue: MenuAction[] = [];
  readonly #repeater: HoldRepeater<MenuDirection>;

  constructor(
    private readonly bindings: Readonly<Record<string, MenuAction>>,
    timing: RepeatTiming,
  ) {
    this.#repeater = new HoldRepeater(timing.repeatDelaySeconds, timing.repeatIntervalSeconds);
  }

  keyDown(event: MenuKeyEvent): void {
    const action = this.bindings[event.code];
    if (action === undefined) return;
    event.preventDefault();
    if (event.repeat) return;
    if (!isMenuDirection(action)) this.#queue.push(action);
    else if (this.#repeater.press(action)) this.#queue.push(action);
  }

  keyUp(event: Pick<MenuKeyEvent, 'code'>): void {
    const action = this.bindings[event.code];
    if (action !== undefined && isMenuDirection(action)) this.#repeater.release(action);
  }

  /** Forgets held keys, e.g. when the window loses focus and key-ups would be missed. */
  releaseAll(): void {
    this.#repeater.releaseAll();
  }

  /** Returns the actions since the last call: presses first, then the repeats due. */
  update(dtSeconds: number): MenuAction[] {
    const actions = [...this.#queue, ...this.#repeater.update(dtSeconds)];
    this.#queue.length = 0;
    return actions;
  }

  /** Listens to `keydown`, `keyup` and `blur` on `target`. Returns a function that stops. */
  listen(target: Pick<EventTarget, 'addEventListener' | 'removeEventListener'>): () => void {
    const down = (e: Event): void => {
      this.keyDown(e as KeyboardEvent);
    };
    const up = (e: Event): void => {
      this.keyUp(e as KeyboardEvent);
    };
    const blur = (): void => {
      this.releaseAll();
    };
    target.addEventListener('keydown', down);
    target.addEventListener('keyup', up);
    target.addEventListener('blur', blur);
    return () => {
      target.removeEventListener('keydown', down);
      target.removeEventListener('keyup', up);
      target.removeEventListener('blur', blur);
    };
  }
}
