import type { RoadRules } from '../../../core/scenery/scenery-level';
import { WORLD_1_ROADS } from '../world-1/props';

/*
 * World 4's own rules. Its buildings are the city's (`city-props.ts`); the volcanic props of the
 * first World 4 were removed (reviewer, 2026-10-28).
 */

/** Roads of World 4: as in World 1 (no crossings, D-046); the looks make them dark and cracked. */
export const WORLD_4_ROADS: RoadRules = WORLD_1_ROADS;
