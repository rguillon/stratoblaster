import { createNoise2D } from '../math/noise';
import { createRng, randomIn, type Random } from '../math/rng';
import type { HeightField } from './height-field';
import type { RoadRules } from './scenery-level';

/** One point of a road's centre line. */
export interface RoadPoint {
  readonly x: number;
  readonly z: number;
  /** False where the road cannot be built (under the sea, too steep, or a too short piece). */
  readonly valid: boolean;
}

/** A road (`main`, along the level) or a path (`cross`, branching off a main road). */
export interface Road {
  readonly index: number;
  readonly kind: 'main' | 'cross';
  readonly width: number;
  readonly points: readonly RoadPoint[];
}

/** A spot by a road where a building may stand, on one side of it. */
export interface RoadSlot {
  readonly road: Road;
  /** Slot number along its road, for hashing. */
  readonly index: number;
  /** Point on the road's centre line. */
  readonly x: number;
  readonly z: number;
  /** Unit vector across the road, towards the side of the slot. */
  readonly nx: number;
  readonly nz: number;
}

interface Segment {
  readonly road: Road;
  readonly ax: number;
  readonly az: number;
  readonly bx: number;
  readonly bz: number;
}

/** Bucket size of the segment index; distance queries see at least this far. */
const BUCKET = 64;
/** Irregular wobble of a main road, as a share of its meander amplitude. */
const WOBBLE = 0.3;

function segmentDistance(x: number, z: number, s: Segment): number {
  const dx = s.bx - s.ax;
  const dz = s.bz - s.az;
  const length2 = dx * dx + dz * dz;
  const t =
    length2 > 0 ? Math.max(0, Math.min(1, ((x - s.ax) * dx + (z - s.az) * dz) / length2)) : 0;
  return Math.hypot(x - (s.ax + t * dx), z - (s.az + t * dz));
}

/**
 * Randomly generated roads and paths of a level (P04-R07). Main roads wind along the whole
 * level; paths branch off them across the level at random intervals and bend gently. Where the
 * ground is under `minHeight` (the sea) or steeper than `maxSlope`, the road breaks, and pieces
 * shorter than `minRun` points are dropped. Buildings stand only along roads, in slots every
 * `slotSpacing` on both sides. Pure and deterministic for a given seed.
 */
export class RoadNetwork {
  readonly roads: Road[] = [];
  readonly slots: RoadSlot[] = [];
  readonly #buckets = new Map<string, Segment[]>();
  /** Gap between road edges and building footprints. */
  readonly setback: number;

  constructor(
    private readonly field: HeightField,
    private readonly rules: RoadRules,
    seed: number,
    /** Z range covered by the main roads. */
    range: { readonly zMin: number; readonly zMax: number },
  ) {
    this.setback = rules.setback;
    const random = createRng(seed + 4);
    const mains = Array.from({ length: rules.mainRoads }, () => this.#mainLine(random, range));
    for (const points of mains) this.#addRoad('main', rules.mainWidth, points);
    for (const points of this.#crossLines(random, range, mains)) {
      this.#addRoad('cross', rules.crossWidth, points);
    }
    for (const road of this.roads) this.#index(road);
    for (const road of this.roads) this.#addSlots(road);
  }

  /**
   * Distance from (`x`, `z`) to the edge of the nearest road other than `except` (negative on
   * a road), or Infinity when no road is within about {@link BUCKET} units.
   */
  edgeDistance(x: number, z: number, except?: Road): number {
    const bx = Math.floor(x / BUCKET);
    const bz = Math.floor(z / BUCKET);
    let best = Infinity;
    for (let i = bx - 1; i <= bx + 1; i++) {
      for (let j = bz - 1; j <= bz + 1; j++) {
        for (const s of this.#buckets.get(`${String(i)},${String(j)}`) ?? []) {
          if (s.road !== except) best = Math.min(best, segmentDistance(x, z, s) - s.road.width / 2);
        }
      }
    }
    return best;
  }

  #mainLine(random: Random, range: { zMin: number; zMax: number }): { x: number; z: number }[] {
    const { meander, spread, step } = this.rules;
    const x0 = randomIn(random, [-spread, spread]);
    const amplitude = randomIn(random, meander.amplitude);
    const wavelength = randomIn(random, meander.wavelength);
    const phase = random() * Math.PI * 2;
    const wobble = createNoise2D(Math.floor(random() * 1e9));
    const points: { x: number; z: number }[] = [];
    for (let z = range.zMin; z <= range.zMax; z += step) {
      const x =
        Math.sin((2 * Math.PI * z) / wavelength + phase) + WOBBLE * wobble(z / wavelength, 0.5);
      points.push({ x: x0 + amplitude * x, z });
    }
    return points;
  }

