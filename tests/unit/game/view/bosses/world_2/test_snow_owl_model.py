# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/snow_owl_model.py`: its guns (MB-SNOW-OWL-03)."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_2 import snow_owl_model as module


def test_mb_snow_owl_03_the_crown_emitter_and_the_chin_guns_have_their_muzzles() -> None:
    kinds = muzzle_kinds(drawn(module.draw_guns))
    assert kinds == ["ring"] + ["gun"] * len(module.OWL_CHIN_GUNS)


def test_mb_snow_owl_03_without_a_crown_only_the_chin_guns_are_drawn(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "OWL_CROWN", [])
    result = drawn(module.draw_guns)
    assert [at for at, _kind in result["muzzles"]] == [
        pytest.approx(boss_point(m[0], m[1], m[2])) for m in module.OWL_CHIN_GUNS
    ]
