# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/shots/missile_model.py`."""

import math
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.config.shot_look import SHOT_LOOK
from game.view.shots import missile_model
from game.view.shots.missile_model import (
    FIN_LENGTH_FRACTION,
    FIN_THICKNESS,
    NOSE_FRACTION,
    SIDES,
    build_missile,
    materials,
)

LOOK = SHOT_LOOK.missile


@pytest.fixture
def nodes(monkeypatch: Any) -> Any:
    """Babylon stand-ins; the meshes and nodes made are recorded by name."""
    stub_babylon(monkeypatch, missile_model)
    made = {}

    def make(name: Any, *_args: Any) -> Any:
        made[name] = MagicMock(name=name)
        return made[name]

    monkeypatch.setattr(missile_model, "new_transform_node", lambda name, _scene: make(name))
    monkeypatch.setattr(missile_model, "create_cylinder", lambda name, _opts, _scene: make(name))
    monkeypatch.setattr(missile_model, "create_box", lambda name, _opts, _scene: make(name))
    monkeypatch.setattr(missile_model, "build_reactor_flame", lambda _name, _opts, _parent: None)
    return made


def test_gfx_shot_06_the_missile_has_a_tube_nose_and_two_crossed_fins() -> None:
    assert SIDES == 6
    assert 0 < NOSE_FRACTION < 1
    assert FIN_LENGTH_FRACTION < 1
    assert FIN_THICKNESS > 0


@pytest.mark.usefixtures("nodes")
def test_gfx_shot_06_materials_are_a_body_and_a_glowing_tip() -> None:
    body, tip = materials(MagicMock())
    assert body is not tip
    assert tip.emissiveColor is not None


def test_gfx_shot_06_the_missile_pivot_points_up_the_playfield(nodes: Any) -> None:
    pivot = build_missile("missile-1", MagicMock())
    assert pivot is nodes["missile-1"]
    model = nodes["missile-1-model"]
    assert model.parent is pivot
    assert model.rotation.x == pytest.approx(-math.pi / 2)


def test_gfx_shot_06_the_body_is_built_along_z_with_its_nose_at_the_front(nodes: Any) -> None:
    build_missile("missile-2", MagicMock())
    nose = nodes["missile-2-nose"]
    tube = nodes["missile-2-tube"]
    nose_length = LOOK.length * NOSE_FRACTION
    assert nose.position.z == pytest.approx(LOOK.length / 2 - nose_length / 2)
    assert tube.position.z == pytest.approx(-nose_length / 2)
    assert nose.rotation.x == pytest.approx(math.pi / 2)


def test_gfx_shot_06_the_fins_are_two_boxes_crossing_at_the_tail(nodes: Any) -> None:
    build_missile("missile-3", MagicMock())
    fins = [nodes["missile-3-fin-0"], nodes["missile-3-fin-1"]]
    assert fins[0].rotation.z == pytest.approx(0)
    assert fins[1].rotation.z == pytest.approx(math.pi / 2)
    fin_length = LOOK.length * FIN_LENGTH_FRACTION
    for fin in fins:
        assert fin.position.z == pytest.approx(-LOOK.length / 2 + fin_length / 2)
