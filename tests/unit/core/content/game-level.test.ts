import { describe, expect, it } from 'vitest';
import { findGameLevel } from '../../../../src/core/content/game-level';
import { SAMPLE_GAME } from '../../../fixtures/sample-game';

describe('findGameLevel', () => {
  it('P06-R02: finds a playable level by the id of its level select entry', () => {
    expect(findGameLevel(SAMPLE_GAME.gameLevels, 'c')?.difficulty.fireRate).toBe(2);
    expect(findGameLevel(SAMPLE_GAME.gameLevels, 'b')).toBeUndefined();
  });
});
