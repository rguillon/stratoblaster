# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/ship_parts.py`."""

from typing import Any
from unittest.mock import MagicMock

from helpers.babylon_stub import stub_babylon

from game.view import ship_parts
from game.view.ship_parts import mirror_x


def test_a_planform_mirrors_across_the_centre_line() -> None:
    outline = [[1.0, 2.0], [3.0, -4.0]]
    assert mirror_x(outline) == [[-1.0, 2.0], [-3.0, -4.0]]
    assert mirror_x(mirror_x(outline)) == outline


def test_a_panel_is_a_prism_with_its_material_on_its_parent(monkeypatch: Any) -> None:
    stub_babylon(monkeypatch, ship_parts)
    prism = MagicMock(name="prism")
    monkeypatch.setattr(
        ship_parts, "create_prism", lambda _name, _outline, _thickness, _scene: prism
    )
    parent = MagicMock(name="parent")
    material = MagicMock(name="material")
    mesh = ship_parts.panel("wing-left", [[0, 0], [1, 0], [1, 1]], 0.1, material, parent)
    assert mesh is prism
    assert mesh.material is material
    assert mesh.parent is parent


def test_a_plate_lies_above_its_parent_by_its_offset(monkeypatch: Any) -> None:
    stub_babylon(monkeypatch, ship_parts)
    prism = MagicMock(name="prism")
    monkeypatch.setattr(
        ship_parts, "create_prism", lambda _name, _outline, _thickness, _scene: prism
    )
    mesh = ship_parts.plate("trim", [[0, 0], [1, 0], [1, 1]], 0.05, MagicMock(), MagicMock())
    assert mesh.position.y == 0.05
