import { describe, expect, it } from 'vitest';
import {
  installViewerTestApi,
  stepFrames,
  type ViewerTestApi,
} from '../../../src/debug/viewer-test-api';
import { installBossViewerTestApi } from '../../../src/debug/boss-viewer-test-api';

function recorder() {
  const calls: (number | 'render')[] = [];
  return {
    calls,
    hooks: { frame: (dt: number) => calls.push(dt), render: () => calls.push('render') },
  };
}

describe('stepFrames', () => {
  it('ENG-52: runs whole frames of 1/60 s, then renders once', () => {
    const { calls, hooks } = recorder();
    stepFrames(hooks, 2);
    stepFrames(hooks, 0);
    expect(calls).toEqual([1 / 60, 1 / 60, 'render', 'render']);
    expect(() => {
      stepFrames(hooks, -1);
    }).toThrow(RangeError);
    expect(() => {
      stepFrames(hooks, 0.5);
    }).toThrow(RangeError);
  });
});

describe('installViewerTestApi', () => {
  it('ENG-52, P03-R10, P04: installs a step-only API under the name given', () => {
    const target: { __SCENERY_TEST__?: ViewerTestApi } = {};
    const { calls, hooks } = recorder();
    installViewerTestApi(target, '__SCENERY_TEST__', hooks);
    target.__SCENERY_TEST__?.step(1);
    expect(calls).toEqual([1 / 60, 'render']);
  });
});

describe('installBossViewerTestApi', () => {
  it('ENG-52, P07-R09: steps the bosses page, then renders once', () => {
    const target: { __BOSSES_TEST__?: { step(frames: number): void } } = {};
    const { calls, hooks } = recorder();
    installBossViewerTestApi(target, { ...hooks, state: () => ({}) as never });
    target.__BOSSES_TEST__?.step(2);
    expect(calls).toEqual([1 / 60, 1 / 60, 'render']);
  });
});
