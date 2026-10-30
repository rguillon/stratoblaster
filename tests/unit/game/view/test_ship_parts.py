"""Unit tests of `src/game/view/ship_parts.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest  # noqa: F401
from helpers.babylon_stub import stub_babylon

from game.view import ship_parts
from game.view.ship_parts import mirror_x, part_of, tag_part


@pytest.fixture(autouse=True)
def python_metadata(monkeypatch):
    """The part tag is kept as a JavaScript `metadata` object: a plain attribute here."""
    monkeypatch.setattr(
        ship_parts,
        "_set_part_metadata",
        lambda node, part: setattr(node, "metadata", SimpleNamespace(part=part)),
    )
    monkeypatch.setattr(
        ship_parts,
        "_part_of_metadata",
        lambda node: node.metadata.part if getattr(node, "metadata", None) else None,
    )


def test_a_planform_mirrors_across_the_centre_line():
    outline = [[1.0, 2.0], [3.0, -4.0]]
    assert mirror_x(outline) == [[-1.0, 2.0], [-3.0, -4.0]]
    assert mirror_x(mirror_x(outline)) == outline


def test_a_node_remembers_the_ship_part_it_was_tagged_with():
    node = MagicMock()
    assert tag_part(node, "wing") is node
    assert part_of(node) == "wing"


def test_an_untagged_node_has_no_part():
    assert part_of(SimpleNamespace()) is None


def test_a_panel_is_a_prism_with_its_material_on_its_parent(monkeypatch):
    stub_babylon(monkeypatch, ship_parts)
    prism = MagicMock(name="prism")
    monkeypatch.setattr(ship_parts, "create_prism", lambda name, outline, thickness, scene: prism)
    parent = MagicMock(name="parent")
    material = MagicMock(name="material")
    mesh = ship_parts.panel("wing-left", [[0, 0], [1, 0], [1, 1]], 0.1, material, parent)
    assert mesh is prism
    assert mesh.material is material
    assert mesh.parent is parent


def test_a_plate_lies_above_its_parent_by_its_offset(monkeypatch):
    stub_babylon(monkeypatch, ship_parts)
    prism = MagicMock(name="prism")
    monkeypatch.setattr(ship_parts, "create_prism", lambda name, outline, thickness, scene: prism)
    mesh = ship_parts.plate("trim", [[0, 0], [1, 0], [1, 1]], 0.05, MagicMock(), MagicMock())
    assert mesh.position.y == 0.05
