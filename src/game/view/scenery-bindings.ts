import type { SceneryBindings } from '../../render/game-view';
import type { PlayfieldCameraLook, SceneryLook } from '../../render/scenery/scenery-look';
import { LEVEL_ZERO_LOOK, PLAYFIELD_CAMERA } from '../config/scenery-look';
import {
  LEVEL_1_1_LOOK,
  LEVEL_1_2_LOOK,
  LEVEL_1_3_LOOK,
  LEVEL_1_4_LOOK,
  LEVEL_1_5_LOOK,
} from '../config/world-1/looks';
import { LEVEL_1_1, LEVEL_1_2 } from '../config/world-1/scenery-coast';
import { LEVEL_1_3, LEVEL_1_4, LEVEL_1_5 } from '../config/world-1/scenery-desert';
import { LEVEL_ZERO } from '../sim/scenery-levels';
import { PROP_MODELS } from './props/prop-models';

const CAMERA: PlayfieldCameraLook = PLAYFIELD_CAMERA;
const LEVEL_ZERO_SCENERY: SceneryLook = LEVEL_ZERO_LOOK;

/** World 1 (P06-R05): one look per level. */
const WORLD_1_LOOKS: Readonly<Record<string, SceneryLook>> = {
  [LEVEL_1_1.id]: LEVEL_1_1_LOOK,
  [LEVEL_1_2.id]: LEVEL_1_2_LOOK,
  [LEVEL_1_3.id]: LEVEL_1_3_LOOK,
  [LEVEL_1_4.id]: LEVEL_1_4_LOOK,
  [LEVEL_1_5.id]: LEVEL_1_5_LOOK,
};

/** How this game's generated levels look (P04, P06). */
export const SCENERY_BINDINGS: SceneryBindings = {
  camera: CAMERA,
  looks: { [LEVEL_ZERO.id]: LEVEL_ZERO_SCENERY, ...WORLD_1_LOOKS },
  propModels: PROP_MODELS,
};
