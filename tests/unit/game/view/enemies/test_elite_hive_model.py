"""Unit tests of `src/game/view/enemies/elite_hive_model.py`."""

from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import elite_hive_model as module


def test_p05_hive_has_a_ring_with_a_gun_and_a_body_with_many_spore_mouths(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_hive)
    assert capture.name == "hive"
    drawn = drawings_of(capture)
    assert len(drawn["ring"]["muzzles"]) == 1
    assert len(drawn["body"]["muzzles"]) == 12
    assert len(drawn["body"]["reactors"]) == 2
