import { describe, expect, it } from 'vitest';
import { parseDebugOptions } from '../../../src/app/debug-options';

describe('parseDebugOptions', () => {
  it('P06-R09: ?level=1-3&t=120 starts level 1-3 at 2:00 with the first ship', () => {
    expect(parseDebugOptions('?level=1-3&t=120')).toEqual({
      levelId: '1-3',
      time: 120,
      shipId: null,
      boss: null,
      weather: true,
      timeOfDay: null,
    });
  });

  it('P06-R09: ship= picks the ship; the time defaults to the start', () => {
    expect(parseDebugOptions('?ship=heavy&level=1-1')).toEqual({
      levelId: '1-1',
      time: 0,
      shipId: 'heavy',
      boss: null,
      weather: true,
      timeOfDay: null,
    });
    expect(parseDebugOptions('?level=1-2&t=oops')?.time).toBe(0);
    expect(parseDebugOptions('?level=1-2&t=-5')?.time).toBe(0);
  });

  it('P07-R09: boss=mini or boss=final starts at that boss; anything else is ignored', () => {
    expect(parseDebugOptions('?level=1-3&boss=final')?.boss).toBe('final');
    expect(parseDebugOptions('?level=1-3&boss=mini')?.boss).toBe('mini');
    expect(parseDebugOptions('?level=1-3&boss=giant')?.boss).toBeNull();
  });

  it('P08-R12: weather=0 turns the weather off; look= forces a time of day', () => {
    expect(parseDebugOptions('?level=2-3&weather=0')?.weather).toBe(false);
    expect(parseDebugOptions('?level=2-3&weather=1')?.weather).toBe(true);
    expect(parseDebugOptions('?level=2-5&look=night')?.timeOfDay).toBe('night');
    expect(parseDebugOptions('?level=2-5&look=noon')?.timeOfDay).toBeNull();
  });

  it('P06-R09: without level=, there is no debug mode', () => {
    expect(parseDebugOptions('')).toBeUndefined();
    expect(parseDebugOptions('?t=120&ship=heavy')).toBeUndefined();
  });
});
