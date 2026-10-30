import type { Caption } from './caption-row';

/** Loading screen (P01-R02). */
export interface LoadingView {
  readonly kind: 'loading';
  readonly text: string;
  /** 0..1. */
  readonly progress: number;
}

/** Title screen (P01-R04). */
export interface TitleView {
  readonly kind: 'title';
  readonly title: string;
  readonly highScoreLabel: string;
  readonly highScore: number;
  readonly start: string;
  /** The Settings entry under Start (P12-R04). */
  readonly settings: string;
  /** The entry selected: 0 Start, 1 Settings. */
  readonly selected: number;
  readonly hint: string;
  /** Version and short commit hash (ENG-83). */
  readonly version: string;
  readonly commit: string;
}

/** Fields shared by the screens that have a Back button. */
interface BackView {
  readonly heading: string;
  readonly hint: string;
  readonly back: string;
  readonly selected: number;
}

/** Ship select screen (P01-R06): one card per ship, under its 3D model. */
export interface ShipSelectView extends BackView {
  readonly kind: 'ship-select';
  readonly ships: readonly Caption[];
  /** Width of the row of cards, in % of the screen, to line them up with the models. */
  readonly cardsWidthPercent: number;
}

/** Level select screen (P01-R07). */
export interface LevelSelectView extends BackView {
  readonly kind: 'level-select';
  readonly columns: number;
  readonly levels: readonly { readonly label: string; readonly locked: boolean }[];
  readonly lockedText: string;
}

/** The "Level complete" overlay (P06-R03), or "Game over" when every life is lost (GD-20). */
export interface LevelCompleteView {
  readonly heading: string;
  /** Whether the game is over (the panel shows as a loss). */
  readonly over: boolean;
  /** The level's label, e.g. `1-2`. */
  readonly level: string;
  /** How many enemies were destroyed out of how many came. */
  readonly enemies: string;
  /** The attempt's score (P11-R03). */
  readonly score: string;
  /** Shown when the score beat the saved high score (P11-R03); none otherwise. */
  readonly newHighScore?: string;
  readonly hint: string;
  /**
   * "Game over" after the mini boss (P07-R08): Continue from the checkpoint or go to the level
   * select screen, and which one is selected. None otherwise.
   */
  readonly choices?: { readonly labels: readonly string[]; readonly selected: number };
}

/** The pause menu (P12-R02), over the dimmed playfield. */
export interface PauseView {
  readonly heading: string;
  /** Resume, Settings, Main menu. */
  readonly entries: readonly string[];
  readonly hint: string;
  /** The `Leave the level?` question, with its No / Yes choices, when it shows. */
  readonly question: {
    readonly text: string;
    readonly choices: readonly string[];
    readonly selected: number;
  } | null;
}

/** Game screen (P06-R02): what the overlay shows over the level being played. */
export interface GameScreenView {
  readonly kind: 'game';
  readonly level: string;
  /** Label of the on-screen fire button. */
  readonly fire: string;
  /** Label of the on-screen pause button (P12-R01). */
  readonly pause: string;
  readonly complete: LevelCompleteView | null;
  /** The pause menu, while the level is paused (P12-R02). */
  readonly paused: PauseView | null;
  /** The entry selected on the panel (its choices, P07-R08, or the pause menu), for taps. */
  readonly selected: number;
}

/** One slider of the settings screen (P12-R04). */
export interface SliderView {
  readonly label: string;
  /** 0 … max. */
  readonly value: number;
  readonly max: number;
}

/** Settings screen (P12-R04): the volume sliders. */
export interface SettingsView extends BackView {
  readonly kind: 'settings';
  readonly sliders: readonly SliderView[];
  /** Opened from the pause menu: the paused level shows dimmed behind it. */
  readonly overLevel: boolean;
}

/** Everything the menu overlay can show. */
export type MenuView =
  LoadingView | TitleView | ShipSelectView | LevelSelectView | GameScreenView | SettingsView;
