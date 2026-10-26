import { canTransition, type MenuScreen } from '../core/menu/menu-screen';
import { moveCursor, type GridShape } from '../core/menu/grid-cursor';
import { firstUnlockedLevel } from '../core/content/level-catalog';
import type { LevelCheckpoint, LevelResult } from '../core/systems/level-run';
import {
  isMenuDirection,
  type MenuAction,
  type MenuCommand,
  type MenuDirection,
} from '../input/menu-action';
import { PauseMenu, type PauseOutcome } from './pause-menu';
import { SettingsMenu, type Volumes } from './settings-menu';
import type { MenuFeedback, MenuFlowOptions, MenuState } from './menu-state';

export type { MenuFeedback, MenuFlowOptions, MenuState } from './menu-state';

/** The title screen's entries (P01-R04, P12-R04). */
const TITLE_ENTRIES = ['start', 'settings'] as const;

/** Volumes and slider size when the options give none. */
const DEFAULT_VOLUMES: Volumes = { music: 10, sfx: 10 };
const DEFAULT_VOLUME_STEPS = 10;

/**
 * Screen state machine of the menus (P01-R01): Title → Ship select → Level select → Game,
 * with Back on each screen; Game ⇄ Pause, and Settings from the title or the pause menu
 * (P12-R02, P12-R04). Pure: no Babylon, no DOM, time comes from {@link update}.
 */
export class MenuFlow {
  #screen: MenuScreen = 'loading';
  #titleIndex = 0;
  #shipIndex: number;
  #levelIndex: number;
  #chosenShipId: string | null = null;
  #chosenLevelId: string | null = null;
  #transitionLeft = 0;
  #revision = 0;
  #result: LevelResult | null = null;
  #choice = 0;
  #attempt = 0;
  #resume: LevelCheckpoint | null = null;
  readonly #pause = new PauseMenu();
  readonly #settings: SettingsMenu;
  /** The screen the settings screen was opened from, which Back goes back to. */
  #settingsFrom: MenuScreen = 'title';

