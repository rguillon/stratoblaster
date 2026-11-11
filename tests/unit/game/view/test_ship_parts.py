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


def test_gfx_ship_09_an_edge_strip_lies_across_the_edge_half_out_past_it(monkeypatch: Any) -> None:
    """D-335: the glowing strip caps the edge, half on the panel, half out away from it."""
    stub_babylon(monkeypatch, ship_parts)
    made: list[Any] = []

    def fake_prism(_name: str, outline: Any, thickness: float, _scene: Any) -> Any:
        made.append((outline, thickness))
        return MagicMock(name="prism")

    monkeypatch.setattr(ship_parts, "create_prism", fake_prism)
    size = {"width": 0.2, "thickness": 0.08}
    # An edge along X at z = 1, the panel behind it (z < 1).
    ship_parts.edge_strip("glow", [[0, 1], [2, 1]], [1, 0], size, MagicMock(), MagicMock())
    outline, thickness = made[0]
    assert thickness == 0.08
    zs = sorted({round(p[1], 9) for p in outline})
    assert zs == [0.9, 1.1]
    assert sorted({p[0] for p in outline}) == [0, 2]


def test_gfx_ship_01_an_intake_runs_straight_then_angles_in_to_its_lip() -> None:
    """D-337: the skin starts straight from the nacelle, then narrows to the lip."""
    intake = ship_parts.REACTOR_INTAKE
    lip = max(range(len(intake)), key=lambda k: intake[k][0])
    straight = [p for p in intake[:lip] if p[0] >= 0]
    assert straight[0][1] == straight[1][1]
    assert intake[lip][1] < straight[-1][1]
    radii = [p[1] for p in intake[1 : lip + 1]]
    assert radii == sorted(radii, reverse=True)


def test_gfx_ship_01_an_intake_has_a_lined_duct_blades_and_a_spinner(monkeypatch: Any) -> None:
    """D-337: the duct lining is turned to face the axis; the fan has its blades."""
    stub_babylon(monkeypatch, ship_parts)
    meshes: dict[str, Any] = {}

    def loft(name: str, *_args: Any) -> Any:
        meshes[name] = MagicMock(name=name)
        return meshes[name]

    monkeypatch.setattr(ship_parts, "create_section_loft", loft)
    blades: list[str] = []
    monkeypatch.setattr(
        ship_parts, "panel", lambda name, *_args: blades.append(name) or MagicMock(name=name)
    )
    ship_parts._add_reactor_intake("r", 0.2, 1.0, MagicMock(name="root"))
    meshes["r-intake-duct"].flipFaces.assert_called_once_with(True)
    assert len(blades) == ship_parts.REACTOR_INTAKE_BLADES["count"]
