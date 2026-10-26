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
  levelResult: null,
  choice: 0,
  attempt: 0,
  resume: null,
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

  it('P06-R02: the game screen shows the level played and the touch fire button', () => {
    const state: MenuState = {
      ...STATE,
      screen: 'game',
      chosenShipId: 'brick',
      chosenLevelId: 'c',
    };
    expect(buildMenuView(state, CTX)).toEqual({
      kind: 'game',
      level: 'LC',
      fire: 'Pew',
      complete: null,
      selected: 0,
    });
  });

  it('P06-R03: after the level, the overlay shows the level and the destroyed / spawned counts', () => {
    const state: MenuState = {
      ...STATE,
      screen: 'game',
      chosenLevelId: 'c',
      levelResult: { levelId: 'c', destroyed: 7, spawned: 9, outcome: 'complete', score: 0 },
    };
    expect(buildMenuView(state, CTX)).toMatchObject({
      complete: { heading: 'Done', over: false, level: 'C', enemies: '7/9', hint: 'Go on' },
    });
    const over: MenuState = {
      ...state,
      levelResult: { levelId: 'c', destroyed: 7, spawned: 9, outcome: 'over', score: 0 },
    };
    expect(buildMenuView(over, CTX)).toMatchObject({ complete: { heading: 'Lost', over: true } });
    expect(buildMenuView(over, CTX)).not.toHaveProperty('complete.choices');
  });

  it('P11-R03: the overlay shows the score, and says when it beat the high score', () => {
    const result = {
      levelId: 'c',
      destroyed: 7,
      spawned: 9,
      outcome: 'complete',
      score: 2500,
    } as const;
    const state: MenuState = { ...STATE, screen: 'game', chosenLevelId: 'c', levelResult: result };
    expect(buildMenuView(state, CTX)).toMatchObject({ complete: { score: 'Pts 2500' } });
    expect(buildMenuView(state, CTX)).not.toHaveProperty('complete.newHighScore');
    const best: MenuState = { ...state, levelResult: { ...result, newHighScore: true } };
    expect(buildMenuView(best, CTX)).toMatchObject({ complete: { newHighScore: 'Record!' } });
  });

  it('P07-R08: a game over after the mini boss offers Continue or level select', () => {
    const checkpoint = {
      progress: 50,
      bossesPassed: 1,
      score: 0,
      weapons: { weapon: 'pea', levels: {} },
    };
    const state: MenuState = {
      ...STATE,
      screen: 'game',
      chosenLevelId: 'c',
      choice: 1,
      levelResult: {
        levelId: 'c',
        destroyed: 7,
        spawned: 9,
        outcome: 'over',
        score: 0,
        checkpoint,
      },
    };
    expect(buildMenuView(state, CTX)).toMatchObject({
      selected: 1,
      complete: { over: true, choices: { labels: ['Again', 'Levels'], selected: 1 } },
    });
  });

  it('shows an unknown level label as "?"', () => {
    const view = buildMenuView({ ...STATE, screen: 'game' }, CTX);
    expect(view).toMatchObject({ level: 'L?' });
  });
});
