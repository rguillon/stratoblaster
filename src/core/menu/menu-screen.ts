/** The screens of the menu flow (`02-game-design.md` §7, P01-R01). */
export type MenuScreen = 'loading' | 'title' | 'ship-select' | 'level-select' | 'game';

/**
 * Allowed screen changes: forward through the flow, Back on each menu screen, and from a
 * completed level back to the level select screen (P06-R03).
 */
export const MENU_TRANSITIONS: Readonly<Record<MenuScreen, readonly MenuScreen[]>> = {
  loading: ['title'],
  title: ['ship-select'],
  'ship-select': ['level-select', 'title'],
  'level-select': ['game', 'ship-select'],
  game: ['title', 'level-select'],
};

/** True when the flow may go from `from` to `to`. */
export function canTransition(from: MenuScreen, to: MenuScreen): boolean {
  return MENU_TRANSITIONS[from].includes(to);
}
