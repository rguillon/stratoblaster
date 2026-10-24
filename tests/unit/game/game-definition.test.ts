import { describe, expect, it } from 'vitest';
import { GAME } from '../../../src/game/index';
import { LEVELS } from '../../../src/game/sim/levels';
import { ENEMY_KINDS } from '../../../src/game/sim/enemy-kinds';
import { ENEMY_BINDINGS } from '../../../src/game/view/enemies/enemy-bindings';
import { MENU_TEXTS } from '../../../src/game/config/menu-texts';
import { PLAYER_WEAPONS } from '../../../src/game/config/player-weapons';

describe('GAME', () => {
  it('ENG-144: exports a GameDefinition for this game', () => {
    expect(GAME.id).toBe('stratoblaster');
    expect(GAME.title).toBe('Stratoblaster');
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

  it('P03-R10: registers the player weapons with a shot renderer each', () => {
    expect(GAME.playerWeapons).toBe(PLAYER_WEAPONS);
    for (const weapon of GAME.playerWeapons) {
      expect(typeof GAME.view.playerShotRenderers[weapon.id]).toBe('function');
    }
    expect(GAME.view.playerShipScale).toBeGreaterThan(0);
  });

  it('P06-R02, P06-R03: names the level played, and counts the enemies at its end', () => {
    expect(MENU_TEXTS.gameLevel('1-2')).toBe('Level 1-2');
    expect(MENU_TEXTS.enemiesDestroyed(42, 60)).toBe('Enemies destroyed: 42 / 60');
  });

  it('P06-R01: registers the five playable levels of World 1', () => {
    expect(GAME.gameLevels.map((l) => l.id)).toEqual(['1-1', '1-2', '1-3', '1-4', '1-5']);
  });

  it('P05-R01..R10, P05-R12: registers the 11 enemy kinds with their look', () => {
    expect(GAME.enemyKinds).toBe(ENEMY_KINDS);
    expect(GAME.enemyKinds).toHaveLength(11);
    expect(GAME.view.enemies).toBe(ENEMY_BINDINGS);
  });
});
