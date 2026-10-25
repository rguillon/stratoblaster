import type { GameLevel } from '../../core/content/game-level';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { WORLD_2_BOSSES } from '../config/world-2/bosses';
import { WORLD_2_DIFFICULTY } from '../config/world-2/difficulty';
import { LEVEL_2_1, LEVEL_2_2 } from '../config/world-2/scenery-coast';
import { LEVEL_2_3, LEVEL_2_4, LEVEL_2_5 } from '../config/world-2/scenery-inland';
import {
  composeBeats,
  PLAN_2_1,
  PLAN_2_2,
  PLAN_2_3,
  PLAN_2_4,
  PLAN_2_5,
  WORLD_2_FILLERS,
  type WavePlan,
} from '../config/world-2/waves';
import { assembleLevel } from './assemble-level';

const TABLES = {
  difficulty: WORLD_2_DIFFICULTY,
  fillers: WORLD_2_FILLERS,
  bosses: WORLD_2_BOSSES,
};

const level = (id: string, scenery: SceneryLevel, plan: WavePlan) =>
  assembleLevel(id, scenery, composeBeats(plan), TABLES);

/**
 * World 2, the Frozen North (P08): five levels of about 5 minutes, from a cold sea with drifting
 * ice to a polar city at night, each with a mini boss and a final boss.
 */
export const WORLD_2: readonly GameLevel[] = [
  level('2-1', LEVEL_2_1, PLAN_2_1),
  level('2-2', LEVEL_2_2, PLAN_2_2),
  level('2-3', LEVEL_2_3, PLAN_2_3),
  level('2-4', LEVEL_2_4, PLAN_2_4),
  level('2-5', LEVEL_2_5, PLAN_2_5),
];
