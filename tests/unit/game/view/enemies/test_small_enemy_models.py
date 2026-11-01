# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/small_enemy_models.py`."""

import math
from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import small_enemy_models as module


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_gnat_01_gnat_is_a_drone_with_three_ducted_fans_and_a_reactor(probe: Any) -> None:
    """Also ENM-GNAT-02 (three fans) and ENM-GNAT-03 (one reactor)."""
    capture, body = probe(module.build_gnat)
    assert capture.name == "gnat"
    assert capture.neon == ENEMY_LOOK.neon.gnat
    # Three fans on their ducts, one reactor at the back, and no wing.
    assert len(body["rotors"]) == 3
    assert len(body["reactors"]) == 1
    assert body["wings"] == []
    assert len(body["parts"].flesh.geometry.positions) > 0


def test_enm_gnat_02_gnat_fans_stand_on_a_ring_120_degrees_apart(probe: Any) -> None:
    _capture, body = probe(module.build_gnat)
    angles = sorted(math.atan2(r.at[0], r.at[2]) % (2 * math.pi) for r in body["rotors"])
    radii = [math.hypot(r.at[0], r.at[2]) for r in body["rotors"]]
    # Each fan sits on the duct ring (6 units out), a third of a turn from the next.
    assert radii == pytest.approx([6, 6, 6])
    gaps = [angles[1] - angles[0], angles[2] - angles[1]]
    assert gaps == pytest.approx([2 * math.pi / 3] * 2)


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


def test_enm_weaver_02_weaver_has_two_reactors_and_two_guns_and_no_wings(probe: Any) -> None:
    """Also ENM-WEAVER-01: two serpents, no wings."""
    capture, body = probe(module.build_weaver)
    assert capture.name == "weaver"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 2
    assert body["wings"] == []


def test_enm_35_every_small_kind_is_a_flesh_body_with_its_own_neon(probe: Any) -> None:
    for builder in (
        module.build_gnat,
        module.build_hornet,
        module.build_scout,
        module.build_strafer,
        module.build_weaver,
    ):
        capture, body = probe(builder)
        assert len(body["parts"].flesh.geometry.positions) > 0, capture.name
        assert capture.neon is not None
