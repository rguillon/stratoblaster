import { describe, expect, it } from 'vitest';
import { RateMeter } from '../../../src/app/rate-meter';

describe('RateMeter', () => {
  it('measures the growth of a total per second over its window', () => {
    const meter = new RateMeter(1);
    expect(meter.rate).toBe(0);
    for (let i = 1; i <= 20; i++) meter.add(0.1, i * 5);
    expect(meter.rate).toBeCloseTo(50);
  });

  it('forgets samples older than the window', () => {
    const meter = new RateMeter(1);
    for (let i = 1; i <= 10; i++) meter.add(0.1, i * 100);
    for (let i = 1; i <= 20; i++) meter.add(0.1, 1000);
    expect(meter.rate).toBeCloseTo(0);
  });
});
