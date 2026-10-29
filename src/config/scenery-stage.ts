/** Tunables of the generated ground under the playfield camera (P04): the game and the viewers. */
export const SCENERY_STAGE_CONFIG = {
  /** Terrain chunk length along Z, and the grid cell of the terrain mesh. */
  chunkLength: 320,
  cell: 8,
  /** Extra ground generated around what the camera sees. */
  margin: 80,
  /** Cloud layers stay at least this high above the highest ground. */
  cloudClearance: 15,
  sunDistance: 2500,
  farClip: 4000,
  // Review: props are drawn only near the ground in view. The tallest stand about 60 high, and
  // the camera looks down at about 35° at the top edge: they show from about 90 past it.
  propReach: [40, 120],
  propStep: 40,
} as const;
