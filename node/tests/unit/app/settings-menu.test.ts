import { describe, expect, it } from 'vitest';
import { SettingsMenu } from '../../../src/app/settings-menu';

describe('SettingsMenu', () => {
  it('P12-R04: up / down pick a slider, left / right change it by one step within 0 … 10', () => {
    const menu = new SettingsMenu({ music: 6, sfx: 8 }, 10);
    expect(menu.selectedId).toBe('music');
    expect(menu.move('left')).toBe('adjusted');
    expect(menu.volumes).toEqual({ music: 5, sfx: 8 });
    expect(menu.move('down')).toBe('moved');
    expect(menu.move('down')).toBe('none');
    expect(menu.selectedId).toBe('sfx');
    expect(menu.move('right')).toBe('adjusted');
    expect(menu.move('right')).toBe('adjusted');
    expect(menu.move('right')).toBe('none');
    expect(menu.volumes).toEqual({ music: 5, sfx: 10 });
    expect(menu.move('up')).toBe('moved');
    expect(menu.select(-1)).toBe('none');
    menu.open();
    expect(menu.selection).toBe(0);
  });

  it('P12-R04: a tap or a drag sets a slider to its nearest step and selects it', () => {
    const menu = new SettingsMenu({ music: 6, sfx: 8 }, 10);
    expect(menu.set(1, 2.6)).toBe('adjusted');
    expect(menu.volumes).toEqual({ music: 6, sfx: 3 });
    expect(menu.selectedId).toBe('sfx');
    expect(menu.set(0, 6)).toBe('moved');
    expect(menu.set(0, 6)).toBe('none');
    expect(menu.set(0, -4)).toBe('adjusted');
    expect(menu.volumes.music).toBe(0);
    expect(menu.set(5, 1)).toBe('none');
    expect(menu.set(0, Number.NaN)).toBe('none');
  });

  it('P12-R04: starts from volumes clamped to the sliders', () => {
    expect(new SettingsMenu({ music: 14, sfx: -2 }, 10).volumes).toEqual({ music: 10, sfx: 0 });
  });
});
