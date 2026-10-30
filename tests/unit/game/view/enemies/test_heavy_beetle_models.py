"""Unit tests of `src/game/view/enemies/heavy_beetle_models.py`."""

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import heavy_beetle_models as module


@pytest.fixture
def probe(monkeypatch):
    def run(builder):
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_p05_bulwark_has_three_reactors_and_two_guns(probe):
    capture, body = probe(module.build_bulwark)
    assert capture.name == "bulwark"
    assert len(body["reactors"]) == 3
    assert len(body["muzzles"]) == 2
    assert body["wings"] == []


def test_p05_splitter_has_one_reactor_and_one_gun(probe):
    capture, body = probe(module.build_splitter)
    assert capture.name == "splitter"
    assert len(body["reactors"]) == 1
    assert len(body["muzzles"]) == 1


def test_p05_splitter_pod_is_a_bare_pod_with_a_reactor_and_no_gun(probe):
    capture, body = probe(module.build_splitter_pod)
    assert capture.name == "splitter-pod"
    assert len(body["reactors"]) == 1
    assert body["muzzles"] == []
    assert len(body["parts"].flesh.geometry.positions) > 0
