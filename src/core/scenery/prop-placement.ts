import { createNoise2D, hash2D, type Noise2D } from '../math/noise';
import { placeHamlets, placeLoners, type AwaySite, type Building } from './away-placement';
import { allowed, between, weighted } from './draws';
import type { HeightField } from './height-field';
import type { RoadNetwork, RoadSlot } from './road-network';
import { blockParts, type Block } from './street-grid';
import type {
  BlockFill,
  PropGroupRule,
  PropKindRule,
  PropRules,
  TerrainSection,
} from './scenery-level';

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
  /** Per-axis scale (X, Y, Z) instead of `scale`, for podiums stretched to their block. */
  readonly size?: readonly [number, number, number];
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

function inside(area: GroundArea, x: number, z: number): boolean {
  return x >= area.xMin && x < area.xMax && z >= area.zMin && z < area.zMax;
}

/** Blocks are cut into parts of about this size, one tower each at most… */
const PART_SIZE = 30;
/** …and at most this many parts across either way. */
const MAX_PARTS = 4;
/** Gap between a tower and the edge of its part of the podium roof. */
const TOWER_MARGIN = 1;
/** Towers are drawn among the kinds at least this share of the largest one that fits. */
const LARGEST_SHARE = 0.75;

/** Smaller kinds a building slot tries when its first choice does not fit. */
const FALLBACKS = 3;

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
 * clusters. With `loners` and `hamlets` (phase 6 review), a few lone buildings and bunches of
 * buildings also stand away from the roads. Trees of the kinds the section allows grow on a grid
 * of cells, away from the roads and the buildings, on rougher ground too.
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
    roads.blocks.forEach((block, i) => {
      this.#fillBlock(block, i);
    });
    for (const slot of mainFirst) {
      if (this.field.sectionAt(slot.z).section.blocks) continue;
      const building = this.#candidates(slot)
        .map((kind) => this.#fit(slot, kind))
        .find((b) => b !== undefined && this.#free(b));
      if (building) this.#occupy(building);
    }
    if (rules.hamlets) placeHamlets(this.#awaySite(), rules.hamlets);
    if (rules.loners) placeLoners(this.#awaySite(), rules.loners);
  }

  /** What `placeHamlets` and `placeLoners` need (phase 6 review). */
  #awaySite(): AwaySite {
    return {
      length: this.field.length,
      offscreenX: this.roads.offscreenX,
      seed: this.seed,
      sectionAt: (z) => this.field.sectionAt(z).section,
      groupAt: (x, z, section) => this.#groupAt(x, z, section),
      roadDistance: (x, z) => this.roads.edgeDistance(x, z),
      ground: (x, z, radius) => this.#standingHeight(x, z, radius, this.rules.maxSlope),
      add: (building, gap) => {
        if (!this.#free(building, gap)) return false;
        this.#occupy(building);
        return true;
      },
    };
  }

  /** The building group of the area around (`x`, `z`), among those `section` allows. */
  #groupAt(x: number, z: number, section: TerrainSection): PropGroupRule | undefined {
    const f = this.rules.zoneFrequency;
    const zone = (this.#zones(x * f, z * f) + 1) / 2;
    const groups = allowed(this.rules.groups, section.groups);
    return weighted(groups, Math.min(0.999999, Math.max(0, zone)));
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

  /** Whether the ground box of `area` keeps `gap` clear of the placed buildings. */
  #free(
    area: { placement: { x: number; z: number }; halfX: number; halfZ: number },
    gap = this.roads.setback,
  ): boolean {
    const { x, z } = area.placement;
    const bx = Math.floor(x / BUILDING_BUCKET);
    const bz = Math.floor(z / BUILDING_BUCKET);
    for (let i = bx - 2; i <= bx + 2; i++) {
      for (let j = bz - 2; j <= bz + 2; j++) {
        for (const b of this.#occupied.get(`${String(i)},${String(j)}`) ?? []) {
          const apartX = Math.abs(b.placement.x - x) >= b.halfX + area.halfX + gap;
          const apartZ = Math.abs(b.placement.z - z) >= b.halfZ + area.halfZ + gap;
          if (!apartX && !apartZ) return false;
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

  /**
   * Fills a block of a section with `blocks` (phase 4 review): a podium over the whole block, if
   * the section has podiums, and buildings on its roof (or on the ground), one per part of the
   * block (parts of about 30, up to 4 × 4), a large kind of the section's groups that fits each part.
   */
  #fillBlock(block: Block, index: number): void {
    const { section } = this.field.sectionAt((block.zMin + block.zMax) / 2);
    const fill = section.blocks;
    if (!fill) return;
    const r = (draw: number): number => hash2D(index, draw, this.seed * 37 + 11);
    const [w, d] = [block.xMax - block.xMin, block.zMax - block.zMin];
    const roof = this.#podium(block, fill, r);
    const groups = allowed(this.rules.groups, section.groups);
    const across = (size: number): number =>
      Math.min(MAX_PARTS, Math.max(1, Math.round(size / PART_SIZE)));
    const parts = blockParts(block, across(w), across(d));
    const towers = Math.round(between(fill.towers, r(2)));
    parts
      .map((part, k) => ({ part, order: r(10 + k) }))
      .sort((a, b) => a.order - b.order)
      .slice(0, towers)
      .forEach(({ part }, k) => {
        const tower = this.#tower(part, groups, roof ?? 0, r(20 + k));
        if (!tower) return;
        // Without a podium, on the lowest ground under its own plan, so it never floats.
        const { placement, halfX } = tower;
        const y = roof ?? this.#lowest(placement.x, placement.z, halfX);
        this.#occupy({ ...tower, placement: { ...placement, y } });
      });
  }

  /** Places the podium of a block, if its section has podiums; the height of its roof. */
  #podium(block: Block, fill: BlockFill, r: (draw: number) => number): number | undefined {
    const [w, d] = [block.xMax - block.xMin, block.zMax - block.zMin];
    const [cx, cz] = [(block.xMin + block.xMax) / 2, (block.zMin + block.zMax) / 2];
    const corners = [
      [block.xMin, block.zMin],
      [block.xMax, block.zMin],
      [block.xMin, block.zMax],
      [block.xMax, block.zMax],
    ] as const;
    const heights = corners.map(([x, z]) => this.field.height(x, z));
    const ground = Math.min(...heights);
    const height = between(fill.podiumHeight, r(0)) + Math.max(...heights) - ground;
    const podium = fill.podiums[Math.floor(r(1) * fill.podiums.length)];
    if (!podium) return undefined;
    this.#occupy({
      placement: {
        kind: podium,
        x: cx,
        y: ground,
        z: cz,
        rotation: 0,
        scale: 1,
        size: [w, height, d],
      },
      halfX: w / 2,
      halfZ: d / 2,
    });
    return ground + height;
  }

  /** The largest kind of `groups` that fits `part`, standing at `y`, with the ground it takes. */
  #tower(
    part: Block,
    groups: readonly PropGroupRule[],
    y: number,
    r: number,
  ): Building | undefined {
    const half = Math.min(part.xMax - part.xMin, part.zMax - part.zMin) / 2 - TOWER_MARGIN;
    const fitting = groups
      .flatMap((g) => g.kinds)
      .map((kind) => ({
        kind,
        scale: Math.min(kind.scale[1], half / (kind.frontage ?? kind.footprint / kind.scale[1])),
      }))
      .filter(({ kind, scale }) => scale >= kind.scale[0]);
    const largest = Math.max(
      ...fitting.map(({ kind, scale }) => (kind.frontage ?? kind.footprint) * scale),
    );
    const choices = fitting.filter(
      ({ kind, scale }) => (kind.frontage ?? kind.footprint) * scale >= largest * LARGEST_SHARE,
    );
    const choice = choices[Math.floor(r * choices.length)];
    if (!choice) return undefined;
    // Shifted within the room its part leaves around it, so towers do not line up (review).
    const size = (choice.kind.frontage ?? choice.kind.footprint) * choice.scale;
    const shift = (min: number, max: number, t: number): number =>
      (min + max) / 2 + (t - 0.5) * Math.max(0, max - min - 2 * (size + TOWER_MARGIN));
    const placement = {
      kind: choice.kind.id,
      x: shift(part.xMin, part.xMax, (r * 31) % 1),
      y,
      z: shift(part.zMin, part.zMax, (r * 57) % 1),
      rotation: (Math.floor(r * 4 * 7919) % 4) * (Math.PI / 2),
      scale: choice.scale,
    };
    return { placement, halfX: size, halfZ: size };
  }

  /**
   * The kinds a slot tries in turn: none when the density draw says no building; else the kind
   * drawn in the area's group, then the smaller kinds of that group from the largest down
   * (at most {@link FALLBACKS}), so gaps too small for the first choice still get a building.
   */
  #candidates(slot: RoadSlot): PropKindRule[] {
    const r = (draw: number): number => this.#random(slot.road.index, slot.index, draw);
    const { section } = this.field.sectionAt(slot.z);
    if (r(Draw.Building) >= section.buildingDensity) return [];
    const group = this.#groupAt(slot.x, slot.z, section);
    const kind = group && weighted(group.kinds, r(Draw.Kind));
    if (!group || !kind) return [];
    const smaller = group.kinds
      .filter((k) => k.footprint < kind.footprint)
      .sort((a, b) => b.footprint - a.footprint)
      .slice(0, FALLBACKS);
    return [kind, ...smaller];
  }

  /** `kind` standing by `slot`, or undefined when the roads or the ground do not allow it. */
  #fit(slot: RoadSlot, kind: PropKindRule): Building | undefined {
    const scale = between(kind.scale, this.#random(slot.road.index, slot.index, Draw.Scale));
    // A square plan stands at the setback; anything else keeps its footprint circle clear.
    const reach = kind.frontage === undefined ? kind.footprint : kind.frontage * scale;
    const offset = slot.road.width / 2 + this.roads.setback + reach;
    const x = slot.x + slot.nx * offset;
    const z = slot.z + slot.nz * offset;
    // Clear of every road, its own too where it curves back towards the building.
    if (this.roads.edgeDistance(x, z) < reach + this.roads.setback - 1e-6) return undefined;
    const y = this.#standingHeight(x, z, kind.footprint, this.rules.maxSlope);
    if (y === undefined) return undefined;
    // The model's front (-Z) faces the road.
    const rotation = Math.atan2(slot.nx, slot.nz);
    // Box of ground taken: the turned square, or the box around the footprint circle.
    const turned = Math.abs(Math.cos(rotation)) + Math.abs(Math.sin(rotation));
    const half = kind.frontage === undefined ? kind.footprint : kind.frontage * scale * turned;
    return { placement: { kind: kind.id, x, y, z, rotation, scale }, halfX: half, halfZ: half };
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
      const ground = kind.footprint;
      if (!this.#free({ placement: { x, z }, halfX: ground, halfZ: ground })) continue;
      const y = this.#standingHeight(x, z, kind.footprint, this.rules.treeMaxSlope);
      if (y !== undefined) {
        placements.push({
          kind: kind.id,
          x,
          y,
          z,
          rotation: r(4) * 2 * Math.PI,
          scale: between(kind.scale, r(3)),
        });
      }
    }
    return placements;
  }

  /** The lowest ground under a square of half side `half` around (x, z). */
  #lowest(x: number, z: number, half: number): number {
    const corners = [-half, half].flatMap((dx) => [-half, half].map((dz) => [x + dx, z + dz]));
    return Math.min(
      this.field.height(x, z),
      ...corners.map(([cx = x, cz = z]) => this.field.height(cx, cz)),
    );
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
