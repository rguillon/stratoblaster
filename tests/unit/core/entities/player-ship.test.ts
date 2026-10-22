import { describe, expect, it } from 'vitest';
import {
  findPlayerShip,
  shipMaxSpeedPxPerSec,
  validatePlayerShipRoster,
  type PlayerShipRoster,
} from '../../../../src/core/entities/player-ship';
import { at } from '../../../helpers/at';

const ROSTER: PlayerShipRoster = {
  baseSpeedPxPerSec: 200,
  ships: [
    { id: 'a', name: 'A', maxSpeedFactor: 1, maxHealth: 10 },
    { id: 'b', name: 'B', maxSpeedFactor: 0.5, maxHealth: 20 },
  ],
};

describe('player ship definitions', () => {
  it('computes the maximal speed in px/s from the base speed and the ship factor', () => {
    expect(shipMaxSpeedPxPerSec(ROSTER, 'a')).toBe(200);
    expect(shipMaxSpeedPxPerSec(ROSTER, 'b')).toBe(100);
  });

  it('finds a ship by id and throws on an unknown id', () => {
    expect(findPlayerShip(ROSTER, 'b').maxHealth).toBe(20);
    expect(() => findPlayerShip(ROSTER, 'zzz')).toThrow(/unknown player ship "zzz"/i);
  });

  it('accepts a valid roster', () => {
    expect(() => {
      validatePlayerShipRoster(ROSTER);
    }).not.toThrow();
  });

  it.each([
    ['an empty roster', { ...ROSTER, ships: [] }, /at least one/],
    ['a non-positive base speed', { ...ROSTER, baseSpeedPxPerSec: 0 }, /base speed/],
    [
      'a duplicate id',
      { ...ROSTER, ships: [at(ROSTER.ships, 0), { ...at(ROSTER.ships, 1), id: 'a' }] },
      /duplicate/i,
    ],
    [
      'a non-positive speed factor',
      { ...ROSTER, ships: [{ ...at(ROSTER.ships, 0), maxSpeedFactor: -1 }] },
      /speed/,
    ],
    [
      'a non-integer health',
      { ...ROSTER, ships: [{ ...at(ROSTER.ships, 0), maxHealth: 1.5 }] },
      /health/,
    ],
  ])('rejects %s', (_label, roster: PlayerShipRoster, message) => {
    expect(() => {
      validatePlayerShipRoster(roster);
    }).toThrow(message);
  });
});
