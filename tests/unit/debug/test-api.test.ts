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
      perf: () => ({
        longFrames: 2,
        longestFrame: 80,
        frames: 100,
        lastLoad: 900,
        longestLoadStep: 120,
      }),
      readability: (share) =>
        Promise.resolve({
          player: share,
          enemy: null,
          enemyBullet: null,
          playerShot: null,
          backgroundLuminance: 0.2,
        }),
    });
    expect(target.__GAME_TEST__?.getState()).toMatchObject({
      // P13-R01: the perf numbers are readable from the test API.
      perf: { longFrames: 2, longestFrame: 80, frames: 100, lastLoad: 900 },
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

  it('P14-R08: forwards readability, and rejects shares outside 0..1', async () => {
    const target: { __GAME_TEST__?: GameTestApi } = {};
    installTestApi(target, {
      state: () => {
        throw new Error('unused');
      },
      audio: () => ({ music: null, sounds: [], context: 'none' }),
      highScore: () => 0,
      loadingProgress: () => [],
      game: () => undefined,
      send: () => undefined,
      bomb: () => undefined,
      step: () => undefined,
      stepHz: 60,
      perf: () => ({
        longFrames: 0,
        longestFrame: 0,
        frames: 0,
        lastLoad: null,
        longestLoadStep: null,
      }),
      readability: (share) =>
        Promise.resolve({
          player: 5,
          enemy: 4,
          enemyBullet: 6,
          playerShot: 3,
          backgroundLuminance: share,
        }),
    });
    const report = await target.__GAME_TEST__?.readability(0.02);
    expect(report?.backgroundLuminance).toBe(0.02);
    expect(() => target.__GAME_TEST__?.readability(2)).toThrow(RangeError);
  });
});
