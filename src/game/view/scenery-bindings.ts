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
import { LEVEL_1_3 } from '../config/world-1/scenery-country';
import { LEVEL_1_4, LEVEL_1_5 } from '../config/world-1/scenery-desert';
import {
  LEVEL_2_1_LOOK,
  LEVEL_2_2_LOOK,
  LEVEL_2_3_LOOK,
  LEVEL_2_4_LOOK,
  LEVEL_2_5_LOOK,
} from '../config/world-2/looks';
import { LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4, LEVEL_2_5 } from '../config/world-2/scenery';
import {
  LEVEL_3_1_LOOK,
  LEVEL_3_2_LOOK,
  LEVEL_3_3_LOOK,
  LEVEL_3_4_LOOK,
  LEVEL_3_5_LOOK,
} from '../config/world-3/looks';
import { LEVEL_3_3, LEVEL_3_4, LEVEL_3_5 } from '../config/world-3/scenery-inland';
import { LEVEL_3_1, LEVEL_3_2 } from '../config/world-3/scenery-river';
import {
  LEVEL_4_1_LOOK,
  LEVEL_4_2_LOOK,
  LEVEL_4_3_LOOK,
  LEVEL_4_4_LOOK,
  LEVEL_4_5_LOOK,
} from '../config/world-4/looks';
import { LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5 } from '../config/world-4/scenery';
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

/** World 2 (P08-R06): one look per level, with its time of day and clouds. */
const WORLD_2_LOOKS: Readonly<Record<string, SceneryLook>> = {
  [LEVEL_2_1.id]: LEVEL_2_1_LOOK,
  [LEVEL_2_2.id]: LEVEL_2_2_LOOK,
  [LEVEL_2_3.id]: LEVEL_2_3_LOOK,
  [LEVEL_2_4.id]: LEVEL_2_4_LOOK,
  [LEVEL_2_5.id]: LEVEL_2_5_LOOK,
};

/** World 3 (P09-R04): one look per level, with its time of day, clouds, rain and lightning. */
const WORLD_3_LOOKS: Readonly<Record<string, SceneryLook>> = {
  [LEVEL_3_1.id]: LEVEL_3_1_LOOK,
  [LEVEL_3_2.id]: LEVEL_3_2_LOOK,
  [LEVEL_3_3.id]: LEVEL_3_3_LOOK,
  [LEVEL_3_4.id]: LEVEL_3_4_LOOK,
  [LEVEL_3_5.id]: LEVEL_3_5_LOOK,
};

/** World 4 (P10-R04): one look per level, with its time of day, clouds, ash and embers. */
const WORLD_4_LOOKS: Readonly<Record<string, SceneryLook>> = {
  [LEVEL_4_1.id]: LEVEL_4_1_LOOK,
  [LEVEL_4_2.id]: LEVEL_4_2_LOOK,
  [LEVEL_4_3.id]: LEVEL_4_3_LOOK,
  [LEVEL_4_4.id]: LEVEL_4_4_LOOK,
  [LEVEL_4_5.id]: LEVEL_4_5_LOOK,
};

/** How this game's generated levels look (P04, P06, P08, P09, P10). */
export const SCENERY_BINDINGS: SceneryBindings = {
  camera: CAMERA,
  looks: {
    [LEVEL_ZERO.id]: LEVEL_ZERO_SCENERY,
    ...WORLD_1_LOOKS,
    ...WORLD_2_LOOKS,
    ...WORLD_3_LOOKS,
    ...WORLD_4_LOOKS,
  },
  propModels: PROP_MODELS,
};
