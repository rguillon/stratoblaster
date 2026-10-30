"""Unit tests of `src/core/content/level_catalog.py`."""

import pytest

from core.content.level_catalog import (
    LevelCatalog,
    LevelEntry,
    build_level_grid,
    first_unlocked_level,
)


def test_level_entry_keeps_its_fields() -> None:
    entry = LevelEntry("2-3", "2-3", 2, 3, False)
    assert (entry.id, entry.label, entry.world, entry.level, entry.unlocked) == (
        "2-3",
        "2-3",
        2,
        3,
        False,
    )


def test_level_catalog_keeps_its_columns_and_levels() -> None:
    catalog = LevelCatalog(4, [])
    assert catalog.columns == 4
    assert catalog.levels == []


def test_grid_has_one_row_per_world() -> None:
    catalog = build_level_grid(2, 3, [])
    assert catalog.columns == 3
    assert [entry.id for entry in catalog.levels] == [
        "1-1",
        "1-2",
        "1-3",
        "2-1",
        "2-2",
        "2-3",
    ]


def test_grid_entries_know_their_world_and_level() -> None:
    entry = build_level_grid(2, 3, []).levels[4]
    assert (entry.world, entry.level, entry.label) == (2, 2, "2-2")


def test_grid_unlocks_only_the_listed_levels() -> None:
    catalog = build_level_grid(2, 2, ["1-1", "2-2"])
    assert [entry.unlocked for entry in catalog.levels] == [True, False, False, True]


@pytest.mark.parametrize(
    ("worlds", "levels"), [(1.5, 2), (2, 2.5), (float("nan"), 2), (2, float("inf"))]
)
def test_grid_sizes_must_be_integers(worlds: float, levels: float) -> None:
    with pytest.raises(ValueError, match="integers"):
        build_level_grid(worlds, levels, [])


@pytest.mark.parametrize(("worlds", "levels"), [(0, 2), (2, 0), (-1, 2)])
def test_grid_needs_at_least_one_level(worlds: int, levels: int) -> None:
    with pytest.raises(ValueError, match="one level"):
        build_level_grid(worlds, levels, [])


def test_first_unlocked_level_is_the_first_unlocked_index() -> None:
    catalog = build_level_grid(2, 2, ["2-1", "1-2"])
    assert first_unlocked_level(catalog) == 1


def test_first_unlocked_level_is_zero_when_all_are_locked() -> None:
    assert first_unlocked_level(build_level_grid(1, 3, [])) == 0


def test_a_grid_takes_whole_numbers_given_as_floats() -> None:
    """Transcrypt's numbers are all floats: a whole number given as one builds the same grid."""
    catalog = build_level_grid(2.0, 1.0, [])
    assert [entry.id for entry in catalog.levels] == ["1-1", "2-1"]
