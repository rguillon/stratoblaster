# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/background_loader.py`: the worker's jobs and replies (PERF-14).

The worker is a fake port that records what is posted; the JavaScript `Map`s are dicts, the
messages plain namespaces, and `to_plain` (ENG-164) wraps what it copies so a test can tell it was
copied.
"""

import json
from types import SimpleNamespace
from typing import Any

import pytest

from render.scenery import background_loader
from render.scenery.background_loader import BackgroundLoader, start_background_loader
from render.scenery.level_ground import GroundReplies
from render.scenery.procedural_textures import TextureJob

# The JavaScript-only helpers as the module defines them, taken before the fixture replaces them.
JS_HELPERS: list[tuple[Any, tuple[Any, ...], Any]] = [
    (background_loader._new_map, (), None),
    (background_loader._map_has, ({}, 1), False),
    (background_loader._map_get, ({}, 1), None),
    (background_loader._map_set, ({}, 1, 2), None),
    (background_loader._map_delete, ({}, 1), None),
    (background_loader._map_values, ({},), []),
    (background_loader._map_clear, ({},), None),
    (background_loader._json_of, ({"a": 1},), ""),
    (background_loader._ground_message, (0, None, 7), None),
    (background_loader._texture_message, (0, None), None),
    (background_loader._chunks_message, (0, 100.0), None),
    (background_loader._roads_message, (0, [], None, False), None),
    (background_loader._worker_available, (), False),
    (background_loader._new_game_worker, (), None),
]


class FakePort:
    """A worker without `terminate`: records the messages posted to it."""

    def __init__(self) -> None:
        self.posted: list[Any] = []
        self.onmessage: Any = None
        self.onerror: Any = None

    def postMessage(self, message: Any) -> None:
        self.posted.append(message)

    def reply(self, **fields: Any) -> None:
        """Answer as the worker: `onmessage` gets an event whose `data` has `fields`."""
        self.onmessage(SimpleNamespace(data=SimpleNamespace(**fields)))


class StoppablePort(FakePort):
    def __init__(self) -> None:
        super().__init__()
        self.terminated = False

    def terminate(self) -> None:
        self.terminated = True


class Replies:
    """What a ground generation sent back, in order, with the `ask` calls it was given."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.ask: Any = None
        self.ask_roads: Any = None

    def ground(self, made: Any, ask: Any, ask_roads: Any) -> None:
        self.calls.append(("ground", made))
        self.ask = ask
        self.ask_roads = ask_roads

    def as_replies(self) -> GroundReplies:
        return GroundReplies(
            self.ground,
            lambda made: self.calls.append(("runout", made)),
            lambda made: self.calls.append(("chunks", made)),
        )


class Env:
    """What the loader called outside itself: the generators it installed, the textures kept."""

    def __init__(self) -> None:
        self.generators: list[Any] = []
        self.kept: dict[str, Any] = {}


def _message(kind: str, **fields: Any) -> SimpleNamespace:
    return SimpleNamespace(kind=kind, **fields)


@pytest.fixture(autouse=True)
def env(monkeypatch: pytest.MonkeyPatch) -> Env:
    recorded = Env()
    loader = background_loader
    monkeypatch.setattr(loader, "_new_map", dict)
    monkeypatch.setattr(loader, "_map_has", lambda c, k: k in c)
    monkeypatch.setattr(loader, "_map_get", lambda c, k: c[k])
    monkeypatch.setattr(loader, "_map_set", lambda c, k, v: c.__setitem__(k, v))
    # `Map.delete` of a missing key does nothing.
    monkeypatch.setattr(loader, "_map_delete", lambda c, k: c.pop(k, None))
    monkeypatch.setattr(loader, "_map_values", lambda c: list(c.values()))
    monkeypatch.setattr(loader, "_map_clear", dict.clear)
    monkeypatch.setattr(loader, "_json_of", lambda v: json.dumps(v, default=vars))
    monkeypatch.setattr(
        loader,
        "_ground_message",
        lambda job_id, level, seed: _message("ground", level=level, seed=seed, id=job_id),
    )
    monkeypatch.setattr(
        loader, "_texture_message", lambda job_id, job: _message("texture", job=job, id=job_id)
    )
    monkeypatch.setattr(
        loader,
        "_chunks_message",
        lambda job_id, through: _message("chunks", id=job_id, through=through),
    )
    monkeypatch.setattr(
        loader,
        "_roads_message",
        lambda ground, spans, look, grid: _message(
            "roads", ground=ground, spans=spans, look=look, grid=grid
        ),
    )
    monkeypatch.setattr(loader, "to_plain", lambda value: {"plain": value})
    monkeypatch.setattr(loader, "generate_grounds_with", recorded.generators.append)
    monkeypatch.setattr(loader, "has_texture", lambda job: _texture_key(job) in recorded.kept)
    monkeypatch.setattr(
        loader,
        "keep_texture",
        lambda job, pixels: recorded.kept.__setitem__(_texture_key(job), pixels),
    )
    return recorded


