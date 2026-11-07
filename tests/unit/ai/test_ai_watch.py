# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/watch.py`: the brain at the controls of the browser game."""

import json
import threading
from http.client import HTTPConnection
from typing import Any

from ai.brain import Brain, BrainShape
from ai.game_env import MOVES, Action, EpisodeSetup, GameEnv
from ai.observation import observe, observe_scene, scene_of
from ai.watch import (
    AI_PATH,
    BOMB_KEY,
    FIRE_KEY,
    MOVE_KEYS,
    SWITCH_KEY,
    Player,
    make_server,
    page_query,
)

SMALL = BrainShape(hidden=32, field_features=16, fovea_features=16, state_features=8)
DIRECTIONS = {"ArrowUp": (0, 1), "ArrowDown": (0, -1), "ArrowLeft": (-1, 0), "ArrowRight": (1, 0)}


def _reading(env: GameEnv, attempt: int = 1) -> dict[str, Any]:
    """Return what the page gives for the level of `env` (its scene is what `getScene()` builds)."""
    return {
        "level": env.setup.level_id,
        "attempt": attempt,
        "time": env.time,
        "duration": 240.0,
        "scene": scene_of(env).data,
    }


def test_each_move_presses_the_arrows_of_its_direction() -> None:
    assert len(MOVE_KEYS) == len(MOVES)
    for keys, (dx, dy) in zip(MOVE_KEYS, MOVES, strict=True):
        x = sum(DIRECTIONS[k][0] for k in keys)
        y = sum(DIRECTIONS[k][1] for k in keys)
        assert (x, y) == ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))


def test_the_browser_scene_is_seen_as_the_python_one() -> None:
    env = GameEnv(EpisodeSetup("1-1"))
    for _ in range(200):
        env.step(Action(3))
    mine = observe(env)
    seen = observe_scene(scene_of(env))
    assert (mine.field == seen.field).all()
    assert (mine.fovea == seen.fovea).all()


def test_in_a_level_the_brain_fires_and_moves_and_outside_it_lets_go() -> None:
    player = Player(Brain(SMALL), greedy=False)
    env = GameEnv(EpisodeSetup("1-1"))
    keys = player.keys(_reading(env))
    assert FIRE_KEY in keys
    assert keys - {FIRE_KEY, BOMB_KEY, SWITCH_KEY} <= set(DIRECTIONS)
    assert player.keys(None) == set()


def test_its_memory_starts_over_with_each_attempt() -> None:
    player = Player(Brain(SMALL), greedy=True)
    env = GameEnv(EpisodeSetup("1-1"))
    player.keys(_reading(env))
    player.keys(_reading(env))
    assert player.memory.abs().sum() > 0
    remembered = player.memory.clone()
    player.keys(_reading(env, attempt=2))
    fresh = Player(Brain(SMALL), greedy=True)
    fresh.brain.load_state_dict(player.brain.state_dict())
    fresh.keys(_reading(env, attempt=2))
    assert (player.memory == fresh.memory).all()
    assert not (player.memory == remembered).all()


def test_the_game_is_asked_for_with_ai_and_the_level_only_when_given() -> None:
    assert page_query(None, None) == "?ai=1"
    assert page_query(None, "heavy") == "?ai=1"
    assert page_query("2-3", None) == "?ai=1&level=2-3"
    assert page_query("2-3", "heavy") == "?ai=1&level=2-3&ship=heavy"


def test_the_server_sends_the_game_on_with_ai_and_answers_with_the_keys() -> None:
    server = make_server(Player(Brain(SMALL), greedy=True), "?ai=1", "127.0.0.1", 0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_address[1], timeout=10)
        connection.request("GET", "/")
        reply = connection.getresponse()
        reply.read()
        assert reply.status == 302
        assert reply.getheader("Location") == "/index.html?ai=1"
        reading = _reading(GameEnv(EpisodeSetup("1-1")))
        connection.request("POST", AI_PATH, json.dumps(reading).encode())
        reply = connection.getresponse()
        keys = json.loads(reply.read())
        assert reply.status == 200
        assert FIRE_KEY in keys
        connection.request("POST", "/elsewhere", b"{}")
        reply = connection.getresponse()
        reply.read()
        assert reply.status == 404
    finally:
        server.shutdown()
        server.server_close()
