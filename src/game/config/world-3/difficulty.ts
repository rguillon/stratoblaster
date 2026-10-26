import type { EnemyDifficulty } from '../../../core/systems/enemy-world';

/**
 * Per-level factors on the phase 5 enemy values in World 3 (P09-R08, tunable values): 3-1 starts
 * as hard as 2-3 and 3-5 is harder than 2-5. Neither ever goes down.
 */
export const WORLD_3_DIFFICULTY: Readonly<Record<string, EnemyDifficulty>> = {
  '3-1': { bulletSpeed: 1, fireRate: 1 },
  '3-2': { bulletSpeed: 1.05, fireRate: 1.05 },
  '3-3': { bulletSpeed: 1.1, fireRate: 1.1 },
  '3-4': { bulletSpeed: 1.2, fireRate: 1.2 },
  '3-5': { bulletSpeed: 1.25, fireRate: 1.25 },
};
