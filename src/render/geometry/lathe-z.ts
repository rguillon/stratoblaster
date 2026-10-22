import type { Scene } from '@babylonjs/core/scene';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { CreateLathe } from '@babylonjs/core/Meshes/Builders/latheBuilder';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';

/** A profile point `[z, radius]` of a body of revolution. */
export type ProfilePoint = readonly [z: number, radius: number];

const DEFAULT_TESSELLATION = 24;

/**
 * Revolves a profile around the Z axis (the ship's nose-to-tail axis). Start and end the
 * profile with a radius of 0 to get a closed body. The profile may run in either direction.
 */
export function createLatheAlongZ(
  name: string,
  profile: readonly ProfilePoint[],
  scene: Scene,
  tessellation = DEFAULT_TESSELLATION,
): Mesh {
  // Lathe faces point outward when the profile runs towards +Z (tail to nose).
  const first = profile[0];
  const last = profile[profile.length - 1];
  const ordered = first && last && first[0] > last[0] ? [...profile].reverse() : profile;
  const shape = ordered.map(([z, r]) => new Vector3(r, z, 0));
  const mesh = CreateLathe(name, { shape, tessellation }, scene);
  // Lathe revolves around Y; +90° around X maps +Y onto +Z.
  mesh.rotation.x = Math.PI / 2;
  mesh.bakeCurrentTransformIntoVertices();
  return mesh;
}

/**
 * Cross-section of a faceted lathe: a number of equal sides, or a different number of sides
 * over the upper half (+Y) and the lower half, e.g. a smooth top over a low-poly belly.
 */
export type LatheSection = number | { readonly upper: number; readonly lower: number };

/**
 * Angles of the section's vertices, counter-clockwise from +X (towards +Y). The first one is
 * always 0, and so is a vertex on -X when the section is split into halves.
 */
export function sectionAngles(section: LatheSection): number[] {
  if (typeof section === 'number') {
    return Array.from({ length: section }, (_, k) => (2 * Math.PI * k) / section);
  }
  const { upper, lower } = section;
  return [
    ...Array.from({ length: upper }, (_, k) => (Math.PI * k) / upper),
    ...Array.from({ length: lower }, (_, k) => Math.PI + (Math.PI * k) / lower),
  ];
}

/** Every pair of neighbouring items: `[a, b, c]` gives `[a, b]` and `[b, c]`. */
function consecutivePairs<T>(items: readonly T[]): [T, T][] {
  return items.slice(1).map((item, i) => [items[i] as T, item]);
}

/**
 * Revolves a profile around the Z axis with a polygonal section, flat-shaded (vertices are
 * not shared between faces). Same profile rules as {@link createLatheAlongZ}.
 */
export function buildFacetedLatheVertexData(
  profile: readonly ProfilePoint[],
  section: LatheSection,
): { positions: number[]; indices: number[] } {
  const first = profile[0];
  const last = profile[profile.length - 1];
  // Faces point outward when the profile runs towards +Z (tail to nose).
  const ordered = first && last && first[0] > last[0] ? [...profile].reverse() : profile;
  const angles = sectionAngles(section);
  const positions: number[] = [];
  const indices: number[] = [];
  const vertex = ([z, r]: ProfilePoint, angle: number): number[] => [
    r * Math.cos(angle),
    r * Math.sin(angle),
    z,
  ];
  const tri = (a: number[], b: number[], c: number[]): void => {
    const base = positions.length / 3;
    positions.push(...a, ...b, ...c);
    indices.push(base, base + 1, base + 2);
  };
  // Facets between consecutive angles, closing the ring with a full turn.
  const facets = consecutivePairs([...angles, 2 * Math.PI]);
  for (const [p, q] of consecutivePairs(ordered)) {
    for (const [angle, next] of facets) {
      // Skip the triangle that would collapse onto the axis.
      if (p[1] > 0) tri(vertex(p, angle), vertex(q, angle), vertex(p, next));
      if (q[1] > 0) tri(vertex(p, next), vertex(q, angle), vertex(q, next));
    }
  }
  return { positions, indices };
}

/**
 * Like {@link createLatheAlongZ}, but polygonal and flat-shaded. With a number of sides, the
 * section is regular with vertices on ±X (6 sides: flat top and bottom).
 */
export function createFacetedLatheAlongZ(
  name: string,
  profile: readonly ProfilePoint[],
  section: LatheSection,
  scene: Scene,
): Mesh {
  const { positions, indices } = buildFacetedLatheVertexData(profile, section);
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
