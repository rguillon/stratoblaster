import { describe, expect, it } from 'vitest';
import { installTestApi, type GameTestApi } from '../../../src/debug/test-api';
import type { MenuAction } from '../../../src/input/menu-action';

describe('installTestApi', () => {
  it('ENG-52: exposes getState and sendAction on the target', () => {
    const target: { __GAME_TEST__?: GameTestApi } = {};
    const sent: MenuAction[] = [];
    installTestApi(target, {
      state: () => ({
        screen: 'title',
        selection: 0,
        selectedId: 'start',
        highlightedShipId: 'balanced',
        chosenShipId: null,
        chosenLevelId: null,
        transitioning: false,
        levelResult: null,
        choice: 0,
        attempt: 0,
      }),
      loadingProgress: () => [0, 1],
      game: () => undefined,
      send: (a) => sent.push(a),
    });
    expect(target.__GAME_TEST__?.getState()).toMatchObject({
      screen: 'title',
      loadingProgress: [0, 1],
      game: null,
    });
    target.__GAME_TEST__?.sendAction('confirm');
    expect(sent).toEqual(['confirm']);
    expect(() => target.__GAME_TEST__?.sendAction('fly' as MenuAction)).toThrow(TypeError);
  });
});
