import { describe, expect, it } from 'vitest';
import { PerfMonitor } from '../../../src/app/perf-monitor';

function monitor(): { perf: PerfMonitor; frame: (ms: number) => void; wait: (ms: number) => void } {
  let now = 0;
  const perf = new PerfMonitor(50, () => now);
  return {
    perf,
    frame: (ms) => {
      perf.frameStarted();
      now += ms;
      perf.frameEnded();
    },
    wait: (ms) => {
      now += ms;
    },
  };
}

describe('PerfMonitor', () => {
  it('P13-R01: counts the frames longer than long_frame_ms and keeps the longest', () => {
    const { perf, frame } = monitor();
    for (const ms of [16, 51, 20, 120, 50]) frame(ms);
    expect(perf.numbers).toEqual({
      longFrames: 2,
      longestFrame: 120,
      frames: 5,
      lastLoad: null,
      longestLoadStep: null,
    });
  });

  it('P13-R01, P13-R03: times a level loading, its longest step, then skips its first frames', () => {
    const { perf, frame, wait } = monitor();
    frame(200);
    perf.loadStarted();
    expect(perf.loading).toBe(true);
    // The loading frames do not count as long frames: they are its steps.
    frame(150);
    wait(10);
    frame(300);
    perf.loadFinished(2);
    expect(perf.loading).toBe(false);
    expect(perf.numbers).toMatchObject({
      lastLoad: 460,
      longestLoadStep: 300,
      longFrames: 0,
      longestFrame: 0,
      frames: 0,
    });
    // P13-R04: the level's first frames (its first second) are skipped.
    frame(90);
    frame(90);
    frame(60);
    expect(perf.numbers).toMatchObject({ frames: 1, longFrames: 1, longestFrame: 60 });
  });

  it('P13-R01: a loading started inside a frame starts with that frame', () => {
    let now = 0;
    const perf = new PerfMonitor(50, () => now);
    perf.frameStarted();
    now += 5;
    perf.loadStarted();
    now += 20;
    perf.frameEnded();
    perf.loadFinished();
    expect(perf.numbers).toMatchObject({ lastLoad: 25, longestLoadStep: 25 });
  });

  it('P13-R01: an end without a start, or a finish without a load, changes nothing', () => {
    const { perf } = monitor();
    perf.frameEnded();
    perf.loadFinished();
    expect(perf.numbers).toMatchObject({ frames: 0, lastLoad: null });
  });
});
