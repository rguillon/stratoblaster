import type { EnemyModelFactory } from '../../../render/game-view';
import { buildBreakwater } from './breakwater-model';
import { buildDustDevil } from './dust-devil-model';
import { buildGullMothership } from './gull-mothership-model';
import { buildMesaFortress } from './mesa-fortress-model';
import { buildOverlord } from './overlord-model';
import { buildReefWarden } from './reef-warden-model';
import { buildRefineryTitan } from './refinery-titan-model';
import { buildScorpion } from './scorpion-model';
import { buildSentinel } from './sentinel-model';
import { buildStormPetrel } from './storm-petrel-model';

/** One model per boss, keyed by its model key (the boss kind id, P07-R05). */
export const BOSS_MODELS: Readonly<Record<string, EnemyModelFactory>> = {
  'reef-warden': buildReefWarden,
  'storm-petrel': buildStormPetrel,
  breakwater: buildBreakwater,
  'gull-mothership': buildGullMothership,
  'dust-devil': buildDustDevil,
  'mesa-fortress': buildMesaFortress,
  scorpion: buildScorpion,
  'refinery-titan': buildRefineryTitan,
  sentinel: buildSentinel,
  overlord: buildOverlord,
};
