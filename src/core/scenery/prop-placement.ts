import { createNoise2D, hash2D, type Noise2D } from '../math/noise';
import type { HeightField } from './height-field';
import type { PropKindRule, PropRules } from './scenery-level';

/** One prop standing on the ground. */
export interface PropPlacement {
  /** Key of the prop's model (`PropKindRule.id`). */
  readonly kind: string;
  readonly x: number;
  /** Height of the ground the prop stands on. */
  readonly y: number;
  readonly z: number;
  /** Turn around the vertical axis, in radians. */
  readonly rotation: number;
  readonly scale: number;
}

/** A rectangle of ground, in world units. */
export interface GroundArea {
  readonly xMin: number;
  readonly xMax: number;
  readonly zMin: number;
  readonly zMax: number;
}

/** Hash streams of one cell; each draw of a cell uses its own stream so they stay independent. */
const Draw = {
  Building: 0,
  BuildingX: 1,
  BuildingZ: 2,
  Kind: 3,
  Turn: 4,
  Scale: 5,
  Trees: 6,
} as const;

/** Draws per tree: position X, position Z, kind, scale, turn. */
const TREE_DRAWS = 5;

function weighted<T extends { readonly weight: number }>(
  items: readonly T[],
  r: number,
): T | undefined {
  const total = items.reduce((sum, item) => sum + item.weight, 0);
  let left = r * total;
  for (const item of items) {
    left -= item.weight;
    if (left < 0) return item;
  }
  return items.at(-1);
}

/**
 * Places props on the flat ground of a level (P04-R04). Candidate spots sit on a jittered grid;
 * a spot gets a building with the section's building density, if the ground under its footprint
 * is flat enough and above `minHeight`. A low-frequency zone noise picks the building group of
 * each area, so industrial buildings, labs and homes gather in clusters. Cells without a
 * building may get a few dead trees on rougher ground.
 *
 * Every cell is decided from a hash of its coordinates, so the same cell always gives the same
 * props whatever area is asked for: areas that touch can be placed separately (terrain chunks).
 * A cell belongs to the area that contains its grid corner.
 */
export class PropPlacer {
  readonly #zones: Noise2D;

  constructor(
    private readonly field: HeightField,
    private readonly rules: PropRules,
    private readonly seed: number,
  ) {
    this.#zones = createNoise2D(seed + 3);
  }

  /** Props of every cell whose corner lies in `area`. */
  place(area: GroundArea): PropPlacement[] {
    const { cellSize } = this.rules;
    const placements: PropPlacement[] = [];
    const [i0, i1] = [Math.ceil(area.xMin / cellSize), Math.ceil(area.xMax / cellSize)];
    const [j0, j1] = [Math.ceil(area.zMin / cellSize), Math.ceil(area.zMax / cellSize)];
    for (let j = j0; j < j1; j++) {
      for (let i = i0; i < i1; i++) {
        const building = this.#building(i, j);
        if (building) placements.push(building);
        else placements.push(...this.#trees(i, j));
      }
    }
    return placements;
  }

  #random(i: number, j: number, draw: number): number {
    return hash2D(i, j, this.seed * 31 + draw);
  }

  #building(i: number, j: number): PropPlacement | undefined {
    const { cellSize, jitter } = this.rules;
    const x = (i + 0.5 + (this.#random(i, j, Draw.BuildingX) - 0.5) * jitter) * cellSize;
    const z = (j + 0.5 + (this.#random(i, j, Draw.BuildingZ) - 0.5) * jitter) * cellSize;
    const density = this.field.sectionAt(z).section.buildingDensity;
    if (this.#random(i, j, Draw.Building) >= density) return undefined;
    const zone = (this.#zones(x * this.rules.zoneFrequency, z * this.rules.zoneFrequency) + 1) / 2;
    const group = weighted(this.rules.groups, Math.min(0.999999, Math.max(0, zone)));
    const kind = group && weighted(group.kinds, this.#random(i, j, Draw.Kind));
    if (!kind) return undefined;
    const y = this.#standingHeight(x, z, kind.footprint, this.rules.maxSlope);
    if (y === undefined) return undefined;
    // Buildings of an area share a street grid: a quarter turn, plus the zone's own angle.
    const quarter = Math.floor(this.#random(i, j, Draw.Turn) * 4);
    return {
      kind: kind.id,
      x,
      y,
      z,
      rotation: (quarter * Math.PI) / 2 + zone * Math.PI,
      scale: this.#scale(kind, this.#random(i, j, Draw.Scale)),
    };
  }

  #trees(i: number, j: number): PropPlacement[] {
    const { cellSize, trees, treesPerCell } = this.rules;
    const density = this.field.sectionAt((j + 0.5) * cellSize).section.treeDensity;
    const count = Math.floor(this.#random(i, j, Draw.Trees) * (treesPerCell + 1) * density);
    const placements: PropPlacement[] = [];
    for (let n = 0; n < count; n++) {
      const r = (k: number): number => this.#random(i, j, Draw.Trees + 1 + n * TREE_DRAWS + k);
      const x = (i + r(0)) * cellSize;
      const z = (j + r(1)) * cellSize;
      const kind = weighted(trees, r(2));
      const y = kind && this.#standingHeight(x, z, kind.footprint, this.rules.treeMaxSlope);
      if (kind && y !== undefined) {
        placements.push({
          kind: kind.id,
          x,
          y,
          z,
          rotation: r(4) * 2 * Math.PI,
          scale: this.#scale(kind, r(3)),
        });
      }
    }
    return placements;
  }

  #scale(kind: PropKindRule, r: number): number {
    const [min, max] = kind.scale;
    return min + (max - min) * r;
  }

  /**
   * Lowest ground height under a footprint of radius `radius` around (`x`, `z`), or undefined
   * when the ground there is too steep or too low.
   */
  #standingHeight(x: number, z: number, radius: number, maxSlope: number): number | undefined {
    const heights = [
      this.field.height(x, z),
      this.field.height(x + radius, z),
      this.field.height(x - radius, z),
      this.field.height(x, z + radius),
      this.field.height(x, z - radius),
    ];
    const low = Math.min(...heights);
    const high = Math.max(...heights);
    if (low < this.rules.minHeight) return undefined;
    return high - low <= maxSlope * radius ? low : undefined;
  }
}
