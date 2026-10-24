import { canTransition, type MenuScreen } from '../core/menu/menu-screen';
import { moveCursor, type GridShape } from '../core/menu/grid-cursor';
import { firstUnlockedLevel, type LevelCatalog } from '../core/content/level-catalog';
import type { LevelResult } from '../core/systems/level-run';
import { isMenuDirection, type MenuCommand, type MenuDirection } from '../input/menu-action';

/** What a command did, so the presentation can give feedback. */
export type MenuFeedback = 'none' | 'moved' | 'screen' | 'locked';

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
}

const TITLE_ENTRY = 'start';

/**
 * Screen state machine of the menus (P01-R01): Title → Ship select → Level select → Game,
 * with Back on each screen. Pure: no Babylon, no DOM, time comes from {@link update}.
 */
export class MenuFlow {
  #screen: MenuScreen = 'loading';
  #shipIndex: number;
  #levelIndex: number;
  #chosenShipId: string | null = null;
  #chosenLevelId: string | null = null;
  #transitionLeft = 0;
  #revision = 0;
  #result: LevelResult | null = null;

  constructor(private readonly options: MenuFlowOptions) {
    if (options.shipIds.length === 0) throw new Error('The menu needs at least one ship');
    if (options.levels.levels.length === 0) throw new Error('The menu needs at least one level');
    this.#shipIndex = Math.max(0, options.shipIds.indexOf(options.initialShipId ?? ''));
    this.#levelIndex = firstUnlockedLevel(options.levels);
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
    };
  }

  /** Goes to `screen` if the flow allows it (P01-R01). Returns false and changes nothing otherwise. */
  goTo(screen: MenuScreen): boolean {
    if (!canTransition(this.#screen, screen)) return false;
    if (screen === 'level-select') this.#levelIndex = firstUnlockedLevel(this.options.levels);
    this.#result = null;
    this.#screen = screen;
    this.#transitionLeft = this.options.transitionSeconds;
    this.#changed();
    return true;
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
    if (typeof command !== 'string') return this.#select(command.select);
    if (isMenuDirection(command)) return this.#move(command);
    if (command === 'back') return this.#back();
    return this.#confirm();
  }

  #changed(): void {
    this.#revision++;
  }

  #shipId(index: number): string {
    return this.options.shipIds[index] ?? '';
  }

  #selection(): number {
    if (this.#screen === 'ship-select') return this.#shipIndex;
    if (this.#screen === 'level-select') return this.#levelIndex;
    return 0;
  }

  #selectedId(selection: number): string | null {
    switch (this.#screen) {
      case 'title':
        return TITLE_ENTRY;
      case 'ship-select':
        return this.#shipId(selection);
      case 'level-select':
        return this.options.levels.levels[selection]?.id ?? null;
      default:
        return null;
    }
  }

  #grid(): GridShape | undefined {
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
    if (this.#screen === 'ship-select') this.#shipIndex = index;
    else this.#levelIndex = index;
    this.#changed();
    return 'moved';
  }

  #move(direction: MenuDirection): MenuFeedback {
    const grid = this.#grid();
    if (!grid) return 'none';
    return this.#setSelection(moveCursor(this.#selection(), direction, grid));
  }

  #select(index: number): MenuFeedback {
    const grid = this.#grid();
    if (!grid || !Number.isInteger(index) || index < 0 || index >= grid.count) return 'none';
    return this.#setSelection(index);
  }

  #back(): MenuFeedback {
    const previous: Partial<Record<MenuScreen, MenuScreen>> = {
      'ship-select': 'title',
      'level-select': 'ship-select',
      game: 'title',
    };
    const target = previous[this.#screen];
    return target && this.goTo(target) ? 'screen' : 'none';
  }

  #confirm(): MenuFeedback {
    switch (this.#screen) {
      case 'title':
        return this.goTo('ship-select') ? 'screen' : 'none';
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
    const { levels } = this.options.levels;
    const played = levels.findIndex((l) => l.id === this.#chosenLevelId);
    const won = this.#result.outcome === 'complete';
    const next = won && levels[played + 1]?.unlocked ? played + 1 : played;
    if (!this.goTo('level-select')) return 'none';
    this.#levelIndex = Math.max(0, next);
    return 'screen';
  }

  #confirmLevel(): MenuFeedback {
    const level = this.options.levels.levels[this.#levelIndex];
    if (!level?.unlocked) return 'locked';
    this.#chosenLevelId = level.id;
    return this.goTo('game') ? 'screen' : 'none';
  }
}
