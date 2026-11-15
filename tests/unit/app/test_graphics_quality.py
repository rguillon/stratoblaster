# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/graphics_quality.py` (D-410)."""

from typing import Any

import pytest

from app import graphics_quality
from app.graphics_quality import QUALITY_MODES, GraphicsQuality, parse_level, saved_level_key
from config.engine import ENGINE_CONFIG


class _Storage:
    def __init__(self, values: dict[str, str] | None = None) -> None:
        self.values = dict(values or {})

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str) -> None:
        self.values[key] = value


@pytest.fixture
def applied(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, float, str]]:
    calls: list[tuple[Any, float, str]] = []
    monkeypatch.setattr(
        graphics_quality,
        "apply_quality",
        lambda scene, scale, shadows: calls.append((scene, scale, shadows)),
    )
    monkeypatch.setattr(graphics_quality, "gpu_frame_ms", lambda _timer: None)
    return calls


def _quality(storage: _Storage, scales: list[float]) -> GraphicsQuality:
    return GraphicsQuality(ENGINE_CONFIG.quality, storage, "game", scales.append, "timer")


def _slow(quality: GraphicsQuality, scene: Any, count: int) -> None:
    for i in range(count):
        quality.frame(1000 / 60 if i % 2 == 0 else 1000 / 30, 3.0, scene, True)


def test_d410_a_saved_level_is_a_digit_within_the_levels() -> None:
    assert saved_level_key("game") == "game_graphics_level"
    assert parse_level("3", 5) == 3
    for raw in [None, "", "7", "12", "x", "-1"]:
        assert parse_level(raw, 5) == 0


def test_d410_the_session_starts_at_the_saved_level(applied: list[Any]) -> None:
    scales: list[float] = []
    quality = _quality(_Storage({"game_graphics_level": "2"}), scales)
    assert quality.level == 2
    assert quality.mode == "auto"
    assert scales == [ENGINE_CONFIG.quality.levels[2].render_scale]
    # No scene yet (the menus): nothing else to apply.
    assert applied == []


def test_d410_a_level_scene_gets_the_level_when_first_seen(applied: list[Any]) -> None:
    quality = _quality(_Storage(), [])
    quality.frame(16.7, 3.0, "scene", False)
    quality.frame(16.7, 3.0, "scene", False)
    assert applied == [("scene", 1.0, "medium")]


def test_d410_slow_play_lowers_the_level_applies_and_saves_it(applied: list[Any]) -> None:
    storage = _Storage()
    scales: list[float] = []
    quality = _quality(storage, scales)
    _slow(quality, "scene", 400)
    assert quality.level >= 1
    level = ENGINE_CONFIG.quality.levels[quality.level]
    assert scales[-1] == level.render_scale
    assert applied[-1] == ("scene", level.render_scale, level.shadow_filter)
    assert storage.values["game_graphics_level"] == str(quality.level)


@pytest.mark.usefixtures("applied")
def test_d410_menus_loading_and_pauses_are_not_judged() -> None:
    quality = _quality(_Storage(), [])
    for i in range(400):
        quality.frame(1000 / 60 if i % 2 == 0 else 1000 / 30, 3.0, None, False)
    assert quality.level == 0


@pytest.mark.usefixtures("applied")
def test_d410_the_setting_holds_a_level_or_lets_the_game_decide() -> None:
    storage = _Storage({"game_graphics_level": "1"})
    scales: list[float] = []
    quality = _quality(storage, scales)
    assert QUALITY_MODES == ["auto", "high", "medium", "low"]
    quality.set_mode("low")
    assert quality.level == ENGINE_CONFIG.quality.low
    # A held level is not changed by slow frames.
    _slow(quality, "scene", 400)
    assert quality.level == ENGINE_CONFIG.quality.low
    quality.set_mode("medium")
    assert quality.level == ENGINE_CONFIG.quality.medium
    quality.set_mode("high")
    assert quality.level == 0
    # The same mode again, or an unknown one, changes nothing.
    quality.set_mode("high")
    quality.set_mode("ultra")
    assert quality.mode == "high"
    # Auto starts again from the level the game chose last.
    quality.set_mode("auto")
    assert quality.level == 1
    assert scales[-1] == ENGINE_CONFIG.quality.levels[1].render_scale


def test_d410_back_in_the_menus_the_scene_is_let_go(applied: list[Any]) -> None:
    quality = _quality(_Storage(), [])
    quality.frame(16.7, 3.0, "scene", True)
    quality.frame(16.7, 3.0, None, False)
    quality.set_mode("low")
    # No scene to apply the held level to: only the page's pixels change.
    assert applied == [("scene", 1.0, "medium")]
