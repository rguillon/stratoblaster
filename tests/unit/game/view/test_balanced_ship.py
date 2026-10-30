"""Unit tests of `src/game/view/balanced_ship.py`."""

from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view import balanced_ship
from game.view.balanced_ship import build_balanced_ship


@pytest.fixture
def scene(monkeypatch):
    stub_babylon(monkeypatch, balanced_ship)
    monkeypatch.setattr(
        balanced_ship, "get_ship_materials", lambda scene: MagicMock(name="materials")
    )
    return MagicMock(name="scene")


def test_the_balanced_ship_is_built_under_a_root_node(scene):
    assert build_balanced_ship(scene) is not None
