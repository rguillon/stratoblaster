import { describe, expect, it } from 'vitest';
import { canTransition, MENU_TRANSITIONS } from '../../../../src/core/menu/menu-screen';

describe('menu screen transitions', () => {
  it('P01-R01: follows the flow forward and Back on each menu screen', () => {
    expect(canTransition('loading', 'title')).toBe(true);
    expect(canTransition('title', 'ship-select')).toBe(true);
    expect(canTransition('ship-select', 'level-select')).toBe(true);
    expect(canTransition('ship-select', 'title')).toBe(true);
    expect(canTransition('level-select', 'game')).toBe(true);
    expect(canTransition('level-select', 'ship-select')).toBe(true);
  });

  it('P12-R01, P12-R02: a level is left through the pause menu, not straight to the title', () => {
    expect(canTransition('game', 'title')).toBe(false);
    expect(canTransition('game', 'pause')).toBe(true);
    expect(canTransition('pause', 'game')).toBe(true);
    expect(canTransition('pause', 'title')).toBe(true);
  });

  it('P12-R04: the settings screen opens from the title and the pause menu, and goes back there', () => {
    expect(canTransition('title', 'settings')).toBe(true);
    expect(canTransition('settings', 'title')).toBe(true);
    expect(canTransition('pause', 'settings')).toBe(true);
    expect(canTransition('settings', 'pause')).toBe(true);
    expect(canTransition('settings', 'game')).toBe(false);
  });

  it('P06-R03: a completed level goes back to the level select screen', () => {
    expect(canTransition('game', 'level-select')).toBe(true);
  });

  it('P01-R01: rejects transitions outside the flow', () => {
    expect(canTransition('title', 'game')).toBe(false);
    expect(canTransition('title', 'loading')).toBe(false);
    expect(canTransition('loading', 'game')).toBe(false);
    expect(canTransition('title', 'title')).toBe(false);
  });

  it('lists every screen', () => {
    expect(Object.keys(MENU_TRANSITIONS).sort()).toEqual(
      ['game', 'level-select', 'loading', 'pause', 'settings', 'ship-select', 'title'].sort(),
    );
  });
});
