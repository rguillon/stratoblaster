import { describe, expect, it } from 'vitest';
import {
  loadSavedChoices,
  parseHighScore,
  saveLastShip,
  savedChoiceKeys,
} from '../../../src/app/saved-choices';
import { MemoryStorage } from '../../../src/platform/key-value-storage';

describe('saved choices', () => {
  it('P01-R04: the high score is 0 when there is no cookie yet', () => {
    expect(loadSavedChoices(new MemoryStorage(), 'stratoblaster')).toEqual({
      highScore: 0,
      lastShipId: null,
    });
  });

  it('P01-R04: reads a high score of 12345 from the cookie', () => {
    const storage = new MemoryStorage();
    storage.set('stratoblaster_high_score', '12345');
    expect(loadSavedChoices(storage, 'stratoblaster').highScore).toBe(12345);
  });

  it('P01-R04: a corrupted value reads as 0 without throwing', () => {
    for (const raw of ['abc', '-5', '12.5', '1e5', '', '99999999999999999999', ' ', '0x10']) {
      expect(parseHighScore(raw)).toBe(0);
    }
    expect(parseHighScore(' 42 ')).toBe(42);
    expect(parseHighScore(null)).toBe(0);
  });

  it('P01-R14: saves and reads the last chosen ship', () => {
    const storage = new MemoryStorage();
    saveLastShip(storage, 'stratoblaster', 'light');
    expect(storage.get('stratoblaster_last_ship')).toBe('light');
    expect(loadSavedChoices(storage, 'stratoblaster').lastShipId).toBe('light');
  });

  it('prefixes the keys with the game id', () => {
    expect(savedChoiceKeys('demo')).toEqual({
      highScore: 'demo_high_score',
      lastShip: 'demo_last_ship',
    });
  });
});
