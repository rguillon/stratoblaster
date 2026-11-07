# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/veteran_heavy_models.py`."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemies_veteran import VETERAN_CONFIG
from game.view.enemies import veteran_heavy_models as module


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_mortar_05_mortar_has_four_reactors_and_one_missile_mouth(probe: Any) -> None:
    """Two big reactors at the tail, one on each shoulder pod; the tube's mouth is its muzzle."""
    capture, body = probe(module.build_mortar)
    assert capture.name == "mortar"
    reactors = sorted(body["reactors"], key=lambda r: r.at[0])
    assert len(reactors) == 4
    big = [r for r in reactors if r.radius == 2.2]
    pods = [r for r in reactors if r.radius < 2.2]
    # The two big ones either side of the tail, the pods' further out.
    assert sorted(r.at[0] for r in big) == pytest.approx([-6.5, 6.5])
    assert sorted(r.at[0] for r in pods) == pytest.approx([
        -module.MORTAR_DRUM["x"],
        module.MORTAR_DRUM["x"],
    ])
    assert all(r.at[2] < 0 for r in reactors)
    # One missile muzzle, at the mouth of the tube: the config's muzzle in model space.
    x, y, height = VETERAN_CONFIG.mortar.muzzles[0][:3]
    assert body["muzzles"] == [[[-x, height, -y], "missile"]]
