/** Anything that gives a ground height at (x, z), e.g. a `HeightField`. */
export interface HeightSource {
  height(x: number, z: number): number;
}

/** A rectangular grid of ground, `columns × rows` cells of `cell` world units. */
export interface TerrainGrid {
  readonly xMin: number;
  readonly zMin: number;
  readonly columns: number;
  readonly rows: number;
  readonly cell: number;
}

/** Vertex data of a terrain grid, ready for a mesh. */
export interface TerrainGeometry {
  readonly positions: Float32Array;
  readonly normals: Float32Array;
}

/**
 * Samples the ground on a grid and computes smooth normals from the neighbouring heights (one
 * extra ring of samples around the grid, so neighbouring chunks get the same normals on their
 * shared edge and the seam does not show).
 */
export function buildTerrainGeometry(source: HeightSource, grid: TerrainGrid): TerrainGeometry {
  const { xMin, zMin, columns, rows, cell } = grid;
  const width = columns + 3;
  const heights = new Float32Array(width * (rows + 3));
  for (let r = -1; r <= rows + 1; r++) {
    for (let c = -1; c <= columns + 1; c++) {
      heights[(r + 1) * width + c + 1] = source.height(xMin + c * cell, zMin + r * cell);
    }
  }
  const at = (c: number, r: number): number => heights[(r + 1) * width + c + 1] ?? 0;
  const count = (columns + 1) * (rows + 1);
  const positions = new Float32Array(count * 3);
  const normals = new Float32Array(count * 3);
  let v = 0;
  for (let r = 0; r <= rows; r++) {
    for (let c = 0; c <= columns; c++) {
      const nx = at(c - 1, r) - at(c + 1, r);
      const nz = at(c, r - 1) - at(c, r + 1);
      const ny = 2 * cell;
      const length = Math.hypot(nx, ny, nz);
      positions.set([xMin + c * cell, at(c, r), zMin + r * cell], v);
      normals.set([nx / length, ny / length, nz / length], v);
      v += 3;
    }
  }
  return { positions, normals };
}

/** Triangle indices of a `columns × rows` grid (row-major vertices), front faces up. */
export function buildGridIndices(columns: number, rows: number): Uint32Array {
  const indices = new Uint32Array(columns * rows * 6);
  let i = 0;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < columns; c++) {
      const a = r * (columns + 1) + c;
      const b = a + columns + 1;
      // Babylon front faces have the normal (c - a) × (b - a): here +Y.
      indices.set([a, a + 1, b, a + 1, b + 1, b], i);
      i += 6;
    }
  }
  return indices;
}
