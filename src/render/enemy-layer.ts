import type { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Enemy } from '../core/entities/enemy';
import type { EnemyModel, EnemyModelFactory } from './game-view';

interface Slot {
  readonly pivot: TransformNode;
  readonly model: EnemyModel;
  readonly key: string;
}

/**
 * Draws enemies on a top-down playfield (XY plane at Z = 0, Y up, seen from -Z, like
 * {@link ShotFrame}): one model per enemy, at its position, its nose along its heading. Models
 * are kept per model key and reused when enemies come and go (ENG-19).
 */
export class EnemyLayer {
  readonly #slots = new Map<Enemy, Slot>();
  readonly #free = new Map<string, Slot[]>();
  #created = 0;

  constructor(
    private readonly scene: Scene,
    private readonly models: Readonly<Record<string, EnemyModelFactory>>,
  ) {}

  /** Number of models built so far (shown or kept for reuse). */
  get modelCount(): number {
    return this.#created;
  }

  /** Number of enemies drawn. */
  get count(): number {
    return this.#slots.size;
  }

  /** Shows `enemies` (and hides the models of the others). */
  sync(enemies: readonly Enemy[], dtSeconds: number): void {
    const seen = new Set(enemies);
    for (const [enemy, slot] of this.#slots) {
      if (!seen.has(enemy)) this.#release(enemy, slot);
    }
    for (const enemy of enemies) {
      const slot = this.#slots.get(enemy) ?? this.#take(enemy);
      slot.pivot.position.set(enemy.x, enemy.y, 0);
      slot.pivot.rotation.z = -enemy.heading;
      slot.model.sync(enemy, dtSeconds);
    }
  }

  /** Hides every model. */
  clear(): void {
    for (const [enemy, slot] of this.#slots) this.#release(enemy, slot);
  }

  #take(enemy: Enemy): Slot {
    const slot = this.#free.get(enemy.model)?.pop() ?? this.#build(enemy.model);
    slot.pivot.setEnabled(true);
    this.#slots.set(enemy, slot);
    return slot;
  }

  #release(enemy: Enemy, slot: Slot): void {
    slot.pivot.setEnabled(false);
    this.#slots.delete(enemy);
    const free = this.#free.get(slot.key) ?? [];
    free.push(slot);
    this.#free.set(slot.key, free);
  }

  #build(key: string): Slot {
    const factory = this.models[key];
    if (!factory) throw new Error(`No model for enemy "${key}"`);
    const pivot = new TransformNode(`enemy-${key}-${String(this.#created++)}`, this.scene);
    // Models face +Z with +Y up: a holder turns the nose to +Y and the top to -Z (the camera).
    const holder = new TransformNode(`${pivot.name}-holder`, this.scene);
    holder.parent = pivot;
    holder.rotation.x = -Math.PI / 2;
    const model = factory(this.scene);
    model.root.parent = holder;
    return { pivot, model, key };
  }

  dispose(): void {
    for (const slot of [...this.#slots.values(), ...[...this.#free.values()].flat()]) {
      slot.pivot.dispose();
    }
    this.#slots.clear();
    this.#free.clear();
  }
}
