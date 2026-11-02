# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/ship_materials.py` (GFX-SHIP-04)."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view import ship_materials


@pytest.fixture
def materials(monkeypatch: Any) -> Any:
    stub_babylon(monkeypatch, ship_materials)
    return ship_materials._create_ship_materials(MagicMock(name="scene"))


def test_the_ship_materials_are_one_set_of_metal_light_and_glow(materials: Any) -> None:
    names = [name for name in vars(materials) if not name.startswith("_")]
    assert names


def test_gfx_ship_04_a_scene_keeps_its_ship_materials(monkeypatch: Any) -> None:
    stub_babylon(monkeypatch, ship_materials)
    scene = MagicMock(name="scene")
    # Under CPython the cache is empty (`_cached_materials` is JavaScript): they are made.
    made = ship_materials.get_ship_materials(scene)
    assert isinstance(made, ship_materials.ShipMaterials)
    monkeypatch.setattr(ship_materials, "_cached_materials", lambda _scene: made)
    assert ship_materials.get_ship_materials(scene) is made
