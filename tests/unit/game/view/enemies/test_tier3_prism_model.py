# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/tier3_prism_model.py`."""

from typing import Any

from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_prism import PRISM_CONFIG
from game.view.enemies import tier3_prism_model as module

# About the triangles of one reactor's nozzle, core and flame (`ENEMY_LOOK.reactor`).
REACTOR_TRIANGLES = 40


def _body(monkeypatch: Any) -> Any:
    return drawings_of(probe_builder(monkeypatch, module.build_prism))["body"]


def test_enm_prism_01_prism_is_built_as_the_prism_kind_in_its_neon(monkeypatch: Any) -> None:
    capture = probe_builder(monkeypatch, module.build_prism)
    assert capture.name == "prism"
    assert capture.neon == ENEMY_LOOK.neon.prism


def test_enm_prism_02_prism_has_a_metal_hull_and_a_glowing_core_crystal(monkeypatch: Any) -> None:
    parts = _body(monkeypatch)["parts"]
    assert len(parts.hull.geometry.positions) > 0
    # The core crystal is lit as a vein, and the wings' edges are neon.
    assert len(parts.vein.geometry.positions) > 0
    assert len(parts.neon.geometry.positions) > 0


def test_enm_prism_04_prism_has_two_emitters_at_the_muzzles_of_its_lasers(monkeypatch: Any) -> None:
    body = _body(monkeypatch)
    muzzles = body["muzzles"]
    assert [kind for _at, kind in muzzles] == ["laser", "laser"]
    # The model's muzzles are the config's emitters: model Z is down the screen's Y.
    drawn = sorted((at[0], at[1], at[2]) for at, _kind in muzzles)
    wanted = sorted((e[0], e[2], -e[1]) for e in PRISM_CONFIG.emitters)
    assert drawn == wanted
    # Their mouths are charge lights.
    assert len(body["parts"].charge.geometry.positions) > 0


def test_enm_prism_03_prism_stays_within_the_tier_3_triangle_budget(monkeypatch: Any) -> None:
    body = _body(monkeypatch)
    parts = body["parts"]
    triangles = sum(
        len(builder.geometry.indices) // 3
        for builder in [parts.hull, parts.flesh, parts.neon, parts.vein, parts.charge]
    )
    triangles += REACTOR_TRIANGLES * len(body["reactors"])
    assert triangles <= ENEMY_LOOK.budget.tier3
