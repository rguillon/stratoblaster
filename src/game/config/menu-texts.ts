import type { MenuTexts } from '../../core/content/menu-texts';

/** Digits the score shows, zero-padded (P11-R02). */
const SCORE_DIGITS = 7;

const padded = (score: number): string => String(score).padStart(SCORE_DIGITS, '0');

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
  gameOver: 'Game over',
  enemiesDestroyed: (destroyed, spawned) =>
    `Enemies destroyed: ${String(destroyed)} / ${String(spawned)}`,
  finalScore: (score) => `Score: ${String(score)}`,
  newHighScore: 'New high score!',
  continueHint: 'Press Space / Enter or tap to go on',
  continueFromCheckpoint: 'Continue',
  toLevelSelect: 'Level select',
  hudHealth: 'HP',
  hudLives: (lives) => `♥ ${String(lives)}`,
  hudWeapon: (weapon, level, levels) => `${weapon} · Lv ${String(level)}/${String(levels)}`,
  hudDestroyed: (count) => `Destroyed: ${String(count)}`,
  hudScore: padded,
  hudHighScore: (score) => `HI ${padded(score)}`,
  hudBomb: (bombs) => `Bomb ${String(bombs)}`,
  hudMiniBoss: 'Mini boss',
  hudBoss: 'Boss',
  unsupported:
    'Sorry! This game cannot run in this browser or on this device. ' +
    'Please try a recent version of Chrome, Edge, Firefox or Safari on a computer.',
};
