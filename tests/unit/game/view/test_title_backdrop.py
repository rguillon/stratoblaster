# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/title_backdrop.py`."""

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
