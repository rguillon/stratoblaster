import type { GameLevel } from '../../core/content/game-level';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { WORLD_4_BOSSES } from '../config/world-4/bosses';
import { WORLD_4_DIFFICULTY } from '../config/world-4/difficulty';
import { LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5 } from '../config/world-4/scenery';
import {
  PLAN_4_1,
  PLAN_4_2,
  PLAN_4_3,
  PLAN_4_4,
  PLAN_4_5,
  WORLD_4_FILLERS,
} from '../config/world-4/waves';
import { composeBeats, type WavePlan } from '../config/world-2/waves';
import { assembleLevel } from './assemble-level';

const TABLES = {
  difficulty: WORLD_4_DIFFICULTY,
  fillers: WORLD_4_FILLERS,
  bosses: WORLD_4_BOSSES,
};

const level = (id: string, scenery: SceneryLevel, plan: WavePlan) =>
  assembleLevel(id, scenery, composeBeats(plan), TABLES);

/**
 * World 4, the Volcanic Lands (P10): five levels of about 5 minutes, from black-sand volcanic
 * islands to an erupting caldera, each with a mini boss and a final boss.
 */
export const WORLD_4: readonly GameLevel[] = [
  level('4-1', LEVEL_4_1, PLAN_4_1),
  level('4-2', LEVEL_4_2, PLAN_4_2),
  level('4-3', LEVEL_4_3, PLAN_4_3),
  level('4-4', LEVEL_4_4, PLAN_4_4),
  level('4-5', LEVEL_4_5, PLAN_4_5),
];
