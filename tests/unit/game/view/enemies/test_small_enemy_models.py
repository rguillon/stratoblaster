# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/small_enemy_models.py`."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import small_enemy_models as module


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_hornet_01_hornet_is_a_stinger_with_two_wings_and_a_gun_free_nose(probe: Any) -> None:
    """Also ENM-HORNET-02: its two wings."""
    capture, body = probe(module.build_hornet)
    assert capture.name == "hornet"
    assert len(body["wings"]) == 2
    assert body["rotors"] == []
    assert len(body["parts"].neon.geometry.positions) > 0


def test_enm_scout_01_scout_has_two_reactors_two_wings_and_one_gun(probe: Any) -> None:
    """Also ENM-SCOUT-02 (a reactor on each boom) and ENM-SCOUT-03 (the nose gun)."""
    capture, body = probe(module.build_scout)
    assert capture.name == "scout"
    assert len(body["reactors"]) == 2
    assert len(body["wings"]) == 2
    assert len(body["muzzles"]) == 1


def test_enm_strafer_03_strafer_has_four_reactors_and_two_guns_on_two_wings(probe: Any) -> None:
    """Also ENM-STRAFER-01: its wide pair of wings."""
    capture, body = probe(module.build_strafer)
    assert capture.name == "strafer"
    assert len(body["reactors"]) == 4
    assert len(body["wings"]) == 2
    assert len(body["muzzles"]) == 2


def test_enm_35_every_small_kind_is_a_flesh_body_with_its_own_neon(probe: Any) -> None:
    for builder in (
        module.build_hornet,
        module.build_scout,
        module.build_strafer,
    ):
        capture, body = probe(builder)
        assert len(body["parts"].flesh.geometry.positions) > 0, capture.name
        assert capture.neon is not None


@pytest.mark.parametrize(("a", "b"), [([0, 0], [10, 0]), ([10, 0], [0, 0])])
def test_an_edge_light_lies_behind_its_edge_whichever_way_the_edge_runs(a: Any, b: Any) -> None:
    """The light is moved `inward` towards the trailing side (-Z) of an edge along X."""
    quad = module.edge_light(a, b, 0.5, 1.0, [4.0, 0.5])
    xs = sorted(p[0] for p in quad)
    zs = sorted(p[1] for p in quad)
    # Centred halfway along the edge, `length` long, from `inward` to `inward` + `width` behind it.
    assert xs == pytest.approx([3.0, 3.0, 7.0, 7.0])
    assert zs == pytest.approx([-1.5, -1.5, -1.0, -1.0])
