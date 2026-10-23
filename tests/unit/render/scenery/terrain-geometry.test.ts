import { describe, expect, it } from 'vitest';
import {
  buildGridIndices,
  buildTerrainGeometry,
} from '../../../../src/render/scenery/terrain-geometry';

const GRID = { xMin: -10, zMin: 100, columns: 4, rows: 2, cell: 5 };

describe('buildTerrainGeometry', () => {
  it('P04-R01: samples the height at every grid point, row by row', () => {
    const { positions } = buildTerrainGeometry({ height: (x, z) => x + z / 10 }, GRID);
    expect(positions).toHaveLength(5 * 3 * 3);
    expect([...positions.slice(0, 3)]).toEqual([-10, 0, 100]);
    expect([...positions.slice(-3)]).toEqual([10, 21, 110]);
  });

  it('P04-R01: flat ground has up normals; a slope tilts them away from the rise', () => {
    const flat = buildTerrainGeometry({ height: () => 3 }, GRID).normals;
    expect([...flat.slice(0, 3)]).toEqual([0, 1, 0]);
    const slope = buildTerrainGeometry({ height: (x) => x }, GRID).normals;
    const [nx, ny, nz] = slope.slice(0, 3);
    expect(nx).toBeCloseTo(-Math.SQRT1_2);
    expect(ny).toBeCloseTo(Math.SQRT1_2);
    expect(nz).toBeCloseTo(0);
  });
});

describe('buildGridIndices', () => {
  it('makes two up-facing triangles per cell', () => {
    const indices = buildGridIndices(2, 1);
    expect(indices).toHaveLength(12);
    expect([...indices.slice(0, 6)]).toEqual([0, 1, 3, 1, 4, 3]);
    // Babylon's front face normal is (c - a) × (b - a): with a, b, c = 0, 1, 3 on a unit grid
    // (x across, z along), (0, 0, 1) × (1, 0, 0) = (0, 1, 0), i.e. up.
  });
});
