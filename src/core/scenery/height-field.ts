import { createNoise2D, fbm, ridged, smoothstep, type Noise2D } from '../math/noise';
import {
  layoutSections,
  type Meander,
  type PlacedSection,
  type SceneryLevel,
  type Surface,
  type TerrainSection,
} from './scenery-level';

/** Octave falloff of every relief: each octave has twice the frequency and half the height. */
const OCTAVES = { lacunarity: 2, gain: 0.5 } as const;
/** Share of `maxHeight` below it where the squashing of peaks starts. */
const PEAK_KNEE = 0.25;
/** Cycles per world unit of the small relief left on flattened ground and canyon floors. */
const DETAIL_FREQUENCY = 1 / 60;
/** How much irregular wobble (as a share of the amplitude) is added to the sine of a meander. */
const MEANDER_WOBBLE = 0.35;

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/** `h`, squashed smoothly so it never exceeds `max`. */
export function softCap(h: number, max: number): number {
  const knee = Math.abs(max) * PEAK_KNEE || 1;
  const start = max - knee;
  return h <= start ? h : start + knee * Math.tanh((h - start) / knee);
}

/**
 * A height the ground of `level` never exceeds, whatever the seed: the top of each section's
 * relief (or its peak cap), of its flattened band and of its sea bed. Carving only lowers the
 * ground, and blending stays between the heights of the blended sections.
 */
export function terrainCeiling(level: SceneryLevel): number {
  return Math.max(
    ...level.sections.map(({ relief, flatten, shore }) => {
      const top = relief.base + Math.abs(relief.amplitude);
      return Math.max(
        relief.maxHeight === undefined ? top : Math.min(top, relief.maxHeight),
        flatten ? flatten.height + Math.abs(flatten.roughness) : -Infinity,
        shore ? shore.seabed : -Infinity,
      );
    }),
  );
}

/**
 * The sculpted ground of a level (P04-R01): every section is a fractal relief, optionally
 * flattened (plateau), carved (canyon) or dropped under the sea (coast), and neighbouring
 * sections blend smoothly over `level.transition`. Before Z = 0 and after the end, the ground
 * continues as the first and last sections. Pure and deterministic for a given seed.
 */
export class HeightField {
  readonly sections: readonly PlacedSection[];
  /** Length of the level along Z. */
  readonly length: number;
  /** The ground never rises above this height ({@link terrainCeiling}). */
  readonly ceiling: number;
  readonly #relief: Noise2D;
  readonly #detail: Noise2D;
  readonly #wobble: Noise2D;
  readonly #transition: number;

  constructor(level: SceneryLevel, seed = level.seed) {
    this.sections = layoutSections(level);
    this.length = this.sections.at(-1)?.end ?? 0;
    this.ceiling = terrainCeiling(level);
    this.#relief = createNoise2D(seed);
    this.#detail = createNoise2D(seed + 1);
    this.#wobble = createNoise2D(seed + 2);
    this.#transition = Math.max(0, level.transition);
  }

  /** Index of the section under `z` (the first or last one outside the level). */
  sectionIndexAt(z: number): number {
    const i = this.sections.findIndex((s) => z < s.end);
    return i < 0 ? this.sections.length - 1 : i;
  }

  /** The section under `z`. */
  sectionAt(z: number): PlacedSection {
    const placed = this.sections[this.sectionIndexAt(z)];
    if (!placed) throw new RangeError('A height field needs a section');
    return placed;
  }

  /** Ground height at (`x`, `z`). */
  height(x: number, z: number): number {
    return this.#blend(z, (i) => this.#sectionHeight(i, x, z));
  }

  /** Ground cover at `z`, blended between sections like the height. */
  surface(z: number): Surface {
    const of = (i: number, key: keyof Surface): number =>
      this.sections[i]?.section.surface?.[key] ?? 0;
    return {
      lush: this.#blend(z, (i) => of(i, 'lush')),
      paved: this.#blend(z, (i) => of(i, 'paved')),
    };
  }

  /** `value` of the section under `z`, blended with its neighbour near their boundary. */
  #blend(z: number, value: (index: number) => number): number {
    const i = this.sectionIndexAt(z);
    const here = value(i);
    const half = this.#transition / 2;
    const placed = this.sections[i];
    if (!placed || half === 0) return here;
    if (i < this.sections.length - 1 && z > placed.end - half) {
      return lerp(here, value(i + 1), smoothstep(placed.end - half, placed.end + half, z));
    }
    if (i > 0 && z < placed.start + half) {
      return lerp(value(i - 1), here, smoothstep(placed.start - half, placed.start + half, z));
    }
    return here;
  }

  /** Steepness at (`x`, `z`): height change per unit of horizontal distance. */
  slope(x: number, z: number, step = 1): number {
    const dx = (this.height(x + step, z) - this.height(x - step, z)) / (2 * step);
    const dz = (this.height(x, z + step) - this.height(x, z - step)) / (2 * step);
    return Math.hypot(dx, dz);
  }

  /** X of a meander line at `z`. */
  pathX(path: Meander, z: number): number {
    const phase = (2 * Math.PI * z) / path.wavelength;
    const wobble = this.#wobble(z / path.wavelength, path.x / path.wavelength);
    return path.x + path.amplitude * (Math.sin(phase) + MEANDER_WOBBLE * wobble);
  }

  #sectionHeight(index: number, x: number, z: number): number {
    const section = this.sections[index]?.section;
    if (!section) return 0;
    let h = this.#reliefHeight(section, x, z);
    h = this.#flatten(section, x, z, h);
    h = this.#carve(section, x, z, h);
    return this.#shore(section, x, z, h);
  }

  #reliefHeight({ relief }: TerrainSection, x: number, z: number): number {
    const f = relief.frequency;
    const options = { ...OCTAVES, octaves: relief.octaves };
    const h =
      relief.style === 'ridged'
        ? relief.base + relief.amplitude * ridged(this.#relief, x * f, z * f, options)
        : relief.base + relief.amplitude * fbm(this.#relief, x * f, z * f, options);
    return relief.maxHeight === undefined ? h : softCap(h, relief.maxHeight);
  }

  #detailNoise(x: number, z: number): number {
    return this.#detail(x * DETAIL_FREQUENCY, z * DETAIL_FREQUENCY);
  }

  #flatten({ flatten }: TerrainSection, x: number, z: number, h: number): number {
    if (!flatten) return h;
    const d = Math.abs(x - this.pathX(flatten.path, z));
    const flat = flatten.height + flatten.roughness * this.#detailNoise(x, z);
    return lerp(flat, h, smoothstep(flatten.halfWidth, flatten.halfWidth + flatten.edge, d));
  }

  #carve({ channel }: TerrainSection, x: number, z: number, h: number): number {
    if (!channel) return h;
    const d = Math.abs(x - this.pathX(channel.path, z));
    const floor = Math.min(h, channel.floor + this.#detailNoise(x, z));
    return lerp(floor, h, smoothstep(channel.halfWidth, channel.halfWidth + channel.wall, d));
  }

  #shore({ shore }: TerrainSection, x: number, z: number, h: number): number {
    if (!shore) return h;
    const inland = shore.landSide * (x - this.pathX(shore.path, z));
    return lerp(shore.seabed, h, smoothstep(-shore.width / 2, shore.width / 2, inland));
  }
}
