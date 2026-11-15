# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/ship_parts.py`."""

import itertools
import math
from typing import Any
from unittest.mock import MagicMock

import pytest
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
    # The panel ahead of it (z > 1): the strip still across the edge, half out past it.
    ship_parts.edge_strip("glow", [[0, 1], [2, 1]], [1, 2], size, MagicMock(), MagicMock())
    outline, _thickness = made[1]
    assert sorted({round(p[1], 9) for p in outline}) == [0.9, 1.1]


def test_gfx_ship_01_an_intake_runs_straight_then_angles_in_to_its_lip() -> None:
    """D-337: the skin starts straight from the nacelle, then narrows to the lip."""
    intake = ship_parts.REACTOR_INTAKE
    lip = max(range(len(intake)), key=lambda k: intake[k][0])
    straight = [p for p in intake[:lip] if p[0] >= 0]
    assert straight[0][1] == straight[1][1]
    assert intake[lip][1] < straight[-1][1]
    radii = [p[1] for p in intake[1 : lip + 1]]
    assert radii == sorted(radii, reverse=True)


def test_gfx_ship_01_an_intake_has_a_lined_duct_and_horizontal_fins(monkeypatch: Any) -> None:
    """D-337, D-338: the duct lining faces the axis; flat fins span it, no fan blades or spinner."""
    stub_babylon(monkeypatch, ship_parts)
    meshes: dict[str, Any] = {}

    def loft(name: str, *_args: Any) -> Any:
        meshes[name] = MagicMock(name=name)
        return meshes[name]

    monkeypatch.setattr(ship_parts, "create_section_loft", loft)
    fins: dict[str, Any] = {}

    def panel(name: str, outline: list[list[float]], *_args: Any) -> Any:
        fins[name] = outline
        return MagicMock(name=name)

    monkeypatch.setattr(ship_parts, "panel", panel)
    lathes: list[str] = []
    monkeypatch.setattr(
        ship_parts,
        "create_faceted_lathe_along_z",
        lambda name, *_args: lathes.append(name) or MagicMock(name=name),
    )
    ship_parts.add_reactor_intake("r", 0.2, 1.0, MagicMock(name="root"))
    meshes["r-intake-duct"].flipFaces.assert_called_once_with(True)
    assert lathes == []
    room = ship_parts.REACTOR_INTAKE_FINS["room"] * math.sqrt(3) / 2 * 0.2
    heights = ship_parts.intake_fin_heights(room)
    assert len(fins) == len(heights)
    for k, height in enumerate(heights):
        outline = fins["r-intake-fin-" + str(k)]
        half = max(p[0] for p in outline)
        assert half == pytest.approx(ship_parts.intake_fin_half_width(height / 0.2) * 0.2)
        assert min(p[0] for p in outline) == pytest.approx(-half)
        # D-351: the ends lie in the ring's wall: out of the duct's lining, inside the lip's skin.
        y = abs(height) / 0.2
        assert half > 0.2 * (ship_parts.REACTOR_INTAKE_DUCT[0][1] - y / math.sqrt(3))
        assert half < 0.2 * (0.86 - y / math.sqrt(3))


def test_gfx_ship_01_the_intake_ducts_end_lies_behind_its_fan_face() -> None:
    """D-341: the duct's end cap and the fan face are not in one plane (they fought for depth)."""
    duct_end = min(z for z, _r in ship_parts.REACTOR_INTAKE_DUCT)
    assert duct_end < ship_parts.REACTOR_INTAKE_FAN["z"] - 0.03