  constructor(private readonly options: MenuFlowOptions) {
    if (options.shipIds.length === 0) throw new Error('The menu needs at least one ship');
    if (options.levels.levels.length === 0) throw new Error('The menu needs at least one level');
    this.#shipIndex = Math.max(0, options.shipIds.indexOf(options.initialShipId ?? ''));
    this.#levelIndex = firstUnlockedLevel(options.levels);
    this.#settings = new SettingsMenu(
      options.volumes ?? DEFAULT_VOLUMES,
      options.volumeSteps ?? DEFAULT_VOLUME_STEPS,
    );
  }

  /** Increases on every state change, so views know when to refresh. */
  get revision(): number {
    return this.#revision;
  }

  get state(): MenuState {
    const selection = this.#selection();
    return {
      screen: this.#screen,
      selection,
      selectedId: this.#selectedId(selection),
      highlightedShipId: this.#shipId(this.#shipIndex),
      chosenShipId: this.#chosenShipId,
      chosenLevelId: this.#chosenLevelId,
      transitioning: this.#transitionLeft > 0,
      levelResult: this.#result,
      choice: this.#screen === 'pause' ? this.#pause.choice : this.#choice,
      attempt: this.#attempt,
      resume: this.#resume,
      paused: this.paused,
      leaving: this.#screen === 'pause' && this.#pause.leaving,
      volumes: this.#settings.volumes,
    };
  }

  /** Whether the level being played is paused (P12-R01). */
  get paused(): boolean {
    return (
      this.#screen === 'pause' || (this.#screen === 'settings' && this.#settingsFrom === 'pause')
    );
  }

  /** Goes to `screen` if the flow allows it (P01-R01). Returns false and changes nothing otherwise. */
  goTo(screen: MenuScreen): boolean {
    if (!canTransition(this.#screen, screen)) return false;
    if (screen === 'level-select') this.#levelIndex = firstUnlockedLevel(this.options.levels);
    if (screen === 'game') this.#startLevel(null);
    if (screen === 'settings') this.#openSettings();
    if (screen === 'pause' && this.#screen === 'game') this.#pause.open();
    if (screen === 'title' && this.#screen !== 'settings') this.#titleIndex = 0;
    this.#result = null;
    this.#screen = screen;
    this.#transitionLeft = this.options.transitionSeconds;
    this.#changed();
    return true;
  }

  /**
   * Pauses the level being played (P12-R01, P12-R03): the pause menu shows. Ignored on other
   * screens, and on the "Level complete" or "Game over" panel.
   */
  pause(): boolean {
    if (this.#screen !== 'game' || this.#result) return false;
    return this.goTo('pause');
  }

  /** Called when loading completes: shows the title screen. */
  finishLoading(): void {
    this.goTo('title');
  }

  /**
   * Shows the "Level complete" (or "Game over") overlay on the game screen (P06-R03); Confirm
   * then goes to the level select screen. Ignored on other screens.
   */
  completeLevel(result: LevelResult): void {
    if (this.#screen !== 'game' || this.#result) return;
    this.#result = result;
    this.#choice = 0;
    this.#transitionLeft = this.options.resultDelaySeconds ?? this.options.transitionSeconds;
    this.#changed();
  }

  /**
   * Starts a level straight away with the given ship, skipping the menus (P06-R09 debug
   * options). Returns false, and changes nothing, if the ship or the level is unknown or the
   * level is locked.
   */
  playDirect(shipId: string, levelId: string): boolean {
    const shipIndex = this.options.shipIds.indexOf(shipId);
    const levelIndex = this.options.levels.levels.findIndex((l) => l.id === levelId);
    if (shipIndex < 0 || !this.options.levels.levels[levelIndex]?.unlocked) return false;
    this.#shipIndex = shipIndex;
    this.#levelIndex = levelIndex;
    this.#chosenShipId = shipId;
    this.#chosenLevelId = levelId;
    this.#result = null;
    this.#startLevel(null);
    this.#screen = 'game';
    this.#transitionLeft = 0;
    this.#changed();
    return true;
  }

  /** Advances the transition timer. */
  update(dtSeconds: number): void {
    if (this.#transitionLeft <= 0) return;
    this.#transitionLeft = Math.max(0, this.#transitionLeft - dtSeconds);
    if (this.#transitionLeft === 0) this.#changed();
  }

  /** Applies a menu command to the current screen. Ignored while loading or in a transition. */
  dispatch(command: MenuCommand): MenuFeedback {
    if (this.#screen === 'loading' || this.#transitionLeft > 0) return 'none';
    if (typeof command === 'string') return this.#action(command);
    if ('select' in command) return this.#select(command.select);
    return this.#adjusted(this.#settings.set(command.set, command.value));
  }

  #action(command: MenuAction): MenuFeedback {
    if (this.#screen === 'pause') return this.#onPause(command);
    if (this.#screen === 'settings') return this.#onSettings(command);
    if (this.#screen === 'game' && !this.#result) return this.#inLevel(command);
    if (isMenuDirection(command)) return this.#move(command);
    if (command === 'back' || command === 'cancel') return this.#back();
    return command === 'confirm' ? this.#confirm() : 'none';
  }

  /**
   * In a level (P12-R01): Escape, P, Start and Select pause it; Back and the other actions do
   * nothing.
   */
  #inLevel(command: MenuAction): MenuFeedback {
    if (command !== 'pause' && command !== 'cancel') return 'none';
    return this.pause() ? 'paused' : 'none';
  }

  /** The pause menu (P12-R02): Back, Escape, P and Start resume the level. */
  #onPause(command: MenuAction): MenuFeedback {
    if (isMenuDirection(command)) return this.#pauseOutcome(this.#pause.move(command));
    const confirm = command === 'confirm';
    return this.#pauseOutcome(confirm ? this.#pause.confirm() : this.#pause.back());
  }

  #pauseOutcome(outcome: PauseOutcome): MenuFeedback {
    if (outcome === 'resume') return this.#resumeLevel();
    if (outcome === 'settings' || outcome === 'leave') {
      return this.goTo(outcome === 'leave' ? 'title' : 'settings') ? 'screen' : 'none';
    }
    if (outcome !== 'none') this.#changed();
    return outcome === 'ask' ? 'screen' : outcome;
  }

  /** Back to the level, as it was: not a new attempt (P12-R01). */
  #resumeLevel(): MenuFeedback {
    this.#screen = 'game';
    this.#transitionLeft = this.options.transitionSeconds;
    this.#changed();
    return 'resumed';
  }

  /** The settings screen (P12-R04): Back returns to where it was opened from. */
  #onSettings(command: MenuAction): MenuFeedback {
    if (isMenuDirection(command)) return this.#adjusted(this.#settings.move(command));
    if (command !== 'back' && command !== 'cancel') return 'none';
    return this.goTo(this.#settingsFrom) ? 'screen' : 'none';
  }

  #adjusted(feedback: 'none' | 'moved' | 'adjusted'): MenuFeedback {
    if (feedback !== 'none') this.#changed();
    return feedback;
  }

  #openSettings(): void {
    this.#settingsFrom = this.#screen;
    this.#settings.open();
  }

  #changed(): void {
    this.#revision++;
  }

  /** A new attempt at the chosen level, from its start or from `checkpoint`. */
  #startLevel(checkpoint: LevelCheckpoint | null): void {
    this.#attempt++;
    this.#resume = checkpoint;
  }

  /** The "Game over" panel offers Continue or level select (P07-R08). */
  get #choosing(): boolean {
    return this.#screen === 'game' && this.#result?.checkpoint !== undefined;
  }

  #shipId(index: number): string {
    return this.options.shipIds[index] ?? '';
  }

  #selection(): number {
    const selections: Partial<Record<MenuScreen, number>> = {
      title: this.#titleIndex,
      'ship-select': this.#shipIndex,
      'level-select': this.#levelIndex,
      pause: this.#pause.selection,
      settings: this.#settings.selection,
    };
    return selections[this.#screen] ?? 0;
  }

  #selectedId(selection: number): string | null {
    switch (this.#screen) {
      case 'title':
        return TITLE_ENTRIES[selection] ?? null;
      case 'pause':
        return this.#pause.selectedId;
      case 'settings':
        return this.#settings.selectedId;
      case 'ship-select':
        return this.#shipId(selection);
      case 'level-select':
        return this.options.levels.levels[selection]?.id ?? null;
      default:
        return null;
    }
  }

  #grid(): GridShape | undefined {
    if (this.#screen === 'title') return { count: TITLE_ENTRIES.length, columns: 1, wrap: false };
    if (this.#screen === 'ship-select') {
      const count = this.options.shipIds.length;
      return { count, columns: count, wrap: true };
    }
    if (this.#screen === 'level-select') {
      const { levels, columns } = this.options.levels;
      return { count: levels.length, columns, wrap: false };
    }
    return undefined;
  }

  #setSelection(index: number): MenuFeedback {
    if (index === this.#selection()) return 'none';
    if (this.#screen === 'title') this.#titleIndex = index;
    else if (this.#screen === 'ship-select') this.#shipIndex = index;
    else this.#levelIndex = index;
    this.#changed();
    return 'moved';
  }

  #move(direction: MenuDirection): MenuFeedback {
    if (this.#choosing) return this.#choose(direction === 'left' || direction === 'up' ? 0 : 1);
    const grid = this.#grid();
    if (!grid) return 'none';
    return this.#setSelection(moveCursor(this.#selection(), direction, grid));
  }

  #select(index: number): MenuFeedback {
    if (this.#screen === 'pause') return this.#pauseOutcome(this.#pause.select(index));
    if (this.#screen === 'settings') return this.#adjusted(this.#settings.select(index));
    if (this.#choosing) return index === 0 || index === 1 ? this.#choose(index) : 'none';
    const grid = this.#grid();
    if (!grid || !Number.isInteger(index) || index < 0 || index >= grid.count) return 'none';
    return this.#setSelection(index);
  }

  #back(): MenuFeedback {
    const previous: Partial<Record<MenuScreen, MenuScreen>> = {
      'ship-select': 'title',
      'level-select': 'ship-select',
    };
    const target = previous[this.#screen];
    return target && this.goTo(target) ? 'screen' : 'none';
  }

  #confirm(): MenuFeedback {
    switch (this.#screen) {
      case 'title':
        return this.goTo(this.#titleIndex === 0 ? 'ship-select' : 'settings') ? 'screen' : 'none';
      case 'ship-select':
        this.#chosenShipId = this.#shipId(this.#shipIndex);
        return this.goTo('level-select') ? 'screen' : 'none';
      case 'level-select':
        return this.#confirmLevel();
      case 'game':
        return this.#leaveCompletedLevel();
      default:
        return 'none';
    }
  }

  /**
   * From the "Level complete" overlay to the level select screen, on the next level; from the
   * "Game over" overlay, on the level played (GD-20).
   */
  #leaveCompletedLevel(): MenuFeedback {
    if (!this.#result) return 'none';
    const { checkpoint } = this.#result;
    if (checkpoint && this.#choice === 0) return this.#continue(checkpoint);
    const { levels } = this.options.levels;
    const played = levels.findIndex((l) => l.id === this.#chosenLevelId);
    const won = this.#result.outcome === 'complete';
    const next = won && levels[played + 1]?.unlocked ? played + 1 : played;
    if (!this.goTo('level-select')) return 'none';
    this.#levelIndex = Math.max(0, next);
    return 'screen';
  }

  #choose(choice: number): MenuFeedback {
    if (choice === this.#choice) return 'none';
    this.#choice = choice;
    this.#changed();
    return 'moved';
  }

  /** The level starts again from its checkpoint, on the game screen (P07-R08). */
  #continue(checkpoint: LevelCheckpoint): MenuFeedback {
    this.#result = null;
    this.#startLevel(checkpoint);
    this.#transitionLeft = this.options.transitionSeconds;
    this.#changed();
    return 'screen';
  }

  #confirmLevel(): MenuFeedback {
    const level = this.options.levels.levels[this.#levelIndex];
    if (!level?.unlocked) return 'locked';
    this.#chosenLevelId = level.id;
    return this.goTo('game') ? 'screen' : 'none';
  }
}
