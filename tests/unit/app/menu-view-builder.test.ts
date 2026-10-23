import { describe, expect, it } from 'vitest';
import { buildMenuView, type MenuViewContext } from '../../../src/app/menu-view-builder';
import type { MenuState } from '../../../src/app/menu-flow';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

const CTX: MenuViewContext = {
  game: SAMPLE_GAME,
  highScore: 12345,
  version: '1.2.3',
  commit: 'abc1234',
  cardsWidthPercent: 90,
  progress: 0.5,
};

const STATE: MenuState = {
  screen: 'title',
  selection: 0,
  selectedId: 'start',
  highlightedShipId: 'cube',
  chosenShipId: null,
  chosenLevelId: null,
  transitioning: false,
};

describe('buildMenuView', () => {
  it('P01-R02: the loading view carries the progress', () => {
    expect(buildMenuView({ ...STATE, screen: 'loading' }, CTX)).toEqual({
      kind: 'loading',
      text: 'Wait',
      progress: 0.5,
    });
  });

  it('P01-R04, ENG-83: the title view has the game title, high score, Start, hint and version', () => {
    expect(buildMenuView(STATE, CTX)).toEqual({
      kind: 'title',
      title: 'Sample Game',
      highScoreLabel: 'Best',
      highScore: 12345,
      start: 'Go',
      hint: 'Press go',
      version: '1.2.3',
      commit: 'abc1234',
    });
  });

  it('P01-R06: the ship select view has a card with name, speed and health per ship', () => {
    const view = buildMenuView({ ...STATE, screen: 'ship-select', selection: 1 }, CTX);
    expect(view).toMatchObject({ kind: 'ship-select', selected: 1, cardsWidthPercent: 90 });
    if (view.kind !== 'ship-select') throw new Error('wrong view');
    expect(view.ships.map((s) => s.title)).toEqual(['Cube', 'Brick']);
    expect(view.ships[1]?.lines).toEqual(['Speed ×0.5 (25 px/s)', 'HP 6']);
  });

  it('P01-R07: the level select view lists every level and which ones are locked', () => {
    const view = buildMenuView({ ...STATE, screen: 'level-select', selection: 2 }, CTX);
    expect(view).toMatchObject({
      kind: 'level-select',
      selected: 2,
      columns: 2,
      lockedText: 'Nope',
      levels: [
        { label: 'A', locked: false },
        { label: 'B', locked: true },
        { label: 'C', locked: false },
      ],
    });
  });

  it('P01-R08: the placeholder shows the chosen ship and level', () => {
    const state: MenuState = {
      ...STATE,
      screen: 'game',
      chosenShipId: 'brick',
      chosenLevelId: 'c',
    };
    expect(buildMenuView(state, CTX)).toEqual({
      kind: 'game',
      message: 'Brick @ C',
      hint: 'Esc',
      back: 'Back',
    });
  });

  it('falls back to the highlighted ship and an unknown level label', () => {
    const view = buildMenuView({ ...STATE, screen: 'game' }, CTX);
    expect(view).toMatchObject({ message: 'Cube @ ?' });
  });
});
