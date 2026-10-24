import type { FlightInput } from '../core/systems/player-flight';
import type { GamepadLike, GamepadSource } from './gamepad-menu-input';
import { HeldDirections } from './held-directions';

/** Which inputs shoot and move the ship (see `config/game-controls.ts`). */
export interface GameControlBindings {
  readonly fireKeys: readonly string[];
  readonly switchKeys: readonly string[];
  readonly fireButtons: readonly number[];
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
}

/**
 * The player's in-game controls (P06-R02, GD §2): arrows / WASD (by key position) or the left
 * stick / D-pad move, Space or the gamepad button shoots while held, and on touch screens the
 * ship follows the finger dragged anywhere while the on-screen button shoots. All devices are
 * merged.
 */
export class GameControls {
  readonly keys = new HeldDirections();
  readonly #fireKeys = new Set<string>();
  readonly #switchKeys = new Set<string>();
  #switches = 0;
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
    if (this.bindings.switchKeys.includes(code)) {
      // Once per press: held keys repeat their key-downs.
      if (down && !this.#switchKeys.has(code)) this.#switches++;
      if (down) this.#switchKeys.add(code);
      else this.#switchKeys.delete(code);
      return true;
    }
    if (!this.bindings.fireKeys.includes(code)) return false;
    if (down) this.#fireKeys.add(code);
    else this.#fireKeys.delete(code);
    return true;
  }

  /** The on-screen fire button is held (`true`) or let go. */
  setTouchFire(held: boolean): void {
    this.#touchFire = held;
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
    this.#switchKeys.clear();
    this.#switches = 0;
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
    let move = Math.hypot(pad.x, pad.y) > Math.hypot(keys.x, keys.y) ? pad : keys;
    const reach = maxSpeed * dt;
    const dragged = Math.hypot(this.#dragX, this.#dragY);
    if (dragged > 0 && reach > 0) {
      const share = Math.min(1, reach / dragged);
      move = { x: (this.#dragX / reach) * share, y: (this.#dragY / reach) * share };
      this.#dragX -= this.#dragX * share;
      this.#dragY -= this.#dragY * share;
    }
    const switchWeapon = this.#switches > 0;
    if (switchWeapon) this.#switches--;
    const fire = this.#fireKeys.size > 0 || this.#touchFire || pad.fire;
    return { move, fire, switchWeapon };
  }

  #readGamepads(): { x: number; y: number; fire: boolean } {
    let best = { x: 0, y: 0, fire: false };
    let fire = false;
    for (const gamepad of this.gamepads()) {
      if (!gamepad) continue;
      const pad = padInput(gamepad, this.bindings);
      fire ||= pad.fire;
      if (Math.hypot(pad.x, pad.y) > Math.hypot(best.x, best.y)) best = pad;
    }
    const length = Math.hypot(best.x, best.y);
    const scale = length > 1 ? 1 / length : 1;
    return { x: best.x * scale, y: best.y * scale, fire };
  }
}

/** One gamepad's direction (the stronger of the stick and the D-pad, Y up) and fire button. */
function padInput(
  gamepad: GamepadLike,
  { fireButtons, dpad, stick }: GameControlBindings,
): { x: number; y: number; fire: boolean } {
  const held = (i: number): boolean => gamepad.buttons[i]?.pressed ?? false;
  const sx = gamepad.axes[stick.xAxis] ?? 0;
  const sy = -(gamepad.axes[stick.yAxis] ?? 0);
  const [px, py] = Math.hypot(sx, sy) >= stick.deadZone ? [sx, sy] : [0, 0];
  const bx = (held(dpad.right) ? 1 : 0) - (held(dpad.left) ? 1 : 0);
  const by = (held(dpad.up) ? 1 : 0) - (held(dpad.down) ? 1 : 0);
  const [x, y] = Math.hypot(bx, by) > Math.hypot(px, py) ? [bx, by] : [px, py];
  return { x, y, fire: fireButtons.some(held) };
}
