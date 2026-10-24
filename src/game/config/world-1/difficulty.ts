import type { EnemyDifficulty } from '../../../core/systems/enemy-world';

/**
 * Per-level factors on the phase 5 enemy values (P06-R08, tunable values): enemy bullets fly
 * faster and enemies attack more often from 1-1 to 1-5. Neither ever goes down.
 */
export const WORLD_1_DIFFICULTY: Readonly<Record<string, EnemyDifficulty>> = {
  '1-1': { bulletSpeed: 0.8, fireRate: 0.8 },
  '1-2': { bulletSpeed: 0.85, fireRate: 0.85 },
  '1-3': { bulletSpeed: 0.9, fireRate: 0.9 },
  '1-4': { bulletSpeed: 1, fireRate: 1 },
  '1-5': { bulletSpeed: 1.1, fireRate: 1.1 },
};
