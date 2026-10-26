import type { GameDefinition } from '../core/content/game-definition';
import type { LevelResult } from '../core/systems/level-run';
import type { MenuCommand } from '../input/menu-action';
import type { MenuActionSource } from '../input/menu-input';
import type { KeyValueStorage } from '../platform/key-value-storage';
import type { MenuView } from '../ui/menu-view';
import { MenuFlow, type MenuState } from './menu-flow';
import { buildMenuView } from './menu-view-builder';
import { loadSavedChoices, saveHighScore, saveLastShip } from './saved-choices';

/** Where the controller shows menus. Implemented by `ui/MenuOverlay`. */
export interface MenuDisplay {
  show(view: MenuView): void;
  shakeSelected(text: string): void;
}

/** Collaborators of a {@link MenuController}. */
export interface MenuControllerDeps {
  readonly display: MenuDisplay;
  readonly input: MenuActionSource;
  readonly storage: KeyValueStorage;
  readonly transitionSeconds: number;
  /** Input is ignored this long after the "Level complete" overlay shows (P06-R03). */
  readonly resultDelaySeconds?: number;
  readonly cardsWidthPercent: number;
  readonly version: string;
  readonly commit: string;
  /** Called after every state change, e.g. to update the 3D scenes. */
  readonly onChange?: (state: MenuState) => void;
}

/**
 * Runs the menus: feeds input to the {@link MenuFlow}, shows the matching view, gives the
 * "locked" feedback and remembers the chosen ship (P01-R14). Free of Babylon.
 */
export class MenuController {
  readonly flow: MenuFlow;
  #highScore: number;
  #progress = 0;
  #shownRevision = -1;
  #shownProgress = -1;
  #savedShipId: string | null;

  constructor(
    private readonly game: GameDefinition,
    private readonly deps: MenuControllerDeps,
  ) {
    const saved = loadSavedChoices(deps.storage, game.id);
    this.#highScore = saved.highScore;
    this.#savedShipId = saved.lastShipId;
    this.flow = new MenuFlow({
      shipIds: game.playerShips.ships.map((s) => s.id),
      levels: game.levels,
      initialShipId: saved.lastShipId,
      transitionSeconds: deps.transitionSeconds,
      ...(deps.resultDelaySeconds === undefined
        ? {}
        : { resultDelaySeconds: deps.resultDelaySeconds }),
    });
    this.refresh();
  }

  /** Loading progress shown on the loading screen, 0..1. */
  setProgress(progress: number): void {
    this.#progress = progress;
    this.refresh();
  }

  finishLoading(): void {
    this.flow.finishLoading();
    this.refresh();
  }

  /** The best score saved so far (P01-R04, P11-R03). */
  get highScore(): number {
    return this.#highScore;
  }

  /**
   * A level attempt ended with `score` (P11-R03): above the high score, it is saved as the new
   * one, and the title screen shows it. Returns whether it beat the high score.
   */
  recordScore(score: number): boolean {
    if (!(score > this.#highScore)) return false;
    this.#highScore = score;
    saveHighScore(this.deps.storage, this.game.id, score);
    return true;
  }

  /**
   * Shows the "Level complete" (or "Game over") overlay (P06-R03), after saving its score if it
   * beat the high score (P11-R03): the overlay then says so.
   */
  completeLevel(result: LevelResult): void {
    const beaten = this.recordScore(result.score);
    this.flow.completeLevel(beaten ? { ...result, newHighScore: true } : result);
    this.refresh();
  }

  /** Starts a level straight away (P06-R09 debug options); see `MenuFlow.playDirect`. */
  playDirect(shipId: string, levelId: string): boolean {
    const started = this.flow.playDirect(shipId, levelId);
    this.refresh();
    return started;
  }

  /** Applies one command (from any device, or the test API). */
  command(command: MenuCommand): void {
    if (this.flow.dispatch(command) === 'locked') {
      this.deps.display.shakeSelected(this.game.texts.locked);
    }
    this.refresh();
  }

  /** Advances time by one frame: transition timer, then the input of the frame. */
  tick(dtSeconds: number): void {
    this.flow.update(dtSeconds);
    for (const action of this.deps.input.update(dtSeconds)) this.command(action);
    this.refresh();
  }

  /** Shows the current view if anything changed since the last call. */
  refresh(): void {
    const { revision } = this.flow;
    if (revision === this.#shownRevision && this.#progress === this.#shownProgress) return;
    this.#shownRevision = revision;
    this.#shownProgress = this.#progress;
    const state = this.flow.state;
    this.#rememberShip(state.chosenShipId);
    this.deps.display.show(
      buildMenuView(state, {
        game: this.game,
        highScore: this.#highScore,
        version: this.deps.version,
        commit: this.deps.commit,
        cardsWidthPercent: this.deps.cardsWidthPercent,
        progress: this.#progress,
      }),
    );
    this.deps.onChange?.(state);
  }

  #rememberShip(shipId: string | null): void {
    if (shipId === null || shipId === this.#savedShipId) return;
    saveLastShip(this.deps.storage, this.game.id, shipId);
    this.#savedShipId = shipId;
  }
}
