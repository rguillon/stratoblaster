import type { ColorFamily, Rgb } from '../../core/math/color';

/**
 * Phase 14 (playability): what keeps the playfield readable. Each kind of gameplay object has a
 * colour family no other uses (P14-R02); the ground is dimmed under a dark veil (P14-R01); and
 * the thresholds the readability check measures (P14-R03..R08). Hues in degrees, colours
 * linear RGB 0..1, sizes in logical pixels, times in seconds.
 */
export const READABILITY = {
  /**
   * P14-R02 (reviewer, 2026-10-27): one hue range per kind of object, none overlapping. Pale
   * colours (sand, beige; under `minSaturation`) read as no colour and belong to none.
   */
  families: {
    /** Player ship accents and player shots: cyan to ice blue (GD-61). */
    player: { from: 180, to: 235, minSaturation: 0.5 },
    /** Enemy and boss neon: violet, magenta, blood red. */
    enemy: { from: 265, to: 5, minSaturation: 0.5 },
    /** Enemy bullets, missiles and lasers: orange to yellow, round a white-hot core. */
    enemyShot: { from: 18, to: 58, minSaturation: 0.5 },
    /** Bonuses: acid green to mint; their shapes tell the kinds apart. */
    pickup: { from: 85, to: 160, minSaturation: 0.5 },
  } satisfies Record<string, ColorFamily>,
  /**
   * P14-R01, per world: the share of their colour the ground, the shores, the water, the roads
   * and the props keep (reviewer, 2026-10-28: in place of a dark veil over the background).
   */
  tones: {
    world0: 0.58,
    world1: 0.55,
    // Snow and ice: the brightest ground.
    world2: 0.45,
    world3: 0.45,
    world4: 0.58,
  },
  /** P14-R01: the ground's brightest pixels (relative luminance), but for a share of the screen. */
  backgroundMaxLuminance: 0.35,
  backgroundBrightPixelBudget: 0.02,
  /** P14-R03, R04: contrast ratio of a ship's outline with the ground round it. */
  minObjectContrast: 3,
  /** P14-R05, R06: contrast ratio of an enemy bullet's core with what is round it. */
  minBulletContrast: 4.5,
  /** P14-R05: an enemy bullet's smallest drawn diameter. */
  minEnemyBulletSize: 6,
  /** P14-R06: the player shots' strength (additive opacity). */
  playerShotMaxOpacity: 0.7,
  /**
   * P14-R08: the contrast a player shot keeps with the ground, toned down (R06 sets no
   * contrast for them: they only must still show).
   */
  minPlayerShotContrast: 2,
  /** P14-R07: an explosion's largest share of the screen, and how long it may last. */
  effectMaxScreenShare: 0.15,
  effectMaxDuration: 0.6,
  /** P14-R03: the player ship's rim glow, and the marker on its hitbox centre. */
  playerOutline: { color: [0.3, 0.9, 1] as Rgb },
  hitboxMarker: { color: [1, 1, 1] as Rgb, rim: [0.2, 0.85, 1] as Rgb, segments: 16 },
  /**
   * P14-R04: the enemies' rim is their neon colour `whiten` of the way to white (violet and
   * magenta alone are too dark to stand out on a dark ground), times `strength`.
   */
  enemyOutline: { whiten: 0.5, strength: 1 },
  /**
   * Reviewer, 2026-10-28: the light on the ships', enemies' and bosses' metal, as factors on the
   * direct light (sun, lamps) and on the sky's reflections, so they stand out brighter.
   */
  hullLight: { direct: 1.8, environment: 1.8 },
  /** Rims (P14-R03, R04): width in logical pixels, and strength. */
  outline: { width: 0.9, intensity: 1.2 },
} as const;
