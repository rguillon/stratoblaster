/** Abstract menu actions every input device is translated into (P01-R12). */
export type MenuAction = 'up' | 'down' | 'left' | 'right' | 'confirm' | 'back';

/** Every menu action, e.g. to validate actions coming from outside (test API). */
export const MENU_ACTIONS: readonly MenuAction[] = [
  'up',
  'down',
  'left',
  'right',
  'confirm',
  'back',
];

/** Selection moves, which repeat while held. */
export type MenuDirection = 'up' | 'down' | 'left' | 'right';

/** Selects entry `select` of the current screen directly (tap or click on a non-selected entry). */
export interface MenuSelect {
  readonly select: number;
}

/** What menu screens react to: an abstract action, or a direct selection by pointer. */
export type MenuCommand = MenuAction | MenuSelect;

/** True for the four selection moves. */
export function isMenuDirection(action: MenuAction): action is MenuDirection {
  return action !== 'confirm' && action !== 'back';
}

/** True when `value` is one of {@link MENU_ACTIONS}. */
export function isMenuAction(value: unknown): value is MenuAction {
  return typeof value === 'string' && (MENU_ACTIONS as readonly string[]).includes(value);
}
