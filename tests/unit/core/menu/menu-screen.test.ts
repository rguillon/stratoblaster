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
    expect(canTransition('game', 'title')).toBe(true);
  });

  it('P01-R01: rejects transitions outside the flow', () => {
    expect(canTransition('title', 'game')).toBe(false);
    expect(canTransition('title', 'loading')).toBe(false);
    expect(canTransition('loading', 'game')).toBe(false);
    expect(canTransition('game', 'level-select')).toBe(false);
    expect(canTransition('title', 'title')).toBe(false);
  });

  it('lists every screen', () => {
    expect(Object.keys(MENU_TRANSITIONS).sort()).toEqual(
      ['game', 'level-select', 'loading', 'ship-select', 'title'].sort(),
    );
  });
});
