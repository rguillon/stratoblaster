"""Unit tests of `src/core/menu/grid_cursor.py`."""

import pytest

from core.menu.grid_cursor import GridShape, move_cursor

SHAPE = GridShape(count=7, columns=3, wrap=False)

WRAP = GridShape(count=7, columns=3, wrap=True)


@pytest.mark.parametrize(
    ("index", "direction", "expected"),
    [
        (0, "right", 1),
        (1, "left", 0),
        (0, "left", 0),  # Clamped at the left edge.
        (2, "right", 2),  # Clamped at the right edge of a full row.
        (0, "down", 3),
        (3, "down", 6),
        (4, "down", 4),  # Row 2 has no entry in column 1: stays.
        (4, "up", 1),
        (0, "up", 0),  # Clamped at the top.
    ],
)
def test_moves_without_wrapping(index: int, direction: str, expected: int) -> None:
    assert move_cursor(index, direction, SHAPE) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("index", "direction", "expected"),
    [
        (2, "right", 0),
        (0, "left", 2),
        (6, "right", 6),  # The short last row has one entry: it wraps onto itself.
        (6, "down", 0),
        (0, "up", 6),
        (1, "up", 1),  # Wraps to row 2 column 1, which is missing: stays.
    ],
)
def test_p01_r01_moves_wrap_around_when_asked(index: int, direction: str, expected: int) -> None:
    assert move_cursor(index, direction, WRAP) == expected  # type: ignore[arg-type]


def test_a_single_column_wraps_vertically() -> None:
    column = GridShape(count=3, columns=1, wrap=True)
    assert move_cursor(2, "down", column) == 0
    assert move_cursor(0, "up", column) == 2


def test_an_empty_grid_stays_at_zero() -> None:
    assert move_cursor(0, "down", GridShape(count=0, columns=3, wrap=True)) == 0


def test_a_grid_with_entries_needs_a_column() -> None:
    with pytest.raises(ValueError, match="at least one column"):
        move_cursor(0, "right", GridShape(count=3, columns=0, wrap=False))
