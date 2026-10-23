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
  /** Placeholder game screen text for the chosen ship name and level label. */
  readonly gamePlaceholder: (shipName: string, levelLabel: string) => string;
  /** How to go back to the title screen from the placeholder game screen. */
  readonly gameHint: string;
  /** Shown instead of the menu when the browser cannot run the game (ENG-06). */
  readonly unsupported: string;
}
