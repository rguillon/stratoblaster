import { describe, expect, it } from 'vitest';
import { LIGHTNING } from '../../../../src/config/weather';
import { resolveSky } from '../../../../src/core/scenery/sky-look';
import { flashed, LightningSchedule } from '../../../../src/core/scenery/lightning';

/** An hour of storm. */
const STORM = 3600;
const BASE = { fog: { start: 1000, end: 2600 }, cloudOpacity: [0.75, 0.5] };

describe('Lightning', () => {
  it('P09-R05: never more than 3 flashes in any 1 s window over a long storm', () => {
    const flashes = new LightningSchedule(3301).flashesBetween(0, STORM);
    expect(flashes.length).toBeGreaterThan(300);
    // The busiest window starts at a flash: count the flashes in the second after each.
    for (const [i, start] of flashes.entries()) {
      const inWindow = flashes.slice(i).filter((t) => t < start + 1).length;
      expect(inWindow, `${String(start)} s`).toBeLessThanOrEqual(LIGHTNING.maxPerSecond);
    }
    expect(LIGHTNING.maxPerSecond).toBe(3);
  });

  it('P09-R05: the strikes come on average once every 4 to 10 s (lightning_gap)', () => {
    const schedule = new LightningSchedule(3301);
    const starts = schedule.strikesBefore(STORM).map((s) => s.flashes[0] ?? 0);
    const gaps = starts.slice(1).map((t, i) => t - (starts[i] ?? 0));
    for (const gap of gaps) {
      expect(gap).toBeGreaterThanOrEqual(LIGHTNING.gap[0]);
      expect(gap).toBeLessThanOrEqual(LIGHTNING.gap[1]);
    }
    const average = gaps.reduce((a, b) => a + b, 0) / gaps.length;
    expect(average).toBeGreaterThanOrEqual(4);
    expect(average).toBeLessThanOrEqual(10);
    // Counting every flash (some strikes flash twice), still one every few seconds.
    const flashes = schedule.flashesBetween(0, STORM);
    expect(STORM / flashes.length).toBeGreaterThanOrEqual(3);
  });

  it('P09-R05: the same level flashes at the same times; another seed elsewhere', () => {
    const times = (seed: number) => new LightningSchedule(seed).flashesBetween(0, 600);
    expect(times(3301)).toEqual(times(3301));
    expect(times(3301)).not.toEqual(times(3401));
    // Asked for in another order, the strikes are the same.
    const late = new LightningSchedule(3301);
    late.flashAt(500);
    expect(late.flashesBetween(0, 600)).toEqual(times(3301));
  });

  it('P09-R05: a flash is short: it rises, peaks and is gone in about 0.15 s', () => {
    const schedule = new LightningSchedule(3301);
    const [first] = schedule.flashesBetween(0, 60);
    if (first === undefined) throw new Error('no flash in a minute');
    expect(schedule.flashAt(first - 0.01)).toBe(0);
    expect(schedule.flashAt(first + LIGHTNING.rise)).toBeCloseTo(1);
    expect(schedule.flashAt(first + LIGHTNING.flash + 0.001)).toBe(0);
    expect(schedule.strikeAt(first + 0.05)?.flashes[0]).toBe(first);
    expect(schedule.strikeAt(first + 3)).toBeUndefined();
  });

  it('P09-R05: a flash lights the ambient light and the sky at most ×1.8, never white', () => {
    const storm = resolveSky(
      {
        timeOfDay: 'afternoon',
        clouds: [0.9, 0.9],
        storm: 1,
        weather: { kind: 'rain', strength: 0.8 },
        lightning: 1,
      },
      BASE,
    );
    expect(storm.lightning).toBe(1);
    const lit = flashed(storm, 1);
    expect(lit.ambient.intensity / storm.ambient.intensity).toBeCloseTo(LIGHTNING.brightness);
    expect(LIGHTNING.brightness).toBeLessThanOrEqual(1.8);
    lit.sky.haze.forEach((c, i) => {
      expect(c).toBeLessThanOrEqual(Math.min(1, (storm.sky.haze[i] ?? 0) * 1.8) + 1e-9);
      expect(c).toBeLessThan(1);
    });
    expect(flashed(storm, 0)).toBe(storm);
    expect(flashed(storm, 3).ambient.intensity).toBeCloseTo(lit.ambient.intensity);
    // No lightning in the look: no flash.
    const calm = { ...storm, lightning: 0 };
    expect(flashed(calm, 1)).toBe(calm);
  });
});
