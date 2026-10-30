import type { GameDefinition } from '../core/content/game-definition';
import { shipCaption } from '../ui/ship-caption';
import type { LevelCompleteView, MenuView, PauseView, SettingsView } from '../ui/menu-view';
import type { MenuState } from './menu-flow';
import { SETTINGS_SLIDERS } from './settings-menu';

/** What a menu view needs besides the flow state. */
export interface MenuViewContext {
  readonly game: GameDefinition;
  readonly highScore: number;
  readonly version: string;
  readonly commit: string;
  /** Width of the row of ship cards, in % of the screen. */
  readonly cardsWidthPercent: number;
  /** Loading progress, 0..1. */
  readonly progress: number;
  /** The volume sliders' highest step (P12-R04). */
  readonly volumeSteps: number;
}

/** The pause menu (P12-R02), and its `Leave the level?` question when it shows. */
function pauseView(state: MenuState, ctx: MenuViewContext): PauseView {
  const { texts } = ctx.game;
  return {
    heading: texts.paused,
    entries: [texts.resume, texts.settings, texts.mainMenu],
    hint: texts.pauseHint,
    question: state.leaving
      ? { text: texts.leaveLevel, choices: [texts.no, texts.yes], selected: state.choice }
      : null,
  };
}

/** The settings screen (P12-R04): one slider per volume. */
function settingsView(state: MenuState, ctx: MenuViewContext): SettingsView {
  const { texts } = ctx.game;
  const labels = { music: texts.musicVolume, sfx: texts.sfxVolume };
  return {
    kind: 'settings',
    heading: texts.settings,
    hint: texts.settingsHint,
    back: texts.back,
    selected: state.selection,
    sliders: SETTINGS_SLIDERS.map((id) => ({
      label: labels[id],
      value: state.volumes[id],
      max: ctx.volumeSteps,
    })),
    overLevel: state.paused,
  };
}

/** The "Level complete" (or "Game over") panel (P06-R03), with its choices (P07-R08). */
function completeView(
  result: NonNullable<MenuState['levelResult']>,
  state: MenuState,
  ctx: MenuViewContext,
  label: (id: string | null) => string,
): LevelCompleteView {
  const { texts } = ctx.game;
  const choices = result.checkpoint && {
    labels: [texts.continueFromCheckpoint, texts.toLevelSelect],
    selected: state.choice,
  };
  return {
    heading: result.outcome === 'over' ? texts.gameOver : texts.levelComplete,
    over: result.outcome === 'over',
    level: label(result.levelId),
    enemies: texts.enemiesDestroyed(result.destroyed, result.spawned),
    score: texts.finalScore(result.score),
    ...(result.newHighScore ? { newHighScore: texts.newHighScore } : {}),
    hint: texts.continueHint,
    ...(choices ? { choices } : {}),
  };
}

/** The entry taps select on the game screen: the pause menu's, or the panel's choice. */
function selectedOnGame(state: MenuState, paused: PauseView | null): number {
  if (paused) return paused.question ? state.choice : state.selection;
  return state.levelResult?.checkpoint ? state.choice : 0;
}

function gameView(state: MenuState, ctx: MenuViewContext): MenuView {
  const { texts, levels } = ctx.game;
  const label = (id: string | null) => levels.levels.find((l) => l.id === id)?.label ?? '?';
  const result = state.levelResult;
  const paused = state.screen === 'pause' ? pauseView(state, ctx) : null;
  return {
    kind: 'game',
    level: texts.gameLevel(label(state.chosenLevelId)),
    fire: texts.fire,
    pause: texts.pauseButton,
    paused,
    selected: selectedOnGame(state, paused),
    complete: result && completeView(result, state, ctx, label),
  };
}

/**
 * Builds what the menu overlay shows for the current state (P01-R04, R06, R07, P06-R02, R03,
 * P12-R02, P12-R04).
 */
export function buildMenuView(state: MenuState, ctx: MenuViewContext): MenuView {
  const { game } = ctx;
  const { texts } = game;
  switch (state.screen) {
    case 'loading':
      return { kind: 'loading', text: texts.loading, progress: ctx.progress };
    case 'title':
      return {
        kind: 'title',
        title: game.title,
        highScoreLabel: texts.highScore,
        highScore: ctx.highScore,
        start: texts.start,
        settings: texts.settings,
        selected: state.selection,
        hint: texts.startHint,
        version: ctx.version,
        commit: ctx.commit,
      };
    case 'ship-select':
      return {
        kind: 'ship-select',
        heading: texts.chooseShip,
        hint: texts.chooseShipHint,
        back: texts.back,
        selected: state.selection,
        ships: game.playerShips.ships.map(({ id }) => shipCaption(game.playerShips, id)),
        cardsWidthPercent: ctx.cardsWidthPercent,
      };
    case 'level-select':
      return {
        kind: 'level-select',
        heading: texts.chooseLevel,
        hint: texts.chooseLevelHint,
        back: texts.back,
        selected: state.selection,
        columns: game.levels.columns,
        levels: game.levels.levels.map((l) => ({ label: l.label, locked: !l.unlocked })),
        lockedText: texts.locked,
      };
    case 'game':
    case 'pause':
      return gameView(state, ctx);
    case 'settings':
      return settingsView(state, ctx);
  }
}
