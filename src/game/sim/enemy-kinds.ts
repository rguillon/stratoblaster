import type { EnemyKindDefinition, EnemySpawnArea } from '../../core/entities/enemy';
import { randomIn } from '../../core/math/rng';
import { ENEMY_CONFIG as C, ENEMY_SPAWN_MARGIN as MARGIN } from '../config/enemies';
import { Bulwark } from './enemies/bulwark';
import { Carrier } from './enemies/carrier';
import { clampEntry, playfieldPath, pickX } from './enemies/enemy-helpers';
import { Gnat } from './enemies/gnat';
import { Hornet } from './enemies/hornet';
import { Lancer } from './enemies/lancer';
import { Rocketeer } from './enemies/rocketeer';
import { Scout } from './enemies/scout';
import { Spinner } from './enemies/spinner';
import { Splitter } from './enemies/splitter';
import { Strafer } from './enemies/strafer';
import { Weaver } from './enemies/weaver';

/** Just above the top edge. */
const top = (area: EnemySpawnArea): number => area.height + MARGIN;
const coin = (area: EnemySpawnArea): boolean => area.random() < 0.5;

/** X where a kind comes in from the top: the wave's entry (P06-R07), or random in `range`. */
const entryX = (area: EnemySpawnArea, range: readonly [number, number]): number =>
  area.entry?.side === 'top'
    ? clampEntry(area.entry.position) * area.width
    : pickX(area.random, range, area.width);

/**
 * Whether to mirror a path that starts at `startX` (a fraction of the width): towards the wave's
 * entry when it has one, at random otherwise.
 */
const mirrorFor = (area: EnemySpawnArea, startX: number): boolean => {
  const entry = area.entry;
  if (!entry) return coin(area);
  const at = entry.side === 'left' ? 0 : entry.side === 'right' ? 1 : entry.position;
  return Math.abs(1 - startX - at) < Math.abs(startX - at);
};

/** A side pass comes from the entry's side, at its height; at random otherwise. */
const sidePass = (area: EnemySpawnArea, heightFraction: number) => {
  const entry = area.entry;
  if (entry && entry.side !== 'top') {
    return { left: entry.side === 'left', y: clampEntry(entry.position) * area.height };
  }
  return { left: coin(area), y: heightFraction * area.height };
};

/** The 11 enemy kinds of P05, in the order of the spec. */
export const ENEMY_KINDS: readonly EnemyKindDefinition[] = [
  {
    id: 'gnat',
    name: 'Gnat',
    spawn: (area) => {
      const path = playfieldPath(C.gnat.path, area, mirrorFor(area, C.gnat.path[0][0]));
      return Array.from(
        { length: C.gnat.groupSize },
        (_, i) => new Gnat(path, i * C.gnat.groupDelay),
      );
    },
  },
  {
    id: 'hornet',
    name: 'Hornet',
    spawn: (area) => [
      new Hornet(entryX(area, C.hornet.xRange), top(area), {
        ...C.hornet,
        stopY: C.hornet.stopFraction * area.height,
      }),
    ],
  },
  {
    id: 'scout',
    name: 'Scout',
    spawn: (area) => [new Scout(entryX(area, C.scout.xRange), top(area))],
  },
  {
    id: 'strafer',
    name: 'Strafer',
    spawn: (area) => {
      const { left, y } = sidePass(area, C.strafer.heightFraction);
      const x = left ? -MARGIN : area.width + MARGIN;
      return [new Strafer(x, y, left ? 'left' : 'right')];
    },
  },
  {
    id: 'weaver',
    name: 'Weaver',
    spawn: (area) => [new Weaver(entryX(area, C.weaver.xRange), top(area))],
  },
  {
    id: 'spinner',
    name: 'Spinner',
    spawn: (area) => {
      const stopY = randomIn(area.random, C.spinner.stopRange) * area.height;
      return [new Spinner(entryX(area, C.spinner.xRange), top(area), stopY)];
    },
  },
  {
    id: 'lancer',
    name: 'Lancer',
    spawn: (area) => {
      const x = entryX(area, C.lancer.xRange);
      return [new Lancer(x, top(area), C.lancer.stopFraction * area.height)];
    },
  },
  {
    id: 'rocketeer',
    name: 'Rocketeer',
    spawn: (area) => [new Rocketeer(entryX(area, C.rocketeer.xRange), top(area))],
  },
  {
    id: 'bulwark',
    name: 'Bulwark',
    spawn: (area) => {
      const x = entryX(area, C.bulwark.xRange);
      return [new Bulwark(x, top(area), C.bulwark.stopFraction * area.height)];
    },
  },
  {
    id: 'splitter',
    name: 'Splitter',
    spawn: (area) => {
      const mirror = mirrorFor(area, C.splitter.path[0][0]);
      return [new Splitter(playfieldPath(C.splitter.path, area, mirror))];
    },
  },
  {
    id: 'carrier',
    name: 'Carrier',
    spawn: (area) => [new Carrier(entryX(area, C.carrier.xRange), top(area))],
  },
];
