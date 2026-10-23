import { createNoise2D, hash2D, type Noise2D } from '../math/noise';
import type { HeightField } from './height-field';
import type { RoadNetwork, RoadSlot } from './road-network';
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

/** Hash streams of a slot or a cell; each draw uses its own stream so they stay independent. */
const Draw = { Building: 0, Kind: 1, Scale: 2, Trees: 3 } as const;

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

function inside(area: GroundArea, x: number, z: number): boolean {
  return x >= area.xMin && x < area.xMax && z >= area.zMin && z < area.zMax;
}

/**
 * Places props on a level (P04-R04, P04-R07). Buildings stand only along the roads: each slot of
 * the road network gets a building with the section's building density, set back from the road
 * edge and facing it, if the ground under its footprint is flat enough, above `minHeight`, and
 * clear of the other roads. Buildings along paths also keep clear of the building rows of the
 * roads they meet. A low-frequency zone noise picks the building group of each area, so
 * industrial buildings, labs and homes gather in clusters. Dead trees grow on a grid of cells,
 * away from the roads, on rougher ground too.
 *
 * Every slot and cell is decided from a hash, so the same place always gives the same props
 * whatever area is asked for: areas that touch can be placed separately (terrain chunks). A
 * slot belongs to the area that contains its point on the road; a cell to the area that
 * contains its corner.
 */
export class PropPlacer {
  readonly #zones: Noise2D;
  /** Depth of a row of buildings along a road, from the road edge. */
  readonly #rowDepth: number;

  constructor(
    private readonly field: HeightField,
    private readonly rules: PropRules,
    private readonly seed: number,
    readonly roads: RoadNetwork,
  ) {
    this.#zones = createNoise2D(seed + 3);
    const footprints = rules.groups.flatMap((g) => g.kinds.map((k) => k.footprint));
    this.#rowDepth = roads.setback + 2 * Math.max(0, ...footprints);
  }

  /** Buildings of the road slots and trees of the cells that lie in `area`. */
  place(area: GroundArea): PropPlacement[] {
    const placements: PropPlacement[] = [];
    for (const slot of this.roads.slots) {
      if (!inside(area, slot.x, slot.z)) continue;
      const building = this.#building(slot);
      if (building) placements.push(building);
    }
    const { cellSize } = this.rules;
    const [i0, i1] = [Math.ceil(area.xMin / cellSize), Math.ceil(area.xMax / cellSize)];
    const [j0, j1] = [Math.ceil(area.zMin / cellSize), Math.ceil(area.zMax / cellSize)];
    for (let j = j0; j < j1; j++) {
      for (let i = i0; i < i1; i++) placements.push(...this.#trees(i, j));
    }
    return placements;
  }

  #random(i: number, j: number, draw: number): number {
    return hash2D(i, j, this.seed * 31 + draw);
  }

  #building(slot: RoadSlot): PropPlacement | undefined {
    const r = (draw: number): number => this.#random(slot.road.index, slot.index, draw);
    if (r(Draw.Building) >= this.field.sectionAt(slot.z).section.buildingDensity) return undefined;
    const f = this.rules.zoneFrequency;
    const zone = (this.#zones(slot.x * f, slot.z * f) + 1) / 2;
    const group = weighted(this.rules.groups, Math.min(0.999999, Math.max(0, zone)));
    const kind = group && weighted(group.kinds, r(Draw.Kind));
    if (!kind) return undefined;
    const offset = slot.road.width / 2 + this.roads.setback + kind.footprint;
    const x = slot.x + slot.nx * offset;
    const z = slot.z + slot.nz * offset;
    // Paths give way to the building rows of the roads they meet.
    const clearance =
      kind.footprint + this.roads.setback + (slot.road.kind === 'cross' ? this.#rowDepth : 0);
    if (this.roads.edgeDistance(x, z, slot.road) < clearance) return undefined;
    const y = this.#standingHeight(x, z, kind.footprint, this.rules.maxSlope);
    if (y === undefined) return undefined;
    // The model's front (-Z) faces the road.
    const rotation = Math.atan2(slot.nx, slot.nz);
    return { kind: kind.id, x, y, z, rotation, scale: this.#scale(kind, r(Draw.Scale)) };
  }

  #trees(i: number, j: number): PropPlacement[] {
    const { cellSize, trees, treesPerCell, treeClearance } = this.rules;
    const density = this.field.sectionAt((j + 0.5) * cellSize).section.treeDensity;
    const count = Math.floor(this.#random(i, j, Draw.Trees) * (treesPerCell + 1) * density);
    const placements: PropPlacement[] = [];
    for (let n = 0; n < count; n++) {
      const r = (k: number): number => this.#random(i, j, Draw.Trees + 1 + n * TREE_DRAWS + k);
      const x = (i + r(0)) * cellSize;
      const z = (j + r(1)) * cellSize;
      const kind = weighted(trees, r(2));
      if (!kind || this.roads.edgeDistance(x, z) < treeClearance + kind.footprint) continue;
      const y = this.#standingHeight(x, z, kind.footprint, this.rules.treeMaxSlope);
      if (y !== undefined) {
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
