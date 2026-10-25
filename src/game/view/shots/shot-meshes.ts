import { Constants } from '@babylonjs/core/Engines/constants';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import type { Scene } from '@babylonjs/core/scene';
import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';

/**
 * A disabled template mesh showing its vertex colours, unlit, added onto what is behind it
 * (black is transparent), without writing depth. Clones of it share its geometry.
 */
export function additiveTemplate(name: string, geo: ColoredGeometry, scene: Scene): Mesh {
  const mesh = new Mesh(name, scene);
  const data = new VertexData();
  data.positions = geo.positions;
  data.indices = geo.indices;
  data.colors = geo.colors;
  data.applyToMesh(mesh);
  const material = new StandardMaterial(name, scene);
  material.emissiveColor = Color3.White();
  material.diffuseColor = Color3.Black();
  material.specularColor = Color3.Black();
  material.disableLighting = true;
  material.backFaceCulling = false;
  material.alphaMode = Constants.ALPHA_ADD;
  // Below 1, so the material goes through the blended pass.
  material.alpha = 0.999;
  material.disableDepthWrite = true;
  mesh.material = material;
  mesh.isPickable = false;
  mesh.setEnabled(false);
  return mesh;
}

/**
 * A disabled template mesh darkening what is behind it (phase 8): a disc of radius 1 in `color`,
 * `alpha` opaque at its centre and fading out to its edge, blended, without writing depth.
 */
export function shadeTemplate(
  name: string,
  [segments, color, alpha]: readonly [number, readonly [number, number, number], number],
  scene: Scene,
): Mesh {
  const positions = [0, 0, 0];
  const colors = [...color, alpha];
  const indices: number[] = [];
  for (let i = 0; i < segments; i++) {
    const angle = (2 * Math.PI * i) / segments;
    positions.push(Math.cos(angle), Math.sin(angle), 0);
    colors.push(...color, 0);
    indices.push(0, 1 + i, 1 + ((i + 1) % segments));
  }
  const mesh = new Mesh(name, scene);
  const data = new VertexData();
  data.positions = positions;
  data.indices = indices;
  data.colors = colors;
  data.applyToMesh(mesh);
  mesh.hasVertexAlpha = true;
  const material = new StandardMaterial(name, scene);
  material.emissiveColor = Color3.White();
  material.diffuseColor = Color3.Black();
  material.specularColor = Color3.Black();
  material.disableLighting = true;
  material.backFaceCulling = false;
  material.disableDepthWrite = true;
  mesh.material = material;
  mesh.isPickable = false;
  return mesh;
}
