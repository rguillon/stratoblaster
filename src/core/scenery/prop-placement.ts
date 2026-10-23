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

/** The `items` whose id is in `ids` (all of them when `ids` is undefined). */
function allowed<T extends { readonly id: string }>(
  items: readonly T[],
  ids?: readonly string[],
): T[] {
  return ids ? items.filter((item) => ids.includes(item.id)) : [...items];
}

function inside(area: GroundArea, x: number, z: number): boolean {
  return x >= area.xMin && x < area.xMax && z >= area.zMin && z < area.zMax;
}

/** A building with the radius of ground it takes. */
interface Building {
  readonly placement: PropPlacement;
  readonly footprint: number;
}

/** Bucket size of the index of placed buildings. */
const BUILDING_BUCKET = 32;

function bucketKey(x: number, z: number): string {
  return `${String(Math.floor(x / BUILDING_BUCKET))},${String(Math.floor(z / BUILDING_BUCKET))}`;
}

/**
 * Places props on a level (P04-R04, P04-R07). Buildings stand only along the roads: each slot of
 * the road network gets a building with the section's building density, set back from the road
 * edge and facing it, if the ground under its footprint is flat enough, above `minHeight`, clear
 * of the other roads and of the buildings already placed. Slots of main roads are served first,
 * so they get the street fronts. A low-frequency zone noise picks the building group of each area
 * among the groups the section allows, so industrial buildings, labs and homes gather in
 * clusters. Trees of the kinds the section allows grow on a grid of cells, away from the roads
 * and the buildings, on rougher ground too.
 *
 * Buildings are decided once for the whole level, in a fixed order, and trees from a hash of
 * their cell, so the same place always gives the same props whatever area is asked for: areas
 * that touch can be placed separately (terrain chunks). A building belongs to the area that
 * contains its centre; a cell to the area that contains its corner.
 */
export class PropPlacer {
  readonly #zones: Noise2D;
  readonly #buildings: Building[] = [];
  readonly #occupied = new Map<string, Building[]>();

  constructor(
    private readonly field: HeightField,
    private readonly rules: PropRules,
    private readonly seed: number,
    readonly roads: RoadNetwork,
  ) {
    this.#zones = createNoise2D(seed + 3);
    const mainFirst = [...roads.slots].sort(
      (a, b) => Number(a.road.kind === 'cross') - Number(b.road.kind === 'cross'),
    );
    for (const slot of mainFirst) {
      const building = this.#building(slot);
      if (building && this.#free(building.placement.x, building.placement.z, building.footprint)) {
        this.#occupy(building);
      }
    }
  }

  /** Buildings and trees that lie in `area`. */
  place(area: GroundArea): PropPlacement[] {
    const placements = this.#buildings
      .map((b) => b.placement)
      .filter((p) => inside(area, p.x, p.z));
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

  /** Whether a circle of radius `radius` at (`x`, `z`) keeps clear of the placed buildings. */
  #free(x: number, z: number, radius: number): boolean {
    const bx = Math.floor(x / BUILDING_BUCKET);
    const bz = Math.floor(z / BUILDING_BUCKET);
    for (let i = bx - 2; i <= bx + 2; i++) {
      for (let j = bz - 2; j <= bz + 2; j++) {
        for (const b of this.#occupied.get(`${String(i)},${String(j)}`) ?? []) {
          const gap = Math.hypot(b.placement.x - x, b.placement.z - z) - b.footprint - radius;
          if (gap < this.roads.setback) return false;
        }
      }
    }
    return true;
  }

  #occupy(building: Building): void {
    this.#buildings.push(building);
    const key = bucketKey(building.placement.x, building.placement.z);
    const bucket = this.#occupied.get(key);
    if (bucket) bucket.push(building);
    else this.#occupied.set(key, [building]);
  }

  #building(slot: RoadSlot): Building | undefined {
    const r = (draw: number): number => this.#random(slot.road.index, slot.index, draw);
    const { section } = this.field.sectionAt(slot.z);
    if (r(Draw.Building) >= section.buildingDensity) return undefined;
    const f = this.rules.zoneFrequency;
    const zone = (this.#zones(slot.x * f, slot.z * f) + 1) / 2;
    const groups = allowed(this.rules.groups, section.groups);
    const group = weighted(groups, Math.min(0.999999, Math.max(0, zone)));
    const kind = group && weighted(group.kinds, r(Draw.Kind));
    if (!kind) return undefined;
    const offset = slot.road.width / 2 + this.roads.setback + kind.footprint;
    const x = slot.x + slot.nx * offset;
    const z = slot.z + slot.nz * offset;
    const clearance = kind.footprint + this.roads.setback;
    if (this.roads.edgeDistance(x, z, slot.road) < clearance) return undefined;
    const y = this.#standingHeight(x, z, kind.footprint, this.rules.maxSlope);
    if (y === undefined) return undefined;
    // The model's front (-Z) faces the road.
    const rotation = Math.atan2(slot.nx, slot.nz);
    const placement = { kind: kind.id, x, y, z, rotation, scale: this.#scale(kind, r(Draw.Scale)) };
    return { placement, footprint: kind.footprint };
  }

  #trees(i: number, j: number): PropPlacement[] {
    const { cellSize, treesPerCell, treeClearance } = this.rules;
    const { section } = this.field.sectionAt((j + 0.5) * cellSize);
    const trees = allowed(this.rules.trees, section.trees);
    const count = Math.floor(
      this.#random(i, j, Draw.Trees) * (treesPerCell + 1) * section.treeDensity,
    );
    const placements: PropPlacement[] = [];
    for (let n = 0; n < count; n++) {
      const r = (k: number): number => this.#random(i, j, Draw.Trees + 1 + n * TREE_DRAWS + k);
      const x = (i + r(0)) * cellSize;
      const z = (j + r(1)) * cellSize;
      const kind = weighted(trees, r(2));
      if (!kind || this.roads.edgeDistance(x, z) < treeClearance + kind.footprint) continue;
      if (!this.#free(x, z, kind.footprint)) continue;
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
