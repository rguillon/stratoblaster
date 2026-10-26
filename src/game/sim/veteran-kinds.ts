import type { EnemyKindDefinition, EnemySpawnArea } from '../../core/entities/enemy';
import { randomIn } from '../../core/math/rng';
import { ENEMY_SPAWN_MARGIN as MARGIN } from '../config/enemies';
import { VETERAN_CONFIG as C } from '../config/enemies-veteran';
import { clampEntry, pickX, topX } from './enemies/enemy-helpers';
import { Mantis } from './enemies/mantis';
import { Minelayer } from './enemies/minelayer';
import { Mortar } from './enemies/mortar';
import { Phantom } from './enemies/phantom';
import { Wasp } from './enemies/wasp';

// Where the veteran kinds come in, as the first kinds do (`enemy-kinds.ts`): kept here, not
// imported from there, as `enemy-kinds.ts` imports this file.

/** Just above the top edge. */
const top = (area: EnemySpawnArea): number => area.height + MARGIN;

/** X where a kind comes in from the top: the wave's entry (P06-R07), or random in `range`. */
const entryX = (area: EnemySpawnArea, range: readonly [number, number]): number =>
  area.entry?.side === 'top'
    ? topX(area, clampEntry(area.entry.position))
    : pickX(area.random, range, area);

/** A side pass comes from the entry's side, at its height; at random otherwise. */
const sidePass = (area: EnemySpawnArea, heightFraction: number) => {
  const entry = area.entry;
  if (entry && entry.side !== 'top') {
    return { left: entry.side === 'left', y: clampEntry(entry.position) * area.height };
  }
  return { left: area.random() < 0.5, y: heightFraction * area.height };
};

/** P05-R14: a group of Wasps side by side, kept inside the range coming in from the top. */
function waspGroup(area: EnemySpawnArea): Wasp[] {
  const { groupSize, groupSpacing, stopFraction } = C.wasp;
  const [min, max] = area.topRange ?? [0, area.width];
  const half = ((groupSize - 1) * groupSpacing) / 2;
  const middle = Math.min(max - half, Math.max(min + half, entryX(area, C.wasp.xRange)));
  return Array.from(
    { length: groupSize },
    (_, i) => new Wasp(middle - half + i * groupSpacing, top(area), stopFraction * area.height),
  );
}

/** The five veteran kinds (P05-R14 to P05-R18), in the order of the spec. */
export const VETERAN_KINDS: readonly EnemyKindDefinition[] = [
  { id: 'wasp', name: 'Wasp', spawn: waspGroup },
  {
    id: 'mortar',
    name: 'Mortar',
    spawn: (area) => [new Mortar(entryX(area, C.mortar.xRange), top(area))],
  },
  {
    id: 'mantis',
    name: 'Mantis',
    spawn: (area) => {
      const stopY = randomIn(area.random, C.mantis.stopRange) * area.height;
      return [new Mantis(entryX(area, C.mantis.xRange), top(area), stopY)];
    },
  },
  {
    id: 'phantom',
    name: 'Phantom',
    spawn: (area) => {
      const stopY = randomIn(area.random, C.phantom.placeY) * area.height;
      return [new Phantom(entryX(area, C.phantom.xRange), top(area), stopY)];
    },
  },
  {
    id: 'minelayer',
    name: 'Minelayer',
    spawn: (area) => {
      const { left, y } = sidePass(area, C.minelayer.heightFraction);
      const x = left ? -MARGIN : area.width + MARGIN;
      // Always in the top half, whatever the entry.
      const high = Math.max(y, C.minelayer.lowestFraction * area.height);
      return [new Minelayer(x, high, left ? 'left' : 'right')];
    },
  },
];
