import { describe, expect, it } from 'vitest';
import { GAME } from '../../../src/game/index';

describe('GAME', () => {
  it('ENG-144: exports a GameDefinition for this game', () => {
    expect(GAME.id).toBe('pewet');
    expect(GAME.title).toBe('Pewet');
  });
});
