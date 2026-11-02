# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/verdant_crown_parts.py`: its thorn cannons."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import design_muzzles, muzzle_kinds, turret_drawings
from helpers.view_probes import probe_builder

from game.view.bosses.world_3 import verdant_crown_parts as module
from game.view.bosses.world_3.verdant_crown_model import build_verdant_crown


def test_a_rect_is_centred_on_the_origin_by_default() -> None:
    assert module.rect(4, 2) == [[-2, -1], [2, -1], [2, 1], [-2, 1]]
    assert module.rect(4, 2, [10, 20]) == [[8, 19], [12, 19], [12, 21], [8, 21]]


def test_the_thorn_pod_is_mossy_on_its_back_only() -> None:
    assert module.pod_paint(module.POD_BACK, 0) == module.JUNGLE["moss"]
    assert module.pod_paint(0, 0) is None


@pytest.mark.parametrize("piece", ["thorn-left", "thorn-right"])
def test_fb_verdant_crown_05_a_thorn_cannon_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_verdant_crown)
    cannon = turret_drawings(capture)[piece]
    assert muzzle_kinds(cannon) == ["laser"]
    assert cannon["muzzles"][0][0] == pytest.approx(
        design_muzzles(capture.design, piece, "laser")[0]
    )
