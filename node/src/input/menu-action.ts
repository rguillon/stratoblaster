/**
 * Abstract menu actions every input device is translated into (P01-R12):
 * - `back`: Back on the menu screens (Backspace, gamepad B); nothing in a level (P12-R01);
 * - `cancel`: the Escape key: Back on the menu screens (P01-R09), pause in a level (P12-R01);
 * - `pause`: pauses a level, or resumes it from the pause menu (P, gamepad Start / Select, the
 *   on-screen pause button);
 * - `resume`: resumes a paused level (test API, P12-R12).
 */
export type MenuAction =
  'up' | 'down' | 'left' | 'right' | 'confirm' | 'back' | 'cancel' | 'pause' | 'resume';

/** Every menu action, e.g. to validate actions coming from outside (test API). */
export const MENU_ACTIONS: readonly MenuAction[] = [
  'up',
  'down',
  'left',
  'right',
  'confirm',
  'back',
  'cancel',
  'pause',
  'resume',
];

/** Selection moves, which repeat while held. */
export type MenuDirection = 'up' | 'down' | 'left' | 'right';

/** Selects entry `select` of the current screen directly (tap or click on a non-selected entry). */
export interface MenuSelect {
  readonly select: number;
}

/** Sets slider `set` of the settings screen to `value` (tap or drag on it, P12-R04). */
export interface MenuSet {
  readonly set: number;
  readonly value: number;
}

/** What menu screens react to: an abstract action, a direct selection or a slider value. */
export type MenuCommand = MenuAction | MenuSelect | MenuSet;

const DIRECTIONS: readonly MenuAction[] = ['up', 'down', 'left', 'right'];

/** True for the four selection moves. */
export function isMenuDirection(action: MenuAction): action is MenuDirection {
  return DIRECTIONS.includes(action);
}

/** True when `value` is one of {@link MENU_ACTIONS}. */
export function isMenuAction(value: unknown): value is MenuAction {
  return typeof value === 'string' && (MENU_ACTIONS as readonly string[]).includes(value);
}
