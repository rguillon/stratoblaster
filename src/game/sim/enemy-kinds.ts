import type { EnemyKindDefinition, EnemySpawnArea } from '../../core/entities/enemy';
import { randomIn } from '../../core/math/rng';
import { ENEMY_CONFIG as C, ENEMY_SPAWN_MARGIN as MARGIN } from '../config/enemies';
import { Bulwark } from './enemies/bulwark';
import { Carrier } from './enemies/carrier';
import { playfieldPath, pickX } from './enemies/enemy-helpers';
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

/** The 11 enemy kinds of P05, in the order of the spec. */
export const ENEMY_KINDS: readonly EnemyKindDefinition[] = [
  {
    id: 'gnat',
    name: 'Gnat',
    spawn: (area) => {
      const path = playfieldPath(C.gnat.path, area, coin(area));
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
      new Hornet(pickX(area.random, C.hornet.xRange, area.width), top(area), {
        ...C.hornet,
        stopY: C.hornet.stopFraction * area.height,
      }),
    ],
  },
  {
    id: 'scout',
    name: 'Scout',
    spawn: (area) => [new Scout(pickX(area.random, C.scout.xRange, area.width), top(area))],
  },
  {
    id: 'strafer',
    name: 'Strafer',
    spawn: (area) => {
      const left = coin(area);
      const x = left ? -MARGIN : area.width + MARGIN;
      return [new Strafer(x, C.strafer.heightFraction * area.height, left ? 'left' : 'right')];
    },
  },
  {
    id: 'weaver',
    name: 'Weaver',
    spawn: (area) => [new Weaver(pickX(area.random, C.weaver.xRange, area.width), top(area))],
  },
  {
    id: 'spinner',
    name: 'Spinner',
    spawn: (area) => {
      const stopY = randomIn(area.random, C.spinner.stopRange) * area.height;
      return [new Spinner(pickX(area.random, C.spinner.xRange, area.width), top(area), stopY)];
    },
  },
  {
    id: 'lancer',
    name: 'Lancer',
    spawn: (area) => {
      const x = pickX(area.random, C.lancer.xRange, area.width);
      return [new Lancer(x, top(area), C.lancer.stopFraction * area.height)];
    },
  },
  {
    id: 'rocketeer',
    name: 'Rocketeer',
    spawn: (area) => [new Rocketeer(pickX(area.random, C.rocketeer.xRange, area.width), top(area))],
  },
  {
    id: 'bulwark',
    name: 'Bulwark',
    spawn: (area) => {
      const x = pickX(area.random, C.bulwark.xRange, area.width);
      return [new Bulwark(x, top(area), C.bulwark.stopFraction * area.height)];
    },
  },
  {
    id: 'splitter',
    name: 'Splitter',
    spawn: (area) => [new Splitter(playfieldPath(C.splitter.path, area, coin(area)))],
  },
  {
    id: 'carrier',
    name: 'Carrier',
    spawn: (area) => [new Carrier(pickX(area.random, C.carrier.xRange, area.width), top(area))],
  },
];
