import type { RoadRules } from '../../../core/scenery/scenery-level';
import { WORLD_3_ROADS } from '../world-3/props';

/*
 * World 4's own rules. Its buildings are the city's (`city-props.ts`); the volcanic props of the
 * first World 4 were removed (reviewer, 2026-10-28).
 */

/**
 * Roads of World 4: as in World 3 (no crossings, D-046, street grids as wide as the ground that
 * shows), and in the city's street grids, wide straight boulevards of 3 and 4 lanes each way
 * (reviewer, 2026-10-28).
 */
export const WORLD_4_ROADS: RoadRules = {
  ...WORLD_3_ROADS,
  boulevards: [
    { lanes: 3, width: 18, share: 0.12 },
    { lanes: 4, width: 24, share: 0.08 },
  ],
};
