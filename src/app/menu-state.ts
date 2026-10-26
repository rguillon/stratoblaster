import type { MenuScreen } from '../core/menu/menu-screen';
import type { LevelCatalog } from '../core/content/level-catalog';
import type { LevelCheckpoint, LevelResult } from '../core/systems/level-run';
import type { Volumes } from './settings-menu';

/**
 * What a command did, so the presentation can give feedback (and its sound, P12-R09): a move,
 * a new screen, a locked level, a level paused or resumed, a slider changed.
 */
export type MenuFeedback =
  'none' | 'moved' | 'screen' | 'locked' | 'paused' | 'resumed' | 'adjusted';

/** Snapshot of the menu flow. */
export interface MenuState {
  readonly screen: MenuScreen;
  /** Index of the selected entry on the current screen. */
  readonly selection: number;
  /** Id of the selected entry (`start`, a ship id, a level id), or null. */
  readonly selectedId: string | null;
  /** Ship highlighted on the ship select screen. */
  readonly highlightedShipId: string;
  readonly chosenShipId: string | null;
  readonly chosenLevelId: string | null;
  /** True during a screen transition, while input is ignored (P01-R15). */
  readonly transitioning: boolean;
  /** The result of the level just completed, while its overlay shows (P06-R03). */
  readonly levelResult: LevelResult | null;
  /**
   * The choice selected on a "Game over" panel with a checkpoint (P07-R08): 0 Continue, 1 level
   * select.
   */
  readonly choice: number;
  /** Goes up each time a level starts, or starts again from a checkpoint. */
  readonly attempt: number;
  /** Where the level being played started again from (P07-R08), or null from its start. */
  readonly resume: LevelCheckpoint | null;
  /**
   * Whether the level being played is paused (P12-R01): on the pause menu, or on the settings
   * screen opened from it.
   */
  readonly paused: boolean;
  /** Whether the pause menu asks `Leave the level?` (P12-R02); `choice` is then 0 No, 1 Yes. */
  readonly leaving: boolean;
  /** The music and sound effect volumes, in slider steps (P12-R04). */
  readonly volumes: Volumes;
}

/** Data and settings of a {@link MenuFlow}. */
export interface MenuFlowOptions {
  /** Ship ids in display order; the first one is the default selection. */
  readonly shipIds: readonly string[];
  readonly levels: LevelCatalog;
  /** Ship to highlight first instead of the default one (P01-R14). Ignored if unknown. */
  readonly initialShipId?: string | null;
  /** Input is ignored for this long after each screen change (P01-R15). */
  readonly transitionSeconds: number;
  /** …and for this long after the "Level complete" overlay shows (P06-R03). */
  readonly resultDelaySeconds?: number;
  /** The saved volumes (P12-R04); the highest step is `volumeSteps`. */
  readonly volumes?: Volumes;
  readonly volumeSteps?: number;
}
