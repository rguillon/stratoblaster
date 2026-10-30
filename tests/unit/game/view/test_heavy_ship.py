"""Unit tests of `src/game/view/heavy_ship.py`."""

from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view import heavy_ship
from game.view.heavy_ship import _for_side, _heavy_planform, build_heavy_ship


@pytest.fixture
def scene(monkeypatch):
    stub_babylon(monkeypatch, heavy_ship)
    monkeypatch.setattr(heavy_ship, "get_ship_materials", lambda scene: MagicMock(name="materials"))
    return MagicMock(name="scene")


def test_the_heavy_planform_is_a_closed_outline():
    outline = _heavy_planform()
    assert len(outline) >= 3
    assert all(len(point) == 2 for point in outline)


def test_each_side_of_the_heavy_planform_mirrors_the_other():
    outline = _heavy_planform()
    right = _for_side(1, outline)
    left = _for_side(-1, outline)
    assert left == [[-x, y] for x, y in right]


def test_the_heavy_ship_is_built_under_a_root_node(scene):
    assert build_heavy_ship(scene) is not None
