import { HoldRepeater } from './hold-repeater';
import { isMenuDirection, type MenuAction, type MenuDirection } from './menu-action';
import type { RepeatTiming } from './keyboard-menu-input';

/** The parts of a `Gamepad` the menu input reads. */
export interface GamepadLike {
  readonly buttons: readonly { readonly pressed: boolean }[];
  readonly axes: readonly number[];
}

/** Returns the connected gamepads, like `navigator.getGamepads()`. */
export type GamepadSource = () => readonly (GamepadLike | null)[];

/** Gamepad mapping and stick settings. */
export interface GamepadMenuBindings extends RepeatTiming {
  readonly gamepadButtons: Readonly<Record<number, MenuAction>>;
  readonly gamepadStick: { readonly xAxis: number; readonly yAxis: number };
  readonly gamepadDeadZone: number;
}

/** Direction of a stick tilt, or undefined inside the dead zone (P01-R10). */
export function stickDirection(x: number, y: number, deadZone: number): MenuDirection | undefined {
  if (Math.hypot(x, y) < deadZone) return undefined;
  if (Math.abs(x) >= Math.abs(y)) return x > 0 ? 'right' : 'left';
  return y > 0 ? 'down' : 'up';
}

/**
 * Gamepad → menu actions (P01-R10), polled once per frame. Buttons fire on press; the
 * D-pad and the left stick repeat while held. All connected gamepads are merged.
 */
export class GamepadMenuInput {
  readonly #repeater: HoldRepeater<MenuDirection>;
  #pressedButtons = new Set<MenuAction>();

  constructor(
    private readonly source: GamepadSource,
    private readonly bindings: GamepadMenuBindings,
  ) {
    this.#repeater = new HoldRepeater(bindings.repeatDelaySeconds, bindings.repeatIntervalSeconds);
  }

  #readHeld(): Set<MenuAction> {
    const held = new Set<MenuAction>();
    const { gamepadButtons, gamepadStick, gamepadDeadZone } = this.bindings;
    for (const pad of this.source()) {
      if (!pad) continue;
      pad.buttons.forEach((button, i) => {
        const action = gamepadButtons[i];
        if (button.pressed && action !== undefined) held.add(action);
      });
      const x = pad.axes[gamepadStick.xAxis] ?? 0;
      const y = pad.axes[gamepadStick.yAxis] ?? 0;
      const tilt = stickDirection(x, y, gamepadDeadZone);
      if (tilt) held.add(tilt);
    }
    return held;
  }

  /** Polls the gamepads and returns the actions of this frame. */
  update(dtSeconds: number): MenuAction[] {
    const held = this.#readHeld();
    const actions: MenuAction[] = [];
    for (const direction of this.#repeater.held) {
      if (!held.has(direction)) this.#repeater.release(direction);
    }
    const repeats = this.#repeater.update(dtSeconds);
    for (const action of held) {
      if (isMenuDirection(action)) {
        if (this.#repeater.press(action)) actions.push(action);
      } else if (!this.#pressedButtons.has(action)) {
        actions.push(action);
      }
    }
    this.#pressedButtons = held;
    return [...actions, ...repeats];
  }
}

/** Gamepad source reading `navigator.getGamepads()`, or no gamepad when unsupported. */
export function browserGamepads(nav: Partial<Pick<Navigator, 'getGamepads'>>): GamepadSource {
  return () => (nav.getGamepads ? nav.getGamepads() : []);
}
