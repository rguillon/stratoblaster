import type { SceneryBindings } from '../../render/game-view';
import type { PlayfieldCameraLook, SceneryLook } from '../../render/scenery/scenery-look';
import { LEVEL_ZERO_LOOK, PLAYFIELD_CAMERA } from '../config/scenery-look';
import { LEVEL_ZERO } from '../sim/scenery-levels';
import { PROP_MODELS } from './props/prop-models';

const CAMERA: PlayfieldCameraLook = PLAYFIELD_CAMERA;
const LEVEL_ZERO_SCENERY: SceneryLook = LEVEL_ZERO_LOOK;

/** How this game's generated levels look (P04). */
export const SCENERY_BINDINGS: SceneryBindings = {
  camera: CAMERA,
  looks: { [LEVEL_ZERO.id]: LEVEL_ZERO_SCENERY },
  propModels: PROP_MODELS,
};
