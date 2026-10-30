import type { PlayerShipRoster } from '../../core/entities/player-ship';

/**
 * Player ships and their stats (P02-R01..R03). Speeds are multiples of the base speed, raised
 * from 100 to 150 px/s, then to 225 px/s, at the reviewer's requests in phase 6 (D-044, D-047).
 */
export const PLAYER_SHIPS = {
  baseSpeedPxPerSec: 225,
  ships: [
    { id: 'balanced', name: 'Balanced', maxSpeedFactor: 1, maxHealth: 100 },
    { id: 'heavy', name: 'Heavy', maxSpeedFactor: 0.8, maxHealth: 140 },
    { id: 'light', name: 'Light', maxSpeedFactor: 1.4, maxHealth: 80 },
  ],
} as const satisfies PlayerShipRoster;
