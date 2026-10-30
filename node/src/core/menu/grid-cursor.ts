/** A direction the selection can move in. */
export type CursorDirection = 'up' | 'down' | 'left' | 'right';

/** Layout of selectable entries, filled row by row. */
export interface GridShape {
  /** Number of entries. */
  readonly count: number;
  /** Entries per row. */
  readonly columns: number;
  /** When true, moving past an edge comes back on the other side of the row or column. */
  readonly wrap: boolean;
}

function step(value: number, delta: number, size: number, wrap: boolean): number {
  const next = value + delta;
  if (wrap) return (next + size) % size;
  return Math.min(size - 1, Math.max(0, next));
}

/**
 * Moves a selection index in a grid of entries. A move that would land on a missing
 * entry (short last row) leaves the selection where it is.
 */
export function moveCursor(index: number, direction: CursorDirection, shape: GridShape): number {
  if (shape.count <= 0) return 0;
  const rows = Math.ceil(shape.count / shape.columns);
  const row = Math.floor(index / shape.columns);
  const column = index % shape.columns;
  const rowLength = Math.min(shape.columns, shape.count - row * shape.columns);
  let target: number;
  switch (direction) {
    case 'left':
    case 'right':
      target =
        row * shape.columns + step(column, direction === 'left' ? -1 : 1, rowLength, shape.wrap);
      break;
    case 'up':
    case 'down':
      target = step(row, direction === 'up' ? -1 : 1, rows, shape.wrap) * shape.columns + column;
      break;
  }
  return target < shape.count ? target : index;
}
