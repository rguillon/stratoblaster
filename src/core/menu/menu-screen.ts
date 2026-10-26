/**
 * The screens of the menu flow (`02-game-design.md` §7, P01-R01): `pause` is the menu over a
 * paused level, `settings` the settings screen, from the title or the pause menu (P12-R02,
 * P12-R04).
 */
export type MenuScreen =
  'loading' | 'title' | 'ship-select' | 'level-select' | 'game' | 'pause' | 'settings';

/**
 * Allowed screen changes: forward through the flow, Back on each menu screen, from a completed
 * level back to the level select screen (P06-R03), and the pause menu and the settings screen
 * (P12-R02, P12-R04). The level is left through the pause menu.
 */
export const MENU_TRANSITIONS: Readonly<Record<MenuScreen, readonly MenuScreen[]>> = {
  loading: ['title'],
  title: ['ship-select', 'settings'],
  'ship-select': ['level-select', 'title'],
  'level-select': ['game', 'ship-select'],
  game: ['pause', 'level-select'],
  pause: ['game', 'settings', 'title'],
  settings: ['title', 'pause'],
};

/** True when the flow may go from `from` to `to`. */
export function canTransition(from: MenuScreen, to: MenuScreen): boolean {
  return MENU_TRANSITIONS[from].includes(to);
}
