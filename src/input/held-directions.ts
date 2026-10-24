import type { MenuDirection } from './menu-action';

/** `KeyboardEvent.code` → direction: arrows and WASD by key position (AZERTY works too, GD §2). */
export const DIRECTION_KEYS: Readonly<Record<string, MenuDirection>> = {
  ArrowUp: 'up',
  ArrowDown: 'down',
  ArrowLeft: 'left',
  ArrowRight: 'right',
  KeyW: 'up',
  KeyS: 'down',
  KeyA: 'left',
  KeyD: 'right',
};

/**
 * The movement keys held down, as a direction to fly in: X right, Y up, at most length 1 (so
 * diagonals are not faster).
 */
export class HeldDirections {
  readonly #held = new Set<string>();

  /** Records a key going down or up; returns whether it is a movement key. */
  key(code: string, down: boolean): boolean {
    if (!(code in DIRECTION_KEYS)) return false;
    if (down) this.#held.add(code);
    else this.#held.delete(code);
    return true;
  }

  /** Releases every key (e.g. when the window loses the focus). */
  clear(): void {
    this.#held.clear();
  }

  get direction(): { readonly x: number; readonly y: number } {
    const held = new Set([...this.#held].map((code) => DIRECTION_KEYS[code]));
    const x = (held.has('right') ? 1 : 0) - (held.has('left') ? 1 : 0);
    const y = (held.has('up') ? 1 : 0) - (held.has('down') ? 1 : 0);
    const length = Math.hypot(x, y) || 1;
    return { x: x / length, y: y / length };
  }
}
