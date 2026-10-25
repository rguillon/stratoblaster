/**
 * Look of the bosses (P07): their neon colours (GD-61), the white flash of a part when hit, the
 * smoke of a part under half its health, and the stump left by a destroyed part (P07-R01).
 * Linear RGB 0..1, sizes in logical pixels, times in seconds.
 */

type Rgb = readonly [number, number, number];

export const BOSS_LOOK = {
  /** Neon colour of each boss (P07-R05), by boss kind id. */
  neon: {
    'reef-warden': [0.1, 0.9, 1],
    'storm-petrel': [1, 0.1, 0.85],
    breakwater: [1, 0.5, 0.05],
    'gull-mothership': [0.2, 1, 0.35],
    'dust-devil': [1, 0.75, 0.15],
    'mesa-fortress': [1, 0.1, 0.12],
    scorpion: [1, 0.9, 0.1],
    'refinery-titan': [1, 0.45, 0.05],
    sentinel: [0.15, 0.4, 1],
    overlord: [0.65, 0.2, 1],
    // World 2 (P08-R10).
    'floe-breaker': [0.1, 0.85, 1],
    narwhal: [0.05, 0.95, 0.75],
    'fjord-lynx': [0.55, 0.95, 1],
    'harbour-kraken': [1, 0.5, 0.08],
    'snow-owl': [0.85, 0.92, 1],
    'aurora-station': [0.3, 1, 0.55],
    avalanche: [1, 0.85, 0.1],
    'glacier-colossus': [1, 0.35, 0.08],
    'ice-queen': [0.55, 0.65, 1],
    'boreal-citadel': [0.35, 1, 0.6],
  } as Readonly<Record<string, Rgb>>,
  /** Its charge lights strobe this many times a second while it holds its fire (P07-R04). */
  stageStrobeHz: 6,
  /** While it is angry, they flicker this many times a second, down to `dim` (phase 7 review). */
  rageFlicker: { hz: 14, dim: 0.35 },
  /** A part flashes this colour for `seconds` after a hit (about one frame and a bit). */
  flash: { color: [1, 1, 1] as Rgb, seconds: 0.05 },
  /**
   * Under `below` of its health a part smokes: `puffs` grey discs `size` × its radius, rising by
   * `rise` and drifting back by `drift` over `seconds`, then starting again.
   */
  smoke: {
    below: 0.5,
    puffs: 3,
    size: 0.45,
    rise: 6,
    drift: 16,
    seconds: 1.1,
    color: [0.16, 0.15, 0.15] as Rgb,
    alpha: 0.55,
  },
  /** A destroyed part's stump: charred metal, and sparks flickering on `sparkChance` of frames. */
  stump: { char: [0.05, 0.04, 0.035] as Rgb, spark: [1, 0.55, 0.15] as Rgb, sparkChance: 0.35 },
} as const;
