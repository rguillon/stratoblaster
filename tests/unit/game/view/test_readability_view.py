# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/readability_view.py`."""

import copy
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.config.readability import READABILITY
from game.view import readability_view
from game.view.readability_view import (
    KEEP,
    all_toned,
    toned,
    toned_shots,
)

LOOK = READABILITY

# The JavaScript-only helpers as the module defines them (the fixture below replaces them in every
# test), each with a value to call it on and the placeholder CPython returns.
_JS_ONLY: dict[str, tuple[Any, Any, Any]] = {
    "_is_array": (readability_view._is_array, [1, 2, 3], False),
    "_is_number_triple": (readability_view._is_number_triple, [1, 2, 3], False),
    "_is_object": (readability_view._is_object, {"a": 1}, False),
    "_entries": (readability_view._entries, {"a": 1}, []),
    "_from_entries": (readability_view._from_entries, [["a", 1]], None),
}


def _is_array(value: Any) -> Any:
    return isinstance(value, list)


def _is_number_triple(value: Any) -> Any:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(v, (int, float)) for v in value)
    )


def _is_object(value: Any) -> Any:
    return isinstance(value, dict)


@pytest.fixture(autouse=True)
def python_json_helpers(monkeypatch: Any) -> None:
    """Patch in Python versions of the JavaScript array and object helpers.

    CPython runs their fallback bodies.
    """
    monkeypatch.setattr(readability_view, "_is_array", _is_array)
    monkeypatch.setattr(readability_view, "_is_number_triple", _is_number_triple)
    monkeypatch.setattr(readability_view, "_is_object", _is_object)
    monkeypatch.setattr(readability_view, "_entries", lambda value: list(value.items()))
    monkeypatch.setattr(readability_view, "_from_entries", dict)
    monkeypatch.setattr(readability_view, "_copy_object", copy.copy)


def test_gfx_read_02_a_colour_is_darkened_by_the_tone() -> None:
    scaled = readability_view._range_scale([0.8, 0.4, 0.2], 0.5, [])
    assert scaled == pytest.approx([0.4, 0.2, 0.1])


def test_gfx_read_02_colours_under_the_skip_keys_keep_their_brightness() -> None:
    look = {"tints": [1.0, 1.0, 1.0], "ground": [0.5, 0.5, 0.5]}
    scaled = readability_view._range_scale(look, 0.5, KEEP)
    assert scaled["tints"] == [1.0, 1.0, 1.0]
    assert scaled["ground"] == pytest.approx([0.25, 0.25, 0.25])


def test_gfx_read_02_numbers_that_are_not_colours_are_left_alone() -> None:
    assert readability_view._range_scale(3.0, 0.5, []) == 3.0
    assert readability_view._range_scale("text", 0.5, []) == "text"


def test_gfx_read_02_nested_colour_lists_are_darkened_one_by_one() -> None:
    scaled = readability_view._range_scale([[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]], 0.5, [])
    assert scaled == [[0.5, 0.5, 0.5], [0.0, 0.0, 0.0]]


def test_gfx_read_02_toning_a_look_darkens_its_ground_sea_and_roads_only() -> None:
    look = SimpleNamespace(
        terrain={"a": [1.0, 1.0, 1.0]},
        sea=[0.2, 0.4, 0.6],
        roads=[1.0, 0.5, 0.0],
        props=[1.0, 1.0, 1.0],
        tone=1,
    )
    result = toned(look, 0.5)
    assert result.terrain["a"] == pytest.approx([0.5, 0.5, 0.5])
    assert result.sea == pytest.approx([0.1, 0.2, 0.3])
    assert result.roads == pytest.approx([0.5, 0.25, 0.0])
    assert result.props == [1.0, 1.0, 1.0]
    assert result.tone == 0.5


def test_gfx_read_02_toning_leaves_the_original_look_as_it_was() -> None:
    look = SimpleNamespace(
        terrain=[1.0, 1.0, 1.0], sea=[1.0, 1.0, 1.0], roads=[1.0, 1.0, 1.0], tone=1
    )
    toned(look, 0.2)
    assert look.terrain == [1.0, 1.0, 1.0]
    assert look.tone == 1


def test_gfx_read_02_all_toned_keeps_the_ids_of_its_looks() -> None:
    looks = {"1-1": SimpleNamespace(terrain=[1, 1, 1], sea=[1, 1, 1], roads=[1, 1, 1], tone=1)}
    result = all_toned(looks, 0.3)
    assert list(result) == ["1-1"]
    assert result["1-1"].tone == 0.3


def test_gfx_read_14_the_shot_renderers_are_wrapped_one_for_each_weapon() -> None:
    renderers = {"bullet": MagicMock(name="create-bullet")}
    wrapped = toned_shots(renderers)
    assert list(wrapped) == ["bullet"]
    assert callable(wrapped["bullet"])


@pytest.mark.parametrize("name", sorted(_JS_ONLY))
def test_gfx_read_02_the_array_and_object_helpers_are_javascript_only(name: str) -> None:
    """Their `__pragma__("js")` body runs in the browser; CPython runs only the placeholder."""
    helper, value, placeholder = _JS_ONLY[name]
    assert helper(value) == placeholder


class _Materials(list):  # type: ignore[type-arg]  # the scene's materials, a JavaScript array
    """The scene's materials: a list with JavaScript's `slice()`."""

    def slice(self) -> list[Any]:
        return list(self)


class _Material:
    """A material: its blend mode and opacity (two materials are never equal, as in JavaScript)."""

    def __init__(self, mode: str, alpha: float) -> None:
        self.alphaMode = mode
        self.alpha = alpha


def test_gfx_read_14_the_new_additive_glows_of_a_shot_renderer_are_toned_down(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(readability_view, "babylon_constant", lambda key: key)
    most = LOOK.playerShotMaxOpacity
    older = _Material("ALPHA_ADD", 1.0)
    scene = SimpleNamespace(materials=_Materials([older]))
    glow = _Material("ALPHA_ADD", 1.0)
    faint = _Material("ALPHA_ADD", most / 2)
    solid = _Material("ALPHA_COMBINE", 1.0)
    renderer = object()

    def create(target: Any) -> Any:
        target.materials.extend([glow, faint, solid])
        return renderer

    assert toned_shots({"laser": create})["laser"](scene) is renderer
    # A glow it added is capped; one already fainter, a blended material and the scene's own
    # materials are left alone.
    assert glow.alpha == most
    assert faint.alpha == most / 2
    assert solid.alpha == 1.0
    assert older.alpha == 1.0
