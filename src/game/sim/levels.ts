import { buildLevelGrid, type LevelCatalog } from '../../core/content/level-catalog';
import { LEVELS_CONFIG } from '../config/levels';
import { WORLD_1 } from './world-1';
import { WORLD_2 } from './world-2';

/** Every playable level of this game, World 1 then World 2 (P06, P08). */
export const GAME_LEVELS = [...WORLD_1, ...WORLD_2];

/** This game's levels (P01-R07): every level that exists is unlocked (P06-R01). */
export const LEVELS: LevelCatalog = buildLevelGrid(
  LEVELS_CONFIG.worlds,
  LEVELS_CONFIG.levelsPerWorld,
  GAME_LEVELS.map((level) => level.id),
);
