import { describe, expect, it } from 'vitest';
import {
  loadSavedSupplies,
  parseSupplies,
  saveSupplies,
  savedSuppliesKey,
} from '../../../src/app/saved-supplies';
import { MemoryStorage } from '../../../src/platform/key-value-storage';

describe('saved lives and bombs', () => {
  it('reviewer, 2026-10-28: keeps the lives and bombs of a completed level and reads them back', () => {
    const storage = new MemoryStorage();
    expect(loadSavedSupplies(storage, 'demo')).toBeNull();
    saveSupplies(storage, 'demo', { lives: 7, bombs: 0 });
    expect(storage.get(savedSuppliesKey('demo'))).not.toBeNull();
    expect(loadSavedSupplies(storage, 'demo')).toEqual({ lives: 7, bombs: 0 });
    expect(loadSavedSupplies(storage, 'other')).toBeNull();
  });

  it('a corrupted value reads as none, without throwing', () => {
    for (const raw of [
      '',
      'abc',
      'null',
      '3',
      '{"lives":3}',
      '{"bombs":3}',
      '{"lives":0,"bombs":3}',
      '{"lives":2,"bombs":-1}',
      '{"lives":2.5,"bombs":3}',
      '{"lives":"2","bombs":3}',
    ]) {
      expect(parseSupplies(raw), raw).toBeNull();
    }
  });
});
