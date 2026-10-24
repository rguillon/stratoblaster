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

/** The "Level complete" overlay (P06-R03). */
export interface LevelCompleteView {
  readonly heading: string;
  /** The level's label, e.g. `1-2`. */
  readonly level: string;
  /** How many enemies were destroyed out of how many came. */
  readonly enemies: string;
  readonly hint: string;
}

/** Game screen (P06-R02): what the overlay shows over the level being played. */
export interface GameScreenView {
  readonly kind: 'game';
  readonly level: string;
  /** Label of the on-screen fire button. */
  readonly fire: string;
  readonly complete: LevelCompleteView | null;
}

/** Everything the menu overlay can show. */
export type MenuView = LoadingView | TitleView | ShipSelectView | LevelSelectView | GameScreenView;
