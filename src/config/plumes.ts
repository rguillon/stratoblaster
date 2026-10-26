type Rgb = readonly [number, number, number];

/**
 * A kind of plume (phase 10, P10-R08): a column of soft, see-through puffs rising from a prop,
 * growing and fading as they rise, drifting with the wind. Only a look; kept faint so it never
 * hides what flies above it.
 */
export interface PlumeKind {
  /** Puffs in one column (each its own quad), and the seconds one takes to rise to the top. */
  readonly puffs: number;
  readonly seconds: number;
  /** Height the column rises to and how far the wind bends it sideways at the top (world units). */
  readonly height: number;
  readonly lean: number;
  /** Puff size (world units across) at the bottom and at the top. */
  readonly size: readonly [bottom: number, top: number];
  /** Colour, lit by the scene's light, and the most opaque a puff is (it fades in and out). */
  readonly color: Rgb;
  readonly alpha: number;
  /** Share (0..1) of its colour it keeps at night, as if lit from below by fire. */
  readonly selfLit: number;
}

/** The plume kinds of the engine (phase 10). */
export const PLUME_KINDS: Readonly<Record<string, PlumeKind>> = {
  // Slow grey-brown smoke columns from vents, cinder cones and chimneys.
  smoke: {
    puffs: 7,
    seconds: 9,
    height: 70,
    lean: 18,
    size: [5, 22],
    color: [0.34, 0.32, 0.3],
    alpha: 0.32,
    selfLit: 0.1,
  },
  // White steam rising where the hot coast meets the sea, and from cooling towers and wells.
  steam: {
    puffs: 6,
    seconds: 6,
    height: 45,
    lean: 10,
    size: [4, 18],
    color: [0.86, 0.87, 0.88],
    alpha: 0.26,
    selfLit: 0.05,
  },
};
