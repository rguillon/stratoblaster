"""Unit tests of `src/game/view/readability_view.py`."""

import copy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.config.readability import READABILITY
from game.view import readability_view
from game.view.readability_view import (
    KEEP,
    MARKER_DEPTH,
    all_toned,
    build_hitbox_marker,
    outlined_ships,
    toned,
    toned_shots,
)

LOOK = READABILITY


def _is_array(value):
    return isinstance(value, list)


def _is_number_triple(value):
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(v, (int, float)) for v in value)
    )


def _is_object(value):
    return isinstance(value, dict)


@pytest.fixture(autouse=True)
def python_json_helpers(monkeypatch):
    """The JavaScript array and object helpers, in Python (CPython runs their fallback bodies)."""
    monkeypatch.setattr(readability_view, "_is_array", _is_array)
    monkeypatch.setattr(readability_view, "_is_number_triple", _is_number_triple)
    monkeypatch.setattr(readability_view, "_is_object", _is_object)
    monkeypatch.setattr(readability_view, "_entries", lambda value: list(value.items()))
    monkeypatch.setattr(readability_view, "_from_entries", dict)
    monkeypatch.setattr(readability_view, "_copy_object", copy.copy)


def test_p14_r01_a_colour_is_darkened_by_the_tone():
    scaled = readability_view._range_scale([0.8, 0.4, 0.2], 0.5, [])
    assert scaled == pytest.approx([0.4, 0.2, 0.1])


def test_p14_r01_colours_under_the_skip_keys_keep_their_brightness():
    look = {"tints": [1.0, 1.0, 1.0], "ground": [0.5, 0.5, 0.5]}
    scaled = readability_view._range_scale(look, 0.5, KEEP)
    assert scaled["tints"] == [1.0, 1.0, 1.0]
    assert scaled["ground"] == pytest.approx([0.25, 0.25, 0.25])


def test_p14_r01_numbers_that_are_not_colours_are_left_alone():
    assert readability_view._range_scale(3.0, 0.5, []) == 3.0
    assert readability_view._range_scale("text", 0.5, []) == "text"


def test_p14_r01_nested_colour_lists_are_darkened_one_by_one():
    scaled = readability_view._range_scale([[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]], 0.5, [])
    assert scaled == [[0.5, 0.5, 0.5], [0.0, 0.0, 0.0]]


def test_p14_r01_toning_a_look_darkens_its_ground_sea_and_roads_only():
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


def test_p14_r01_toning_leaves_the_original_look_as_it_was():
    look = SimpleNamespace(
        terrain=[1.0, 1.0, 1.0], sea=[1.0, 1.0, 1.0], roads=[1.0, 1.0, 1.0], tone=1
    )
    toned(look, 0.2)
    assert look.terrain == [1.0, 1.0, 1.0]
    assert look.tone == 1


def test_p14_r01_all_toned_keeps_the_ids_of_its_looks():
    looks = {"1-1": SimpleNamespace(terrain=[1, 1, 1], sea=[1, 1, 1], roads=[1, 1, 1], tone=1)}
    result = all_toned(looks, 0.3)
    assert list(result) == ["1-1"]
    assert result["1-1"].tone == 0.3


def test_p14_r03_each_ship_model_gets_an_outline_in_the_player_colour(monkeypatch):
    outline = MagicMock(name="outline")
    monkeypatch.setattr(readability_view, "outline_model", outline)
    root = MagicMock(name="root")
    models = outlined_ships({"light": lambda scene: root})
    assert models["light"]("scene") is root
    outline.assert_called_once_with(root, LOOK.playerOutline.color)


def test_p14_r03_the_hitbox_marker_is_a_disc_over_the_ship(monkeypatch):
    stub_babylon(monkeypatch, readability_view)
    discs = []

    def blended(name, geo, alphas, scene):
        discs.append(
            SimpleNamespace(
                name=name,
                geo=geo,
                alphas=alphas,
                material=MagicMock(),
                parent=None,
                position=MagicMock(),
                scaling=MagicMock(),
                setEnabled=MagicMock(),
                alphaIndex=None,
            )
        )
        return discs[-1]

    monkeypatch.setattr(readability_view, "blended_template", blended)
    monkeypatch.setattr(
        readability_view, "window", SimpleNamespace(Number=SimpleNamespace(MAX_SAFE_INTEGER=9))
    )
    root = build_hitbox_marker(MagicMock(), 3.0)
    disc = discs[0]
    assert disc.name == "hitbox-marker"
    assert disc.parent is root
    disc.position.set.assert_called_with(0, 0, MARKER_DEPTH)
    disc.scaling.setAll.assert_called_with(3.0)
    # One centre disc then rings of the marker's segments: every vertex is opaque.
    assert all(a == 1 for a in disc.alphas)
    assert disc.alphaIndex == 9


def test_p14_r06_the_shot_renderers_are_wrapped_one_for_each_weapon(monkeypatch):
    renderers = {"bullet": MagicMock(name="create-bullet")}
    wrapped = toned_shots(renderers)
    assert list(wrapped) == ["bullet"]
    assert callable(wrapped["bullet"])
