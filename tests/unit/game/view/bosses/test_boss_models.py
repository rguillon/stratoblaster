# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/boss_models.py`."""

import importlib
import math
import pathlib
from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config import bosses as bosses_config
from game.view.bosses.boss_models import BOSS_MODELS

CONFIG_ROOT = pathlib.Path(bosses_config.__file__).parent

_STUB_REASON = "CPython only: the drawing comes from a __pragma__('js') helper (None under CPython)"
_RECORD_REASON = (
    "CPython only: the draw reads a Transcrypt object literal with attribute access (a dict here)"
)

# Bosses whose drawing is built by a Transcrypt-only `__pragma__("js")` helper: the model cannot be
# probed under CPython, so its drawing is not checked here.
CPYTHON_STUBBED: set[str] = set()

# Bosses whose whole drawing is None under CPython (the body and parts cannot be read).
CPYTHON_NO_DRAWING: set[str] = set()

# Bosses whose drawings read object literals with attribute access, which Transcrypt compiles to JS
# objects but CPython runs as dicts (or records, or calls): they cannot run on real builders here.
CPYTHON_RECORDS = {}


def _config_boss_ids() -> set[str]:
    """Return the ids of every boss design in `game/config/bosses`."""
    modules = ["mini_bosses", "final_bosses"]
    for world in ("world_2", "world_3", "world_4"):
        modules.extend(
            f"{world}.{path.stem}"
            for path in sorted((CONFIG_ROOT / world).glob("*.py"))
            if path.name != "__init__.py"
        )
    ids: set[str] = set()
    for name in modules:
        module = importlib.import_module(f"game.config.bosses.{name}")
        for value in vars(module).values():
            boss_id = getattr(value, "id", None)
            if isinstance(boss_id, str) and hasattr(value, "stats"):
                ids.add(boss_id)
    return ids


# ENG-163: a known CPython-only gap is a strict xfail with its reason, never a skip.
def _with_reason(boss_id: str, reason: str) -> Any:
    return pytest.param(
        boss_id,
        marks=pytest.mark.xfail(strict=True, reason=reason),
        id=boss_id,
    )


def test_every_boss_design_has_its_model_and_no_model_is_orphaned() -> None:
    """BOSS-01: every boss design has its own model, and every model a design."""
    assert set(BOSS_MODELS) == _config_boss_ids()
    assert len(BOSS_MODELS) == 40


@pytest.mark.parametrize(
    "boss_id",
    [
        _with_reason(key, _STUB_REASON) if key in CPYTHON_STUBBED else key
        for key in sorted(BOSS_MODELS)
    ],
)
def test_each_boss_model_draws_every_part_its_design_has(monkeypatch: Any, boss_id: Any) -> None:
    """BOSS-47, and each boss file's parts requirement (e.g. MB-REEF-WARDEN-03)."""
    capture = probe_builder(monkeypatch, BOSS_MODELS[boss_id])
    assert capture.design.id == boss_id
    design_parts = sorted(part.id for part in capture.design.stats.parts)
    drawn = list((capture.drawing.get("parts") or {}).keys())
    # Hidden weapons are drawn from their look (`hidden_weapon_shapes`).
    drawn.extend((capture.design.get("weapons") or {}).keys())
    assert sorted(set(drawn)) == design_parts


@pytest.mark.parametrize(
    "boss_id",
    [
        _with_reason(key, _STUB_REASON)
        if key in CPYTHON_NO_DRAWING
        else _with_reason(key, _RECORD_REASON)
        if key in CPYTHON_RECORDS
        else key
        for key in sorted(BOSS_MODELS)
    ],
)
def test_each_boss_model_builds_geometry_for_its_body_and_parts(
    monkeypatch: Any, boss_id: Any
) -> None:
    """BOSS-47: each model builds geometry for its body and parts."""
    capture = probe_builder(monkeypatch, BOSS_MODELS[boss_id])
    drawings = drawings_of(capture)
    assert "body" in drawings
    body_faces = sum(len(d["parts"].hull.geometry.positions) for d in drawings.values())
    assert body_faces > 0
    for name, drawing in drawings.items():
        for coords in (
            drawing["parts"].hull.geometry.positions,
            drawing["parts"].flesh.geometry.positions,
            drawing["parts"].neon.geometry.positions,
        ):
            assert not any(math.isnan(v) for v in coords), f"{boss_id} {name}: NaN in geometry"


def test_mb_scorpion_03_the_scorpion_model_has_jointed_arms_and_a_jaw_on_each_side(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, BOSS_MODELS["scorpion"])
    limbs = sorted(capture.drawing["limbs"].keys())
    assert "shoulder-left" in limbs
    assert "shoulder-right" in limbs
    assert "jaw-left-outer" in limbs
    assert "jaw-right-outer" in limbs
