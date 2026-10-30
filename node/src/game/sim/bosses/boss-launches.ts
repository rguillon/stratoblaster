import type { Enemy } from '../../../core/entities/enemy';
import type { BossVolley } from '../../../core/systems/boss-pattern';
import { Path, type PathPoint } from '../../../core/systems/enemy-motion';
import type { Launch } from '../../config/bosses/boss-kit';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Gnat } from '../enemies/gnat';
import { Hornet } from '../enemies/hornet';

const GNATS = ENEMY_CONFIG.gnat;
const CARRIER = ENEMY_CONFIG.carrier;

/** Gnats leaving a hangar: out to its side (the side of the boss it is on), then down. */
function gnats(count: number, side: number): (x: number, y: number) => Enemy[] {
  return (x, y) => {
    const path = new Path(CARRIER.launchPath.map(([px, py]): PathPoint => [x + side * px, y + py]));
    return Array.from({ length: count }, (_, i) => new Gnat(path, i * GNATS.groupDelay));
  };
}

/** Hornets leaving a bay: they pause, turn to the player and dive (P05-R02). */
function hornets(count: number): (x: number, y: number) => Enemy[] {
  return (x, y) =>
    Array.from(
      { length: count },
      (_, i) => new Hornet(x + (i - (count - 1) / 2) * 14, y, ENEMY_CONFIG.hornet),
    );
}

/**
 * The launch volley of `launch`, from its part (P07-R05: hangars, drone bays). `side` is which
 * side of the boss the part is on (-1 left, 1 right), for the Gnats' way out.
 */
export function launchVolley(launch: Launch, side: number): BossVolley {
  const fire = launch.kind === 'gnats' ? gnats(launch.count, side || 1) : hornets(launch.count);
  return {
    from: launch.from,
    every: launch.every,
    ...(launch.first === undefined ? {} : { first: launch.first }),
    shape: { kind: 'launch', launch: fire },
  };
}
