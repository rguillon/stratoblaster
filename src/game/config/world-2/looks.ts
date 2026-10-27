import type { SkyLook } from '../../../core/scenery/sky-look';
import { LEVEL_ZERO_LOOK, texture } from '../scenery-look';
import { DESERT_ROCK, DRY_EARTH, SAND } from '../world-1/looks';

/*
 * How the World 2 levels look (P08-R06, R07; reworked at the reviewer's request, 2026-10-27):
 * World 1's desert ground, sand and red rock on dry earth, slowly covered by the stained
 * concrete of the industry (the `paved` cover the sections raise level after level); and a
 * time of day per level, fixed within it: morning (2-1), midday (2-2), afternoon (2-3), dusk
 * through the smog (2-4) and night over the lit factories (2-5). Gamma-space RGB, 0..1.
 */

/** Industrial concrete: grey, stained with oil and soot, sand blown into its cracks. */
export const INDUSTRIAL_PAVING = texture(
  [
    [0.3, 0.29, 0.28],
    [0.4, 0.38, 0.36],
    [0.5, 0.48, 0.44],
  ],
  10,
  { speckle: 0.045, speckleColor: [0.62, 0.52, 0.36] },
);

/** The ground of the whole world: the desert, more and more paved along the levels. */
const TERRAIN = {
  ...LEVEL_ZERO_LOOK.terrain,
  ground: DRY_EARTH,
  low: SAND,
  sand: SAND,
  steep: DESERT_ROCK,
  paved: INDUSTRIAL_PAVING,
  // Only cliffs (mesas, canyon walls) are bare rock: the lee sides of the dunes stay sand.
  steepSlope: [0.95, 1.35],
  tints: [
    [1.04, 0.98, 0.92],
    [0.9, 0.86, 0.8],
  ],
} as const;

/** A World 2 look: the desert and industrial ground, under `sky` for the whole level. */
const industrial = (sky: SkyLook) =>
  ({
    ...LEVEL_ZERO_LOOK,
    terrain: TERRAIN,
    fog: { start: 1100, end: 2800 },
    glow: { intensity: 0.4, blurKernelSize: 16 },
    atmosphere: { start: sky },
  }) as const;

/** 2-1: a clear desert morning over the great erg. */
export const LEVEL_2_1_LOOK = industrial({ timeOfDay: 'morning', clouds: [0.15, 0.1] });

/** 2-2: a high, hard midday sun over the mesas and the mines. */
export const LEVEL_2_2_LOOK = industrial({ timeOfDay: 'midday', clouds: [0.2, 0.15] });

/** 2-3: golden afternoon over the oil fields, the clouds a little greyed by their smoke. */
export const LEVEL_2_3_LOOK = industrial({
  timeOfDay: 'afternoon',
  clouds: [0.25, 0.2],
  storm: 0.15,
});

/** 2-4: dusk through the smog of the industrial belt, its lights coming on. */
export const LEVEL_2_4_LOOK = industrial({ timeOfDay: 'dusk', clouds: [0.35, 0.25], storm: 0.3 });

/** 2-5: night over the factories, lit by their windows, neon, streets and cars. */
export const LEVEL_2_5_LOOK = industrial({ timeOfDay: 'night', clouds: [0.4, 0.3], storm: 0.35 });
