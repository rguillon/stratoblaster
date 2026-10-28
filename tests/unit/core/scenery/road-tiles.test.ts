import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import { roadPieces } from '../../../../src/core/scenery/road-tiles';
import { columnFits } from '../../../../src/core/scenery/tile-streets';

// Phase 15: the road pieces found from the streets on a grid of tiles.

const TILE = { size: 10, sidewalk: 2 };

describe('road pieces (phase 15)', () => {
  const street = (points: { x: number; z: number }[], lanes: 1 | 2 | 3 | 4, index = 0): Road => ({
    index,
    kind: 'street',
    width: lanes * TILE.size,
    lanes,
    points: points.map((p) => ({ ...p, width: lanes * TILE.size })),
  });

  it('P15-R03: two one-tile streets crossing make an X between straights', () => {
    const pieces = roadPieces(
      [
        street(
          [
            { x: -45, z: 5 },
            { x: 45, z: 5 },
          ],
          1,
        ),
        street(
          [
            { x: 5, z: -45 },
            { x: 5, z: 45 },
          ],
          1,
          1,
        ),
      ],
      TILE,
    );
    const cross = pieces.filter((p) => p.kind === 'cross');
    expect(cross).toHaveLength(1);
    expect(cross[0]).toMatchObject({ x: 0, z: 0, size: 1, adapter: false });
    expect(pieces.filter((p) => p.kind === 'straight').length).toBeGreaterThan(10);
  });

  it('P15-R04: a one-tile street crossing a 3-tile boulevard enters its adapter in the middle', () => {
    // The boulevard covers tiles 0..2 along Z (middle at 15); the street, tile 4 along X.
    const pieces = roadPieces(
      [
        street(
          [
            { x: -95, z: 15 },
            { x: 95, z: 15 },
          ],
          3,
        ),
        street(
          [
            { x: 45, z: -45 },
            { x: 45, z: 75 },
          ],
          1,
          1,
        ),
      ],
      TILE,
    );
    const adapter = pieces.find((p) => p.adapter);
    expect(adapter).toMatchObject({ x: 3, z: 0, size: 3, kind: 'cross' });
    expect(adapter?.sides[0]).toEqual({ size: 1, offset: 1 });
    expect(adapter?.sides[1]).toEqual({ size: 3, offset: 0 });
    // The boulevard's straights are 3 × 3, on its lattice.
    for (const p of pieces.filter((q) => q.size === 3 && q.kind === 'straight')) {
      expect(p.x % 3).toBe(0);
    }
  });

  it('P15-R04: a street ending on a wider road is a T adapter; two ending together a turn', () => {
    const tee = roadPieces(
      [
        street(
          [
            { x: -95, z: 10 },
            { x: 95, z: 10 },
          ],
          2,
        ),
        street(
          [
            { x: 5, z: 10 },
            { x: 5, z: 75 },
          ],
          1,
          1,
        ),
      ],
      TILE,
    ).find((p) => p.adapter);
    expect(tee?.kind).toBe('tee');
    const turn = roadPieces(
      [
        street(
          [
            { x: 5, z: 5 },
            { x: 95, z: 5 },
          ],
          1,
        ),
        street(
          [
            { x: 5, z: 5 },
            { x: 5, z: 95 },
          ],
          1,
          1,
        ),
      ],
      TILE,
    ).find((p) => p.kind === 'turn');
    expect(turn).toMatchObject({ x: 0, z: 0, size: 1 });
  });

  it('P15-R04: a column fits a row of N tiles when its junction starts on the row lattice', () => {
    expect([0, 1, 2, 3].filter((s) => columnFits(s, 3))).toEqual([1]);
    expect([0, 1, 2, 3].filter((s) => columnFits(s, 4))).toEqual([1, 2]);
    expect([0, 1].filter((s) => columnFits(s, 2))).toEqual([0, 1]);
  });
});
