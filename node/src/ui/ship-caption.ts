import {
  findPlayerShip,
  shipMaxSpeedPxPerSec,
  type PlayerShipRoster,
} from '../core/entities/player-ship';
import type { Caption } from './caption-row';

/** Caption showing a player ship's name and stats, and its model's polygon count if given. */
export function shipCaption(roster: PlayerShipRoster, id: string, polygons?: number): Caption {
  const ship = findPlayerShip(roster, id);
  const pxPerSec = Math.round(shipMaxSpeedPxPerSec(roster, id));
  return {
    title: ship.name,
    lines: [
      `Speed ×${String(ship.maxSpeedFactor)} (${String(pxPerSec)} px/s)`,
      `HP ${String(ship.maxHealth)}`,
      ...(polygons === undefined ? [] : [`${polygons.toLocaleString('en-US')} polygons`]),
    ],
  };
}
