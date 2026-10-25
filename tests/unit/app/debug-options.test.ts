import { describe, expect, it } from 'vitest';
import { parseDebugOptions } from '../../../src/app/debug-options';

describe('parseDebugOptions', () => {
  it('P06-R09: ?level=1-3&t=120 starts level 1-3 at 2:00 with the first ship', () => {
    expect(parseDebugOptions('?level=1-3&t=120')).toEqual({
      levelId: '1-3',
      time: 120,
      shipId: null,
    });
  });

  it('P06-R09: ship= picks the ship; the time defaults to the start', () => {
    expect(parseDebugOptions('?ship=heavy&level=1-1')).toEqual({
      levelId: '1-1',
      time: 0,
      shipId: 'heavy',
    });
    expect(parseDebugOptions('?level=1-2&t=oops')?.time).toBe(0);
    expect(parseDebugOptions('?level=1-2&t=-5')?.time).toBe(0);
  });

  it('P06-R09: without level=, there is no debug mode', () => {
    expect(parseDebugOptions('')).toBeUndefined();
    expect(parseDebugOptions('?t=120&ship=heavy')).toBeUndefined();
  });
});
