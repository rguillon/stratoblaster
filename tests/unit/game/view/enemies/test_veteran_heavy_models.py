"""Unit tests of `src/game/view/enemies/veteran_heavy_models.py`."""

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import veteran_heavy_models as module


@pytest.fixture
def probe(monkeypatch):
    def run(builder):
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_p05_r14_mortar_has_two_reactors_and_one_mortar_mouth(probe):
    capture, body = probe(module.build_mortar)
    assert capture.name == "mortar"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 1


def test_p05_r15_minelayer_has_two_reactors_and_three_mine_chutes(probe):
    capture, body = probe(module.build_minelayer)
    assert capture.name == "minelayer"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 3
