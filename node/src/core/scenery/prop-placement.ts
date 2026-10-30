import { createNoise2D, hash2D, type Noise2D } from '../math/noise';
import {
  placeHamlets,
  placeLoners,
  type AwaySite,
  type Building,
  type ZRange,
} from './away-placement';
import { towerIn } from './block-towers';
import { allowed, between, weighted } from './draws';
import { fixedPieces, floatingIn } from './float-placement';
import { lowestUnder, standingHeight } from './ground-fit';
import type { HeightField } from './height-field';
import type { RoadNetwork, RoadSlot } from './road-network';
import { blockParts, type Block } from './street-grid';
import { packDistricts } from './district-packing';
import type {
  BlockFill,
  PropGroupRule,
  PropKindRule,
  PropRules,
  TerrainSection,
} from './scenery-level';
import {
  BuildingIndex,
  inside,
  overlap,
  type GroundArea,
  type GroundBox,
  type PlacerSnapshot,
  type PropPlacement,
} from './ground-boxes';

export type { GroundArea, PlacerSnapshot, PropPlacement } from './ground-boxes';

/** Hash streams of a slot or a cell; each draw uses its own stream so they stay independent. */
const Draw = { Building: 0, Kind: 1, Scale: 2, Trees: 3 } as const;

/** Draws per tree: position X, position Z, kind, scale, turn. */
const TREE_DRAWS = 5;

/** Blocks are cut into parts of about this size, one tower each at most… */
const PART_SIZE = 30;
/** …and at most this many parts across either way. */
const MAX_PARTS = 4;

/** Smaller kinds a building slot tries when its first choice does not fit. */
const FALLBACKS = 3;

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
 * contains its centre; a cell to the area that contains its corner. The buildings of the runout,
 * past the level's end, are placed after the others ({@link placeRunout}).
 */

export class PropPlacer {
  readonly #zones: Noise2D;
  readonly #buildings: Building[] = [];
  readonly #occupied = new BuildingIndex();
  /** Phase 9: set pieces and lines, larger than a bucket: every placement checks them all. */
  readonly #fixed: Building[] = [];
  #runoutPlaced = false;

