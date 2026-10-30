import { describe, expect, it } from 'vitest';
import { VoicePool } from '../../../src/audio/voice-pool';

describe('VoicePool', () => {
  it('P12-R10: given 40 explosions in one frame, at most 16 play', () => {
    const pool = new VoicePool(16, 0.03);
    let played = 0;
    for (let i = 0; i < 40; i++) {
      if (pool.request(`explosion-${String(i)}`, 4, 0, 1).play) played++;
    }
    expect(pool.voices).toHaveLength(16);
    // Each new one of equal priority replaced the oldest.
    expect(played).toBe(40);
    expect(pool.voices[0]?.name).toBe('explosion-24');
  });

  it('P12-R10: the same sound requested twice 10 ms apart plays once', () => {
    const pool = new VoicePool(16, 0.03);
    expect(pool.request('hit', 2, 1, 0.1).play).toBe(true);
    expect(pool.request('hit', 2, 1.01, 0.1)).toEqual({ play: false, retrigger: true });
    expect(pool.request('hit', 2, 1.05, 0.1).play).toBe(true);
  });

  it('P12-R10: a player sound plays when all voices are taken by enemy shots; an enemy shot does not replace a player sound', () => {
    const pool = new VoicePool(4, 0.03);
    for (let i = 0; i < 4; i++) pool.request(`enemy-${String(i)}`, 0, 0, 1);
    const decision = pool.request('player-hit', 6, 0.1, 1);
    expect(decision).toMatchObject({ play: true, evicted: { name: 'enemy-0' } });
    for (let i = 0; i < 3; i++) pool.request(`player-${String(i)}`, 6, 0.2, 1);
    expect(pool.request('enemy-shot', 0, 0.3, 1)).toEqual({ play: false, retrigger: false });
  });

  it('frees voices once they are over, released or cleared', () => {
    const pool = new VoicePool(2, 0.03);
    const first = pool.request('a', 1, 0, 0.5);
    pool.request('b', 1, 0, Infinity);
    expect(pool.request('c', 1, 1, 1)).toMatchObject({ play: true });
    expect(pool.voices.map((v) => v.name)).toEqual(['b', 'c']);
    if (first.play) pool.release(first.id);
    const b = pool.voices[0];
    if (b) pool.release(b.id);
    expect(pool.voices.map((v) => v.name)).toEqual(['c']);
    pool.clear();
    expect(pool.voices).toEqual([]);
    expect(pool.request('c', 1, 1, 1).play).toBe(true);
  });
});
