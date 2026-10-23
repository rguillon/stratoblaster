import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { LEVEL_ZERO_CONFIG } from '../config/level-zero';

/** Level Zero, the test level of the terrain tools (P04). */
export const LEVEL_ZERO: SceneryLevel = LEVEL_ZERO_CONFIG;

/** This game's levels with generated ground, shown by the `level_zero/` page. */
export const SCENERY_LEVELS: readonly SceneryLevel[] = [LEVEL_ZERO];
