import { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';

/** Number of triangles drawn for `root` and all the meshes under it. */
export function countTriangles(root: TransformNode): number {
  const meshes = root.getChildMeshes(false);
  if (root instanceof AbstractMesh) meshes.push(root);
  let triangles = 0;
  for (const mesh of meshes) {
    const indices = mesh.getTotalIndices();
    triangles += (indices > 0 ? indices : mesh.getTotalVertices()) / 3;
  }
  return Math.round(triangles);
}
