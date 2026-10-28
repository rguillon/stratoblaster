// The districts of a level: the runs of sections with street grids (phase 4 review), split out
// of `street-grid.ts`, and the parts of them laid apart (reviewer, 2026-10-28).
import type { PlacedSection, StreetGrid } from './scenery-level';

/** A run of consecutive sections with street grids (phase 4 review). */
export interface District {
  readonly zMin: number;
  zMax: number;
  readonly parts: { readonly grid: StreetGrid; readonly zMin: number; readonly zMax: number }[];
  /**
   * It goes on from the district before it (the runout's, see {@link splitDistricts}): its first
   * row is that district's last one, laid with it, and its columns start there.
   */
  readonly continues?: boolean;
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

/** The part of `d` between `from` and `to`, if any (its own ends where they are closer). */
function cut(d: District, from: number, to: number): District | undefined {
  if (d.zMax <= from || d.zMin >= to) return undefined;
  if (d.zMin >= from && d.zMax <= to) return d;
  const parts = d.parts
    .filter((p) => p.zMax > from && p.zMin < to)
    .map((p) => ({ ...p, zMin: Math.max(p.zMin, from), zMax: Math.min(p.zMax, to) }));
  return { zMin: Math.max(d.zMin, from), zMax: Math.min(d.zMax, to), parts };
}

/**
 * `districts` from `z` on (reviewer, 2026-10-28): one that reaches lower starts at `z`, with a
 * full row there.
 */
export function districtsFrom(districts: readonly District[], z: number): District[] {
  return districts.flatMap((d) => cut(d, z, Infinity) ?? []);
}

/**
 * `districts` cut where the runout starts, at `z` (reviewer, 2026-10-28): the districts before
 * it, ending with a full row at `z`, and those after it, which go on from that row (`continues`).
 */
export function splitDistricts(
  districts: readonly District[],
  z: number,
): { before: District[]; after: District[] } {
  const before = districts.flatMap((d) => cut(d, -Infinity, z) ?? []);
  const after = districts.flatMap((d) => {
    const rest = cut(d, z, Infinity);
    return rest ? [rest.zMin > d.zMin ? { ...rest, continues: true } : rest] : [];
  });
  return { before, after };
}

/**
 * The parts of `districts` laid as the level is generated: from `streetsFrom` on, before the
 * runout (`before`) and in it (`after`, laid later), when the level has one at `runoutFrom`.
 */
export function laidDistricts(
  districts: readonly District[],
  {
    streetsFrom,
    runoutFrom,
  }: { readonly streetsFrom?: number | undefined; readonly runoutFrom?: number | undefined },
): { before: District[]; after: District[] } {
  const laid = streetsFrom === undefined ? [...districts] : districtsFrom(districts, streetsFrom);
  return runoutFrom === undefined ? { before: laid, after: [] } : splitDistricts(laid, runoutFrom);
}
