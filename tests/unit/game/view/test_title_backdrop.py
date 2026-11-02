# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/title_backdrop.py`."""

import math
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from core.math.rng import create_rng
from game.view import title_backdrop
from game.view.title_backdrop import _build_city, _build_sky, build_title_backdrop


@pytest.fixture
def scene(monkeypatch: Any) -> Any:
    stub_babylon(monkeypatch, title_backdrop)
    monkeypatch.setattr(
        title_backdrop, "build_gradient_rect", lambda *_a: MagicMock(name="sky"), raising=False
    )
    return MagicMock(name="scene")


def test_the_title_sky_and_skyline_are_built_without_glow(scene: Any) -> None:
    """UI-TITLE-10: the dark sky and skyline are kept out of the glow."""
    meshes = _build_sky(scene, create_rng(1))
    assert len(meshes) == 2


def test_the_title_city_is_two_chunks_end_to_end(scene: Any) -> None:
    """UI-TITLE-07: the street loops forever."""
    city = _build_city(scene, create_rng(2))
    assert city is not None


def test_the_title_backdrop_is_built_in_its_scene(scene: Any) -> None:
    assert build_title_backdrop(scene) is not None


@pytest.fixture
def backdrop(monkeypatch: Any, scene: Any) -> SimpleNamespace:
    """Build the backdrop with its nodes and meshes recorded by name, and its handle a dict."""
    made = SimpleNamespace(nodes={}, steps=[], ship=MagicMock(name="ship"))

    def node(label: str, _scene: Any) -> Any:
        made.nodes[label] = MagicMock(name=label)
        made.nodes[label].rotation.y = 0.0
        return made.nodes[label]

    monkeypatch.setattr(title_backdrop, "new_transform_node", node)
    monkeypatch.setattr(title_backdrop, "new_mesh", node)
    monkeypatch.setattr(title_backdrop, "js_object", dict)
    monkeypatch.setattr(
        title_backdrop, "js_set", lambda obj, key, value: obj.__setitem__(key, value)
    )
    monkeypatch.setattr(title_backdrop, "build_balanced_ship", lambda _scene: made.ship)
    # Empty geometry for the street, skyline and rain: the meshes are stand-ins anyway.
    empty = SimpleNamespace(positions=[], indices=[], colors=[])
    parts = {"structure": empty, "lights": empty}
    monkeypatch.setattr(title_backdrop, "build_city_chunk", lambda _look, _random: parts)
    monkeypatch.setattr(title_backdrop, "build_skyline", lambda _look, _random: parts)
    monkeypatch.setattr(title_backdrop, "build_rain", lambda _look, _random: empty)
    monkeypatch.setattr(
        title_backdrop, "step_model_animations", lambda root, dt: made.steps.append((root, dt))
    )
    made.handle = build_title_backdrop(scene)
    return made


def test_ui_title_10_the_sky_skyline_street_and_rain_are_kept_out_of_the_glow(
    backdrop: SimpleNamespace,
) -> None:
    excluded = backdrop.handle["glowExcludedMeshes"]
    nodes = backdrop.nodes
    assert excluded[0] is nodes["title-sky"]
    assert excluded[1] is nodes["title-skyline"]
    assert excluded[2] is nodes["title-city-structure"]
    assert excluded[-1] is nodes["title-rain"]
    assert nodes["title-city-lights"] not in excluded


def test_ui_title_07_each_frame_scrolls_the_street_drops_the_rain_and_turns_the_ship(
    backdrop: SimpleNamespace,
) -> None:
    look = title_backdrop.LOOK
    nodes = backdrop.nodes
    backdrop.handle["update"](0.25)
    backdrop.handle["update"](0.25)
    t = 0.5
    assert t * look.city.scrollSpeed < look.city["length"]
    assert t * look.rain.speed < look.rain.height
    assert nodes["title-city"].position.z == pytest.approx(-(t * look.city.scrollSpeed))
    assert nodes["title-rain"].position.y == pytest.approx(look.rain.y - t * look.rain.speed)
    pivot = nodes["title-ship"]
    assert pivot.rotation.y == pytest.approx(look.ship.rotationSpeedRadPerSec * t)
    bob = look.ship.bobAmplitude * math.sin(2 * math.pi * look.ship.bobHz * t)
    assert pivot.position.y == pytest.approx(look.ship.position[1] + bob)
    # The ship floats on its pivot, its reactors' flames stepped each frame.
    assert backdrop.ship.parent is pivot
    assert backdrop.steps == [(backdrop.ship, 0.25), (backdrop.ship, 0.25)]


def test_ui_title_07_the_street_and_the_rain_loop_once_they_have_gone_round(
    backdrop: SimpleNamespace,
) -> None:
    look = title_backdrop.LOOK
    loop = look.city["length"] / look.city.scrollSpeed
    backdrop.handle["update"](loop + 1)
    assert backdrop.nodes["title-city"].position.z == pytest.approx(-look.city.scrollSpeed)
    fallen = ((loop + 1) * look.rain.speed) % look.rain.height
    assert backdrop.nodes["title-rain"].position.y == pytest.approx(look.rain.y - fallen)


@pytest.mark.parametrize(("screen", "shown"), [("ship-select", False), ("title", True)])
def test_ui_title_09_the_ship_is_hidden_on_the_ship_select_screen(
    backdrop: SimpleNamespace, screen: str, shown: bool
) -> None:
    backdrop.handle["showScreen"](screen)
    backdrop.nodes["title-ship"].setEnabled.assert_called_once_with(shown)
