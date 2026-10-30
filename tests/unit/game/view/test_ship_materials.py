"""Unit tests of `src/game/view/ship_materials.py`."""

from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view import ship_materials


@pytest.fixture
def materials(monkeypatch):
    stub_babylon(monkeypatch, ship_materials)
    return ship_materials._create_ship_materials(MagicMock(name="scene"))


def test_the_ship_materials_are_one_set_of_metal_light_and_glow(materials):
    names = [name for name in vars(materials) if not name.startswith("_")]
    assert names
