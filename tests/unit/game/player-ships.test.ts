import { describe, expect, it } from 'vitest';
import {
  findPlayerShip,
  shipMaxSpeedPxPerSec,
  validatePlayerShipRoster,
} from '../../../src/core/entities/player-ship';
import { PLAYER_SHIPS } from '../../../src/game/config/player-ships';

describe('player ship data', () => {
  it('has a base speed of 100 px/s and a valid roster', () => {
    expect(PLAYER_SHIPS.baseSpeedPxPerSec).toBe(100);
    expect(() => {
      validatePlayerShipRoster(PLAYER_SHIPS);
    }).not.toThrow();
    expect(PLAYER_SHIPS.ships).toHaveLength(3);
  });

  it('P02-R01: balanced ship has a maximal speed of 1 (100 px/s) and 100 HP', () => {
    expect(findPlayerShip(PLAYER_SHIPS, 'balanced')).toMatchObject({
      maxSpeedFactor: 1,
      maxHealth: 100,
    });
    expect(shipMaxSpeedPxPerSec(PLAYER_SHIPS, 'balanced')).toBe(100);
  });

  it('P02-R02: heavy ship has a maximal speed of 0.8 (80 px/s) and 140 HP', () => {
    expect(findPlayerShip(PLAYER_SHIPS, 'heavy')).toMatchObject({
      maxSpeedFactor: 0.8,
      maxHealth: 140,
    });
    expect(shipMaxSpeedPxPerSec(PLAYER_SHIPS, 'heavy')).toBeCloseTo(80);
  });

  it('P02-R03: light ship has a maximal speed of 1.4 (140 px/s) and 80 HP', () => {
    expect(findPlayerShip(PLAYER_SHIPS, 'light')).toMatchObject({
      maxSpeedFactor: 1.4,
      maxHealth: 80,
    });
    expect(shipMaxSpeedPxPerSec(PLAYER_SHIPS, 'light')).toBeCloseTo(140);
  });
});
