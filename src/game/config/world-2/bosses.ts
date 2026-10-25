import type { LevelBosses } from '../world-1/bosses';

/**
 * The bosses of each World 2 level (P08-R10): a mini boss at the middle of the level and a final
 * boss at its end, by boss kind id, and the seconds of ground drawn past the level's end for the
 * fights (see `WORLD_1_BOSSES`).
 */
export const WORLD_2_BOSSES: Readonly<Record<string, LevelBosses>> = {
  '2-1': { mini: 'floe-breaker', final: 'narwhal', runout: 160 },
  '2-2': { mini: 'fjord-lynx', final: 'harbour-kraken', runout: 50 },
  '2-3': { mini: 'snow-owl', final: 'aurora-station', runout: 80 },
  '2-4': { mini: 'avalanche', final: 'glacier-colossus', runout: 120 },
  '2-5': { mini: 'ice-queen', final: 'boreal-citadel', runout: 80 },
};
