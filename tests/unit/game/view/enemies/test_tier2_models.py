# Copyright (c) 2026 Renaud Guillon
"""Unit tests of the tier 2 enemy models (Harrier, Sweeper, Hatchery)."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import tier2_harrier_model, tier2_hatchery_model, tier2_sweeper_model
from game.view.enemies.enemy_models import ENEMY_MODELS

# Triangles of one reactor (`ENEMY_LOOK.reactor`: about 40).
REACTOR_TRIANGLES = 40

MODELS = [
    ("harrier", tier2_harrier_model.build_harrier),
    ("sweeper", tier2_sweeper_model.build_sweeper),
    ("hatchery", tier2_hatchery_model.build_hatchery),
]


def _body(monkeypatch: Any, builder: Any) -> tuple[Any, Any]:
    capture = probe_builder(monkeypatch, builder)
    return capture, drawings_of(capture)["body"]


def _triangles(body: Any) -> int:
    parts = body["parts"]
    total = len(body["reactors"]) * REACTOR_TRIANGLES
    for builder in (parts.hull, parts.flesh, parts.vein, parts.neon, parts.charge):
        total += len(builder.geometry.indices) // 3
    return total


@pytest.mark.parametrize(("kind", "builder"), MODELS)
def test_enm_tier2_the_kind_is_built_under_its_own_key_in_its_tier_neon(
    monkeypatch: Any, kind: str, builder: Any
) -> None:
    """ENM-HARRIER-04, ENM-SWEEPER-04, ENM-HATCHERY-04: tier 2's lime neon, under the kind's key."""
    capture, body = _body(monkeypatch, builder)
    assert capture.name == kind
    assert capture.neon == ENEMY_LOOK.neon[kind]
    assert ENEMY_MODELS[kind] is builder
    assert len(body["parts"].neon.geometry.positions) > 0
    assert len(body["parts"].hull.geometry.positions) > 0
    assert len(body["parts"].flesh.geometry.positions) > 0


@pytest.mark.parametrize(("kind", "builder"), MODELS)
def test_enm_tier2_the_model_stays_in_the_tier_2_triangle_budget(
    monkeypatch: Any, kind: str, builder: Any
) -> None:
    """ENM-HARRIER-10, ENM-SWEEPER-10, ENM-HATCHERY-10: the triangle budget of tier 2."""
    _capture, body = _body(monkeypatch, builder)
    assert _triangles(body) <= ENEMY_LOOK.budget.tier2, kind


def test_enm_harrier_01_the_harrier_is_a_dart_with_one_reactor(monkeypatch: Any) -> None:
    """Also ENM-HARRIER-04: one reactor, in lime neon."""
    _capture, body = _body(monkeypatch, tier2_harrier_model.build_harrier)
    assert len(body["reactors"]) == 1
    assert len(body["parts"].neon.geometry.positions) > 0


def test_enm_harrier_02_the_harrier_has_twin_rails_with_charge_lights(monkeypatch: Any) -> None:
    """Also ENM-HARRIER-03: the rails' charge lights."""
    _capture, body = _body(monkeypatch, tier2_harrier_model.build_harrier)
    kinds = [kind for _at, kind in body["muzzles"]]
    assert kinds == ["missile", "missile"]
    xs = sorted(at[0] for at, _kind in body["muzzles"])
    assert xs[0] == -xs[1]
    assert len(body["parts"].charge.geometry.positions) > 0


def test_enm_sweeper_02_the_sweeper_has_one_laser_emitter_with_a_charge_light(
    monkeypatch: Any,
) -> None:
    """Also ENM-SWEEPER-01 (a disc and its barrel) and ENM-SWEEPER-03 (the charge light)."""
    _capture, body = _body(monkeypatch, tier2_sweeper_model.build_sweeper)
    assert [kind for _at, kind in body["muzzles"]] == ["laser"]
    assert len(body["parts"].charge.geometry.positions) > 0


def test_enm_sweeper_04_the_sweeper_has_three_reactors(monkeypatch: Any) -> None:
    _capture, body = _body(monkeypatch, tier2_sweeper_model.build_sweeper)
    assert len(body["reactors"]) == 3


def test_enm_hatchery_02_the_hatchery_has_a_hatch_with_a_charge_light(monkeypatch: Any) -> None:
    """Also ENM-HATCHERY-03: the charge light."""
    _capture, body = _body(monkeypatch, tier2_hatchery_model.build_hatchery)
    assert len(body["parts"].charge.geometry.positions) > 0
    assert body["muzzles"] == []


def test_enm_hatchery_04_the_hatchery_has_two_reactors(monkeypatch: Any) -> None:
    _capture, body = _body(monkeypatch, tier2_hatchery_model.build_hatchery)
    assert len(body["reactors"]) == 2


def test_enm_hatchery_01_the_plates_outline_is_a_hexagon_round_its_centre() -> None:
    outline = tier2_hatchery_model.plate_outline([10, 9, 4, 3])
    assert len(outline) == 6
    assert min(p[1] for p in outline) == 7
    assert max(p[1] for p in outline) == 13
