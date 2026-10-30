"""Unit tests of `src/game/view/shots/shot_meshes.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view.shots import shot_meshes
from game.view.shots.shot_meshes import (
    ALPHA_SLOT,
    RGBA,
    _vertex_colour,
    additive_template,
    blended_template,
)


@pytest.fixture
def babylon(monkeypatch):
    """Babylon stand-ins, with the vertex data recorded."""
    stub_babylon(monkeypatch, shot_meshes)
    data = []

    def record(positions, indices, uvs, colors):
        data.append(SimpleNamespace(positions=positions, indices=indices, colors=colors))
        return data[-1]

    monkeypatch.setattr(shot_meshes, "vertex_data_of", record)
    return data


GEO = SimpleNamespace(positions=[0, 0, 0, 1, 0, 0, 0, 1, 0], indices=[0, 1, 2], colors=[0.5] * 12)


def test_p03_r01_alpha_components_take_the_vertex_alphas():
    assert RGBA == 4
    assert ALPHA_SLOT == 3
    alphas = [0.25, 0.75]
    assert _vertex_colour(0.5, 0, alphas) == 0.5
    assert _vertex_colour(0.5, 3, alphas) == 0.25
    assert _vertex_colour(0.5, 7, alphas) == 0.75


def test_p03_r01_a_missing_alpha_keeps_the_colour():
    assert _vertex_colour(0.5, 3, [None]) == 0.5


def test_p03_r01_additive_template_is_a_disabled_unlit_mesh(babylon):
    mesh = additive_template("bullet", GEO, MagicMock())
    mesh.setEnabled.assert_called_with(False)
    assert mesh.material.disableLighting is True
    assert mesh.material.disableDepthWrite is True
    assert mesh.material.backFaceCulling is False
    assert mesh.material.alpha == pytest.approx(0.999)
    assert mesh.isPickable is False
    assert babylon[-1].colors == GEO.colors


def test_p03_r01_an_additive_template_on_top_draws_over_the_models(babylon, monkeypatch):
    # The depth function is set only on top: `ALWAYS` in Babylon's constants.
    monkeypatch.setattr(shot_meshes, "babylon_constant", lambda key: key)
    on_top = additive_template("laser", GEO, MagicMock(), on_top=True)
    below = additive_template("laser", GEO, MagicMock(), on_top=False)
    assert on_top.material.depthFunction == "ALWAYS"
    assert below.material.depthFunction != "ALWAYS"


def test_p03_r01_a_blended_template_takes_its_alpha_from_the_vertices(babylon):
    # One alpha per vertex of GEO (three): they replace the fourth component of each.
    mesh = blended_template("snow-trail", GEO, [0.5, 0.25, 1.0], MagicMock())
    assert mesh.hasVertexAlpha is True
    mesh.setEnabled.assert_called_with(False)
    colours = babylon[-1].colors
    assert [colours[3], colours[7], colours[11]] == [0.5, 0.25, 1.0]
    assert colours[0] == pytest.approx(0.5)
