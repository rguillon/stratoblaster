import { buildLevelGrid, type LevelCatalog } from '../../core/content/level-catalog';
import { LEVELS_CONFIG } from '../config/levels';

/** This game's levels (P01-R07). */
export const LEVELS: LevelCatalog = buildLevelGrid(
  LEVELS_CONFIG.worlds,
  LEVELS_CONFIG.levelsPerWorld,
  LEVELS_CONFIG.unlocked,
);
