import type { LogicalScreen } from '../../core/content/game-definition';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import type { AtmosphereOptions } from './atmosphere-of';
import type { SceneryKitFactory } from './scenery-kit';
import type { PlayfieldCameraLook, PropModelFactory, SceneryLook } from './scenery-look';

/** Engine settings of a `SceneryStage`. */
export interface SceneryStageConfig {
  /** Terrain chunk length along Z and grid cell size. */
  readonly chunkLength: number;
  readonly cell: number;
  /** Extra ground generated around what the camera sees. */
  readonly margin: number;
  /** Smallest gap between the highest ground and a cloud layer. */
  readonly cloudClearance: number;
  /** How far behind the scene the sun is placed, for its shadows. */
  readonly sunDistance: number;
  /** Far clipping distance of the camera. */
  readonly farClip: number;
  /**
   * How far before and past the ground in view props are drawn (tall ones show from further),
   * and by how much the drawn range is widened, so it is uploaded again only now and then.
   */
  readonly propReach: readonly [near: number, far: number];
  readonly propStep: number;
}

export interface SceneryStageOptions {
  readonly screen: LogicalScreen;
  readonly camera: PlayfieldCameraLook;
  readonly level: SceneryLevel;
  readonly look: SceneryLook;
  readonly propModels: Readonly<Record<string, PropModelFactory>>;
  readonly kit: SceneryKitFactory;
  readonly config: SceneryStageConfig;
  /** Debug choices on the level's look (P08-R12): a forced time of day, no weather. */
  readonly atmosphere?: AtmosphereOptions;
}
