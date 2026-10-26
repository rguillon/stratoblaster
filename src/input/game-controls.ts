import type { FlightInput } from '../core/systems/player-flight';
import type { GamepadLike, GamepadSource } from './gamepad-menu-input';
import { HeldDirections } from './held-directions';

/** Which inputs shoot and move the ship (see `config/game-controls.ts`). */
export interface GameControlBindings {
  readonly fireKeys: readonly string[];
  readonly switchKeys: readonly string[];
  /** Keys that set a bomb off, once per press (P11-R06). */
  readonly bombKeys: readonly string[];
  readonly fireButtons: readonly number[];
  /** Gamepad buttons that set a bomb off, once per press (P11-R06). */
  readonly bombButtons: readonly number[];
  readonly dpad: {
    readonly up: number;
    readonly down: number;
    readonly left: number;
    readonly right: number;
  };
  readonly stick: { readonly xAxis: number; readonly yAxis: number; readonly deadZone: number };
}

/** The controls of one simulation step. */
export interface ControlState {
  readonly move: FlightInput;
  readonly fire: boolean;
  /** Switch to the next weapon (once per press). */
  readonly switchWeapon: boolean;
  /** Set a bomb off (once per press, P11-R06). */
  readonly bomb: boolean;
}

/** Counts the presses of a set of keys: held keys repeat their key-downs, which do not count. */
class Presses {
  readonly #held = new Set<string>();
  count = 0;

  /** Whether `code` is one of `codes`; a press if it goes down while not held. */
  key(codes: readonly string[], code: string, down: boolean): boolean {
    if (!codes.includes(code)) return false;
    if (down && !this.#held.has(code)) this.count++;
    if (down) this.#held.add(code);
    else this.#held.delete(code);
    return true;
  }

  /** Takes one press, if there is one. */
  take(): boolean {
    if (this.count <= 0) return false;
    this.count--;
    return true;
  }

  clear(): void {
    this.#held.clear();
    this.count = 0;
  }
}

/**
 * The player's in-game controls (P06-R02, GD §2): arrows / WASD (by key position) or the left
 * stick / D-pad move, Space or the gamepad button shoots while held, and on touch screens the
 * ship follows the finger dragged anywhere while the on-screen button shoots. E switches the
 * weapon; R, the left Shift, a gamepad button or the on-screen bomb button set a bomb off
 * (P11-R06). All devices are merged.
 */
export class GameControls {
  readonly keys = new HeldDirections();
  readonly #fireKeys = new Set<string>();
  readonly #switches = new Presses();
  readonly #bombs = new Presses();
  /** Whether a gamepad's bomb button was down at the last read (a press is a new one). */
  #padBombHeld = false;
  #touchFire = false;
  /** Drag distance not flown yet, in logical pixels. */
  #dragX = 0;
  #dragY = 0;

  constructor(
    private readonly bindings: GameControlBindings,
    private readonly gamepads: GamepadSource = () => [],
  ) {}

  /** A key going down or up (`code` is `KeyboardEvent.code`); returns whether it is a control. */
  key(code: string, down: boolean): boolean {
    if (this.keys.key(code, down)) return true;
    if (this.#switches.key(this.bindings.switchKeys, code, down)) return true;
    if (this.#bombs.key(this.bindings.bombKeys, code, down)) return true;
    if (!this.bindings.fireKeys.includes(code)) return false;
    if (down) this.#fireKeys.add(code);
    else this.#fireKeys.delete(code);
    return true;
  }

  /** The on-screen fire button is held (`true`) or let go. */
  setTouchFire(held: boolean): void {
    this.#touchFire = held;
  }

  /** The on-screen bomb button was tapped (P11-R06). */
  bomb(): void {
    this.#bombs.count++;
  }

  /** The finger moved by (`dx`, `dy`) logical pixels, Y up: the ship follows it. */
  drag(dx: number, dy: number): void {
    this.#dragX += dx;
    this.#dragY += dy;
  }

  /** Lets go of everything (e.g. the window lost the focus, so key-ups would be missed). */
  clear(): void {
    this.keys.clear();
    this.#fireKeys.clear();
    this.#switches.clear();
    this.#bombs.clear();
    this.#touchFire = false;
    this.#dragX = this.#dragY = 0;
  }

  /**
   * The controls for a step of `dt` seconds of a ship flying at `maxSpeed`: the strongest of
   * the keys, the gamepads and the drag, which is used up as the ship covers it.
   */
  read(dt: number, maxSpeed: number): ControlState {
    const pad = this.#readGamepads();
    const keys = this.keys.direction;
    let move: FlightInput =
      Math.hypot(pad.x, pad.y) > Math.hypot(keys.x, keys.y) ? { x: pad.x, y: pad.y } : keys;
    const reach = maxSpeed * dt;
    const dragged = Math.hypot(this.#dragX, this.#dragY);
    if (dragged > 0 && reach > 0) {
      const share = Math.min(1, reach / dragged);
      move = { x: (this.#dragX / reach) * share, y: (this.#dragY / reach) * share };
      this.#dragX -= this.#dragX * share;
      this.#dragY -= this.#dragY * share;
    }
    if (pad.bomb && !this.#padBombHeld) this.#bombs.count++;
    this.#padBombHeld = pad.bomb;
    const fire = this.#fireKeys.size > 0 || this.#touchFire || pad.fire;
    return { move, fire, switchWeapon: this.#switches.take(), bomb: this.#bombs.take() };
  }

  #readGamepads(): PadInput {
    let best: PadInput = { x: 0, y: 0, fire: false, bomb: false };
    let [fire, bomb] = [false, false];
    for (const gamepad of this.gamepads()) {
      if (!gamepad) continue;
      const pad = padInput(gamepad, this.bindings);
      fire ||= pad.fire;
      bomb ||= pad.bomb;
      if (Math.hypot(pad.x, pad.y) > Math.hypot(best.x, best.y)) best = pad;
    }
    const length = Math.hypot(best.x, best.y);
    const scale = length > 1 ? 1 / length : 1;
    return { x: best.x * scale, y: best.y * scale, fire, bomb };
  }
}

/** One gamepad's direction (Y up), and whether its fire and bomb buttons are down. */
interface PadInput {
  readonly x: number;
  readonly y: number;
  readonly fire: boolean;
  readonly bomb: boolean;
}

/** One gamepad's direction (the stronger of the stick and the D-pad, Y up) and buttons. */
function padInput(
  gamepad: GamepadLike,
  { fireButtons, bombButtons, dpad, stick }: GameControlBindings,
): PadInput {
  const held = (i: number): boolean => gamepad.buttons[i]?.pressed ?? false;
  const sx = gamepad.axes[stick.xAxis] ?? 0;
  const sy = -(gamepad.axes[stick.yAxis] ?? 0);
  const [px, py] = Math.hypot(sx, sy) >= stick.deadZone ? [sx, sy] : [0, 0];
  const bx = (held(dpad.right) ? 1 : 0) - (held(dpad.left) ? 1 : 0);
  const by = (held(dpad.up) ? 1 : 0) - (held(dpad.down) ? 1 : 0);
  const [x, y] = Math.hypot(bx, by) > Math.hypot(px, py) ? [bx, by] : [px, py];
  return { x, y, fire: fireButtons.some(held), bomb: bombButtons.some(held) };
}
