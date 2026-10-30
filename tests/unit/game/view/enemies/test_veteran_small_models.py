"""Unit tests of `src/game/view/enemies/veteran_small_models.py`."""

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import vetelite_organic
from game.view.enemies import veteran_small_models as module


@pytest.fixture
def probe(monkeypatch):
    def run(builder):
        # The wings are copied with `Object.assign` in the game; under CPython that copy is a
        # plain dict merge (the Transcrypt stub returns None here).
        monkeypatch.setattr(
            vetelite_organic,
            "_with_wing",
            lambda wing, root, tips: {**wing, "root": root, "tips": tips},
        )
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_p05_r14_wasp_has_two_pairs_of_wings_two_reactors_and_a_nose_gun(probe):
    capture, body = probe(module.build_wasp)
    assert capture.name == "wasp"
    # Two membrane pairs of wings: four flaps in all.
    assert len(body["wings"]) == 4
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 1


def test_p05_r17_phantom_is_a_flying_wing_with_two_reactors_and_one_gun(probe):
    capture, body = probe(module.build_phantom)
    assert capture.name == "phantom"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 1
    assert len(body["parts"].flesh.geometry.positions) > 0
