import type { Node } from '@babylonjs/core/node';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';

/** Advances one animated part of a model by `dtSeconds`. */
export type ModelAnimation = (dtSeconds: number) => void;

const ANIMATIONS = new WeakMap<Node, ModelAnimation[]>();

/**
 * Attaches a per-frame animation to a node of a model (reactor flames, blinking lights...).
 * It runs whenever the model is stepped with {@link stepModelAnimations} and is dropped with
 * the node.
 */
export function addModelAnimation(node: TransformNode, animation: ModelAnimation): void {
  const list = ANIMATIONS.get(node);
  if (list) list.push(animation);
  else ANIMATIONS.set(node, [animation]);
}

/** Runs the animations attached to `root` and to all its descendants. */
export function stepModelAnimations(root: TransformNode, dtSeconds: number): void {
  for (const node of [root, ...root.getDescendants(false)]) {
    const list = ANIMATIONS.get(node);
    if (list) for (const animation of list) animation(dtSeconds);
  }
}
