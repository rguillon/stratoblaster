"""Unit tests of `src/game/view/enemies/veteran_mantis_model.py`."""

from helpers.view_probes import drawings_of, jointed_design_ids, probe_builder

from game.view.enemies import veteran_mantis_model as module


def test_p05_mantis_draws_every_part_its_design_asks_for(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_mantis)
    design_ids, drawn_ids = jointed_design_ids(capture)
    assert capture.name == "mantis"
    assert sorted(design_ids) == sorted(drawn_ids)


def test_p05_mantis_arms_are_grafted_on_shoulder_joints(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_mantis)
    drawn = drawings_of(capture)
    assert {"limbs.left-shoulder", "limbs.right-shoulder"} <= set(drawn)
    assert len(drawn["parts.left-arm"]["muzzles"]) == 2
    assert len(drawn["parts.right-arm"]["muzzles"]) == 2


def test_p05_mantis_body_has_a_reactor_and_a_gun(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_mantis)
    body = drawings_of(capture)["body"]
    assert len(body["reactors"]) == 1
    assert len(body["muzzles"]) == 1