def _texture_key(job: TextureJob) -> str:
    return job.name + ":" + json.dumps(job.args)


def _ground_job(loader: BackgroundLoader, level: Any = "level", seed: int = 7) -> Replies:
    """Ask `loader` for a ground (as `level_ground` does): what comes back is recorded."""
    replies = Replies()
    loader._ground_generator(level, seed, replies.as_replies())
    return replies


@pytest.mark.parametrize(("helper", "args", "placeholder"), JS_HELPERS)
def test_the_javascript_helpers_return_their_placeholder_under_cpython(
    helper: Any, args: tuple[Any, ...], placeholder: Any
) -> None:
    """The `Map`, JSON, message and `Worker` helpers are `__pragma__("js")` bodies.

    CPython runs only the placeholder return after them.
    """
    assert helper(*args) == placeholder


def test_perf_14_the_loader_listens_to_the_worker_and_takes_over_the_grounds(env: Env) -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    assert port.onmessage == loader._on_message
    assert port.onerror == loader._on_error
    assert env.generators == [loader._ground_generator]


def test_perf_14_eng_164_a_ground_job_posts_the_level_as_plain_data() -> None:
    port = FakePort()
    _ground_job(BackgroundLoader(port), "the level", 42)
    [message] = port.posted
    assert message.kind == "ground"
    assert message.level == {"plain": "the level"}
    assert message.seed == 42
    assert message.id == 0


def test_perf_14_each_job_has_its_own_id() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    _ground_job(loader)
    _ground_job(loader)
    assert [m.id for m in port.posted] == [0, 1]


def test_perf_14_a_ground_waits_for_its_runout_and_its_last_chunks() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    replies = _ground_job(loader)
    port.reply(id=0, ground="ground")
    assert replies.calls == [("ground", "ground")]
    port.reply(id=0, runout="runout", chunks=None)
    port.reply(id=0, runout=None, chunks=["a"], done=False)
    assert 0 in loader._waiting.handlers
    port.reply(id=0, runout=None, chunks=["b"], done=True)
    assert replies.calls == [
        ("ground", "ground"),
        ("runout", "runout"),
        ("chunks", ["a"]),
        ("chunks", ["b"]),
    ]
    assert 0 not in loader._waiting.handlers


def test_perf_14_the_last_chunks_before_the_runout_keep_the_job_waiting() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    replies = _ground_job(loader)
    port.reply(id=0, ground="ground")
    port.reply(id=0, runout=None, chunks=["a"], done=True)
    assert 0 in loader._waiting.handlers
    port.reply(id=0, runout="runout", chunks=None)
    assert replies.calls[-1] == ("runout", "runout")
    assert 0 not in loader._waiting.handlers


def test_perf_14_a_ground_that_failed_in_the_worker_is_handed_back_as_none() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    replies = _ground_job(loader)
    port.reply(id=0, ground=None)
    assert replies.calls == [("ground", None)]
    assert 0 not in loader._waiting.handlers


def test_perf_14_the_chunks_are_asked_for_under_the_ground_job_id() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    _ground_job(loader)
    replies = _ground_job(loader)
    port.reply(id=1, ground="ground")
    replies.ask(2500.0)
    message = port.posted[-1]
    assert (message.kind, message.id, message.through) == ("chunks", 1, 2500.0)


