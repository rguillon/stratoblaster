import { describe, expect, it } from 'vitest';
import { GAME } from '../../../src/game/index';
import { LEVELS } from '../../../src/game/sim/levels';
import { MENU_TEXTS } from '../../../src/game/config/menu-texts';

describe('GAME', () => {
  it('ENG-144: exports a GameDefinition for this game', () => {
    expect(GAME.id).toBe('pewet');
    expect(GAME.title).toBe('Pewet');
  });

  it('GD-02: lays the screens out at 480×640', () => {
    expect(GAME.screen).toEqual({ width: 480, height: 640 });
  });

  it('P01-R04, P01-R07: provides the title, menu texts and levels from src/game/', () => {
    expect(GAME.levels).toBe(LEVELS);
    expect(GAME.texts).toBe(MENU_TEXTS);
    expect(GAME.playerShips.ships[0]?.id).toBe('balanced');
    expect(typeof GAME.view.menuBackdrop).toBe('function');
  });

  it('P01-R08: the placeholder names the ship and the level', () => {
    expect(MENU_TEXTS.gamePlaceholder('Balanced', '1-1')).toBe(
      'Balanced ship — Level 1-1 — Gameplay coming soon',
    );
  });
});
