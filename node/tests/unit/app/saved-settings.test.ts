import { describe, expect, it } from 'vitest';
import {
  loadVolumes,
  parseVolume,
  saveVolumes,
  savedSettingKeys,
} from '../../../src/app/saved-settings';
import { MemoryStorage } from '../../../src/platform/key-value-storage';

const DEFAULTS = { music: 6, sfx: 8 };

describe('saved settings', () => {
  it('P12-R04: the cookies are named after the game: <gameId>_music_volume, <gameId>_sfx_volume', () => {
    expect(savedSettingKeys('stratoblaster')).toEqual({
      music: 'stratoblaster_music_volume',
      sfx: 'stratoblaster_sfx_volume',
    });
  });

  it('P12-R04: no cookie reads as the defaults', () => {
    expect(loadVolumes(new MemoryStorage(), 'g', 10, DEFAULTS)).toEqual(DEFAULTS);
  });

  it('P12-R04: a cookie of "banana" or "42" reads as the default, without an error', () => {
    for (const raw of ['banana', '42', '-1', '3.5', '', ' ']) {
      expect(parseVolume(raw, 10, 6)).toBe(6);
    }
    expect(parseVolume(null, 10, 6)).toBe(6);
    expect(parseVolume(' 3 ', 10, 6)).toBe(3);
    expect(parseVolume('0', 10, 6)).toBe(0);
    expect(parseVolume('10', 10, 6)).toBe(10);
  });

  it('P12-R04: saved volumes are read back', () => {
    const storage = new MemoryStorage();
    saveVolumes(storage, 'g', { music: 3, sfx: 0 });
    expect(storage.get('g_music_volume')).toBe('3');
    expect(loadVolumes(storage, 'g', 10, DEFAULTS)).toEqual({ music: 3, sfx: 0 });
  });
});
