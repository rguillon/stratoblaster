import type { RoadRules } from '../../../core/scenery/scenery-level';
import { WORLD_3_ROADS } from '../world-3/props';

/*
 * World 4's own rules. Its buildings are the city's (`city-props.ts`); the volcanic props of the
 * first World 4 were removed (reviewer, 2026-10-28).
 */

/**
 * Roads of World 4: as in World 3 (no crossings, D-046, street grids as wide as the ground that
 * shows), and in the city's street grids, wide straight boulevards of 3 lanes each way, 3 × 3
 * tiles (reviewer, 2026-10-28; the 4-lane ones dropped, 3 × 3 is enough).
 */
export const WORLD_4_ROADS: RoadRules = {
  ...WORLD_3_ROADS,
  boulevards: [{ lanes: 3, width: 18, share: 0.2 }],
};
