"""Unit tests of `src/game/view/enemies/elite_juggernaut_model.py`."""

from helpers.view_probes import drawings_of, jointed_design_ids, probe_builder

from game.view.enemies import elite_juggernaut_model as module


def test_p05_juggernaut_draws_its_cannons_and_plates_on_their_joints(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_juggernaut)
    design_ids, drawn_ids = jointed_design_ids(capture)
    assert capture.name == "juggernaut"
    assert sorted(design_ids) == sorted(drawn_ids)
    drawn = drawings_of(capture)
    assert len(drawn["parts.cannon-left"]["muzzles"]) == 1
    assert len(drawn["parts.cannon-right"]["muzzles"]) == 1
    assert {"limbs.shoulder-left", "limbs.shoulder-right"} <= set(drawn)


def test_p05_juggernaut_body_has_three_reactors_and_two_guns(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_juggernaut)
    body = drawings_of(capture)["body"]
    assert len(body["reactors"]) == 3
    assert len(body["muzzles"]) == 2
