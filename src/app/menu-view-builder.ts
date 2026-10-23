import type { GameDefinition } from '../core/content/game-definition';
import { findPlayerShip } from '../core/entities/player-ship';
import { shipCaption } from '../ui/ship-caption';
import type { MenuView } from '../ui/menu-view';
import type { MenuState } from './menu-flow';

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
}

function gameView(state: MenuState, ctx: MenuViewContext): MenuView {
  const { game } = ctx;
  const ship = findPlayerShip(game.playerShips, state.chosenShipId ?? state.highlightedShipId);
  const level = game.levels.levels.find((l) => l.id === state.chosenLevelId);
  return {
    kind: 'game',
    message: game.texts.gamePlaceholder(ship.name, level?.label ?? '?'),
    hint: game.texts.gameHint,
    back: game.texts.back,
  };
}

/** Builds what the menu overlay shows for the current state (P01-R04, R06, R07, R08). */
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
      return gameView(state, ctx);
  }
}
