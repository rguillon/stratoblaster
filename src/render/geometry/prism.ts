import type { Scene } from '@babylonjs/core/scene';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { ringAt, type OutlinePoint } from './outline';
import { triangulatePolygon } from './triangulate';

/** Raw geometry of a prism, before it is turned into a Babylon mesh. */
export interface PrismGeometry {
  readonly positions: number[];
  readonly indices: number[];
}

function signedArea(outline: readonly OutlinePoint[]): number {
  let area = 0;
  outline.forEach(([x1, z1], i) => {
    const [x2, z2] = ringAt(outline, i + 1);
    area += x1 * z2 - x2 * z1;
  });
  return area / 2;
}

/**
 * Extrudes a planform outline (in the XZ plane) into a flat prism of the given thickness,
 * centred on Y = 0. Faces are flat-shaded (vertices are not shared between faces).
 * The outline must be a simple polygon (concave is fine); either winding order is accepted.
 */
export function buildPrismVertexData(
  outline: readonly OutlinePoint[],
  thickness: number,
): PrismGeometry {
  if (outline.length < 3) throw new Error('A prism outline needs at least 3 points');
  // Babylon front faces: outward normal = (c - a) × (b - a); caps need a CCW outline.
  const pts = signedArea(outline) < 0 ? [...outline].reverse() : outline;
  const h = thickness / 2;
  const positions: number[] = [];
  const indices: number[] = [];
  const tri = (a: number[], b: number[], c: number[]): void => {
    const base = positions.length / 3;
    positions.push(...a, ...b, ...c);
    indices.push(base, base + 1, base + 2);
  };
  const at = (i: number, y: number): number[] => {
    const [x, z] = ringAt(pts, i);
    return [x, y, z];
  };

  for (const [a, b, c] of triangulatePolygon(pts)) {
    tri(at(a, h), at(b, h), at(c, h));
    tri(at(a, -h), at(c, -h), at(b, -h));
  }
  pts.forEach((_, i) => {
    tri(at(i, h), at(i, -h), at(i + 1, h));
    tri(at(i + 1, h), at(i, -h), at(i + 1, -h));
  });
  return { positions, indices };
}

/** Creates a flat-shaded prism mesh from a planform outline (see {@link buildPrismVertexData}). */
export function createPrism(
  name: string,
  outline: readonly OutlinePoint[],
  thickness: number,
  scene: Scene,
): Mesh {
  const { positions, indices } = buildPrismVertexData(outline, thickness);
  const normals: number[] = [];
  VertexData.ComputeNormals(positions, indices, normals);
  const data = new VertexData();
  data.positions = positions;
  data.indices = indices;
  data.normals = normals;
  const mesh = new Mesh(name, scene);
  data.applyToMesh(mesh);
  return mesh;
}