@pytest.mark.parametrize("stretch", [1.0, 1.3, 2.05])
def test_gfx_ship_01_every_intakes_fins_have_one_size_whatever_the_stretch(
    monkeypatch: Any, stretch: float
) -> None:
    """D-350: the fins are as thick and deep in any intake; only their width varies."""
    thicknesses: list[float] = []
    depths: list[float] = []

    def panel(name: str, outline: Any, thickness: float, *_args: Any) -> Any:
        if "-fin-" in name:
            thicknesses.append(thickness * stretch)
            depths.append(max(p[1] for p in outline) - min(p[1] for p in outline))
        return MagicMock(name=name)

    stub_babylon(monkeypatch, ship_parts)
    monkeypatch.setattr(ship_parts, "get_ship_materials", lambda _scene: MagicMock())
    monkeypatch.setattr(ship_parts, "create_section_loft", lambda name, *_a: MagicMock(name=name))
    monkeypatch.setattr(ship_parts, "panel", panel)
    ship_parts.add_reactor_intake("r", 0.124, 0.0, MagicMock(name="root"), 8, stretch)
    size = ship_parts.INTAKE_FIN_SIZE
    count = len(thicknesses)
    assert count >= 3
    assert thicknesses == pytest.approx([size["thickness"]] * count)
    assert depths == pytest.approx([size["depth"]] * count)
    # D-396: the depth stays ahead of the smallest intake's fan face (the tip's, 0.15, D-404).
    front = ship_parts.REACTOR_INTAKE_FINS["front"] * 0.15
    assert front - size["depth"] > ship_parts.REACTOR_INTAKE_FAN["z"] * 0.15


def test_gfx_ship_01_the_fins_stand_one_spacing_apart_round_the_middle() -> None:
    """D-351: one in the middle, the same spacing in every intake, as many as the room holds."""
    size = ship_parts.INTAKE_FIN_SIZE
    heights = ship_parts.intake_fin_heights(0.1876)
    assert len(heights) == 9
    assert heights[len(heights) // 2] == 0
    gaps = {round(b - a, 9) for a, b in itertools.pairwise(heights)}
    assert gaps == {size["spacing"]}
    assert max(heights) + size["thickness"] / 2 <= 0.1876
    assert ship_parts.intake_fin_heights(0.04) == [0.0]


def test_gfx_ship_01_raked_sections_move_each_point_by_its_height_but_the_kept_back() -> None:
    """D-364: each ring point gets its own Z offset, the last `keep` sections none."""
    sections = [[1.0, [[0.0, 1.0], [0.0, -1.0]]], [0.0, [[0.0, 1.0], [0.0, -1.0]]]]
    raked = ship_parts.raked_sections(sections, lambda y: 0.5 if y > 0 else 0.0, 1)
    assert raked[0] == [1.0, [[0.0, 1.0, 0.5], [0.0, -1.0, 0.0]]]
    assert raked[1] is sections[1]
    assert ship_parts.raked_sections(sections, None, 1) is sections


def test_gfx_ship_01_a_raked_intakes_mouth_and_fins_move_its_back_stays(monkeypatch: Any) -> None:
    """D-364: the shell's and duct's fronts and the fins follow the rake; their backs do not."""
    stub_babylon(monkeypatch, ship_parts)
    monkeypatch.setattr(ship_parts, "get_ship_materials", lambda _scene: MagicMock())
    lofts: dict[str, Any] = {}

    def loft(name: str, sections: Any, *_args: Any) -> Any:
        lofts[name] = sections
        return MagicMock(name=name)

    fins: dict[str, Any] = {}

    def panel(name: str, *_args: Any) -> Any:
        fins[name] = MagicMock(name=name)
        return fins[name]

    monkeypatch.setattr(ship_parts, "create_section_loft", loft)
    monkeypatch.setattr(ship_parts, "panel", panel)

    def rake(y: float) -> float:
        return 0.1 if y > 0 else 0.0

    ship_parts.add_reactor_intake("r", 0.124, 0.0, MagicMock(name="root"), 8, 2.05, rake)
    for name in ["r-intake-shell", "r-intake-duct"]:
        front = lofts[name][0][1]
        assert {p[2] for p in front if p[1] > 0} == {0.1}
        assert {p[2] for p in front if p[1] < 0} == {0.0}
        assert all(len(p) == 2 for p in lofts[name][-1][1])
    for fin in fins.values():
        assert fin.position.z == rake(fin.position.y)
