import { describe, expect, it } from 'vitest';
import { shipCaption } from '../../../src/ui/ship-caption';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

describe('shipCaption', () => {
  it('shows the ship name, its speed (factor and px/s) and its health', () => {
    expect(shipCaption(SAMPLE_GAME.playerShips, 'brick')).toEqual({
      title: 'Brick',
      lines: ['Speed ×0.5 (25 px/s)', 'HP 6'],
    });
  });

  it("adds the model's polygon count when given", () => {
    expect(shipCaption(SAMPLE_GAME.playerShips, 'cube', 12345).lines).toEqual([
      'Speed ×1 (50 px/s)',
      'HP 3',
      '12,345 polygons',
    ]);
  });
});
