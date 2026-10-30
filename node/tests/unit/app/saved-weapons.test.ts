import { describe, expect, it } from 'vitest';
import {
  loadSavedWeapons,
  parseWeaponLevels,
  saveWeapons,
  savedWeaponsKey,
} from '../../../src/app/saved-weapons';
import { MemoryStorage } from '../../../src/platform/key-value-storage';

describe('saved weapons', () => {
  it('phase 8 review: keeps the weapons of a completed level and reads them back', () => {
    const storage = new MemoryStorage();
    expect(loadSavedWeapons(storage, 'demo')).toBeNull();
    const weapons = { weapon: 'ray', levels: { pea: 3, ray: 2 } };
    saveWeapons(storage, 'demo', weapons);
    expect(storage.get(savedWeaponsKey('demo'))).not.toBeNull();
    expect(loadSavedWeapons(storage, 'demo')).toEqual(weapons);
    expect(loadSavedWeapons(storage, 'other')).toBeNull();
  });

  it('phase 8 review: a corrupted value reads as none, without throwing', () => {
    for (const raw of [
      '',
      'abc',
      'null',
      '3',
      '{"levels":{"pea":2}}',
      '{"weapon":"pea"}',
      '{"weapon":"pea","levels":null}',
      '{"weapon":"pea","levels":{"pea":0}}',
      '{"weapon":"pea","levels":{"pea":1.5}}',
      '{"weapon":"pea","levels":{"pea":"2"}}',
    ]) {
      expect(parseWeaponLevels(raw)).toBeNull();
    }
    expect(parseWeaponLevels(null)).toBeNull();
  });
});
