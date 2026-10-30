import { describe, expect, it } from 'vitest';
import { ScrollTrack } from '../../../../src/core/scenery/scroll-track';

describe('ScrollTrack', () => {
  it('P04-R06: scrolls at its speed and ends after length / speed seconds', () => {
    const track = new ScrollTrack(60, 10_800);
    expect(track.duration).toBe(180);
    track.step(2);
    expect(track.time).toBe(2);
    expect(track.distance).toBe(120);
    expect(track.ended).toBe(false);
    track.step(500);
    expect(track.time).toBe(180);
    expect(track.ended).toBe(true);
  });

  it('pauses, fast-forwards, seeks within the level and restarts', () => {
    const track = new ScrollTrack(10, 100);
    track.timeScale = 0;
    track.step(1);
    expect(track.time).toBe(0);
    track.timeScale = 4;
    track.step(1);
    expect(track.time).toBe(4);
    track.step(-1);
    expect(track.time).toBe(4);
    track.seek(-5);
    expect(track.time).toBe(0);
    track.seek(7);
    expect(track.distance).toBe(70);
    track.restart();
    expect(track.time).toBe(0);
  });

  it('P07-R03: the ground speed factor eases to its new value over the given seconds', () => {
    const track = new ScrollTrack(60, 100_000);
    track.setSpeedFactor(0.5, 2);
    track.step(1);
    expect(track.speedFactor).toBeCloseTo(0.75);
    track.step(1);
    expect(track.speedFactor).toBe(0.5);
    const before = track.distance;
    track.step(1);
    expect(track.distance - before).toBeCloseTo(30);
    track.setSpeedFactor(0, 0);
    track.step(1);
    expect(track.speedFactor).toBe(0);
    expect(track.distance - before).toBeCloseTo(30);
    expect(() => {
      track.setSpeedFactor(-1, 1);
    }).toThrow(RangeError);
  });

  it('P07-R03: held, the ground scrolls on (past the end too) but the progress waits', () => {
    const track = new ScrollTrack(10, 100);
    track.step(5);
    track.held = true;
    track.step(20);
    expect(track.progress).toBe(50);
    expect(track.time).toBe(5);
    expect(track.distance).toBe(250);
    track.held = false;
    track.step(10);
    expect(track.ended).toBe(true);
    expect(track.distance).toBe(300);
    // Seeking keeps the ground's lead, so the scenery does not jump back.
    track.seek(2);
    expect(track.distance).toBe(220);
    track.restart();
    expect([track.distance, track.speedFactor, track.held]).toEqual([0, 1, false]);
  });

  it('rejects a speed that is not positive or a negative length', () => {
    expect(() => new ScrollTrack(0, 10)).toThrow(RangeError);
    expect(() => new ScrollTrack(1, -1)).toThrow(RangeError);
  });
});
