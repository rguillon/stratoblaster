/**
 * Look of the enemies (P05, GD-61: dark metallic hulls with neon lights), of their shots (GD-43:
 * colourful bullets) and of their explosions (GD-62). Linear RGB, 0..1; sizes in logical pixels;
 * durations in seconds.
 */

type Rgb = readonly [number, number, number];

/** Glow disc colours, centre to edge (black edge: soft fade with additive blending). */
const glow = (core: Rgb, mid: Rgb, rim: Rgb): readonly Rgb[] => [core, mid, rim, [0, 0, 0]];

export const ENEMY_LOOK = {
  /**
   * Hull shades, multiplied into a dark PBR metal. The metal is `tint` of the way from white to
   * the enemy's neon colour, and glows `selfLight` of it (phase 5 review: enemies easier to tell
   * from the ground and its shadows).
   */
  hull: {
    base: [0.1, 0.105, 0.12],
    panel: [0.16, 0.16, 0.19],
    dark: [0.045, 0.045, 0.055],
    metallic: 0.85,
    roughness: 0.38,
    tint: 0.6,
    selfLight: 0.04,
  },
  /** Neon colours of each enemy (P05-R01..R10, P05-R12). */
  neon: {
    gnat: [0.1, 0.95, 1],
    hornet: [1, 0.08, 0.1],
    scout: [0.05, 0.9, 1],
    strafer: [1, 0.1, 0.85],
    weaver: [0.2, 1, 0.3],
    spinner: [1, 0.5, 0.05],
    lancer: [1, 0.25, 0.35],
    rocketeer: [1, 0.12, 0.08],
    bulwark: [0.15, 0.4, 1],
    splitter: [0.65, 0.2, 1],
    carrier: [1, 0.7, 0.1],
  },
  /**
   * Reactors (phase 5 review): a dark nozzle with a glowing core, and the player ships' animated
   * flame, all in the same light blue `color` on every enemy. Sizes relative to the nozzle
   * radius; the inner flame is `whiten` of the way from `color` to white. Kept light (phase 5 review): an open
   * nozzle, a flat core, 4-sided flame cones without caps and 2 tetrahedron puffs, about 40
   * triangles a reactor (about 150 before).
   */
  reactor: {
    color: [0.55, 0.85, 1] as Rgb,
    flameSides: 4,
    puffs: 2,
    depth: 1.2,
    core: 0.75,
    flameLength: 5,
    flameWidth: 1.5,
    puffSize: 1.1,
    sides: 6,
    exhaustAlpha: 0.45,
    flameAlpha: 0.75,
    plasmaAlpha: 0.6,
    whiten: 0.55,
  },
  /** Rotors (the Gnat's ducted fans): blades, hub radius relative to the blades, spin. */
  rotor: {
    blades: 2,
    hub: 0.22,
    spinRadPerSec: 30,
  },
  /** A charging light (`Enemy.charge`) goes from `idle` to full brightness. */
  chargeIdle: 0.18,
  /** Glow layer over the playfield (enemies' neon, shots). */
  glow: { intensity: 0.6, blurKernelSize: 24 },
  bullets: {
    /** Visual radius relative to the hit radius. */
    scale: 1.6,
    segments: 10,
    styles: {
      red: glow([1, 0.9, 0.85], [1, 0.15, 0.1], [0.4, 0, 0]),
      magenta: glow([1, 0.9, 1], [1, 0.1, 0.8], [0.35, 0, 0.3]),
      green: glow([0.9, 1, 0.85], [0.2, 1, 0.25], [0, 0.35, 0.05]),
      orange: glow([1, 0.95, 0.8], [1, 0.5, 0.05], [0.4, 0.12, 0]),
      blue: glow([0.85, 0.9, 1], [0.2, 0.45, 1], [0, 0.08, 0.4]),
      purple: glow([0.95, 0.85, 1], [0.65, 0.2, 1], [0.2, 0, 0.4]),
    },
  },
  missile: {
    /** Body length and radius. */
    length: 11,
    radius: 1.8,
    tip: [1, 0.12, 0.08],
    flame: glow([1, 0.95, 0.7], [1, 0.45, 0.1], [0.35, 0.05, 0]),
    flameSize: [2.6, 6],
  },
  laser: {
    /** The thin warning line, blinking at `blinkHz`, then the beam. */
    warning: {
      width: 2,
      colors: [
        [1, 0.35, 0.4],
        [0.5, 0.05, 0.1],
        [0, 0, 0],
      ],
      blinkHz: 8,
    },
    beam: {
      colors: [
        [1, 0.95, 0.95],
        [1, 0.3, 0.4],
        [0.5, 0.02, 0.1],
        [0, 0, 0],
      ],
      /** Visual width relative to the beam width. */
      glowWidth: 2,
      flicker: 0.12,
      flickerHz: 21,
    },
    emitter: glow([1, 0.95, 0.95], [1, 0.3, 0.4], [0.3, 0, 0.05]),
    emitterRadius: 9,
  },
  blasts: {
    seed: 11,
    /** Fireball: grows to `radiusFactor` times the enemy radius over `duration`. */
    fireball: {
      colors: glow([1, 0.95, 0.75], [1, 0.5, 0.1], [0.45, 0.08, 0]),
      segments: 16,
      radiusFactor: 2.2,
      duration: 0.45,
    },
    /** Hot debris flying out, slowing down, fading. */
    debris: {
      colors: glow([1, 0.9, 0.6], [1, 0.45, 0.1], [0.3, 0.05, 0]),
      segments: 6,
      perRadius: 0.8,
      min: 6,
      max: 26,
      speed: [60, 220],
      size: [1.5, 3.5],
      life: [0.35, 0.8],
      drag: 3,
    },
    /** Missiles blow up smaller. */
    missileScale: 0.6,
  },
} as const;
