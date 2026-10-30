"""Unit tests of `src/game/view/enemies/elite_hydra_model.py`."""

from helpers.view_probes import drawings_of, jointed_design_ids, probe_builder

from game.view.enemies import elite_hydra_model as module


def test_p05_r19_hydra_draws_every_head_its_design_asks_for(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_hydra)
    design_ids, drawn_ids = jointed_design_ids(capture)
    assert capture.name == "hydra"
    assert sorted(design_ids) == sorted(drawn_ids)
    assert len(design_ids) == 3


def test_p05_r19_each_head_hangs_on_a_neck_joint_and_fires_from_its_mouth(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_hydra)
    drawn = drawings_of(capture)
    for joint in ("neck-left", "neck-middle", "neck-right"):
        assert "limbs." + joint in drawn
    for head in ("head-left", "head-middle", "head-right"):
        assert len(drawn["parts." + head]["muzzles"]) == 1


def test_p05_r19_body_has_two_reactors(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_hydra)
    assert len(drawings_of(capture)["body"]["reactors"]) == 2
