# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/veteran_heavy_models.py`."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import veteran_heavy_models as module


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_mortar_05_mortar_has_two_reactors_and_one_mortar_mouth(probe: Any) -> None:
    capture, body = probe(module.build_mortar)
    assert capture.name == "mortar"
    assert len(body["reactors"]) == 2
    assert len(body["muzzles"]) == 1
