import { describe, expect, it } from 'vitest';
import { HoldRepeater } from '../../../src/input/hold-repeater';

describe('HoldRepeater', () => {
  it('P01-R09: repeats a held key after the delay, then at the interval', () => {
    const repeater = new HoldRepeater<'right'>(0.35, 0.12);
    expect(repeater.press('right')).toBe(true);
    expect(repeater.update(0.3)).toEqual([]);
    expect(repeater.update(0.05)).toEqual(['right']);
    expect(repeater.update(0.1)).toEqual([]);
    expect(repeater.update(0.02)).toEqual(['right']);
    expect(repeater.update(0.24)).toEqual(['right', 'right']);
  });

  it('does not treat a key that is still held as a new press', () => {
    const repeater = new HoldRepeater<'up'>(0.35, 0.12);
    repeater.press('up');
    expect(repeater.press('up')).toBe(false);
  });

  it('stops repeating on release', () => {
    const repeater = new HoldRepeater<'up' | 'down'>(0.1, 0.1);
    repeater.press('up');
    repeater.press('down');
    expect(repeater.held).toEqual(['up', 'down']);
    repeater.release('up');
    expect(repeater.update(0.1)).toEqual(['down']);
    repeater.releaseAll();
    expect(repeater.held).toEqual([]);
    expect(repeater.update(1)).toEqual([]);
  });

  it('rejects a non-positive interval or a negative delay', () => {
    expect(() => new HoldRepeater(0.3, 0)).toThrow(RangeError);
    expect(() => new HoldRepeater(-1, 0.1)).toThrow(RangeError);
  });
});
