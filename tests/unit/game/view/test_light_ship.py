"""Unit tests of `src/game/view/light_ship.py`."""

from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view import light_ship
from game.view.light_ship import _light_wings, build_light_ship


@pytest.fixture
def scene(monkeypatch):
    stub_babylon(monkeypatch, light_ship)
    monkeypatch.setattr(light_ship, "get_ship_materials", lambda scene: MagicMock(name="materials"))
    return MagicMock(name="scene")


def test_the_light_ship_has_a_front_and_a_rear_wing_on_each_side():
    wings = _light_wings()
    assert len(wings) == 4
    assert sorted((w["pair"], w["side"]) for w in wings) == [
        ("front", -1),
        ("front", 1),
        ("rear", -1),
        ("rear", 1),
    ]


def test_the_light_ship_is_built_under_a_root_node(scene):
    root = build_light_ship(scene)
    assert root is not None
