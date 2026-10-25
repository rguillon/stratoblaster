import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Boss } from '../../../core/entities/boss';
import type { Enemy } from '../../../core/entities/enemy';
import type { EnemyModel } from '../../../render/game-view';
import type { BossDesign } from '../../config/bosses/boss-kit';
import type { EnemyParts } from '../enemies/enemy-mesh';

// The moving limbs of boss models (phase 7 review): their joints as nodes, and what is drawn on
// them. Model space as in `boss-model.ts`.
type Vec3 = [number, number, number];

/**
 * Model space of a boss: logical pixels, its nose at +Z, +Y up (towards the camera). A boss
 * faces down the screen, so the point `(x, y)` of the playfield (X right, Y up, from its centre)
 * is model `(-x, height, -y)`.
 */
export function bossPoint(x: number, y: number, height = 0): Vec3 {
  return [-x, height, -y];
}

/** A limb drawn on a joint (see {@link BossDrawing.limbs}). */
export interface LimbDrawing {
  readonly draw: (parts: EnemyParts) => void;
  /** The part it belongs to, if any. */
  readonly part?: string;
}

/** Where things hanging on a joint are drawn: its node, and its pivot in model space. */
export interface JointFrame {
  readonly node: TransformNode;
  readonly origin: Vec3;
}

/** The joints of a boss as nodes (phase 7 review), each at its pivot on the one it hangs on. */
export class JointFrames {
  readonly #frames = new Map<string, JointFrame>();

  constructor(design: BossDesign, root: TransformNode) {
    const specs = design.stats.joints ?? {};
    const make = (id: string): JointFrame => {
      const made = this.#frames.get(id);
      const spec = specs[id];
      if (made) return made;
      if (!spec) throw new Error(`Boss "${design.id}" has no joint "${id}"`);
      const parent = spec.parent === undefined ? { node: root, origin: ORIGIN } : make(spec.parent);
      const origin = bossPoint(spec.x, spec.y);
      const node = new TransformNode(`${design.id}-${id}-joint`, root.getScene());
      node.parent = parent.node;
      node.position.set(...sub(origin, parent.origin));
      const frame = { node, origin };
      this.#frames.set(id, frame);
      return frame;
    };
    for (const id of Object.keys(specs)) make(id);
  }

  /** The frame of `joint`, or `holder` at the model's origin without one. */
  frame(joint: string | undefined, holder: TransformNode): JointFrame {
    const frame = joint === undefined ? undefined : this.#frames.get(joint);
    if (joint !== undefined && !frame) throw new Error(`No boss joint "${joint}"`);
    return frame ?? { node: holder, origin: ORIGIN };
  }

  /** Turns them as `boss`'s joints are now; at rest without one. */
  show(boss: Boss | undefined): void {
    for (const [id, { node }] of this.#frames) node.rotation.y = boss?.joints.angle(id) ?? 0;
  }
}

export const ORIGIN: Vec3 = [0, 0, 0];
const sub = (a: Vec3, b: Vec3): Vec3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];

/** Puts `node` (drawn in model space) at `at` on `frame`. */
export function hang(node: TransformNode, at: Vec3, frame: JointFrame): void {
  node.parent = frame.node;
  node.position.set(...sub(at, frame.origin));
}

/** A limb's model, flashing when what it belongs to is hit. */
interface LimbGroup {
  readonly model: EnemyModel;
  show(sinceHit: number): void;
}

/**
 * The limbs of a boss model (see `BossDrawing.limbs`), each built by `build` and hung on its
 * joint; one that belongs to a part goes and flashes with it, the others with the core.
 */
export class BossLimbs {
  readonly #limbs: { readonly group: LimbGroup; readonly part: number }[];

  constructor(
    design: BossDesign,
    limbs: Readonly<Record<string, LimbDrawing>> | undefined,
    private readonly joints: JointFrames,
    build: (joint: string, draw: (parts: EnemyParts) => void) => LimbGroup,
  ) {
    this.#limbs = Object.entries(limbs ?? {}).map(([joint, limb]) => {
      const group = build(joint, limb.draw);
      hang(group.model.root, ORIGIN, joints.frame(joint, group.model.root));
      const part = design.stats.parts.findIndex((p) => p.id === limb.part);
      if (limb.part !== undefined && part < 0)
        throw new Error(`Boss "${design.id}": limb "${joint}" belongs to no part "${limb.part}"`);
      return { group, part };
    });
  }

  /** Shows them as `boss` is now (its joints turned); at rest for a stand-in. */
  show(boss: Boss | undefined, lit: Enemy, dt: number): void {
    this.joints.show(boss);
    for (const { group, part } of this.#limbs) {
      group.model.sync(lit, dt);
      if (!boss) continue;
      const owner = boss.parts[part];
      group.model.root.setEnabled(!owner?.destroyed);
      group.show(owner ? owner.sinceHit : boss.core.sinceHit);
    }
  }
}
