import type { EnemyModelFactory } from '../../../render/game-view';
import { buildMinelayer, buildMortar } from './veteran-heavy-models';
import { buildMantis } from './veteran-mantis-model';
import { buildPhantom, buildWasp } from './veteran-small-models';

/** One model per veteran model key (P05-R14 to P05-R18). */
export const VETERAN_MODELS: Readonly<Record<string, EnemyModelFactory>> = {
  wasp: buildWasp,
  mortar: buildMortar,
  mantis: buildMantis,
  phantom: buildPhantom,
  minelayer: buildMinelayer,
};
