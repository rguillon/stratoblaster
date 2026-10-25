import { hash2D } from '../math/noise';
import { between, weighted } from './draws';
import type { HeightField } from './height-field';
import type { GroundArea, PropPlacement } from './prop-placement';
import type { FloatRules, PropLine } from './scenery-level';

// Props that do not follow the roads (phase 8): floating ice on the sea, and lines of props
// along the level (a pipeline). Pure and deterministic for a given seed.

/** Draws per floating prop: position X, position Z, kind, scale, turn. */
const FLOAT_DRAWS = 5;
/** Hash stream of the number of floating props in a cell. */
const FLOAT_COUNT = 101;

/**
 * The floating props of cell (`i`, `j`) (P08-R07: ice floes, icebergs): up to `perCell`, with the
 * chance of their section's `floatDensity`, each where the sea is at least `depth` deep under its
 * whole footprint. They float at `seaLevel`.
 */
export function floatingProps(
  rules: FloatRules,
  field: HeightField,
  [seaLevel, seed]: readonly [number, number],
  [i, j]: readonly [number, number],
): PropPlacement[] {
  const { cellSize } = rules;
  const density = field.sectionAt((j + 0.5) * cellSize).section.floatDensity ?? 0;
  if (density <= 0) return [];
  const r = (draw: number): number => hash2D(i, j, seed * 53 + draw);
  const count = Math.floor(r(FLOAT_COUNT) * (rules.perCell + 1) * density);
  const props: PropPlacement[] = [];
  for (let n = 0; n < count; n++) {
    const d = (k: number): number => r(FLOAT_COUNT + 1 + n * FLOAT_DRAWS + k);
    const kind = weighted(rules.kinds, d(2));
    if (!kind) continue;
    const x = (i + d(0)) * cellSize;
    const z = (j + d(1)) * cellSize;
    const reach = kind.footprint;
    const deep = [
      [0, 0],
      [reach, 0],
      [-reach, 0],
      [0, reach],
      [0, -reach],
    ].every(([dx = 0, dz = 0]) => field.height(x + dx, z + dz) <= seaLevel - rules.depth);
    if (!deep) continue;
    const scale = between(kind.scale, d(3));
    props.push({ kind: kind.id, x, y: seaLevel, z, rotation: d(4) * 2 * Math.PI, scale });
  }
  return props;
}

/** The floating props of the cells whose corner lies in `area` (see {@link floatingProps}). */
export function floatingIn(
  rules: FloatRules,
  field: HeightField,
  sea: readonly [level: number, seed: number],
  area: GroundArea,
): PropPlacement[] {
  const size = rules.cellSize;
  const [i0, i1] = [Math.ceil(area.xMin / size), Math.ceil(area.xMax / size)];
  const [j0, j1] = [Math.ceil(area.zMin / size), Math.ceil(area.zMax / size)];
  const placements: PropPlacement[] = [];
  for (let j = j0; j < j1; j++) {
    for (let i = i0; i < i1; i++) placements.push(...floatingProps(rules, field, sea, [i, j]));
  }
  return placements;
}

/** A piece of a line of props, with the radius of ground it takes. */
export interface LinePiece {
  readonly placement: PropPlacement;
  readonly footprint: number;
}

/**
 * The pieces of `line` over the whole level (P08-R03: a pipeline on stilts): one every
 * `spacing` along its path, turned along it, where the ground is above `seaLevel` and gentle
 * enough, in the sections it runs through.
 */
export function linePieces(
  line: PropLine,
  field: HeightField,
  seaLevel: number | undefined,
): LinePiece[] {
  const pieces: LinePiece[] = [];
  const step = line.spacing;
  for (let z = step / 2; z < field.length; z += step) {
    const name = field.sectionAt(z).section.name;
    if (line.sections && !line.sections.includes(name)) continue;
    const x = field.pathX(line.path, z);
    const y = field.height(x, z);
    if (seaLevel !== undefined && y <= seaLevel) continue;
    if (field.slope(x, z, line.footprint) > line.maxSlope) continue;
    const dx = field.pathX(line.path, z + 1) - field.pathX(line.path, z - 1);
    // The model's length runs along X: turned so that X follows the path (Z along the level).
    const rotation = Math.atan2(-2, dx);
    pieces.push({
      placement: { kind: line.kind, x, y, z, rotation, scale: 1 },
      footprint: line.footprint,
    });
  }
  return pieces;
}
