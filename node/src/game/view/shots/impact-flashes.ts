import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { Scene } from '@babylonjs/core/scene';
import type { ShotImpact } from '../../../core/systems/shot-world';
import { NodePool } from '../../../render/node-pool';
import { buildGlowDisc } from '../shot-geometry';
import { additiveTemplate } from './shot-meshes';

type Rgb = readonly [number, number, number];

/** A flash in progress. */
export interface Flash {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
  age: number;
}

/** Size of a flash at `age` over `duration`, relative to its radius: grows fast, then shrinks. */
export function flashScale(age: number, duration: number): number {
  const t = age / duration;
  if (t <= 0 || t >= 1) return 0;
  return Math.sin(Math.PI * Math.sqrt(t));
}

/** Short glowing discs where shots hit (P03-R01, P03-R03), kept in a pool. */
export class ImpactFlashes {
  readonly flashes: Flash[] = [];
  readonly #pool: NodePool<Mesh>;

  constructor(
    scene: Scene,
    name: string,
    look: { readonly colors: readonly Rgb[]; readonly segments: number },
    private readonly duration: number,
    private readonly radiusOf: (impact: ShotImpact) => number,
  ) {
    const template = additiveTemplate(name, buildGlowDisc(look.segments, look.colors), scene);
    this.#pool = new NodePool((i) => template.clone(`${name}-${String(i)}`));
  }

  /** Starts a flash per impact, ages the others by `dt`, and draws them. */
  sync(impacts: readonly ShotImpact[], dt: number): void {
    for (const flash of this.flashes) flash.age += dt;
    for (let i = this.flashes.length - 1; i >= 0; i--) {
      if ((this.flashes[i]?.age ?? 0) >= this.duration) this.flashes.splice(i, 1);
    }
    for (const impact of impacts) {
      this.flashes.push({ x: impact.x, y: impact.y, radius: this.radiusOf(impact), age: 0 });
    }
    this.#pool.show(this.flashes.length).forEach((mesh, i) => {
      const flash = this.flashes[i];
      if (!flash) return;
      // A new flash shows at a small size on its first frame.
      const size = flash.radius * Math.max(0.3, flashScale(flash.age, this.duration));
      mesh.position.set(flash.x, flash.y, -1);
      mesh.scaling.set(size, size, 1);
    });
  }

  dispose(): void {
    this.#pool.dispose();
  }
}
