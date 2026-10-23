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

  it('rejects a speed that is not positive or a negative length', () => {
    expect(() => new ScrollTrack(0, 10)).toThrow(RangeError);
    expect(() => new ScrollTrack(1, -1)).toThrow(RangeError);
  });
});
