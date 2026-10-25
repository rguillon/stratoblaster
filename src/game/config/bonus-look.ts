/**
 * Look of the weapon bonuses (phase 6 review): an acid-yellow hexagon badge with cyan chevrons
 * pointing up (a level up), swinging from side to side over a pulsing yellow halo; a cyan ring flashes
 * out where the ship picks one up. Linear RGB, 0..1; sizes in logical pixels; times in seconds.
 */

type Rgb = readonly [number, number, number];

export const BONUS_LOOK = {
  /** Radius of the badge (corner of its hexagon). */
  size: 11,
  /** In front of the ships and the explosions (towards the camera, -Z). */
  depth: -4,
  // Below full strength: the playfield's glow would wash them out to white.
  frame: [0.8, 0.6, 0.03] as Rgb,
  face: [0.06, 0.04, 0.1] as Rgb,
  chevrons: [0.02, 0.6, 0.75] as Rgb,
  /** Inner edge of the frame, as a share of the size. */
  frameInset: 0.78,
  /**
   * It swings around its upright axis, up to `amplitude` radians each way, `hz` times a second
   * (a whole turn would show it edge on half the time).
   */
  swing: { amplitude: 0.9, hz: 0.7 },
  halo: {
    colors: [
      [0.5, 0.43, 0.05],
      [0.22, 0.18, 0.03],
      [0.06, 0.05, 0.01],
      [0, 0, 0],
    ] as readonly Rgb[],
    /** Radius, as a multiple of the badge size. */
    size: 1.7,
    /** It swells and shrinks by this share, this many times a second. */
    pulse: 0.2,
    pulseHz: 2.5,
    segments: 20,
  },
  flash: { size: 4, life: 0.35, color: [0.3, 1, 1] as Rgb, segments: 32 },
} as const;
