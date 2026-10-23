import type { PlacedSection, RoadRules, StreetGrid } from './scenery-level';

/** Streets along a district are spread over this share of the screen half-width. */
const ALONG_SPREAD = 0.8;
/** Wavelength of the wobble of the streets along a district. */
const ALONG_WAVELENGTH = 700;

/** A run of consecutive sections with street grids (phase 4 review). */
export interface District {
  readonly zMin: number;
  zMax: number;
  readonly parts: { readonly grid: StreetGrid; readonly zMin: number; readonly zMax: number }[];
}

/**
 * Runs of consecutive sections with a street grid. Districts at the ends of the level go on
 * past them (to `range`), out of view.
 */
export function findDistricts(
  sections: readonly PlacedSection[],
  range: { readonly zMin: number; readonly zMax: number },
): District[] {
  const districts: District[] = [];
  sections.forEach((placed, i) => {
    const grid = placed.section.streets;
    if (!grid) return;
    const zMin = i === 0 ? range.zMin : placed.start;
    const zMax = i === sections.length - 1 ? range.zMax : placed.end;
    const previous = districts.at(-1);
    if (previous && sections[i - 1]?.section.streets) {
      previous.parts.push({ grid, zMin, zMax });
      previous.zMax = zMax;
    } else {
      districts.push({ zMin, zMax, parts: [{ grid, zMin, zMax }] });
    }
  });
  return districts;
}

/** A straight street across the level at `z`, from past one screen edge to past the other. */
export function acrossStreet(
  z: number,
  { step, offscreenX, crossWidth }: RoadRules,
): { x: number; z: number; width: number }[] {
  const count = Math.ceil((2 * offscreenX) / step) + 2;
  return Array.from({ length: count + 1 }, (_, i) => ({
    x: -offscreenX - step + i * step,
    z,
    width: crossWidth,
  }));
}

/** Centre line of street `k` of `count` along a district, wobbling by up to `wobble`. */
export function alongStreet(
  k: number,
  count: number,
  wobble: number,
  district: District,
  phase: number,
  { step, offscreenX }: RoadRules,
): { x: number; z: number }[] {
  const spread = offscreenX * ALONG_SPREAD;
  const x0 = -spread + ((k + 0.5) * 2 * spread) / count;
  const points: { x: number; z: number }[] = [];
  for (let z = district.zMin; z <= district.zMax; z += step) {
    const sway = Math.sin((2 * Math.PI * z) / ALONG_WAVELENGTH + phase);
    points.push({ x: x0 + wobble * sway, z });
  }
  return points;
}
