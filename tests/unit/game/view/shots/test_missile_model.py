"""Unit tests of `src/game/view/shots/missile_model.py`."""

import math
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
def nodes(monkeypatch):
    """Babylon stand-ins; the meshes and nodes made are recorded by name."""
    stub_babylon(monkeypatch, missile_model)
    made = {}

    def make(name, *args):
        made[name] = MagicMock(name=name)
        return made[name]

    monkeypatch.setattr(missile_model, "new_transform_node", lambda name, scene: make(name))
    monkeypatch.setattr(missile_model, "create_cylinder", lambda name, opts, scene: make(name))
    monkeypatch.setattr(missile_model, "create_box", lambda name, opts, scene: make(name))
    monkeypatch.setattr(missile_model, "build_reactor_flame", lambda name, opts, parent: None)
    return made


def test_p03_r03_the_missile_has_a_tube_nose_and_two_crossed_fins():
    assert SIDES == 6
    assert 0 < NOSE_FRACTION < 1
    assert FIN_LENGTH_FRACTION < 1
    assert FIN_THICKNESS > 0


def test_p03_r03_materials_are_a_body_and_a_glowing_tip(nodes):
    body, tip = materials(MagicMock())
    assert body is not tip
    assert tip.emissiveColor is not None


def test_p03_r03_the_missile_pivot_points_up_the_playfield(nodes):
    pivot = build_missile("missile-1", MagicMock())
    assert pivot is nodes["missile-1"]
    model = nodes["missile-1-model"]
    assert model.parent is pivot
    assert model.rotation.x == pytest.approx(-math.pi / 2)


def test_p03_r03_the_body_is_built_along_z_with_its_nose_at_the_front(nodes):
    build_missile("missile-2", MagicMock())
    nose = nodes["missile-2-nose"]
    tube = nodes["missile-2-tube"]
    nose_length = LOOK.length * NOSE_FRACTION
    assert nose.position.z == pytest.approx(LOOK.length / 2 - nose_length / 2)
    assert tube.position.z == pytest.approx(-nose_length / 2)
    assert nose.rotation.x == pytest.approx(math.pi / 2)


def test_p03_r03_the_fins_are_two_boxes_crossing_at_the_tail(nodes):
    build_missile("missile-3", MagicMock())
    fins = [nodes["missile-3-fin-0"], nodes["missile-3-fin-1"]]
    assert fins[0].rotation.z == pytest.approx(0)
    assert fins[1].rotation.z == pytest.approx(math.pi / 2)
    fin_length = LOOK.length * FIN_LENGTH_FRACTION
    for fin in fins:
        assert fin.position.z == pytest.approx(-LOOK.length / 2 + fin_length / 2)
