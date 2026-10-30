"""Unit tests of `src/game/view/enemies/carrier_model.py`."""

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import carrier_model as module


def test_p05_r12_carrier_is_built_as_the_carrier_kind_in_its_neon(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_carrier)
    assert capture.name == "carrier"
    assert capture.neon == ENEMY_LOOK.neon.carrier


@pytest.mark.xfail(
    strict=True,
    reason="CPython only: the carrier's placements are object literals read with attribute access",
)
def test_p05_r12_carrier_draws_its_body_on_real_builders(monkeypatch):
    capture = probe_builder(monkeypatch, module.build_carrier)
    assert len(drawings_of(capture)["body"]["parts"].hull.geometry.positions) > 0
