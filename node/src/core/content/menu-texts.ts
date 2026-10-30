/** Texts of the engine's menu screens, provided by the game (ENG-140, ENG-144). */
export interface MenuTexts {
  readonly loading: string;
  readonly highScore: string;
  readonly start: string;
  /** Short controls hint on the title screen. */
  readonly startHint: string;
  readonly chooseShip: string;
  readonly chooseShipHint: string;
  readonly chooseLevel: string;
  readonly chooseLevelHint: string;
  /** Label of the on-screen Back button. */
  readonly back: string;
  /** Feedback shown when a locked level is confirmed. */
  readonly locked: string;
  /** Game screen (P06-R02): the level shown in a corner, for its label. */
  readonly gameLevel: (levelLabel: string) => string;
  /** Label of the on-screen fire button (touch screens). */
  readonly fire: string;
  /** "Level complete" overlay (P06-R03): heading, enemy count and how to go on. */
  readonly levelComplete: string;
  /** Heading of the same overlay when every life is lost (GD-20). */
  readonly gameOver: string;
  readonly enemiesDestroyed: (destroyed: number, spawned: number) => string;
  /** The attempt's score on the same overlay, and the line shown when it beat the high score (P11-R03). */
  readonly finalScore: (score: number) => string;
  readonly newHighScore: string;
  readonly continueHint: string;
  /**
   * The "Game over" panel's two choices after the mini boss (P07-R08): go on from the
   * checkpoint, or back to the level select screen.
   */
  readonly continueFromCheckpoint: string;
  readonly toLevelSelect: string;
  /** In-game HUD: the health bar's label, lives, the weapon and its level, enemies destroyed. */
  readonly hudHealth: string;
  readonly hudLives: (lives: number) => string;
  readonly hudWeapon: (weaponName: string, level: number, levels: number) => string;
  /** The bombs left, next to the lives (P11-R05; a count since they have no limit, reviewer 2026-10-28). */
  readonly hudBombs: (bombs: number) => string;
  /** The score, and the high score line under it (P11-R02). */
  readonly hudScore: (score: number) => string;
  readonly hudHighScore: (score: number) => string;
  /** Label of the on-screen bomb button (touch screens, P11-R06), with the bombs left. */
  readonly hudBomb: (bombs: number) => string;
  /** Kinds shown on the boss health bar (P07-R02). */
  readonly hudMiniBoss: string;
  readonly hudBoss: string;
  /** Shown instead of the menu when the browser cannot run the game (ENG-06). */
  readonly unsupported: string;
  /** The title screen's Settings entry and the settings screen's heading (P12-R04). */
  readonly settings: string;
  readonly settingsHint: string;
  /** The volume sliders' labels (P12-R04). */
  readonly musicVolume: string;
  readonly sfxVolume: string;
  /** Label of the on-screen pause button (P12-R01). */
  readonly pauseButton: string;
  /** The pause menu (P12-R02): heading, entries, hint, and the question before leaving. */
  readonly paused: string;
  readonly resume: string;
  readonly mainMenu: string;
  readonly pauseHint: string;
  readonly leaveLevel: string;
  readonly no: string;
  readonly yes: string;
}
