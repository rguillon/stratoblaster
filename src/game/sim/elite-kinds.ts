import type { EnemyKindDefinition, EnemySpawnArea } from '../../core/entities/enemy';
import { randomIn } from '../../core/math/rng';
import { ENEMY_SPAWN_MARGIN as MARGIN } from '../config/enemies';
import { ELITE_CONFIG as C } from '../config/enemies-elite';
import { clampEntry, pickX, topX } from './enemies/enemy-helpers';
import { Hive } from './enemies/hive';
import { Hydra } from './enemies/hydra';
import { Juggernaut } from './enemies/juggernaut';
import { Orbiter } from './enemies/orbiter';
import { Scissor } from './enemies/scissor';

/** Just above the top edge. */
const top = (area: EnemySpawnArea): number => area.height + MARGIN;

/**
 * X where a kind comes in from the top: the wave's entry (P06-R07), or random in `range`, both
 * taken across the area's `topRange` (as in `enemy-kinds.ts`).
 */
const entryX = (area: EnemySpawnArea, range: readonly [number, number]): number =>
  area.entry?.side === 'top'
    ? topX(area, clampEntry(area.entry.position))
    : pickX(area.random, range, area);

/** The five elite kinds (P05-R19 to P05-R23), in the order of the spec. */
export const ELITE_KINDS: readonly EnemyKindDefinition[] = [
  {
    id: 'hydra',
    name: 'Hydra',
    spawn: (area) => {
      const x = entryX(area, C.hydra.xRange);
      return [new Hydra(x, top(area), C.hydra.stopFraction * area.height)];
    },
  },
  {
    id: 'orbiter',
    name: 'Orbiter',
    spawn: (area) => {
      const stopY = randomIn(area.random, C.orbiter.stopRange) * area.height;
      return [new Orbiter(entryX(area, C.orbiter.xRange), top(area), stopY)];
    },
  },
  {
    id: 'scissor',
    name: 'Scissor',
    spawn: (area) => {
      const x = entryX(area, C.scissor.xRange);
      return [new Scissor(x, top(area), C.scissor.stopFraction * area.height)];
    },
  },
  {
    id: 'juggernaut',
    name: 'Juggernaut',
    spawn: (area) => {
      const x = entryX(area, C.juggernaut.xRange);
      return [new Juggernaut(x, top(area), C.juggernaut.stopFraction * area.height)];
    },
  },
  {
    id: 'hive',
    name: 'Hive',
    spawn: (area) => [new Hive(entryX(area, C.hive.xRange), top(area))],
  },
];