  constructor(
    private readonly field: HeightField,
    private readonly rules: PropRules,
    private readonly seed: number,
    readonly roads: RoadNetwork,
    /** The level's sea level, if it has a sea: floating props float on it (phase 8). */
    private readonly seaLevel?: number,
    /** The buildings placed before (e.g. in a worker, P13-R03): taken as they are. */
    made?: PlacerSnapshot,
  ) {
    this.#zones = createNoise2D(seed + 3);
    if (made) {
      this.#restore(made);
      return;
    }
    // Phase 9: set pieces, then (phase 8) lines of props first: the rest keeps clear of them.
    this.#fixed.push(...fixedPieces(rules, field, seaLevel));
    for (const piece of this.#fixed) this.#occupy(piece);
    this.#placeBuildings({ from: -Infinity, to: roads.runoutFrom ?? Infinity });
  }

  /** Whether the buildings of the runout are placed (see {@link placeRunout}). */
  get runoutPlaced(): boolean {
    return this.#runoutPlaced;
  }

  /**
   * Places the buildings of the runout (reviewer, 2026-10-28: after the others, so the level is
   * ready sooner), once its streets are laid (`RoadNetwork.addRunout`), or takes those `made`
   * before (e.g. in a worker), and returns them. Once only: afterwards, it adds nothing.
   */
  placeRunout(made?: readonly Building[]): readonly Building[] {
    const from = this.roads.runoutFrom;
    if (this.#runoutPlaced || from === undefined) return [];
    this.#runoutPlaced = true;
    const before = this.#buildings.length;
    if (made) for (const building of made) this.#occupy(building);
    else this.#placeBuildings({ from, to: Infinity });
    return this.#buildings.slice(before);
  }

  /** The buildings of the blocks, the road slots and the spots away from the roads in `range`. */
  #placeBuildings(range: ZRange): void {
    const within = (z: number): boolean => z >= range.from && z < range.to;
    const { tiles } = this.roads;
    if (tiles) {
      packDistricts(
        {
          field: this.field,
          rules: this.rules,
          roads: this.roads,
          seed: this.seed,
          groupAt: (x, z, section) => this.#groupAt(x, z, section),
          occupy: (building) => {
            this.#occupy(building);
          },
        },
        within,
        tiles,
      );
    } else {
      this.roads.blocks.forEach((block, i) => {
        if (within((block.zMin + block.zMax) / 2)) this.#fillBlock(block, i);
      });
    }
    const mainFirst = this.roads.slots
      .filter((slot) => within(slot.z))
      .sort((a, b) => Number(a.road.kind === 'cross') - Number(b.road.kind === 'cross'));
    for (const slot of mainFirst) {
      if (this.field.sectionAt(slot.z).section.blocks) continue;
      const building = this.#buildingBy(slot);
      if (building) this.#occupy(building);
    }
    const { hamlets, loners } = this.rules;
    if (hamlets) placeHamlets(this.#awaySite(), hamlets, range);
    if (loners) placeLoners(this.#awaySite(), loners, range);
  }

  /** What `placeHamlets` and `placeLoners` need (phase 6 review). */
  #awaySite(): AwaySite {
    return {
      length: this.field.length,
      offscreenX: this.roads.offscreenX,
      seed: this.seed,
      sectionAt: (z) => this.field.sectionAt(z).section,
      groupAt: (x, z, section) => this.#groupAt(x, z, section),
      clearOfRoads: (x, z, clearance) => this.roads.clearOf(x, z, clearance),
      ground: (x, z, radius) =>
        standingHeight(this.field, [x, z, radius], [this.rules.maxSlope, this.rules.minHeight]),
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
    const { floating } = this.rules;
    if (floating && this.seaLevel !== undefined) {
      placements.push(...floatingIn(floating, this.field, [this.seaLevel, this.seed], area));
    }
    return placements;
  }

  #random(i: number, j: number, draw: number): number {
    return hash2D(i, j, this.seed * 31 + draw);
  }

  /** Whether the ground box of `area` keeps `gap` clear of the placed buildings. */
  #free(area: GroundBox, gap = this.roads.setback): boolean {
    if (this.#fixed.some((b) => overlap(b, area, gap))) return false;
    return this.#occupied.clear(area, gap);
  }

  /** The buildings placed before, occupying the ground in the order they were placed. */
  #restore(made: PlacerSnapshot): void {
    this.#fixed.push(...made.buildings.slice(0, made.fixed));
    for (const building of made.buildings) this.#occupy(building);
  }

  /** What this placer placed so far (P13-R03). */
  snapshot(): PlacerSnapshot {
    return { buildings: [...this.#buildings], fixed: this.#fixed.length };
  }

  #occupy(building: Building): void {
    this.#buildings.push(building);
    this.#occupied.add(building);
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
        const tower = towerIn(part, groups, roof ?? 0, r(20 + k));
        if (!tower) return;
        // Without a podium, on the lowest ground under its own plan, so it never floats.
        const { placement, halfX } = tower;
        const y = roof ?? lowestUnder(this.field, placement.x, placement.z, halfX);
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

  /**
   * The first of the kinds `slot` tries that fits there, free of the others (reviewer,
   * 2026-10-28: the smaller ones are only fitted when the ones before do not fit).
   */
  #buildingBy(slot: RoadSlot): Building | undefined {
    for (const kind of this.#candidates(slot)) {
      const building = this.#fit(slot, kind);
      if (building && this.#free(building)) return building;
    }
    return undefined;
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
    if (!this.roads.clearOf(x, z, reach + this.roads.setback - 1e-6)) return undefined;
    const y = standingHeight(
      this.field,
      [x, z, kind.footprint],
      [this.rules.maxSlope, this.rules.minHeight],
    );
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
      if (!kind || !this.roads.clearOf(x, z, treeClearance + kind.footprint)) continue;
      const ground = kind.footprint;
      if (!this.#free({ placement: { x, z }, halfX: ground, halfZ: ground })) continue;
      const y = standingHeight(
        this.field,
        [x, z, kind.footprint],
        [this.rules.treeMaxSlope, this.rules.minHeight],
      );
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
}
