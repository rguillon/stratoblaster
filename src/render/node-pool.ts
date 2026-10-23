import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';

/**
 * Reusable nodes for things drawn in varying numbers (shots, particles, flashes): nodes are
 * created on demand, then shown or hidden instead of being created and disposed every frame
 * (ENG-19).
 */
export class NodePool<T extends TransformNode> {
  readonly nodes: T[] = [];

  constructor(private readonly create: (index: number) => T) {}

  /** Enables the first `count` nodes, creating missing ones, and disables the others. */
  show(count: number): readonly T[] {
    while (this.nodes.length < count) this.nodes.push(this.create(this.nodes.length));
    this.nodes.forEach((node, i) => {
      node.setEnabled(i < count);
    });
    return this.nodes.slice(0, count);
  }

  dispose(): void {
    for (const node of this.nodes) node.dispose();
    this.nodes.length = 0;
  }
}
