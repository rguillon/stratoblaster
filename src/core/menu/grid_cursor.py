"""Moves a selection index in a grid of entries, ported from `core/menu/grid-cursor.ts`."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Literal  # noqa: E402

CursorDirection = Literal["up", "down", "left", "right"]

__pragma__("noskip")

import math  # noqa: E402


class GridShape:
    """Layout of selectable entries, filled row by row."""

    def __init__(self, count: int, columns: int, wrap: bool) -> None:
        """`count` is the number of entries; `columns` the entries per row; `wrap`: when true,
        moving past an edge comes back on the other side of the row or column.
        """
        self.count = count
        self.columns = columns
        self.wrap = wrap


def _step(value: int, delta: int, size: int, wrap: bool) -> int:
    nxt = value + delta
    if wrap:
        return (nxt + size) % size
    return min(size - 1, max(0, nxt))


def move_cursor(index: int, direction: CursorDirection, shape: GridShape) -> int:
    """Moves a selection index in a grid of entries. A move that would land on a missing entry
    (short last row) leaves the selection where it is.
    """
    if shape.count <= 0:
        return 0
    if shape.columns <= 0:
        raise ValueError("A grid with entries needs at least one column")
    rows = math.ceil(shape.count / shape.columns)
    row = math.floor(index / shape.columns)
    column = index % shape.columns
    row_length = min(shape.columns, shape.count - row * shape.columns)
    if direction in ["left", "right"]:
        delta = -1 if direction == "left" else 1
        target = row * shape.columns + _step(column, delta, row_length, shape.wrap)
    else:
        delta = -1 if direction == "up" else 1
        target = _step(row, delta, rows, shape.wrap) * shape.columns + column
    return target if target < shape.count else index
