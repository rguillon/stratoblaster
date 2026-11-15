# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/glow_marks.py` (D-428)."""

from types import SimpleNamespace
from typing import Any

import pytest

from render import glow_marks


@pytest.fixture(autouse=True)
def plain_metadata(monkeypatch: Any) -> None:
    """Make the metadata helpers, which are JavaScript, work on plain dicts."""
    monkeypatch.setattr(
        glow_marks, "object_with_field", lambda old, key, value: {**(old or {}), key: value}
    )
    monkeypatch.setattr(
        glow_marks, "metadata_field", lambda metadata, key: (metadata or {}).get(key)
    )


def test_d428_a_marked_mesh_glows_as_drawn_and_keeps_its_metadata() -> None:
    mesh = SimpleNamespace(metadata={"trim": [1, 0, 0]})
    assert glow_marks.glows_as_drawn(mesh) is False
    glow_marks.mark_glows_as_drawn(mesh)
    assert glow_marks.glows_as_drawn(mesh) is True
    assert mesh.metadata["trim"] == [1, 0, 0]


def test_d428_a_mesh_without_metadata_is_not_marked() -> None:
    assert glow_marks.glows_as_drawn(SimpleNamespace(metadata=None)) is False
