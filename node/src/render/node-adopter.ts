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
 * Draw order (`alphaIndex`) from which a layer's see-through meshes are drawn over all those
 * that set none (P14-R05: the enemy shots). Babylon draws a mesh left at its default order
 * (`Number.MAX_VALUE`) after every other, so a layer gives such meshes the one just below.
 */
export const ON_TOP_ALPHA_INDEX = 1_000_000;

/**
 * Puts what some code creates into a layer: every mesh or node created while {@link run} runs,
 * and left without a parent, is parented to `root`, and every new mesh is drawn in
 * `renderingGroupId`, under {@link ON_TOP_ALPHA_INDEX} if it sets no draw order. It lets drawing
 * code written for a flat playfield (shot renderers draw in the XY plane) be shown in another
 * space, e.g. the tilted level view, without knowing about it. Clones of an adopted template
 * keep its parent, group and draw order by themselves.
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
        if (mesh.alphaIndex === Number.MAX_VALUE) mesh.alphaIndex = ON_TOP_ALPHA_INDEX - 1;
        this.onMesh(mesh);
      }
    }
  }

  #parent(node: TransformNode): void {
    if (node.parent === null && node !== this.root) node.parent = this.root;
  }
}
