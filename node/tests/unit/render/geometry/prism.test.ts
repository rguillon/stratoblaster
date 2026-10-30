import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { buildPrismVertexData, createPrism } from '../../../../src/render/geometry/prism';
import { at } from '../../../helpers/at';

const SQUARE: readonly (readonly [number, number])[] = [
  [0, 0],
  [1, 0],
  [1, 1],
  [0, 1],
];

describe('prism geometry', () => {
  it('builds top, bottom and side faces with outward-facing triangles', () => {
    const { positions, indices } = buildPrismVertexData(SQUARE, 0.2);
    // 2 cap triangles top + 2 bottom + 2 per side.
    expect(indices).toHaveLength((2 + 2 + 8) * 3);
    const normals: number[] = [];
    VertexData.ComputeNormals(positions, indices, normals);
    const vertexCount = positions.length / 3;
    const centre = [0.5, 0, 0.5] as const;
    for (let v = 0; v < vertexCount; v++) {
      const p = [at(positions, 3 * v), at(positions, 3 * v + 1), at(positions, 3 * v + 2)];
      const n = [at(normals, 3 * v), at(normals, 3 * v + 1), at(normals, 3 * v + 2)];
      const out =
        (at(p, 0) - centre[0]) * at(n, 0) +
        (at(p, 1) - centre[1]) * at(n, 1) +
        (at(p, 2) - centre[2]) * at(n, 2);
      expect(out, `vertex ${String(v)} normal points outward`).toBeGreaterThan(0);
    }
  });

  it('spans the outline in XZ and the thickness in Y', () => {
    const { positions } = buildPrismVertexData(SQUARE, 0.2);
    const ys = positions.filter((_, i) => i % 3 === 1);
    expect(Math.max(...ys)).toBeCloseTo(0.1);
    expect(Math.min(...ys)).toBeCloseTo(-0.1);
  });

  it('accepts clockwise outlines by reordering them', () => {
    const cw = buildPrismVertexData([...SQUARE].reverse(), 0.2);
    const ccw = buildPrismVertexData(SQUARE, 0.2);
    expect(cw.positions).toHaveLength(ccw.positions.length);
    const normals: number[] = [];
    VertexData.ComputeNormals(cw.positions, cw.indices, normals);
    // First vertex belongs to the top face.
    expect(normals[1]).toBeGreaterThan(0.99);
  });

  it('rejects outlines with fewer than 3 points', () => {
    expect(() =>
      buildPrismVertexData(
        [
          [0, 0],
          [1, 1],
        ],
        1,
      ),
    ).toThrow(/3 points/);
  });

  it('supports concave outlines', () => {
    const c: readonly (readonly [number, number])[] = [
      [0, 0],
      [3, 0],
      [3, 0.2],
      [0.2, 0.2],
      [0.2, 2.8],
      [3, 2.8],
      [3, 3],
      [0, 3],
    ];
    // (n - 2) cap triangles top and bottom + 2 per side.
    expect(buildPrismVertexData(c, 1).indices).toHaveLength((6 + 6 + 16) * 3);
  });

  it('creates a Babylon mesh from the outline', () => {
    const scene = new Scene(new NullEngine());
    const mesh = createPrism('wing', SQUARE, 0.2, scene);
    expect(mesh.getTotalVertices()).toBeGreaterThan(0);
    expect(mesh.getBoundingInfo().boundingBox.maximum.x).toBeCloseTo(1);
    scene.dispose();
  });
});
