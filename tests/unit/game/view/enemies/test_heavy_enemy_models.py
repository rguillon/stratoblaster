"""Unit tests of `src/game/view/enemies/heavy_enemy_models.py`."""

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import heavy_enemy_models as module


@pytest.fixture
def probe(monkeypatch):
    def run(builder):
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_p05_spinner_is_a_turret_of_four_guns_and_no_reactor(probe):
    capture, body = probe(module.build_spinner)
    assert capture.name == "spinner"
    assert capture.neon == ENEMY_LOOK.neon.spinner
    assert len(body["muzzles"]) == 4
    assert body["reactors"] == []
    assert body["wings"] == []


def test_p05_lancer_has_three_reactors_and_one_lance_gun(probe):
    capture, body = probe(module.build_lancer)
    assert capture.name == "lancer"
    assert len(body["reactors"]) == 3
    assert len(body["muzzles"]) == 1


def test_p05_rocketeer_has_two_reactors_and_two_rocket_mouths(probe):
    capture, body = probe(module.build_rocketeer)
    assert capture.name == "rocketeer"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 2


def test_heavy_kinds_are_bodies_with_their_neon_lights(probe):
    for builder in (module.build_spinner, module.build_lancer, module.build_rocketeer):
        capture, body = probe(builder)
        assert len(body["parts"].neon.geometry.positions) > 0, capture.name
