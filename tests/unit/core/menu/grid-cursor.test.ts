import { describe, expect, it } from 'vitest';
import { moveCursor, type GridShape } from '../../../../src/core/menu/grid-cursor';

const ROW: GridShape = { count: 3, columns: 3, wrap: true };
const GRID: GridShape = { count: 25, columns: 5, wrap: false };

describe('moveCursor', () => {
  it('P01-R06: moves along a wrapping row, wrapping around at both ends', () => {
    expect(moveCursor(0, 'right', ROW)).toBe(1);
    expect(moveCursor(2, 'right', ROW)).toBe(0);
    expect(moveCursor(0, 'left', ROW)).toBe(2);
    expect(moveCursor(1, 'up', ROW)).toBe(1);
    expect(moveCursor(1, 'down', ROW)).toBe(1);
  });

  it('P01-R07: moves in a grid with the arrows and stops at the edges', () => {
    expect(moveCursor(0, 'right', GRID)).toBe(1);
    expect(moveCursor(0, 'down', GRID)).toBe(5);
    expect(moveCursor(6, 'up', GRID)).toBe(1);
    expect(moveCursor(6, 'left', GRID)).toBe(5);
    expect(moveCursor(0, 'left', GRID)).toBe(0);
    expect(moveCursor(0, 'up', GRID)).toBe(0);
    expect(moveCursor(4, 'right', GRID)).toBe(4);
    expect(moveCursor(24, 'down', GRID)).toBe(24);
  });

  it('wraps rows and columns in a wrapping grid', () => {
    const shape: GridShape = { count: 6, columns: 3, wrap: true };
    expect(moveCursor(0, 'up', shape)).toBe(3);
    expect(moveCursor(3, 'down', shape)).toBe(0);
    expect(moveCursor(5, 'right', shape)).toBe(3);
  });

  it('stays put rather than landing on a missing entry of a short last row', () => {
    const shape: GridShape = { count: 4, columns: 3, wrap: false };
    expect(moveCursor(2, 'down', shape)).toBe(2);
    expect(moveCursor(1, 'down', shape)).toBe(1);
    expect(moveCursor(0, 'down', shape)).toBe(3);
    expect(moveCursor(3, 'right', shape)).toBe(3);
  });

  it('returns 0 for an empty grid', () => {
    expect(moveCursor(3, 'right', { count: 0, columns: 3, wrap: true })).toBe(0);
  });
});
