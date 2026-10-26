import type { LevelBosses } from '../world-1/bosses';

/**
 * The bosses of each World 4 level (P10-R11): a mini boss at the middle of the level and a final
 * boss at its end, by boss kind id, and the seconds of ground drawn past the level's end for the
 * fights (see `WORLD_1_BOSSES`).
 */
export const WORLD_4_BOSSES: Readonly<Record<string, LevelBosses>> = {
  '4-1': { mini: 'cinder-crab', final: 'steam-dreadnought', runout: 120 },
  '4-2': { mini: 'ash-wraith', final: 'geyser-rig', runout: 150 },
  '4-3': { mini: 'magma-salamander', final: 'obsidian-golem', runout: 100 },
  '4-4': { mini: 'furnace-drake', final: 'foundry-ark', runout: 100 },
  '4-5': { mini: 'ember-herald', final: 'caldera-throne', runout: 130 },
};
