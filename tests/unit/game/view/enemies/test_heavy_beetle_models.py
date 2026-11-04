# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/heavy_beetle_models.py`."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.view.enemies import heavy_beetle_models as module


@pytest.fixture
def probe(monkeypatch: Any) -> Any:
    def run(builder: Any) -> Any:
        capture = probe_builder(monkeypatch, builder)
        return capture, drawings_of(capture)["body"]

    return run


def test_enm_splitter_02_splitter_has_one_reactor_and_no_gun(probe: Any) -> None:
    capture, body = probe(module.build_splitter)
    assert capture.name == "splitter"
    assert len(body["reactors"]) == 1
    assert body["muzzles"] == []


def test_p05_splitter_pod_is_a_bare_pod_with_a_reactor_and_no_gun(probe: Any) -> None:
    capture, body = probe(module.build_splitter_pod)
    assert capture.name == "splitter-pod"
    assert len(body["reactors"]) == 1
    assert body["muzzles"] == []
    assert len(body["parts"].flesh.geometry.positions) > 0
