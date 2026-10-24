import { describe, expect, it } from 'vitest';
import {
  installEnemyViewerTestApi,
  type EnemyViewerTestApi,
  type EnemyViewerTestState,
} from '../../../src/debug/enemy-viewer-test-api';

const STATE: EnemyViewerTestState = {
  enemies: [{ model: 'gnat', x: 1, y: 2, health: 10 }],
  bullets: 3,
  missiles: 0,
  lasers: ['warning'],
  kills: 4,
  score: 200,
  player: { x: 240, y: 90 },
};

describe('installEnemyViewerTestApi', () => {
  it('ENG-52, P05-R11: exposes the enemies page state and steps it frame by frame', () => {
    const target: { __ENEMIES_TEST__?: EnemyViewerTestApi } = {};
    const frames: number[] = [];
    installEnemyViewerTestApi(target, { state: () => STATE, frame: (dt) => frames.push(dt) });
    expect(target.__ENEMIES_TEST__?.getState()).toEqual(STATE);
    target.__ENEMIES_TEST__?.step(3);
    expect(frames).toEqual([1 / 60, 1 / 60, 1 / 60]);
  });
});
