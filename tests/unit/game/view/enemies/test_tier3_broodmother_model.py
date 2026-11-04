# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/tier3_broodmother_model.py`."""

from typing import Any

from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import tier3_broodmother_model as module

# About the triangles of one reactor's nozzle, core and flame (`ENEMY_LOOK.reactor`).
REACTOR_TRIANGLES = 40


def _body(monkeypatch: Any) -> Any:
    return drawings_of(probe_builder(monkeypatch, module.build_broodmother))["body"]


def test_enm_broodmother_01_it_is_built_as_the_broodmother_kind_in_its_neon(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, module.build_broodmother)
    assert capture.name == "broodmother"
    assert capture.neon == ENEMY_LOOK.neon.broodmother


def test_enm_broodmother_02_the_body_is_flesh_under_metal_armour_plates(monkeypatch: Any) -> None:
    parts = _body(monkeypatch)["parts"]
    assert len(parts.flesh.geometry.positions) > 0
    assert len(parts.hull.geometry.positions) > 0
    # Eyes and veins are lit.
    assert len(parts.vein.geometry.positions) > 0


def test_enm_broodmother_03_egg_sacs_are_charge_lights_along_both_flanks(monkeypatch: Any) -> None:
    charge = _body(monkeypatch)["parts"].charge.geometry.positions
    xs = [charge[i] for i in range(0, len(charge), 3)]
    assert min(xs) < -module.EGG_OUT + 1
    assert max(xs) > module.EGG_OUT - 1


def test_enm_broodmother_04_the_hatch_muzzle_is_where_the_phantoms_come_out(
    monkeypatch: Any,
) -> None:
    muzzles = _body(monkeypatch)["muzzles"]
    assert [kind for _at, kind in muzzles] == ["launch"]
    at = muzzles[0][0]
    # Model Z is down the screen's Y, and the hatch hangs below the body.
    assert at[2] == -BROODMOTHER_CONFIG.port[1]
    assert at[0] == BROODMOTHER_CONFIG.port[0]
    assert at[1] < 0


def test_enm_broodmother_05_it_has_two_reactors_within_the_tier_3_triangle_budget(
    monkeypatch: Any,
) -> None:
    body = _body(monkeypatch)
    assert len(body["reactors"]) == 2
    parts = body["parts"]
    triangles = sum(
        len(builder.geometry.indices) // 3
        for builder in [parts.hull, parts.flesh, parts.neon, parts.vein, parts.charge]
    )
    triangles += REACTOR_TRIANGLES * len(body["reactors"])
    assert triangles <= ENEMY_LOOK.budget.tier3
