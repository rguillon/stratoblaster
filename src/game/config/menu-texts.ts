import type { MenuTexts } from '../../core/content/menu-texts';

/** Menu texts: short words, readable by kids (vision). */
export const MENU_TEXTS: MenuTexts = {
  loading: 'Loading…',
  highScore: 'High score',
  start: 'Start',
  startHint: 'Press Space / Enter or tap to start',
  chooseShip: 'Choose your ship',
  chooseShipHint: '◀ ▶ to pick · Enter or tap again to go',
  chooseLevel: 'Choose a level',
  chooseLevelHint: 'Arrows to pick · Enter or tap again to go',
  back: 'Back',
  locked: 'Locked!',
  gameLevel: (level) => `Level ${level}`,
  fire: 'Fire',
  levelComplete: 'Level complete!',
  enemiesDestroyed: (destroyed, spawned) =>
    `Enemies destroyed: ${String(destroyed)} / ${String(spawned)}`,
  continueHint: 'Press Space / Enter or tap to go on',
  hudHealth: 'HP',
  hudWeapon: (weapon, level, levels) => `${weapon} · Lv ${String(level)}/${String(levels)}`,
  hudDestroyed: (count) => `Destroyed: ${String(count)}`,
  unsupported:
    'Sorry! This game cannot run in this browser or on this device. ' +
    'Please try a recent version of Chrome, Edge, Firefox or Safari on a computer.',
};
