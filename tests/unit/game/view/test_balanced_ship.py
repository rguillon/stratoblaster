# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/balanced_ship.py` (GFX-SHIP-01)."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view import balanced_ship
from game.view.balanced_hull import TOP_POINTS, hull_sections
from game.view.balanced_ship import build_balanced_ship
from game.view.ship_parts import SMOOTH_PART_SECTION
from render.geometry.lathe_z import build_smooth_top_lathe_vertex_data, smooth_profile
from render.geometry.section_loft import build_section_loft


@pytest.fixture
def scene(monkeypatch: Any) -> Any:
    stub_babylon(monkeypatch, balanced_ship)
    monkeypatch.setattr(
        balanced_ship, "get_ship_materials", lambda _scene: MagicMock(name="materials")
    )
    return MagicMock(name="scene")


def test_the_balanced_ship_is_built_under_a_root_node(scene: Any) -> None:
    assert build_balanced_ship(scene) is not None


def _upper_share(profile: list[list[float]], halves: Any) -> float:
    """Share of the lathe's triangles whose centre lies over the upper half (Y >= 0)."""
    positions, indices, _normals = build_smooth_top_lathe_vertex_data(profile, halves)
    upper = 0
    for t in range(0, len(indices), 3):
        y = sum(positions[indices[t + k] * 3 + 1] for k in range(3))
        upper += 1 if y >= 0 else 0
    return upper / (len(indices) / 3)


@pytest.mark.parametrize(
    ("profile", "halves"),
    [
        (
            smooth_profile(balanced_ship.CANOPY, balanced_ship.PROFILE_STEPS),
            balanced_ship.CANOPY_SECTION,
        ),
        (balanced_ship.INTAKE, SMOOTH_PART_SECTION),
    ],
)
def test_gfx_ship_05_the_round_parts_put_their_triangles_on_the_upper_half(
    profile: list[list[float]], halves: Any
) -> None:
    """D-327: at least three quarters of each round part's triangles are over the upper half."""
    assert _upper_share(profile, halves) >= 0.75


def test_gfx_ship_05_the_hull_puts_its_triangles_on_the_upper_half() -> None:
    """D-327: at least three quarters of the blended hull's triangles are over the upper half."""
    positions, indices, _normals = build_section_loft(hull_sections(), TOP_POINTS)
    upper = 0
    for t in range(0, len(indices), 3):
        y = sum(positions[indices[t + k] * 3 + 1] for k in range(3))
        upper += 1 if y >= 0 else 0
    assert upper / (len(indices) / 3) >= 0.75
