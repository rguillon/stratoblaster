import { describe, expect, it } from 'vitest';
import { PauseMenu } from '../../../src/app/pause-menu';

describe('PauseMenu', () => {
  it('P12-R02: opens on Resume; up / down move through Resume, Settings, Main menu', () => {
    const menu = new PauseMenu();
    expect(menu.selectedId).toBe('resume');
    expect(menu.move('up')).toBe('none');
    expect(menu.move('left')).toBe('none');
    expect(menu.move('down')).toBe('moved');
    expect(menu.selectedId).toBe('settings');
    expect(menu.move('down')).toBe('moved');
    expect(menu.move('down')).toBe('none');
    expect(menu.selectedId).toBe('main-menu');
    expect(menu.select(0)).toBe('moved');
    expect(menu.select(0)).toBe('none');
    expect(menu.select(3)).toBe('none');
    expect(menu.select(1.5)).toBe('none');
  });

  it('P12-R02: Resume resumes, Settings opens the settings, Back resumes', () => {
    const menu = new PauseMenu();
    expect(menu.confirm()).toBe('resume');
    menu.select(1);
    expect(menu.confirm()).toBe('settings');
    expect(menu.back()).toBe('resume');
  });

  it('P12-R02: Main menu asks "Leave the level?" with No first; Yes leaves, No and Back close it', () => {
    const menu = new PauseMenu();
    menu.select(2);
    expect(menu.confirm()).toBe('ask');
    expect(menu.leaving).toBe(true);
    expect(menu.choice).toBe(0);
    expect(menu.confirm()).toBe('ask');
    expect(menu.leaving).toBe(false);
    menu.confirm();
    expect(menu.back()).toBe('ask');
    expect(menu.leaving).toBe(false);
    menu.confirm();
    expect(menu.move('right')).toBe('moved');
    expect(menu.move('down')).toBe('none');
    expect(menu.move('up')).toBe('moved');
    expect(menu.select(1)).toBe('moved');
    expect(menu.select(4)).toBe('none');
    expect(menu.confirm()).toBe('leave');
    menu.open();
    expect(menu).toMatchObject({ selection: 0, leaving: false, choice: 0 });
  });
});