def test_eng_164_the_street_surfaces_are_asked_for_with_a_plain_look() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    replies = _ground_job(loader)
    port.reply(id=0, ground="ground")
    taken: list[Any] = []
    replies.ask_roads([[3, 0, 100]], "look", True, taken.append)
    message = port.posted[-1]
    assert message.kind == "roads"
    assert message.ground == 0
    assert message.spans == [[3, 0, 100]]
    assert message.look == {"plain": "look"}
    assert message.grid is True
    # The roads request is a job of its own, answered once.
    assert message.id == 1
    port.reply(id=1, chunks=["street"], atlas=None)
    assert [reply.chunks for reply in taken] == [["street"]]
    assert 1 not in loader._waiting.handlers


def test_a_reply_to_no_job_waiting_is_ignored() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    replies = _ground_job(loader)
    port.reply(id=9, ground="other")
    assert replies.calls == []
    assert list(loader._waiting.handlers) == [0]


def test_perf_14_a_broken_worker_fails_every_job_waiting() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    before = _ground_job(loader)
    after = _ground_job(loader)
    port.reply(id=1, ground="ground")
    port.onerror(SimpleNamespace(message="boom"))
    # The job not answered yet hands back no ground; the other just stops waiting.
    assert before.calls == [("ground", None)]
    assert after.calls == [("ground", "ground")]
    assert loader._waiting.handlers == {}


def test_perf_14_eng_164_textures_not_kept_are_posted_as_plain_jobs() -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    job = TextureJob("noise", [64, 8, 3])
    loader.prefetch_textures([job])
    [message] = port.posted
    assert (message.kind, message.id) == ("texture", 0)
    assert message.job == {"plain": job}


def test_perf_14_a_texture_kept_or_on_its_way_is_not_asked_for_again(env: Env) -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    kept = TextureJob("ground", [64, "look", 1])
    env.kept[_texture_key(kept)] = "pixels"
    asked = TextureJob("noise", [64, 8, 3])
    loader.prefetch_textures([kept, asked, TextureJob("noise", [64, 8, 3])])
    assert [m.job for m in port.posted] == [{"plain": asked}]


def test_perf_14_the_pixels_of_a_texture_reply_are_kept(env: Env) -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    job = TextureJob("water", [64, 1])
    loader.prefetch_textures([job])
    port.reply(id=0, pixels=[1, 2, 3, 4])
    assert env.kept == {_texture_key(job): [1, 2, 3, 4]}
    assert loader._textures == {}
    assert loader._waiting.handlers == {}


def test_perf_14_a_texture_that_failed_is_asked_for_again_next_time(env: Env) -> None:
    port = FakePort()
    loader = BackgroundLoader(port)
    job = TextureJob("water", [64, 1])
    loader.prefetch_textures([job])
    port.reply(id=0, pixels=None)
    assert env.kept == {}
    loader.prefetch_textures([job])
    loader._on_error(None)
    assert env.kept == {}
    assert [m.id for m in port.posted] == [0, 1]
    assert loader._textures == {}


def test_perf_14_stopping_hands_the_grounds_back_and_ends_the_worker(env: Env) -> None:
    port = StoppablePort()
    loader = BackgroundLoader(port)
    loader.stop()
    assert env.generators == [loader._ground_generator, None]
    assert port.terminated


def test_perf_14_a_port_that_cannot_be_ended_is_only_let_go(env: Env) -> None:
    loader = BackgroundLoader(FakePort())
    loader.stop()
    assert env.generators[-1] is None


def test_perf_14_without_workers_there_is_no_loader() -> None:
    # CPython has no `Worker`: the real check says so.
    assert start_background_loader() is None


def test_perf_14_with_workers_the_loader_runs_on_the_game_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    port = StoppablePort()
    monkeypatch.setattr(background_loader, "_worker_available", lambda: True)
    monkeypatch.setattr(background_loader, "_new_game_worker", lambda: port)
    loader = start_background_loader()
    assert loader is not None
    assert loader.port is port
    assert port.onmessage == loader._on_message
