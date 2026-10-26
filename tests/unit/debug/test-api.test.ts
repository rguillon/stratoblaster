import { describe, expect, it } from 'vitest';
import { installTestApi, type GameTestApi } from '../../../src/debug/test-api';
import type { MenuAction } from '../../../src/input/menu-action';

describe('installTestApi', () => {
  it('ENG-52: exposes getState, sendAction, step and advance on the target', () => {
    const target: { __GAME_TEST__?: GameTestApi } = {};
    const sent: MenuAction[] = [];
    const stepped: [number, boolean][] = [];
    let bombs = 0;
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
        paused: false,
        leaving: false,
        volumes: { music: 6, sfx: 8 },
      }),
      audio: () => ({ music: 'menu', sounds: ['menu-move'], context: 'none' }),
      highScore: () => 4200,
      loadingProgress: () => [0, 1],
      game: () => undefined,
      send: (a) => sent.push(a),
      bomb: () => bombs++,
      step: (frames, render) => stepped.push([frames, render]),
      stepHz: 60,
    });
    expect(target.__GAME_TEST__?.getState()).toMatchObject({
      screen: 'title',
      loadingProgress: [0, 1],
      game: null,
      highScore: 4200,
      paused: false,
      volumes: { music: 6, sfx: 8 },
      music: 'menu',
      sounds: ['menu-move'],
      audio: 'none',
    });
    target.__GAME_TEST__?.sendAction('confirm');
    expect(sent).toEqual(['confirm']);
    // P12-R12: `pause` and `resume` are actions too.
    target.__GAME_TEST__?.sendAction('pause');
    target.__GAME_TEST__?.sendAction('resume');
    expect(sent).toEqual(['confirm', 'pause', 'resume']);
    // P11-R08: `bomb` sets a bomb off, as the bomb key would.
    target.__GAME_TEST__?.sendAction('bomb');
    expect([sent, bombs]).toEqual([['confirm', 'pause', 'resume'], 1]);
    expect(() => target.__GAME_TEST__?.sendAction('fly' as MenuAction)).toThrow(TypeError);
    target.__GAME_TEST__?.step(3);
    target.__GAME_TEST__?.step(2, false);
    // advance(seconds) steps whole frames, rounded up, and renders.
    target.__GAME_TEST__?.advance(4);
    target.__GAME_TEST__?.advance(0.01);
    expect(stepped).toEqual([
      [3, true],
      [2, false],
      [240, true],
      [1, true],
    ]);
    expect(() => target.__GAME_TEST__?.step(-1)).toThrow(RangeError);
    expect(() => target.__GAME_TEST__?.step(1.5)).toThrow(RangeError);
    expect(() => target.__GAME_TEST__?.advance(-1)).toThrow(RangeError);
  });
});
