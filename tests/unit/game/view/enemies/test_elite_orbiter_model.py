"""Unit tests of `src/game/view/enemies/elite_orbiter_model.py`."""

from helpers.view_probes import drawings_of, jointed_design_ids, probe_builder

from game.view.enemies import elite_orbiter_model as module


def test_p05_r20_orbiter_draws_one_part_per_drone_its_design_lists(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_orbiter)
    design_ids, drawn_ids = jointed_design_ids(capture)
    assert capture.name == "orbiter"
    assert sorted(design_ids) == sorted(drawn_ids) == ["drone-0", "drone-1", "drone-2"]


def test_p05_r20_each_drone_has_its_gun_and_the_heart_has_a_dozen_mouths(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_orbiter)
    drawn = drawings_of(capture)
    for i in range(3):
        assert len(drawn[f"parts.drone-{i}"]["muzzles"]) == 1
    assert len(drawn["body"]["muzzles"]) == 12
