/**
 * Look of a bomb going off (P11-R05): a cyan shockwave ring growing from the ship until it
 * covers the playfield, fading as it goes, and a short warm flash at the ship. One bomb at a
 * time and each lasting 1 s, there is never more than one flash a second (below the 3 a
 * second limit). Linear RGB, 0..1; sizes in logical pixels; times in seconds.
 */

type Rgb = readonly [number, number, number];

export const BOMB_LOOK = {
  /** In front of the ships and the explosions (towards the camera, -Z). */
  depth: -5,
  wave: {
    /** Radius it reaches as the bomb ends: past the corners of the 480 × 640 playfield. */
    radius: 820,
    /** Rings from the centre out: black (nothing, added on) inside, a bright rim. */
    colors: [
      [0, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
      [0.05, 0.25, 0.3],
      [0.3, 0.9, 1],
      [0, 0, 0],
    ] as readonly Rgb[],
    segments: 48,
  },
  flash: {
    /** Seconds it fades over, and its radius. */
    seconds: 0.3,
    radius: 320,
    colors: [
      [0.7, 0.6, 0.4],
      [0.4, 0.3, 0.18],
      [0.12, 0.08, 0.04],
      [0, 0, 0],
    ] as readonly Rgb[],
    segments: 32,
  },
} as const;
