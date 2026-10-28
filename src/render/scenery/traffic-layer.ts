import type { Scene } from '@babylonjs/core/scene';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { GroundArea } from '../../core/scenery/prop-placement';
import type { Road } from '../../core/scenery/road-network';
import type { CarRules } from '../../core/scenery/scenery-level';
import { Traffic } from '../../core/scenery/traffic';
import { PropField, type PropMaterials } from './prop-field';
import type { PropModelFactory } from './scenery-look';

/** The roads the cars drive on, the ground under them, and the seed of the level. */
export interface TrafficSource {
  readonly roads: readonly Road[];
  readonly height: (x: number, z: number) => number;
  readonly seed: number;
}

/**
 * The moving cars of a level (phase 4 review): the cars in view are placed again every frame,
 * as thin instances of their own meshes, apart from the props that stay put.
 */
export class TrafficLayer {
  readonly #field: PropField;
  #traffic: Traffic | undefined;
  #roads: readonly Road[] | undefined;

  constructor(
    scene: Scene,
    models: Readonly<Record<string, PropModelFactory>>,
    materials: PropMaterials,
    private readonly rules: CarRules | undefined,
  ) {
    const kinds = new Set(rules?.kinds ?? []);
    const cars = Object.fromEntries(Object.entries(models).filter(([id]) => kinds.has(id)));
    this.#field = new PropField(scene, cars, materials);
  }

  /** Meshes of the headlights and tail lights (e.g. for a glow layer). */
  get lightMeshes(): Mesh[] {
    return this.#field.lightMeshes;
  }

  /** Meshes of the car bodies (e.g. to hide lights behind them in a glow layer). */
  get structureMeshes(): Mesh[] {
    return this.#field.structureMeshes;
  }

  /** Number of cars in view. */
  get count(): number {
    return this.#field.count;
  }

  /**
   * Places the cars in `area` at `time`. New roads (a new seed) get new traffic; roads that go on
   * from the ones before (the runout's, reviewer 2026-10-28) only add theirs.
   */
  update(time: number, area: GroundArea, source: TrafficSource): void {
    if (!this.rules) return;
    const before = this.#roads;
    if (source.roads !== before) {
      this.#roads = source.roads;
      if (this.#traffic && before && goesOn(before, source.roads)) {
        this.#traffic.add(source.roads.slice(before.length));
      } else this.#traffic = new Traffic(source.roads, source.height, this.rules, source.seed);
    }
    this.#field.setChunk(0, this.#traffic?.at(time, area) ?? []);
    this.#field.sync();
  }
}

/** Whether `roads` starts with `before` (the same roads, more after them). */
function goesOn(before: readonly Road[], roads: readonly Road[]): boolean {
  return roads.length >= before.length && before.every((road, i) => roads[i] === road);
}
