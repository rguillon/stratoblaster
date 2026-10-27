import type { GameLevel } from '../../core/content/game-level';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { WORLD_3_BOSSES } from '../config/world-3/bosses';
import { WORLD_3_DIFFICULTY } from '../config/world-3/difficulty';
import { LEVEL_3_1, LEVEL_3_2, LEVEL_3_3, LEVEL_3_4, LEVEL_3_5 } from '../config/world-3/scenery';
import {
  PLAN_3_1,
  PLAN_3_2,
  PLAN_3_3,
  PLAN_3_4,
  PLAN_3_5,
  WORLD_3_FILLERS,
} from '../config/world-3/waves';
import { composeBeats, type WavePlan } from '../config/world-2/waves';
import { assembleLevel } from './assemble-level';

const TABLES = {
  difficulty: WORLD_3_DIFFICULTY,
  fillers: WORLD_3_FILLERS,
  bosses: WORLD_3_BOSSES,
};

const level = (id: string, scenery: SceneryLevel, plan: WavePlan) =>
  assembleLevel(id, scenery, composeBeats(plan), TABLES);

/**
 * World 3 (P09; reworked at the reviewer's request, 2026-10-27): five levels of about 5 minutes,
 * from the factories World 2 ended on to garden villages of small houses, each with a mini boss
 * and a final boss.
 */
export const WORLD_3: readonly GameLevel[] = [
  level('3-1', LEVEL_3_1, PLAN_3_1),
  level('3-2', LEVEL_3_2, PLAN_3_2),
  level('3-3', LEVEL_3_3, PLAN_3_3),
  level('3-4', LEVEL_3_4, PLAN_3_4),
  level('3-5', LEVEL_3_5, PLAN_3_5),
];
