# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/debug/play_scene.py` (D-290: the playfield for the AI player)."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers import js_shims

from debug import play_scene as play_scene_module
from debug import test_api
from debug.play_scene import play_scene
from debug.test_api import install_test_api, scene_state


@pytest.fixture(autouse=True)
def js_twins(monkeypatch: pytest.MonkeyPatch) -> None:
    for module in (play_scene_module, test_api):
        monkeypatch.setattr(module, "js_object", js_shims.js_object)
        monkeypatch.setattr(module, "js_set", js_shims.js_set)


def _target(x: float, health: float = 10, gone: bool = False, **more: Any) -> SimpleNamespace:
    return SimpleNamespace(x=x, y=500, radius=20, health=health, max_health=20, gone=gone, **more)


def _run(boss: Any = None, hull: bool = True, bombs: Any = 2, bonuses: bool = True) -> Any:
    enemies = [_target(100), _target(200, gone=True)]
    if boss is not None:
        enemies.append(boss)
    shots = SimpleNamespace(
        bullets=[
            SimpleNamespace(alive=True, x=1, y=2, heading=3, speed=4),
            SimpleNamespace(alive=False, x=0, y=0, heading=0, speed=0),
        ],
        missiles=[SimpleNamespace(alive=True, x=5, y=6, heading=7, speed=8)],
        lasers=[SimpleNamespace(x=9, y=10, heading=11, length=12, phase="warning")],
    )
    active = None if bombs != "active" else object()
    return SimpleNamespace(
        ship=SimpleNamespace(x=500, y=90, vx=10, vy=-5, max_speed=400),
        hull=SimpleNamespace(health=80, max_health=100, lives=2, invincible=0.5) if hull else None,
        bombs=SimpleNamespace(count=2, active=active) if bombs is not None else None,
        arsenal=SimpleNamespace(
            snapshot=lambda: SimpleNamespace(weapon="laser", levels={"bullet": 2, "laser": 3})
        ),
        track=SimpleNamespace(progress=1200, length_=16800),
        fights=SimpleNamespace(boss=boss, active=boss is not None, rank="mini" if boss else None),
        enemies=SimpleNamespace(enemies=enemies, shots=shots),
        bonuses=SimpleNamespace(bonuses=[SimpleNamespace(x=300, y=400, kind="life")])
        if bonuses
        else None,
    )


def test_d_265_the_scene_has_the_ship_its_supplies_weapons_and_the_level() -> None:
    scene = play_scene(_run())
    assert scene["ship"] == [500, 90, 10, -5, 400]
    assert scene["hull"] == [80, 100, 2, 0.5]
    assert scene["bombs"] == [2, False]
    assert scene["weapon"] == "laser"
    assert scene["weapons"] == [["bullet", 2], ["laser", 3]]
    assert scene["track"] == [1200, 16800]
    assert scene["boss"] == [False, None, 0, 0]


def test_d_265_the_scene_has_the_enemies_shots_lasers_and_bonuses() -> None:
    scene = play_scene(_run())
    assert scene["targets"] == [[100, 500, 20, 10, 20, False]]  # the one gone is left out
    assert scene["bullets"] == [[1, 2, 3, 4]]  # the free entry of the pool too
    assert scene["missiles"] == [[5, 6, 7, 8]]
    assert scene["lasers"] == [[9, 10, 11, 12, False]]
    assert scene["bonuses"] == [[300, 400, "life"]]


def test_d_265_a_boss_shows_its_pieces_or_itself_when_none_can_be_hit() -> None:
    part = _target(450, health=5)
    boss = _target(400, health=300, shot_targets=[part])
    boss.max_health = 600
    scene = play_scene(_run(boss=boss))
    assert scene["boss"] == [True, "mini", 300, 600]
    assert scene["targets"][-1] == [450, 500, 20, 5, 20, True]
    boss.shot_targets = []
    scene = play_scene(_run(boss=boss))
    assert scene["targets"][-1] == [400, 500, 20, 300, 600, True]


def test_d_265_no_hull_no_bombs_no_bonuses_and_a_bomb_going_off() -> None:
    scene = play_scene(_run(hull=False, bombs=None, bonuses=False))
    assert scene["hull"] is None
    assert scene["bombs"] is None
    assert scene["bonuses"] == []
    assert play_scene(_run(bombs="active"))["bombs"] == [2, True]


def test_d_265_get_scene_is_the_level_played_or_null() -> None:
    run = _run()
    playing = SimpleNamespace(game=lambda: SimpleNamespace(run=run))
    assert scene_state(playing)["track"] == [1200, 16800]
    assert scene_state(SimpleNamespace(game=lambda: None)) is None
    window: dict[str, Any] = {}
    api = install_test_api(window, playing)
    assert api["getScene"]()["ship"][0] == 500
