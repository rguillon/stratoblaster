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
from game.view.title_backdrop import _build_sky, _build_streaks, _build_trench, build_title_backdrop


@pytest.fixture
def scene(monkeypatch: Any) -> Any:
    stub_babylon(monkeypatch, title_backdrop)
    monkeypatch.setattr(
        title_backdrop, "build_gradient_rect", lambda *_a: MagicMock(name="sky"), raising=False
    )
    return MagicMock(name="scene")


def test_the_title_sky_is_built(scene: Any) -> None:
    assert _build_sky(scene) is not None


def test_ui_title_07_the_trench_is_two_stretches_end_to_end(scene: Any) -> None:
    trench = _build_trench(scene, create_rng(2))
    assert len(trench["structure"]) == 2


def test_ui_title_07_the_streaks_are_built(scene: Any) -> None:
    assert _build_streaks(scene, create_rng(3)) is not None


def test_the_title_backdrop_is_built_in_its_scene(scene: Any) -> None:
    assert build_title_backdrop(scene) is not None


@pytest.fixture
def backdrop(monkeypatch: Any, scene: Any) -> SimpleNamespace:
    """Build the backdrop with its nodes and meshes recorded by name, and its handle a dict."""
    made = SimpleNamespace(nodes={}, steps=[], ship=MagicMock(name="ship"))

    def node(label: str, _scene: Any) -> Any:
        made.nodes[label] = MagicMock(name=label)
        made.nodes[label].rotation.z = 0.0
        return made.nodes[label]

    monkeypatch.setattr(title_backdrop, "new_transform_node", node)
    monkeypatch.setattr(title_backdrop, "new_mesh", node)
    monkeypatch.setattr(title_backdrop, "js_object", dict)
    monkeypatch.setattr(
        title_backdrop, "js_set", lambda obj, key, value: obj.__setitem__(key, value)
    )
    monkeypatch.setattr(title_backdrop, "build_balanced_ship", lambda _scene: made.ship)
    # Empty geometry for the trench and the streaks: the meshes are stand-ins anyway.
    empty = SimpleNamespace(positions=[], indices=[], colors=[])
    parts = {"structure": empty, "lights": empty}
    monkeypatch.setattr(title_backdrop, "build_trench_chunk", lambda _look, _random: parts)
    monkeypatch.setattr(title_backdrop, "build_streaks", lambda _look, _random: empty)
    monkeypatch.setattr(
        title_backdrop, "step_model_animations", lambda root, dt: made.steps.append((root, dt))
    )
    made.handle = build_title_backdrop(scene)
    return made


def test_ui_title_10_the_sky_and_the_trench_structure_are_kept_out_of_the_glow(
    backdrop: SimpleNamespace,
) -> None:
    excluded = backdrop.handle["glowExcludedMeshes"]
    nodes = backdrop.nodes
    assert excluded[0] is nodes["title-sky"]
    assert excluded[1] is nodes["title-trench-structure"]
    assert nodes["title-trench-lights"] not in excluded
    assert nodes["title-streak-mesh"] not in excluded


def test_ui_title_07_each_frame_scrolls_the_trench_and_the_faster_streaks_away(
    backdrop: SimpleNamespace,
) -> None:
    look = title_backdrop.LOOK
    nodes = backdrop.nodes
    assert look.streaks.speed > look.trench.speed
    backdrop.handle["update"](0.1)
    backdrop.handle["update"](0.1)
    t = 0.2
    assert t * look.trench.speed < look.trench["length"]
    assert t * look.streaks.speed < look.streaks["length"]
    trench_z = look.trench.startZ - t * look.trench.speed
    assert nodes["title-trench"].position.z == pytest.approx(trench_z)
    streaks_z = look.streaks.startZ - t * look.streaks.speed
    assert nodes["title-streaks"].position.z == pytest.approx(streaks_z)


def test_ui_title_07_the_trench_and_the_streaks_loop_once_they_have_gone_round(
    backdrop: SimpleNamespace,
) -> None:
    look = title_backdrop.LOOK
    loop = look.trench["length"] / look.trench.speed
    backdrop.handle["update"](loop + 0.1)
    expected = look.trench.startZ - 0.1 * look.trench.speed
    assert backdrop.nodes["title-trench"].position.z == pytest.approx(expected)
    gone = ((loop + 0.1) * look.streaks.speed) % look.streaks["length"]
    assert backdrop.nodes["title-streaks"].position.z == pytest.approx(look.streaks.startZ - gone)


def test_ui_title_07_the_ship_faces_the_camera_sways_banks_and_floats(
    backdrop: SimpleNamespace,
) -> None:
    look = title_backdrop.LOOK
    s = look.ship
    # The camera is ahead of the ship, along +Z, where the model's nose points.
    assert look.camera.position[2] > s.position[2]
    pivot = backdrop.nodes["title-ship"]
    t = 1 / (4 * s.swayHz)
    backdrop.handle["update"](t)
    # A quarter sway: at its widest, not moving sideways, so not banked.
    assert pivot.position.x == pytest.approx(s.position[0] + s.swayAmplitude)
    assert pivot.rotation.z == pytest.approx(0, abs=1e-9)
    bob = s.bobAmplitude * math.sin(2 * math.pi * s.bobHz * t)
    assert pivot.position.y == pytest.approx(s.position[1] + bob)
    backdrop.handle["update"](t)
    # Half a sway: back in the middle, moving towards -X, banked the most, its -X wing down.
    assert pivot.position.x == pytest.approx(s.position[0], abs=1e-9)
    assert pivot.rotation.z == pytest.approx(s.bankRad)
    assert backdrop.ship.parent is pivot
    assert backdrop.steps == [(backdrop.ship, t), (backdrop.ship, t)]
