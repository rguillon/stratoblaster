import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import {
  buildFacetedLatheVertexData,
  createFacetedLatheAlongZ,
  createLatheAlongZ,
  sectionAngles,
} from '../../../../src/render/geometry/lathe-z';
import { at } from '../../../helpers/at';

describe('createLatheAlongZ', () => {
  it('revolves a (z, radius) profile around the Z axis', () => {
    const scene = new Scene(new NullEngine());
    const mesh = createLatheAlongZ(
      'body',
      [
        [2, 0],
        [0, 0.5],
        [-1, 0],
      ],
      scene,
    );
    const box = mesh.getBoundingInfo().boundingBox;
    expect(box.maximum.z).toBeCloseTo(2);
    expect(box.minimum.z).toBeCloseTo(-1);
    expect(box.maximum.x).toBeCloseTo(0.5, 1);
    expect(box.maximum.y).toBeCloseTo(0.5, 1);
    scene.dispose();
  });

  it.each([
    [
      'nose to tail',
      [
        [2, 0],
        [0, 0.5],
        [-1, 0],
      ],
    ],
    [
      'tail to nose',
      [
        [-1, 0],
        [0, 0.5],
        [2, 0],
      ],
    ],
  ] as const)('has outward normals for a %s profile', (_label, profile) => {
    const scene = new Scene(new NullEngine());
    const mesh = createLatheAlongZ('body', profile, scene);
    const p = Array.from(mesh.getVerticesData('position') ?? []);
    const normals: number[] = [];
    VertexData.ComputeNormals(p, Array.from(mesh.getIndices() ?? []), normals);
    for (let v = 0; v < p.length / 3; v++) {
      const radial = at(p, 3 * v) * at(normals, 3 * v) + at(p, 3 * v + 1) * at(normals, 3 * v + 1);
      expect(radial).toBeGreaterThanOrEqual(-1e-6);
    }
    scene.dispose();
  });
});

describe('createFacetedLatheAlongZ', () => {
  it('builds a flat-shaded polygonal body with the given number of sides', () => {
    const scene = new Scene(new NullEngine());
    const mesh = createFacetedLatheAlongZ(
      'pod',
      [
        [1, 0],
        [1, 0.5],
        [-1, 0.5],
        [-1, 0],
      ],
      6,
      scene,
    );
    const box = mesh.getBoundingInfo().boundingBox;
    expect(box.maximum.z).toBeCloseTo(1);
    expect(box.minimum.z).toBeCloseTo(-1);
    // Hexagon with vertices on ±X: full radius across X, flat top and bottom at r·sin 60°.
    expect(box.maximum.x).toBeCloseTo(0.5);
    expect(box.maximum.y).toBeCloseTo(0.5 * Math.sin(Math.PI / 3));
    // Flat shading: every side's normals are parallel, one direction per facet.
    const normals = Array.from(mesh.getVerticesData('normal') ?? []);
    const radial = new Set<string>();
    for (let v = 0; v < normals.length / 3; v++) {
      if (Math.abs(at(normals, 3 * v + 2)) > 0.5) continue; // end caps
      radial.add(`${at(normals, 3 * v).toFixed(3)},${at(normals, 3 * v + 1).toFixed(3)}`);
    }
    expect(radial.size).toBe(6);
    scene.dispose();
  });
});

describe('sectionAngles', () => {
  it('spreads a regular section evenly from +X', () => {
    expect(sectionAngles(4)).toEqual([0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2]);
  });

  it('uses more, smaller facets on the upper half of a split section', () => {
    const angles = sectionAngles({ upper: 4, lower: 2 });
    expect(angles).toEqual([
      0,
      Math.PI / 4,
      Math.PI / 2,
      (3 * Math.PI) / 4,
      Math.PI,
      (3 * Math.PI) / 2,
    ]);
  });
});

describe('buildFacetedLatheVertexData', () => {
  const PROFILE = [
    [-1, 0],
    [-1, 0.5],
    [1, 0.5],
    [1, 0],
  ] as const;

  it.each([
    ['regular', 6],
    ['split', { upper: 8, lower: 3 }],
  ] as const)('has outward faces for a %s section', (_label, section) => {
    for (const profile of [PROFILE, [...PROFILE].reverse()]) {
      const { positions: p } = buildFacetedLatheVertexData(profile, section);
      for (let t = 0; t < p.length / 9; t++) {
        const v = (k: number): number[] => [0, 1, 2].map((c) => at(p, 9 * t + 3 * k + c));
        const [a, b, c] = [v(0), v(1), v(2)];
        // Babylon front face: outward normal = (c - a) × (b - a).
        const u = [0, 1, 2].map((i) => at(c, i) - at(a, i));
        const w = [0, 1, 2].map((i) => at(b, i) - at(a, i));
        const n = [
          at(u, 1) * at(w, 2) - at(u, 2) * at(w, 1),
          at(u, 2) * at(w, 0) - at(u, 0) * at(w, 2),
          at(u, 0) * at(w, 1) - at(u, 1) * at(w, 0),
        ];
        const centroid = [0, 1, 2].map((i) => (at(a, i) + at(b, i) + at(c, i)) / 3);
        // Outward: away from the axis on the sides, away from the middle on the end caps.
        const out = [at(centroid, 0), at(centroid, 1), at(centroid, 2)];
        expect(
          at(n, 0) * at(out, 0) + at(n, 1) * at(out, 1) + at(n, 2) * at(out, 2),
        ).toBeGreaterThan(0);
      }
    }
  });

  it('skips the triangles that would collapse onto the axis', () => {
    const { positions, indices } = buildFacetedLatheVertexData(PROFILE, 6);
    // 6 cap triangles at each end + 6 quads (12 triangles) along the side.
    expect(indices).toHaveLength(3 * 24);
    expect(positions).toHaveLength(3 * 3 * 24);
  });
});
