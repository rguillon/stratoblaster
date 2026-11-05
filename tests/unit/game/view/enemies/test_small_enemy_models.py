# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/small_enemy_models.py`."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import small_enemy_models as module
from render.geometry.solids import SolidBuilder


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_hornet_01_hornet_is_a_stinger_with_two_wings_one_reactor_and_a_gun_free_nose(
    probe: Any,
) -> None:
    """Also ENM-HORNET-02 (its two fluttering wings) and ENM-HORNET-03 (one reactor, a vein)."""
    capture, body = probe(module.build_hornet)
    assert capture.name == "hornet"
    assert len(body["wings"]) == 2
    assert body["rotors"] == []
    assert len(body["reactors"]) == 1
    # Its nose holds a metal stinger, no gun.
    assert body["muzzles"] == []
    assert body["slides"] == []
    assert len(body["parts"].hull.geometry.positions) > 0
    # Its light is the vein along its back (no eye any more).
    assert len(body["parts"].vein.geometry.positions) > 0
    assert body["parts"].neon.geometry.positions == []


def test_enm_hornet_01_hornet_body_is_an_abdomen_and_a_head_lobe() -> None:
    """`hornet_body` draws flesh only, from the abdomen's tail to the head lobe's tip."""
    flesh = SolidBuilder()
    module.hornet_body(flesh)
    zs = flesh.geometry.positions[2::3]
    assert min(zs) == pytest.approx(module.HORNET_ABDOMEN[0][0], abs=0.5)
    assert max(zs) == pytest.approx(10.5, abs=0.5)


def test_enm_scout_01_scout_has_two_reactors_fixed_wings_and_one_turret_gun(probe: Any) -> None:
    """Also ENM-SCOUT-02 (fixed airplane wings, no flapping) and ENM-SCOUT-03 (the turret gun)."""
    capture, body = probe(module.build_scout)
    assert capture.name == "scout"
    assert len(body["reactors"]) == 2
    assert body["wings"] == []
    assert len(body["muzzles"]) == 1
    assert len(body["slides"]) == 1
    assert body["slides"][0].swivel


def test_enm_strafer_03_strafer_has_four_reactors_and_six_guns_in_two_flank_pods(
    probe: Any,
) -> None:
    """Also ENM-STRAFER-01 (its wide pair of wings, held still: drawn on the body)."""
    capture, body = probe(module.build_strafer)
    assert capture.name == "strafer"
    assert len(body["reactors"]) == 4
    # Its wings are fixed: no fluttering wing node, their lights on the body's neon.
    assert body["wings"] == []
    assert len(body["parts"].neon.geometry.positions) > 0
    # WPN-04: three barrels on each side, each its own piece that slides back (WPN-03).
    assert len(body["muzzles"]) == 6
    assert len(body["slides"]) == 6
    assert {piece.index for piece in body["slides"]} == set(range(6))
    # Its guns are the bigger `STRAFER_GUN`: each recoils by its share of that length.
    recoil = module.STRAFER_GUN[0] * ENEMY_LOOK.barrelRecoil
    assert all(piece.distance == pytest.approx(recoil) for piece in body["slides"])
    # A gun pod on each flank holds the barrels' housings (metal either side of the body).
    xs = body["parts"].hull.geometry.positions[0::3]
    assert min(xs) < -module.STRAFER_POD[0]
    assert max(xs) > module.STRAFER_POD[0]


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
