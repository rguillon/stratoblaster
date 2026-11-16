# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/mesh_merge.py`: its work is JavaScript, checked in the browser."""

from types import SimpleNamespace

from render.mesh_merge import keep_apart, merge_rigid_meshes, merge_still_meshes


def test_the_javascript_helpers_do_nothing_in_cpython() -> None:
    node = SimpleNamespace()
    assert keep_apart(node) is None
    assert merge_still_meshes(node) == 0
    assert merge_rigid_meshes(node) == 0
