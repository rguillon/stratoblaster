import { buildLevelGrid, type LevelCatalog } from '../../core/content/level-catalog';
import { LEVELS_CONFIG } from '../config/levels';
import { WORLD_1 } from './world-1';

/** This game's levels (P01-R07): every level that exists is unlocked (P06-R01). */
export const LEVELS: LevelCatalog = buildLevelGrid(
  LEVELS_CONFIG.worlds,
  LEVELS_CONFIG.levelsPerWorld,
  WORLD_1.map((level) => level.id),
);