  #crossLines(
    random: Random,
    range: { zMin: number; zMax: number },
    mains: readonly { x: number; z: number }[][],
  ): { x: number; z: number }[][] {
    const { crossSpacing, crossLength, crossBend, step } = this.rules;
    const lines: { x: number; z: number }[][] = [];
    if (mains.length === 0) return lines;
    for (
      let z = range.zMin + randomIn(random, crossSpacing);
      z < range.zMax;
      z += randomIn(random, crossSpacing)
    ) {
      const main = mains[Math.floor(random() * mains.length)] ?? [];
      const start = main[Math.round((z - range.zMin) / step)];
      if (!start) continue;
      const direction = random() < 0.5 ? -1 : 1;
      const count = Math.max(2, Math.round(randomIn(random, crossLength) / step));
      const bend = randomIn(random, [-crossBend, crossBend]);
      lines.push(
        Array.from({ length: count + 1 }, (_, i) => ({
          x: start.x + direction * i * step,
          z: start.z + bend * Math.sin((Math.PI * i) / count),
        })),
      );
    }
    return lines;
  }

  #addRoad(kind: Road['kind'], width: number, line: readonly { x: number; z: number }[]): void {
    const { minHeight, maxSlope, step } = this.rules;
    const buildable = line.map(
      (p) =>
        this.field.height(p.x, p.z) >= minHeight && this.field.slope(p.x, p.z, step) <= maxSlope,
    );
    // Drop pieces shorter than minRun points.
    const valid = [...buildable];
    let start = 0;
    for (let i = 0; i <= line.length; i++) {
      if (i < line.length && buildable[i]) continue;
      if (i - start < this.rules.minRun) valid.fill(false, start, i);
      start = i + 1;
    }
    const points = line.map((p, i) => ({ ...p, valid: valid[i] ?? false }));
    this.roads.push({ index: this.roads.length, kind, width, points });
  }

  #index(road: Road): void {
    road.points.forEach((a, i) => {
      const b = road.points[i + 1];
      if (!b || !a.valid || !b.valid) return;
      const segment = { road, ax: a.x, az: a.z, bx: b.x, bz: b.z };
      const keys = new Set(
        [a, b].map(
          (p) => `${String(Math.floor(p.x / BUCKET))},${String(Math.floor(p.z / BUCKET))}`,
        ),
      );
      for (const key of keys) {
        const bucket = this.#buckets.get(key);
        if (bucket) bucket.push(segment);
        else this.#buckets.set(key, [segment]);
      }
    });
  }

  /** Slots every `slotSpacing` along the valid segments of a road, on both sides. */
  #addSlots(road: Road): void {
    const { slotSpacing } = this.rules;
    let travelled = slotSpacing / 2;
    road.points.forEach((a, i) => {
      const b = road.points[i + 1];
      if (!b) return;
      const length = Math.hypot(b.x - a.x, b.z - a.z);
      if (!a.valid || !b.valid || length === 0) {
        // Spacing starts again after a break in the road.
        travelled = slotSpacing / 2;
        return;
      }
      for (; travelled < length; travelled += slotSpacing) {
        const t = travelled / length;
        const [tx, tz] = [(b.x - a.x) / length, (b.z - a.z) / length];
        const x = a.x + (b.x - a.x) * t;
        const z = a.z + (b.z - a.z) * t;
        const index = this.slots.length;
        this.slots.push(
          { road, index, x, z, nx: tz, nz: -tx },
          { road, index: index + 1, x, z, nx: -tz, nz: tx },
        );
      }
      travelled -= length;
    });
  }
}

/** World units of road generated before the start and after the end of a level. */
const LEVEL_MARGIN = 3000;

/** The roads of a whole level, a little beyond both ends (the camera sees past them). */
export function levelRoads(field: HeightField, rules: RoadRules, seed: number): RoadNetwork {
  return new RoadNetwork(field, rules, seed, {
    zMin: -LEVEL_MARGIN,
    zMax: field.length + LEVEL_MARGIN,
  });
}
