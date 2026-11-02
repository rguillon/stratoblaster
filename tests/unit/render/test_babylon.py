# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/babylon.py`: the one module that touches the Babylon.js global.

Most of its helpers are raw JavaScript (ENG-158): CPython runs only their placeholder Python return,
so `test_eng_158_...` calls each one and checks that placeholder. The helpers that do their work in
Python are tested on fakes.
"""

import inspect
import re
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from render import babylon
from render.babylon import (
    apply_vertex_data,
    bake_transform,
    dispose_node,
    draw_calls_last_frame,
    is_enabled,
    scene_unique_id,
    set_enabled,
    update_vertices_data,
    vertex_data_of,
    weak_map_set,
)

# The placeholder each JavaScript-only helper returns under CPython: None unless listed here.
_PLACEHOLDERS: dict[str, Any] = {
    "node_name": "",
    "child_meshes": [],
    "descendants": [],
    "scene_meshes": [],
    "scene_transform_nodes": [],
    "compute_normals": [],
    "mesh_positions": [],
    "mesh_indices": [],
    "world_matrix": [],
    "unique_id": 0,
    "vector3_dot": 0,
    "render_painter_sort_compare": 0,
    "number_max_value": 0,
    "block_material_marks": False,
    "is_raw_cube_texture": False,
    "is_instance_of": False,
}

_JS_BODY = re.compile(r'__pragma__\(\s*"js"')


def _js_helpers() -> list[Callable[..., Any]]:
    """Return the functions of `render.babylon` whose body is raw JavaScript, in source order."""
    found = []
    for _name, value in inspect.getmembers(babylon, inspect.isfunction):
        if value.__module__ == babylon.__name__ and _JS_BODY.search(inspect.getsource(value)):
            found.append(value)
    return sorted(found, key=lambda f: f.__code__.co_firstlineno)


class _Node:
    def __init__(self) -> None:
        self.enabled = True
        self.disposed = False

    def setEnabled(self, on: bool) -> None:
        self.enabled = on

    def isEnabled(self) -> int:
        return 1 if self.enabled else 0

    def dispose(self) -> None:
        self.disposed = True


def test_a_node_is_enabled_or_disabled_through_babylon() -> None:
    node = _Node()
    set_enabled(node, False)
    assert node.enabled is False
    assert is_enabled(node) is False
    set_enabled(node, True)
    assert is_enabled(node) is True


def test_a_node_is_disposed_through_babylon() -> None:
    node = _Node()
    dispose_node(node)
    assert node.disposed is True


def test_the_scene_counter_is_a_number() -> None:
    scene = SimpleNamespace(getUniqueId=lambda: 7)
    assert scene_unique_id(scene) == pytest.approx(7)
    assert isinstance(scene_unique_id(scene), float)


def test_eng_158_the_placeholders_listed_are_those_of_javascript_helpers() -> None:
    names = [helper.__name__ for helper in _js_helpers()]
    # Every helper listed with a placeholder is raw JavaScript, and there are many more.
    assert set(_PLACEHOLDERS) <= set(names)
    assert len(names) > 80


@pytest.mark.parametrize("helper", _js_helpers(), ids=lambda helper: helper.__name__)
def test_eng_158_a_javascript_helper_returns_its_placeholder_under_cpython(
    helper: Callable[..., Any],
) -> None:
    """CPython skips the raw JavaScript and runs only the placeholder return after it."""
    arguments = [object() for _ in inspect.signature(helper).parameters]
    result = helper(*arguments)
    expected = _PLACEHOLDERS.get(helper.__name__)
    assert result == expected
    assert type(result) is type(expected)


def test_eng_158_a_list_placeholder_is_a_fresh_list_each_call() -> None:
    # Callers may push into what `child_meshes` and `compute_normals` give them.
    assert babylon.child_meshes(object(), False) is not babylon.child_meshes(object(), False)
    assert babylon.compute_normals([], []) is not babylon.compute_normals([], [])


def test_eng_106_the_draw_calls_of_the_last_frame_are_the_counter_s_count() -> None:
    calls = draw_calls_last_frame(SimpleNamespace(count=42))
    assert calls == pytest.approx(42)
    assert isinstance(calls, float)


def test_vertex_data_gets_the_arrays_given_and_not_the_ones_left_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(babylon, "new_vertex_data", SimpleNamespace)
    positions = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    indices = [0, 1, 2]
    bare = vertex_data_of(positions, indices)
    assert (bare.positions, bare.indices) == (positions, indices)
    assert not hasattr(bare, "normals")
    assert not hasattr(bare, "colors")
    assert not hasattr(bare, "uvs")
    normals = [0.0, 0.0, -1.0] * 3
    colors = [1.0, 1.0, 1.0, 1.0] * 3
    uvs = [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    full = vertex_data_of(positions, indices, normals, colors, uvs)
    assert (full.normals, full.colors, full.uvs) == (normals, colors, uvs)


def test_python_wrappers_call_the_babylon_method_they_stand_for() -> None:
    data = MagicMock()
    mesh = MagicMock()
    apply_vertex_data(data, mesh)
    data.applyToMesh.assert_called_once_with(mesh)
    bake_transform(mesh)
    mesh.bakeCurrentTransformIntoVertices.assert_called_once_with()
    update_vertices_data(mesh, "position", [1.0, 2.0, 3.0])
    mesh.updateVerticesData.assert_called_once_with("position", [1.0, 2.0, 3.0])
    weak_map = MagicMock()
    key = object()
    weak_map_set(weak_map, key, "value")
    weak_map.set.assert_called_once_with(key, "value")
