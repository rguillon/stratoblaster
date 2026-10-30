import { describe, expect, it } from 'vitest';
import { FixedStepClock } from '../../../../src/core/loop/fixed-step-clock';

describe('FixedStepClock', () => {
  it('ENG-100: runs one step per 1/60 s at 60 Hz', () => {
    const clock = new FixedStepClock(60, 5);
    expect(clock.advance(1 / 60).steps).toBe(1);
  });

  it('ENG-100: accumulates partial frames and reports interpolation alpha', () => {
    const clock = new FixedStepClock(60, 5);
    const first = clock.advance(0.5 / 60);
    expect(first.steps).toBe(0);
    expect(first.alpha).toBeCloseTo(0.5);
    expect(clock.advance(0.75 / 60).steps).toBe(1);
  });

  it('ENG-100: is independent of the display refresh rate', () => {
    const at144 = new FixedStepClock(60, 5);
    let steps = 0;
    for (let i = 0; i < 144; i++) steps += at144.advance(1 / 144).steps;
    expect(steps).toBeGreaterThanOrEqual(59);
    expect(steps).toBeLessThanOrEqual(60);
  });

  it('caps steps per frame after a long stall and drops the excess', () => {
    const clock = new FixedStepClock(60, 5);
    expect(clock.advance(1)).toEqual({ steps: 5, alpha: 0 });
    expect(clock.advance(0).steps).toBe(0);
  });

  it('ignores negative frame times', () => {
    const clock = new FixedStepClock(60, 5);
    expect(clock.advance(-1).steps).toBe(0);
  });

  it('rejects invalid parameters', () => {
    expect(() => new FixedStepClock(0, 5)).toThrow(RangeError);
    expect(() => new FixedStepClock(60, 0)).toThrow(RangeError);
  });
});
