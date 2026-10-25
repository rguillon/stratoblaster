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
import { buildFloeBreaker } from './world-2/floe-breaker-model';
import { buildNarwhal } from './world-2/narwhal-model';
import { buildFjordLynx } from './world-2/fjord-lynx-model';
import { buildHarbourKraken } from './world-2/harbour-kraken-model';
import { buildSnowOwl } from './world-2/snow-owl-model';
import { buildAuroraStation } from './world-2/aurora-station-model';
import { buildAvalanche } from './world-2/avalanche-model';
import { buildGlacierColossus } from './world-2/glacier-colossus-model';
import { buildIceQueen } from './world-2/ice-queen-model';
import { buildBorealCitadel } from './world-2/boreal-citadel-model';

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
  // World 2 (P08-R10).
  'floe-breaker': buildFloeBreaker,
  narwhal: buildNarwhal,
  'fjord-lynx': buildFjordLynx,
  'harbour-kraken': buildHarbourKraken,
  'snow-owl': buildSnowOwl,
  'aurora-station': buildAuroraStation,
  avalanche: buildAvalanche,
  'glacier-colossus': buildGlacierColossus,
  'ice-queen': buildIceQueen,
  'boreal-citadel': buildBorealCitadel,
};
