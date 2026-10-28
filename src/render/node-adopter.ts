import type { Scene } from '@babylonjs/core/scene';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';

/** Nodes of `list` created after the node numbered `after` (lists are in creation order). */
export function newer<T extends { readonly uniqueId: number }>(
  list: readonly T[],
  after: number,
): T[] {
  let i = list.length;
  while (i > 0 && (list[i - 1]?.uniqueId ?? 0) > after) i--;
  return list.slice(i);
}

/**
 * Puts what some code creates into a layer: every mesh or node created while {@link run} runs,
 * and left without a parent, is parented to `root`, and every new mesh is drawn in
 * `renderingGroupId`. It lets drawing code written for a flat playfield (shot renderers draw in
 * the XY plane) be shown in another space, e.g. the tilted level view, without knowing about it.
 * Clones of an adopted template keep its parent and group by themselves.
 */
export class NodeAdopter {
  constructor(
    private readonly scene: Scene,
    readonly root: TransformNode,
    readonly renderingGroupId: number,
    /** Called with each mesh adopted (e.g. to add it to a glow layer). */
    private readonly onMesh: (mesh: AbstractMesh) => void = () => undefined,
  ) {}

  /** Runs `create`, then adopts what it created. Returns what `create` returned. */
  run<T>(create: () => T): T {
    // Babylon numbers every node from one counter: what `create` builds gets higher numbers.
    const before = this.scene.getUniqueId();
    try {
      return create();
    } finally {
      for (const node of newer(this.scene.transformNodes, before)) this.#parent(node);
      for (const mesh of newer(this.scene.meshes, before)) {
        this.#parent(mesh);
        mesh.renderingGroupId = this.renderingGroupId;
        this.onMesh(mesh);
      }
    }
  }

  #parent(node: TransformNode): void {
    if (node.parent === null && node !== this.root) node.parent = this.root;
  }
}
