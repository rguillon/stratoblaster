"""Unit tests of `src/game/view/enemies/elite_scissor_model.py`."""

from helpers.view_probes import drawings_of, jointed_design_ids, probe_builder

from game.view.enemies import elite_scissor_model as module


def test_p05_scissor_draws_its_two_arms_on_their_shoulders(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_scissor)
    design_ids, drawn_ids = jointed_design_ids(capture)
    assert capture.name == "scissor"
    assert sorted(design_ids) == sorted(drawn_ids) == ["arm-left", "arm-right"]
    drawn = drawings_of(capture)
    assert {"limbs.shoulder-left", "limbs.shoulder-right"} <= set(drawn)
    assert len(drawn["parts.arm-left"]["muzzles"]) == 1


def test_p05_scissor_body_has_two_reactors(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_scissor)
    assert len(drawings_of(capture)["body"]["reactors"]) == 2
